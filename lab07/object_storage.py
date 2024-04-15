from typing import List, Optional, NamedTuple

from common_types import ObjectName, Data, DataNodeIdx, DataSize
from underlying_api import MetadataKvs, DataNode


class DiskUsageStats(NamedTuple):
    data_node_idx: DataNodeIdx
    used_space: DataSize


class ObjectStorage:
    def __init__(self, metadata_kvs: MetadataKvs, data_nodes: List[DataNode]):
        self.metadata_kvs = metadata_kvs
        self.data_nodes = data_nodes
        self.num_nodes = len(self.data_nodes)

    def write_object(self, object_name: ObjectName, data: Data):
        self.data_nodes[0].write_file(object_name, data)

    def read_object(self, object_name: ObjectName) -> Optional[Data]:
        return self.data_nodes[0].read_file(object_name)

    def delete_object(self, object_name: ObjectName):
        self.data_nodes[0].delete_file(object_name)

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
