import itertools
import random

import pytest

from common_types import Data
from object_storage import ObjectStorage
from underlying_api import DataNode, MetadataKvs, Constraints


def create_sample_file(size: int, prefix='') -> Data:
    """
    >>> create_sample_file(11, "PRE_")
    b'PRE_aaa aab'
    >>> create_sample_file(10, "PRE_")
    b'pre_aaa aa'
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    contents = [prefix]
    contents_len = len(prefix)
    for chars in itertools.product(alphabet, alphabet, alphabet):
        contents.append(''.join(chars) + ' ')
        contents_len += 4
        if contents_len > size:
            break
    return ''.join(contents)[:size].encode("ascii")


class TestHelper:
    @staticmethod
    def create_new_object_storage(num_data_nodes: int):
        constraints = Constraints(num_data_nodes)
        data_nodes = [DataNode({}, is_healthy=True, constraints=constraints) for _ in range(num_data_nodes)]
        metadata_kvs = MetadataKvs({}, constraints=constraints)
        object_storage = ObjectStorage(metadata_kvs=metadata_kvs, data_nodes=data_nodes)
        return object_storage

    @staticmethod
    def fail_non_empty_node(object_storage: ObjectStorage) -> DataNode:
        non_empty_data_nodes = [node for node in object_storage.data_nodes if node.is_healthy and node.get_disk_usage() > 0]
        data_node = random.choice(non_empty_data_nodes)
        data_node.is_healthy = False
        return data_node


@pytest.mark.parametrize("object_size,num_data_nodes", itertools.product(
    [1, 10, 16, 20, 50, 64, 100, 150],
    [5, 8, 10, 20, 100],
))
def test_write_small_object(object_size: int, num_data_nodes: int):
    object_storage = TestHelper.create_new_object_storage(num_data_nodes=8)
    sample_file = create_sample_file(object_size)
    object_storage.write_object('file1', sample_file)

    assert object_storage.read_object('file1') == sample_file


@pytest.mark.parametrize("object_size,num_data_nodes", itertools.product(
    [200, 500, 1000, 2000, 5000],
    [8, 10, 20, 100],
))
def test_write_larger_object_many_datanodes(object_size: int, num_data_nodes: int):
    object_storage = TestHelper.create_new_object_storage(num_data_nodes=num_data_nodes)
    sample_file = create_sample_file(object_size)
    object_storage.write_object('file1', sample_file)

    assert object_storage.read_object('file1') == sample_file


@pytest.mark.parametrize("object_size,num_data_nodes", itertools.product(
    [200, 500, 1000, 2000, 5000],
    [8, 10, 20, 100],
))
def test_delete_larger_object(object_size: int, num_data_nodes: int):
    object_storage = TestHelper.create_new_object_storage(num_data_nodes=num_data_nodes)
    sample_file = create_sample_file(object_size)

    assert object_storage.get_disk_usage() < 100
    object_storage.write_object('file1', sample_file)
    assert object_storage.get_disk_usage() >= object_size

    assert object_storage.read_object('file1') == sample_file

    object_storage.delete_object('file1')
    assert object_storage.get_disk_usage() < 100

    assert object_storage.read_object('file1') is None


@pytest.mark.parametrize("object_size,num_objects", itertools.product(
    [20, 30],
    [5, 10, 100, 200],
))
def test_write_many_small_objects(object_size: int, num_objects: int):
    object_storage = TestHelper.create_new_object_storage(num_data_nodes=12)
    sample_objects = []
    for file_index in range(num_objects):
        object_contents = create_sample_file(object_size, prefix="%03d " % file_index)
        sample_objects.append(('file%d' % file_index, object_contents))

    for (object_name, object_contents) in sample_objects:
        object_storage.write_object(object_name, object_contents)

    for (object_name, object_contents) in sample_objects:
        assert object_storage.read_object(object_name) == object_contents


@pytest.mark.parametrize("object_size,num_objects", itertools.product(
    [20, 30],
    [5, 10, 100, 200],
))
def test_write_and_many_small_objects(object_size: int, num_objects: int):
    object_storage = TestHelper.create_new_object_storage(num_data_nodes=12)
    sample_objects = []
    for file_index in range(num_objects):
        object_contents = create_sample_file(object_size, prefix="%03d " % file_index)
        sample_objects.append(('file%d' % file_index, object_contents))

    for (object_name, object_contents) in sample_objects:
        object_storage.write_object(object_name, object_contents)

    for (object_name, object_contents) in sample_objects:
        assert object_storage.read_object(object_name) == object_contents

    for (object_name, object_contents) in sample_objects[::2]:
        object_storage.delete_object(object_name)

    for (idx, (object_name, object_contents)) in enumerate(sample_objects):
        if idx % 2 == 0:
            assert object_storage.read_object(object_name) is None
        else:
            assert object_storage.read_object(object_name) == object_contents


@pytest.mark.parametrize("object_size,num_data_nodes", itertools.product(
    [1, 10, 16, 20, 50, 64, 100, 150],
    [5, 8, 10, 20, 100],
))
def test_write_small_object_fail_node_read_data(object_size: int, num_data_nodes: int):
    object_storage = TestHelper.create_new_object_storage(num_data_nodes=num_data_nodes)
    sample_file = create_sample_file(object_size)
    object_storage.write_object('file1', sample_file)

    TestHelper.fail_non_empty_node(object_storage)

    assert object_storage.read_object('file1') == sample_file

    object_storage.debug_dump()


@pytest.mark.parametrize("fail_data_node", [False, True], ids=["normal", "one-node-destroyed"])
def test_write_many_small_and_two_large_objects(fail_data_node: bool):
    object_storage = TestHelper.create_new_object_storage(num_data_nodes=16)
    sample_objects = []

    # 100x 15B == 1500 B
    for file_index in range(200):
        object_contents = create_sample_file(15, prefix="%03d " % file_index)
        sample_objects.append(('file%d' % file_index, object_contents))

    sample_objects.append(('large_1', create_sample_file(3000, 'large1')))
    sample_objects.append(('large_2', create_sample_file(2000, 'large2')))

    # 100x 15B == 1500 B
    for file_index in range(100):
        object_contents = create_sample_file(15, prefix="%03d " % file_index)
        sample_objects.append(('FILE%d' % file_index, object_contents))

    for (object_name, object_contents) in sample_objects:
        object_storage.write_object(object_name, object_contents)

    for (object_name, object_contents) in sample_objects:
        assert object_storage.read_object(object_name) == object_contents

    assert object_storage.get_disk_usage() > 5600

    if fail_data_node:
        TestHelper.fail_non_empty_node(object_storage)

    for (object_name, object_contents) in sample_objects:
        assert object_storage.read_object(object_name) == object_contents


@pytest.mark.parametrize("fail_data_nodes", [False, True], ids=["normal", "many-nodes-unhealthy"])
def test_write_huge_object_in_large_system(fail_data_nodes: bool):
    object_storage = TestHelper.create_new_object_storage(num_data_nodes=100)

    if fail_data_nodes:
        for node_idx in range(0, 100, 25):
            object_storage.data_nodes[node_idx].is_healthy = False

    sample_file = create_sample_file(750 * 100)
    object_storage.write_object('file1', sample_file)

    assert object_storage.read_object('file1') == sample_file


@pytest.mark.parametrize("object_size,num_data_nodes", zip(
    [375 * 100, 750 * 100],
    [50, 100],
))
def test_write_larger_object_data_loss(object_size: int, num_data_nodes: int):
    object_storage = TestHelper.create_new_object_storage(num_data_nodes=num_data_nodes)
    sample_file = create_sample_file(object_size)
    object_storage.write_object('file1', sample_file)

    assert object_storage.read_object('file1') == sample_file

    TestHelper.fail_non_empty_node(object_storage)

    assert object_storage.read_object('file1') == sample_file

    data_loss_occurred = False
    last_failed_datanode = None
    for _ in range(num_data_nodes // 2):
        last_failed_datanode = TestHelper.fail_non_empty_node(object_storage)
        try:
            object_storage.read_object('file1')
        except Exception:
            data_loss_occurred = True
            break

    assert data_loss_occurred

    last_failed_datanode.is_healthy = True

    assert object_storage.read_object('file1') == sample_file
