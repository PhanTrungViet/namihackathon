#!/usr/bin/env python3

import hashlib
import struct

KEY_LENGTH = 32
VALUE_LENGTH = 32


class Transaction:
    FORMAT = f"<{KEY_LENGTH}p{VALUE_LENGTH}p"
    SIZE = struct.calcsize(FORMAT)

    key = None
    value = None

    def _check_size(self, s: str, max_length: int):
        b = s.encode("utf-8")
        if len(b) > max_length:
            raise ValueLengthException

    def __init__(self, key: str, value: str):
        self._check_size(key, KEY_LENGTH)
        self._check_size(value, VALUE_LENGTH)

        self.key = key
        self.value = value

    @staticmethod
    def from_bytes(b: bytes):
        (key, value) = struct.unpack(Transaction.FORMAT, b)
        key = key.decode("utf-8")
        value = value.decode("utf-8")
        return Transaction(key, value)

    def to_bytes(self) -> bytes:
        b = struct.pack(self.FORMAT, self.key.encode("utf-8"),
                                    self.value.encode("utf-8"))
        return b

    def _append_null_padding(self, b: bytearray, s: str, length: int):
        sb = s.encode("utf-8")
        padding = b"\x00" * (length - len(sb))
        b.extend(sb)
        b.extend(padding)

    def hash(self):
        h = hashlib.sha256(self.to_bytes())
        return h.digest()

    def hash_hex(self):
        h = hashlib.sha256(self.to_bytes())
        return h.hexdigest()

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return self.key == other.key and self.value == other.value


class ValueLengthException(Exception):
    pass


if __name__ == "__main__":
    tx = Transaction("goodluck1", "goodlucsdadasdasdk")
    print(tx.to_bytes().hex())
    print(tx.hash_hex())

    tx2 = Transaction.from_bytes(tx.to_bytes())
    print(tx2.key)
    print(tx2.value)
    print(tx2.hash_hex())
