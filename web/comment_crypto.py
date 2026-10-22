"""AES-GCM storage format for NotesApp comments."""

import base64
import binascii
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


PREFIX = "gcm1:"
NONCE_BYTES = 12


def _load_cipher():
    encoded_key = os.environ.get("NOTESAPP_COMMENT_KEY", "")
    try:
        key = base64.b64decode(encoded_key, validate=True)
    except binascii.Error as exc:
        raise RuntimeError("NOTESAPP_COMMENT_KEY must be base64-encoded") from exc
    if len(key) != 32:
        raise RuntimeError("NOTESAPP_COMMENT_KEY must encode a 32-byte key")
    return AESGCM(key)


_cipher = _load_cipher()


def encrypt_comment(comment):
    if comment is None:
        return None
    nonce = os.urandom(NONCE_BYTES)
    ciphertext = _cipher.encrypt(nonce, comment.encode("utf-8"), None)
    return PREFIX + base64.b64encode(nonce + ciphertext).decode("ascii")


def decrypt_comment(stored):
    if stored is None:
        return None
    if not stored.startswith(PREFIX):
        raise ValueError("Comment has not been encrypted")
    payload = base64.b64decode(stored[len(PREFIX):], validate=True)
    if len(payload) < NONCE_BYTES + 16:
        raise ValueError("Invalid encrypted comment")
    nonce = payload[:NONCE_BYTES]
    ciphertext = payload[NONCE_BYTES:]
    return _cipher.decrypt(nonce, ciphertext, None).decode("utf-8")
