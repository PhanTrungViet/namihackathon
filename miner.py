#!/usr/bin/env python3

import random
import logging

from api import BlockchainAPI, KeyNotFound, UnknownError
from utils import random_string

api = BlockchainAPI()

logging.basicConfig(style = "{", format = "{levelno} - {asctime} - {module} - {funcName} - {message}", level = logging.INFO)

logging.info("miner+tester starting")

data = {}

while True:
    logging.info("adding 10 random keys")
    for i in range(10):
        key = random_string(10)
        value = random_string(10)
        data[key] = value
        api.set(key, value)

    (block, target) = api.get_mining_template()
    logging.info(f"got block template")
    logging.info(f"target: {target.hex()}")
    logging.info(f"begin trialing nonce")
    for nonce in range(1 << 32):
        block.header.nonce = nonce
        if block.hash() <= target:
            mined = True
            logging.info(f"found winning nonce: {nonce}")
            logging.info(f"new block hash: {block.hash_hex()}")
            logging.info(f"sending")
            api.submit_block(block)
            break

    logging.info("trialing 10 random keys")
    for i in range(10):
        key = random.choice(list(data.keys()))
        try:
            value = api.get(key)
            if data[key] != value:
                logging.fatal(f"error at checking key {key}, expect {data[key]} but got {value}")
                exit()
        except KeyNotFound:
            logging.fatal(f"error at checking key {key}, key should be stored but isn't")
            exit()
    logging.info("key trialing success")