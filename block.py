#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import struct
import copy
from typing import List

from transaction import Transaction
from utils import int256_to_bytes, sha256

FIXED_TARGET = 0x0000100000000000000000000000000000000000000000000000000000000000


# Block structure:
#  * signature: const 10 byte = "TUANKIET^%"
#  * block size (byte): 4 byte LE
#  * block header:
#  ** timestamp: 4 byte LE
#  ** prev_hash: 32 byte LE
#  ** target: 32 byte LE
#  ** tx_hash: 32 byte LE
#  ** nonce: 4 byte LE
#  * tx_count: 4 byte LE
#  * tx: variable

class BlockHeader:
    FORMAT = "<L32s32s32sL"
    SIZE = struct.calcsize(FORMAT)

    timestamp: int = None
    prev_hash: bytes = None
    target: bytes = None
    tx_hash: bytes = None
    nonce: int = None

    def __init__(self, timestamp: int, prev_hash: bytes, target: bytes, tx_hash: bytes, nonce: int):
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.target = target
        self.tx_hash = tx_hash
        self.nonce = nonce

    @staticmethod
    def from_bytes(b: bytes):
        hdr_data = struct.unpack(BlockHeader.FORMAT, b)
        return BlockHeader(timestamp = hdr_data[0],
                           prev_hash = hdr_data[1],
                           target = hdr_data[2],
                           tx_hash = hdr_data[3],
                           nonce = hdr_data[4])

    def to_bytes(self):
        return struct.pack(self.FORMAT, self.timestamp, self.prev_hash,
                           self.target, self.tx_hash, self.nonce)

    def hash(self) -> bytes:
        b = self.to_bytes()
        h = hashlib.sha256(b)
        return h.digest()

    def hash_hex(self) -> str:
        b = self.to_bytes()
        h = hashlib.sha256(b)
        return h.hexdigest()


class Block:
    SIGNATURE: bytes = b"TUANKIET^%"

    size = None
    header: BlockHeader = None
    tx_count = None
    txs: List[Transaction] = None

    def __init__(self, header: BlockHeader, txs: List[Transaction]):
        self.header = header
        self.txs = copy.deepcopy(txs)
        self.tx_count = len(self.txs)
        self.size = len(self.SIGNATURE) + 4 + BlockHeader.SIZE + 4 + (self.tx_count * Transaction.SIZE)

    def hash(self) -> bytes:
        return self.header.hash()

    def hash_hex(self) -> str:
        return self.header.hash_hex()

    def to_bytes(self) -> bytes:
        b = bytearray()
        b.extend(self.SIGNATURE)
        b.extend(struct.pack("<L", self.size))
        b.extend(self.header.to_bytes())
        b.extend(struct.pack("<L", self.tx_count))
        for tx in self.txs:
            b.extend(tx.to_bytes())

        return b

    @staticmethod
    def from_bytes(b: bytes) -> Block:
        ptr = 0

        if b[:len(Block.SIGNATURE)] != Block.SIGNATURE:
            raise InvalidBlock("Invalid signature")
        ptr += len(Block.SIGNATURE)

        size = struct.unpack("<L", b[ptr:ptr + 4])[0]
        if size != len(b):
            raise InvalidBlock(f"Size in block does not match real size (size: {size}, real: {len(b)})")
        ptr += 4

        header = BlockHeader.from_bytes(b[ptr:ptr + BlockHeader.SIZE])
        ptr += BlockHeader.SIZE

        tx_count = struct.unpack("<L", b[ptr:ptr + 4])[0]
        ptr += 4

        txs = []
        for i in range(tx_count):
            txs.append(Transaction.from_bytes(b[ptr:ptr + Transaction.SIZE]))
            ptr += Transaction.SIZE

        return Block(header = header,
                     txs = txs)

    def get(self, key: str):
        for tx in self.txs:
            if tx.key == key:
                return tx.value
        return None

class InvalidBlock(Exception):
    pass


GENESIS_TX = Transaction("Welcome to Nami Blockchain", "@tuankiet65_nicememe")

GENESIS_BLOCK_HEADER = BlockHeader(timestamp = 1534613194,
                                   prev_hash = int256_to_bytes(0x0),
                                   target = int256_to_bytes(FIXED_TARGET),
                                   tx_hash = sha256(GENESIS_TX.hash()),
                                   nonce = 0x69696969)

GENESIS_BLOCK = Block(header = GENESIS_BLOCK_HEADER,
                      txs = [GENESIS_TX])

if __name__ == "__main__":
    block = GENESIS_BLOCK

    print(block.to_bytes().hex())
    print(block.hash_hex())

    block2 = Block.from_bytes(block.to_bytes())
    print(block2.header.timestamp)
    print(block2.header.nonce)
    print(block2.header.hash_hex())
    print(block2.tx_count)
    print(block2.txs[0].key)
    print(block2.txs[0].value)
    print(block2.header.prev_hash)
    print(block2.header.target)
