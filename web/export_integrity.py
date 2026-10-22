"""HMAC-SHA256 generation and verification for grade CSV exports."""

import base64
import binascii
import hashlib
import hmac
import os
import sys


HMAC_PREFIX = b"# HMAC: "


def _load_key():
    encoded_key = os.environ.get("NOTESAPP_EXPORT_HMAC_KEY", "")
    try:
        key = base64.b64decode(encoded_key, validate=True)
    except binascii.Error as exc:
        raise RuntimeError("NOTESAPP_EXPORT_HMAC_KEY must be base64-encoded") from exc
    if len(key) != 32:
        raise RuntimeError("NOTESAPP_EXPORT_HMAC_KEY must encode a 32-byte key")
    return key


def sign_export(csv_bytes):
    """Append an HMAC line to the exact UTF-8 bytes produced by csv.writer."""
    if not csv_bytes.endswith(b"\r\n"):
        raise ValueError("CSV data must end with CRLF")
    tag = hmac.new(_load_key(), csv_bytes, hashlib.sha256).hexdigest().encode("ascii")
    return csv_bytes + HMAC_PREFIX + tag + b"\r\n"


def verify_export(export_bytes):
    """Verify the CSV body against its final HMAC line."""
    if not export_bytes.endswith(b"\r\n"):
        return False
    body, separator, trailer = export_bytes[:-2].rpartition(b"\r\n")
    if not separator or not trailer.startswith(HMAC_PREFIX):
        return False
    expected = hmac.new(_load_key(), body + separator, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected.encode("ascii"), trailer[len(HMAC_PREFIX):])


if __name__ == "__main__":
    valid = verify_export(sys.stdin.buffer.read())
    print("CHECK PASSED" if valid else "CHECK FAILED")
    raise SystemExit(0 if valid else 1)
