import hashlib
import time
from pathlib import Path


folder = Path(__file__).parent
accounts = {}
for line in (folder / "leaked_users.txt").read_text().splitlines():
    username, digest = line.split(":", 1)
    accounts[username] = digest
wordlist = [word.strip() for word in (folder / "wordlist.txt").read_text().splitlines() if word.strip()]

start = time.perf_counter()
cracked = {}
for candidate in wordlist:
    digest = hashlib.md5(candidate.encode()).hexdigest()
    for username, stored in accounts.items():
        if username not in cracked and digest == stored:
            cracked[username] = candidate
elapsed = time.perf_counter() - start

print(f"cracked {len(cracked)} / {len(accounts)} in {elapsed * 1000:.3f} ms")
for username, password in cracked.items():
    print(f"  {username}: {password}")
