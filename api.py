#!/usr/bin/env python3

import requests
from block import Block

class BlockchainAPI:
    url = "https://nami-hackathon.tuankiet65.moe"

    sess = requests.Session()

    def get(self, key: str) -> str:
        path = "/get"
        req = self.sess.get(self.url + path, params = {
            "key": key
        })

        data = req.json()
        if data['result'] == "ok":
            return data["value"]
        else:
            raise KeyNotFound

    def set(self, key: str, value: str):
        path = "/set"
        req = self.sess.post(self.url + path, data = {
            "key"  : key,
            "value": value
        })

        data = req.json()
        if data['result'] != "ok":
            raise UnknownError

    def get_mining_template(self) -> (Block, bytes):
        path = "/get_mining_template"
        req = self.sess.get(self.url + path)

        data = req.json()
        block = Block.from_bytes(bytes.fromhex(data['template']))
        target = bytes.fromhex(data['target'])
        return (block, target)

    def submit_block(self, block: Block):
        path = "/submit_block"
        req = self.sess.post(self.url + path, data = {
            "block": block.to_bytes().hex()
        })

        data = req.json()
        if data['result'] != "ok":
            raise UnknownError

class KeyNotFound(Exception):
    pass


class UnknownError(Exception):
    pass
