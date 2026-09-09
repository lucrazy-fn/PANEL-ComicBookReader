
from __future__ import annotations

import hashlib
import hmac
import os
import base64
import struct
import time

_ITERATIONS = 260_000


def hash_password(plain_password: str) -> tuple[str, str]:
    pass
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, _ITERATIONS)
    return digest.hex(), salt.hex()


def verify_password(plain_password: str, password_hash: str, password_salt: str) -> bool:
    salt = bytes.fromhex(password_salt)
    digest = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, _ITERATIONS)
    return hmac.compare_digest(digest.hex(), password_hash)

def new_totp_secret(): return base64.b32encode(os.urandom(20)).decode().rstrip("=")
def totp_code(secret: str, at: int | None=None) -> str:
    counter=int((at or time.time())//30); padded=secret+"="*((8-len(secret)%8)%8)
    digest=hmac.new(base64.b32decode(padded),struct.pack(">Q",counter),hashlib.sha1).digest()
    offset=digest[-1]&15; value=(struct.unpack(">I",digest[offset:offset+4])[0]&0x7fffffff)%1_000_000
    return f"{value:06d}"
def verify_totp(secret: str, code: str) -> bool:
    now=int(time.time())
    return any(hmac.compare_digest(totp_code(secret,now+step*30),str(code).zfill(6)) for step in (-1,0,1))
