import hashlib
import time

from argon2 import PasswordHasher


count = 100_000
start = time.perf_counter()
for _ in range(count):
    hashlib.md5(b"guess").hexdigest()
md5_rate = count / (time.perf_counter() - start)

ph = PasswordHasher()
start = time.perf_counter()
ph.hash("guess")
argon2_seconds = time.perf_counter() - start
argon2_rate = 1 / argon2_seconds

print(f"MD5: {md5_rate:.3f} guesses/second; {md5_rate * 86_400:.3f} guesses/day")
print(f"Argon2: {argon2_seconds * 1000:.3f} ms/guess; {argon2_rate:.3f} guesses/second; {argon2_rate * 86_400:.3f} guesses/day")
print(f"Argon2 is {md5_rate / argon2_rate:.3f} times slower per guess.")
