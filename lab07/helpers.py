from typing import List, Optional, Sequence

from common_types import Data, Byte


def pad_data(x: Data, size: int, pad_byte=b'0'):
    """
    Pads data at the end so that padded data is divisbile by size.

    >>> pad_data(b'abcd1234', 6, pad_byte=b'X')
    b'abcd1234XXXX'
    >>> pad_data(b'ab', 3)
    b'ab0'
    >>> pad_data(b'abcd', 2)
    b'abcd'
    """
    return x + pad_byte * (-len(x) % size)


def split_data(data: Data, max_segment_size: int) -> List[Data]:
    """
    Splits data into segments so that every segment (except the last one) has max_segment_size bytes.

    >>> split_data(b'01234567', 3)
    [b'012', b'345', b'67']
    >>> split_data(b'012345', 3)
    [b'012', b'345']
    """
    return split_sequence(data, max_segment_size)


def split_sequence(data: Sequence, max_segment_size: int) -> List:
    """
    Splits data into segments so that every segment (except the last one) has max_segment_size bytes.

    >>> split_sequence(['ab', 'cd', 'ef', 'gh'], 3)
    [['ab', 'cd', 'ef'], ['gh']]
    >>> split_sequence(['ab', 'cd', 'ef', 'gh'], 4)
    [['ab', 'cd', 'ef', 'gh']]
    >>> split_sequence(['ab', 'cd', 'ef', 'gh', 'ij'], 2)
    [['ab', 'cd'], ['ef', 'gh'], ['ij']]
    """
    return [data[i:i + max_segment_size] for i in range(0, len(data), max_segment_size)]


def swap_elements(target_list: List, idx1, idx2) -> None:
    """
    Swaps two elements in given list in place.

    >>> x = [0, 1, 2, 3, 4]
    >>> swap_elements(x, 1, 3)
    >>> x
    [0, 3, 2, 1, 4]
    """

    tmp = target_list[idx1]
    target_list[idx1] = target_list[idx2]
    target_list[idx2] = tmp


def erasure_code_bytes(orig_bytes: List[Byte]) -> Byte:
    """
    Simple parity (n+1) erasure code.
    Returns computed parity byte.

    >>> erasure_code_bytes([0, 63])
    63
    >>> erasure_code_bytes([0, 1, 8, 15])
    6
    """

    parity_byte = 0
    for byte in orig_bytes:
        parity_byte = parity_byte ^ byte
    return parity_byte


def erasure_code(orig_chunks: List[Data]) -> List[Data]:
    """
    Applies erasure_code() element-wise to list of data chunks.
    Returns new list with parity chunk appended at its end.
    """

    parity_chunk = []
    for zipped_bytes in zip(*orig_chunks):
        parity_byte = erasure_code_bytes(list(zipped_bytes))
        parity_chunk.append(parity_byte)
    parity_chunk = bytes(parity_chunk)

    result_chunks = orig_chunks[:]
    result_chunks.append(parity_chunk)
    return result_chunks


def reconstruct_bytes(chunks: List[Optional[Byte]]) -> List[Byte]:
    """
    Returns new list of bytes.
    """
    missing_chunks_indices = [idx for idx, chunk in enumerate(chunks) if chunk is None]
    num_missing_chunks = len(missing_chunks_indices)

    if num_missing_chunks == 0:
        return chunks

    if num_missing_chunks > 1:
        raise ValueError("Too many missing chunks")

    parity_index = len(chunks) - 1
    missing_idx = missing_chunks_indices[0]

    chunks = chunks[:]
    swap_elements(chunks, missing_idx, parity_index)
    chunks[-1] = erasure_code_bytes(chunks[:-1])
    swap_elements(chunks, missing_idx, parity_index)

    return chunks


def reconstruct(chunks: List[Optional[Data]], chunk_size: int) -> List[Data]:
    reconstructed_chunks = [[] for _ in range(len(chunks))]

    for byte_idx in range(chunk_size):
        bytes_to_reconstruct = []
        for chunk in chunks:
            bytes_to_reconstruct.append(None if chunk is None else chunk[byte_idx])
        reconstructed_bytes = reconstruct_bytes(bytes_to_reconstruct)

        for (chunk_idx, reconstructed_byte) in enumerate(reconstructed_bytes):
            reconstructed_chunks[chunk_idx].append(reconstructed_byte)

    return [bytes(chunk_bytes) for chunk_bytes in reconstructed_chunks]


def cyclic_shift(x, d):
    return ((x << (8 - d)) & 255) | (x >> d)


def test_reconstruct_bytes():
    import random
    num_input_chunks = 4

    for _ in range(10):
        input_data = [random.randint(0, 255) for _ in range(num_input_chunks)]
        data_with_ec = input_data + [erasure_code_bytes(input_data)]
        missing_chunk_idx = random.randint(0, num_input_chunks + 1 - 1)
        corrupted_data = data_with_ec[:]
        corrupted_data[missing_chunk_idx] = None
        reconstruct_data = reconstruct_bytes(corrupted_data)

        assert reconstruct_data == data_with_ec
        assert reconstruct_data[:-1] == input_data
