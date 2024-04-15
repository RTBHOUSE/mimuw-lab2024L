import json
from dataclasses import dataclass
from typing import Dict, Optional

from common_types import FileName, Data, DataSize, KvsKey, KvsValue


class Constraints:
    """
    Storage limits for DataNode and MetadataKvs given total number of data nodes in the system.
    """
    ObjectStorageMaxNameLen = 10
    ObjectStorageMaxNumObjectsPerDataNode = 250

    DataNodeMaxFileLen = ObjectStorageMaxNameLen + 4
    DataNodeMaxNumFiles = ObjectStorageMaxNumObjectsPerDataNode * 3  # 3 data files per every storage object
    DataNodeMaxDiskUsage = 1024  # 1KB of data

    KvsMaxKeyLen = ObjectStorageMaxNameLen + 4
    KvsMaxValueSize = 400  # 400 bytes per key

    def __init__(self, num_data_nodes: int):
        self.KvsMaxNumKeys = self.ObjectStorageMaxNumObjectsPerDataNode * num_data_nodes * 3  # 3 keys per every object
        self.KvsMaxValueSizeSum = num_data_nodes * self.DataNodeMaxDiskUsage // 4  # but no more than 25% data capacity


class DataNodeException(Exception):
    pass


class NodeUnhealthyException(DataNodeException):
    pass


@dataclass
class DataNode:
    """Simple limited storage that can be used to store data in more complex system."""

    files: Dict[FileName, Data]
    is_healthy: bool
    constraints: Constraints

    def write_file(self, file_name: FileName, data: Data):
        """Stores data under user specified file name."""

        if not self.is_healthy:
            raise NodeUnhealthyException()

        if len(file_name) > self.constraints.DataNodeMaxFileLen:
            raise ValueError("File name too long: %s" % file_name)

        if len(self.files) >= self.constraints.DataNodeMaxNumFiles and file_name not in self.files:
            raise ValueError("Maximum number of files per node reached: %s (when writing %s)" % (
                file_name, self.constraints.DataNodeMaxNumFiles))

        if len(data) + self.get_disk_usage() - len(self.files.get(file_name, b'')) > self.constraints.DataNodeMaxDiskUsage:
            raise ValueError(
                "Disk space exceeded; current disk usage: %s/%s, new file size: %s" % (
                    self.get_disk_usage(), self.constraints.DataNodeMaxDiskUsage, len(data))
            )

        self.files[file_name] = data

    def read_file(self, file_name: FileName) -> Data:
        """Retrieves data stored under given file name."""

        if not self.is_healthy:
            raise NodeUnhealthyException()

        if file_name not in self.files:
            raise ValueError("File not found: %s" % file_name)

        return self.files[file_name]

    def delete_file(self, file_name: FileName):
        """Deletes data stored under given file name."""

        if not self.is_healthy:
            raise NodeUnhealthyException()

        if file_name not in self.files:
            raise ValueError("File not found: %s" % file_name)

        del self.files[file_name]

    def get_disk_usage(self) -> DataSize:
        """Returns number of bytes stored on that data node."""

        if not self.is_healthy:
            raise NodeUnhealthyException()

        return sum([len(data) for data in self.files.values()])

    def debug_dump(self, verbose_level=0):
        """For debugging purposes only."""

        if not self.is_healthy:
            print("UNHEALTHY")
            return

        print("disk_usage: %10s; num_files: %s" % (self.get_disk_usage(), len(self.files)))
        if verbose_level > 1:
            for key, value in self.files.items():
                print("%15s = %s" % (key, value))


@dataclass
class MetadataKvs:
    """
    Basic Key-Value Store that can be used to store small amounts of data.

    The storage capacity and number of keys is limited.
    """
    storage: Dict[KvsKey, Data]
    constraints: Constraints

    def write_key(self, key: KvsKey, value: KvsValue):
        """Stores data stored under given key."""

        if len(key) > self.constraints.KvsMaxKeyLen:
            raise ValueError(f"Key name too long: {key}")

        if len(self.storage) >= self.constraints.KvsMaxNumKeys and key not in self.storage:
            raise ValueError(f"Maximum number of keys reached: {self.constraints.KvsMaxNumKeys} (key: {key})")

        if len(value) - len(self.storage.get(key, b'')) > self.constraints.KvsMaxValueSize:
            raise ValueError(f"Value to large %s > %s (key: %s)" % (len(value), self.constraints.KvsMaxValueSize, key))

        if len(value) + self.get_disk_usage() - len(self.storage.get(key, b'')) > self.constraints.KvsMaxValueSizeSum:
            raise ValueError(
                "Metadata space exceeded; current usage: %s/%s, new value size: %s (key: %s)" % (
                    self.get_disk_usage(), self.constraints.KvsMaxValueSizeSum, len(value), key))

        self.storage[key] = value

    def read_key(self, key: KvsKey) -> Optional[KvsValue]:
        """
        Retrieves data stored under given key.

        Returns node if KVS does not contain specified key.
        """

        if key not in self.storage:
            return None

        return self.storage[key]

    def delete_key(self, key: KvsKey):
        """Retrieves data stored under given key."""

        if key not in self.storage:
            raise ValueError("Key not found: %s" % key)
        del self.storage[key]

    def kvs_encode(self, obj: any) -> Data:
        """Helper methods that serializes Python objects into bytes."""
        return json.dumps(obj, separators=(',', ':')).encode('utf8')

    def kvs_decode(self, data: Data) -> any:
        """Helper methods that deserializes Python objects serialized using kvs_encode."""
        return json.loads(data.decode('utf8'))

    def get_disk_usage(self) -> DataSize:
        """Returns number of bytes stored in KVS."""
        return sum([len(value) for value in self.storage.values()])

    def debug_dump(self):
        """For debugging purposes only."""

        for key, value in self.storage.items():
            print("%15s = %s" % (key, value))
