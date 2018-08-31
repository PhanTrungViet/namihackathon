#!/usr/bin/env python3

import hashlib
import string
import random
import time

int256 = int


def sha256(b):
    h = hashlib.sha256(b)
    return h.digest()


def sha256_hex(b):
    h = hashlib.sha256(b)
    return h.hexdigest()


def get_current_timestamp() -> int:
    return int(time.time())


def int256_to_bytes(n: int256) -> bytearray:
    b = bytearray()
    for i in range(256 // 8):
        b.append(n % (1 << 8))
        n //= (1 << 8)
    return b


def bytes_to_int256(b) -> int256:
    n = 0
    for i in range(256 // 8):
        n = (n * (1 << 8)) + b[i]
    return n

def random_string(length: int = 50) -> str:
    rand = random.SystemRandom()
    letters = string.ascii_letters + string.digits
    return ''.join(rand.choice(letters) for _ in range(length))