#!/usr/bin/env python3
"""Recover an HS256 JWT secret from a wordlist.

Usage: python3 crack_jwt.py <token-file> <wordlist> [<wordlist> ...]
"""
import base64
import hashlib
import hmac
import sys


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


token = open(sys.argv[1]).read().strip()
header_b64, payload_b64, signature_b64 = token.split(".")
signing_input = f"{header_b64}.{payload_b64}".encode()

for path in sys.argv[2:]:
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            candidate = line.strip()
            if not candidate:
                continue
            expected = b64url(
                hmac.new(candidate.encode(), signing_input, hashlib.sha256).digest()
            )
            if hmac.compare_digest(expected, signature_b64):
                print(f"CRACKED — the secret is: {candidate!r}")
                sys.exit(0)

print("not in the list")
sys.exit(1)
