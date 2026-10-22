import hashlib
from pathlib import Path


accounts = {
    "liwei": "123456",
    "sofia": "iloveyou",
    "tomk": "qwerty123",
    "aisha": "password1",
    "marie": "mariepw",
    "raj": "Gv7#pLm2!xQ",
}

dump = Path(__file__).with_name("leaked_users.txt")
with dump.open("w") as output:
    for username, password in accounts.items():
        digest = hashlib.md5(password.encode()).hexdigest()
        output.write(f"{username}:{digest}\n")
print("wrote crack/leaked_users.txt")
