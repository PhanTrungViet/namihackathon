#!/usr/bin/env python3

from __future__ import annotations

import struct
from typing import List

from block import Block, BlockHeader, InvalidBlock, GENESIS_BLOCK, FIXED_TARGET
from transaction import Transaction
from utils import int256_to_bytes, get_current_timestamp, sha256, random_string


class Blockchain:
    filename = "_blockchain_nami.bin"

    blocks: List[Block] = []
    tx_queue: List[Transaction] = []

    def __init__(self):
        self.load()

    def load(self):
        print(f"Loading blockchain from file {self.filename}")
        try:
            f = open(self.filename, "rb")
        except FileNotFoundError:
            print("File not found, creating a new one")
            self.init()
        else:
            block_count = struct.unpack("<L", f.read(4))[0]
            print(f"{block_count} blocks available")
            for i in range(block_count):
                block_size = struct.unpack("<L", f.read(4))[0]
                b = f.read(block_size)
                print(f"Block {i} size: {block_size}")
                self.add_block(Block.from_bytes(b), False)
            f.close()

    def get_block_with_id(self, id: str) -> Block:
        for block in self.blocks:
            if block.hash_hex() == id:
                return block
        raise BlockNotFound

    def get_top_block(self) -> Block:
        return self.blocks[-1]

    def get_current_target(self):
        return self.get_top_block().header.target[::-1]

    def init(self):
        self.add_block(GENESIS_BLOCK)

    def save(self):
        print("Writing blocks to file")
        with open(self.filename, "wb") as f:
            block_count = len(self.blocks)
            f.write(struct.pack("<L", block_count))
            print(f"{block_count} blocks available")
            for block in self.blocks:
                b = block.to_bytes()
                length = len(b)
                f.write(struct.pack("<L", length))
                f.write(b)

    def add_block(self, block: Block, autosave: bool = True):
        print(f"Trying to add block {block.hash_hex()}")
        print(f"Block hex: {block.to_bytes().hex()}")

        if len(self.blocks) == 0:
            self.blocks.append(block)
            return 0

        # Checks to perform:
        #  * prev_hash matches hash of top block
        #  * hash is smaller or equal to top block's target value
        top = self.get_top_block()
        print(f"Top block hash is {top.hash_hex()}")
        if block.header.prev_hash != top.hash():
            print("block prev_hash does not match top block's hash")
            raise InvalidBlock("block prev_hash does not match top block's hash")
        if block.hash() > self.get_current_target():
            print("block prev_hash does not match top block's hash")
            raise InvalidBlock("block hash is larger than target")

        print("Block is valid, adding")
        self.blocks.append(block)
        if autosave:
            self.save()

    def set_key(self, key: str, value: str):
        print(f"Setting {key} to {value}")
        tx = Transaction(key, value)
        self.tx_queue.append(tx)

    def tx_in_queue(self, key: str):
        for tx in self.tx_queue:
            if tx.key == key:
                return True
        return False

    def get_key(self, key: str):
        for block in self.blocks:
            result = block.get(key)
            if result is not None:
                return result
        raise KeyNotFound

    def get_queued_tx_hash(self):
        hashes = bytearray()
        if not self.tx_queue:
            hashes = b'\x00' * 32
        else:
            for tx in self.tx_queue:
                hashes.extend(tx.hash())

        return sha256(hashes)

    def get_mining_template(self) -> Block:
        hdr = BlockHeader(timestamp = get_current_timestamp(),
                          prev_hash = self.get_top_block().hash(),
                          target = int256_to_bytes(FIXED_TARGET),
                          nonce = 0x00000000,
                          tx_hash = self.get_queued_tx_hash())
        block = Block(header = hdr, txs = self.tx_queue)
        return block

    def add_raw_block(self, b):
        block = Block.from_bytes(b)
        self.add_block(block)
        for tx in block.txs:
            if tx in self.tx_queue:
                self.tx_queue.remove(tx)


class KeyNotFound(Exception):
    pass

class BlockNotFound(Exception):
    pass

if __name__ == "__main__":
    blockchain = Blockchain()

    while True:
        key = random_string(16)
        value = random_string(16)
        blockchain.set_key(key, value)

        block = blockchain.get_mining_template()

        for i in range(1, 1 << 32):
            block.header.nonce = i
            if block.hash() < blockchain.get_current_target():
                print(f"Winning nonce: {i}")
                print(blockchain.get_current_target().hex())
                print(block.hash().hex())
                print("Adding to chain")
                blockchain.add_raw_block(block.to_bytes())
                break

        try:
            blockchain.get_key(key)
            print("key test passed")
        except KeyNotFound:
            print("key test failed")
            break
