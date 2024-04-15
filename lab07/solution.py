from typing import List, Optional, NamedTuple

from common_types import ObjectName, Data, FileName, DataNodeIdx, DataSize
from helpers import pad_data, split_data, erasure_code, reconstruct, split_sequence
from underlying_api import MetadataKvs, DataNode, NodeUnhealthyException


class DiskUsageStats(NamedTuple):
    data_node_idx: DataNodeIdx
    used_space: DataSize


class ChunkLocation(NamedTuple):
    data_node_idx: DataNodeIdx
    file_name: FileName


ChunkSize = 16
NumOriginalChunks = 4
NumRedundantChunks = 1


class ObjectStorage:
    def __init__(self, metadata_kvs: MetadataKvs, data_nodes: List[DataNode]):
        self.metadata_kvs = metadata_kvs
        self.data_nodes = data_nodes
        self.num_nodes = len(self.data_nodes)

    def write_object(self, object_name: ObjectName, data: Data):
        output_chunks = self.erasure_code_blocks(self.split_into_blocks(data))
        num_chunks = len(output_chunks)

        disk_usage_stats = self.get_disk_usage_stats()
        used_nodes_indices = [stats.data_node_idx for stats in disk_usage_stats[:num_chunks]]
        chunk_locations = self.compute_chunk_locations(object_name, num_chunks, used_nodes_indices)

        for chunk, chunk_location in zip(output_chunks, chunk_locations):
            target_data_node = self.data_nodes[chunk_location.data_node_idx]
            target_data_node.write_file(chunk_location.file_name, chunk)

        metadata = (num_chunks, len(data), used_nodes_indices)
        self.metadata_kvs.write_key(object_name, self.metadata_kvs.kvs_encode(metadata))

    def read_object(self, object_name: ObjectName) -> Optional[Data]:
        raw_object_metadata = self.metadata_kvs.read_key(object_name)
        if raw_object_metadata is None:
            return None

        object_metadata = self.metadata_kvs.kvs_decode(raw_object_metadata)
        num_chunks, data_size, used_nodes_indices = object_metadata

        stored_chunks = self.read_chunks(object_name, num_chunks, used_nodes_indices)
        blocks = split_sequence(stored_chunks, NumOriginalChunks + NumRedundantChunks)
        output_chunks = []

        for block in blocks:
            block_chunks = block
            if [chunk for chunk in block if chunk is None]:
                block_chunks = reconstruct(block_chunks, ChunkSize)
            output_chunks.append(b''.join(block_chunks[:-NumRedundantChunks]))

        return b''.join(output_chunks)[:data_size]

    def delete_object(self, object_name: ObjectName):
        raw_object_metadata = self.metadata_kvs.read_key(object_name)
        if raw_object_metadata is None:
            return

        object_metadata = self.metadata_kvs.kvs_decode(raw_object_metadata)
        num_chunks, _, used_nodes_indices = object_metadata

        for chunk_location in self.compute_chunk_locations(object_name, num_chunks, used_nodes_indices):
            target_data_node = self.data_nodes[chunk_location.data_node_idx]
            target_data_node.delete_file(chunk_location.file_name)

        self.metadata_kvs.delete_key(object_name)

    def split_into_blocks(self, data):
        data_padded = pad_data(data, ChunkSize)
        input_chunks = split_data(data_padded, max_segment_size=ChunkSize)
        input_blocks = split_sequence(input_chunks, NumOriginalChunks)
        return input_blocks

    def erasure_code_blocks(self, input_blocks):
        output_blocks = [erasure_code(block) for block in input_blocks]
        output_chunks = [chunk for block in output_blocks for chunk in block]
        return output_chunks

    def read_chunks(self, object_name, num_chunks, used_nodes_indices):
        chunks = []
        for chunk_location in self.compute_chunk_locations(object_name, num_chunks, used_nodes_indices):
            target_data_node = self.data_nodes[chunk_location.data_node_idx]
            try:
                chunk = target_data_node.read_file(chunk_location.file_name)
            except NodeUnhealthyException:
                chunk = None
            chunks.append(chunk)
        return chunks

    def compute_chunk_locations(self, object_name: FileName, num_chunks: int, used_nodes_indices: List[DataNodeIdx]) -> List[ChunkLocation]:
        chunk_locations = []
        for chunk_idx in range(num_chunks):
            chunk_file_name = f"{object_name}.{chunk_idx:02}"
            node_idx = used_nodes_indices[chunk_idx % len(used_nodes_indices)]
            chunk_locations.append(ChunkLocation(node_idx, chunk_file_name))

        return chunk_locations

    def get_disk_usage(self):
        return sum(stats.used_space for stats in self.get_disk_usage_stats())

    def get_disk_usage_stats(self) -> List[DiskUsageStats]:
        """
        :return: list of DiskUsageStats sorted (ascending) by the disk usage
        """
        disk_usage_stats = []
        for (node_idx, data_node) in enumerate(self.data_nodes):
            if data_node.is_healthy:
                disk_usage_stats.append(DiskUsageStats(node_idx, data_node.get_disk_usage()))
        disk_usage_stats = sorted(disk_usage_stats, key=lambda stats: stats.used_space)

        return disk_usage_stats

    def debug_dump(self, verbose_level=0):
        print("\n================== KVS ====================")
        self.metadata_kvs.debug_dump()
        print("=" * 100)
        print("================== Data Nodes ====================")
        for data_node_idx, data_node in enumerate(self.data_nodes):
            print("----- node: %3d -----" % data_node_idx)
            data_node.debug_dump(verbose_level)
        print("=" * 100)
