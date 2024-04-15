# Simple Object Storage

In this laboratory you will implement very **basic** scalable **Object Storage** in a simulated environment. If you are stuck, ask the instructor for
help.

## Goal

The goal is to create a simple Object Storage that passes all tests.

To do so, you need implement `object_storage.ObjectStorage` class with following interface:

```python
class ObjectStorage:
    def write_object(self, object_name: ObjectName, data: Data): ...

    def read_object(self, object_name: ObjectName) -> Optional[Data]: ...

    def delete_object(self, object_name: ObjectName): ...
```

To simplify things a little, in this exercise you have to use following components:

- `underlying_api.DataNode` (there will be variable number of DataNodes)
- `underlying_api.MetadataKvs` (there will be always only one Key-Value Store)

Those components provide simple API for storing data and metadata. We want to focus on high-level object storage design, so those component store data
in the Object Storage process memory.

### Object Storage constraints and requirements

- each DataNode can store up to 1024 bytes of data and up to 750 files
- the metadata KVS has limited number of storage (so it can be used only for storing metadata)
- every object name is no longer than 10 bytes
- Object Storage should be able to store 250 objects per every data node in the system
- Object Storage should be able to store files larger than single DataNode capacity
- **Object Storage should handle** a single DataNode failure
- you must not store data outside DataNodes and MetadataKvs

## Installation

```
pip3 install pytest
```

## Running tests

Running all test cases:

```bash
$ pytest -vv -s tests.py
...
tests.py::test_write_small_object_fail_node_read_data[150-20]             PASSED
tests.py::test_write_small_object_fail_node_read_data[150-100]            PASSED
tests.py::test_write_many_small_and_two_large_objects[normal]             PASSED
tests.py::test_write_many_small_and_two_large_objects[one-node-destroyed] PASSED
tests.py::test_write_huge_object_in_large_system                          PASSED  
```

Less verbose output:

```bash
pytest --tb=no -v tests.py
```

Running subset of tests cases which match the given substring expression:

```bash
pytest -vv -s tests.py -k 'write_larger'
```

Automatically running the Python Debugger on failed test.

```bash
$ pytest --pdb -vv -s tests.py 
...
E           ValueError: Metadata space exceeded; current usage: 504/512, new value size: 14 (key: file36)
(Pdb) up
(Pdb) p self.metadata_kvs.storage['file0']
b'[3,30,[0,1,2]]'
```

## Hints

You may find helper functions from `helpers.py` useful.
