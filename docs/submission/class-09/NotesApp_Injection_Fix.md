# NotesApp Injection Fix

Date: 17 November 2026

Class 9 lab ("Your words become commands"), run against the local NotesApp
clone. The app is served over HTTPS at `https://localhost` under the Class 5/7
configuration, so the commands use `curl -k` for the local self-signed
certificate (this is the local equivalent of the lab's `http://localhost:8080`).

Two injection flaws are exercised and then closed with the same one idea —
**stop gluing user input into a command string; pass it as data in its own
envelope**:

- **Flaw #8 — SQL injection** on the login query.
- **Flaw #9 — command injection** on the admin "ping a host" box.

## One difference from the lab handout

The handout assumes the login SQL embeds the password:

```sql
WHERE username = '...' AND password = '...'
```

This clone had already moved the password check into Python (Argon2 verify,
from the Class 5 lab), so the query was only:

```python
"SELECT id, username, role, password FROM users WHERE username = '" + username + "'"
```

Because of that, the handout's classic payload `admin' -- ` does **not** log you
in here: it returns the admin row, but Python then verifies the password
(`anything`) and fails. The SQL injection is still fully exploitable, just via a
**UNION** that forges a row whose `password` column equals a value we also
submit — which satisfies Python's plaintext-compare branch:

```
username = zzz' UNION SELECT 1,'admin','admin','pwn' --
password = pwn
```

This is exactly the handout's point: filtering or avoiding `--` is not a fix,
because the attacker picks the grammar. Only parameterisation closes it.

## Audit line

```text
INJECTION FIX — NotesApp flaws #8 (SQL injection) and #9 (command injection) closed

  SQLi proof (break):   username  zzz' UNION SELECT 1,'admin','admin','pwn' --   (password: pwn)
                        -> HTTP 302, logged in as admin, no real admin password used
  SQLi fix:             login() uses a parameterised query (WHERE username = %s + tuple), no string gluing
  SQLi proof (closed):  same username -> HTTP 200 (login redrawn), /admin -> Redirecting... (blocked)

  CmdI proof (break):   host  127.0.0.1; id; head -2 /etc/passwd
                        -> ping output + uid=0(root) gid=0(root) + root:x:0:0:root:... from /etc/passwd
  CmdI fix:             admin_ping() uses subprocess.run(["ping","-c","1",host]) list, no shell=True
                        plus a hostname allow-list regex (defence in depth)
  CmdI proof (closed):  same host -> "Invalid host." — no ping, no id, no /etc/passwd

  Real use still works: alice login OK [x]   plain 127.0.0.1 ping OK [x]   admin/admin123 login OK [x]
```

## Part 1 — SQL injection (the break)

`login()` built the query by concatenating `username` straight into the SQL
string. Sending the UNION payload above made the database return an
attacker-defined row (`id=1, username='admin', role='admin', password='pwn'`);
Python's plaintext branch then compared `'pwn' == 'pwn'` and authenticated us as
admin. The `/admin` page opened, with no admin password ever supplied.

Full output: [before-fix.txt](class-09-evidence/before-fix.txt).

## Part 2 — SQL injection (the fix)

[`web/app.py`](../../../web/app.py), `login()`:

```python
# before
query = ("SELECT id, username, role, password FROM users "
         "WHERE username = '" + username + "'")
cur.execute(query)

# after
query = "SELECT id, username, role, password FROM users WHERE username = %s"
cur.execute(query, (username,))
```

The `%s` is a placeholder the psycopg2 driver fills with `username` as **data**,
never as SQL grammar. The UNION payload is now looked up as a literal username —
no such user exists, so login simply fails. The quote is just a quote.

## Part 3 — command injection (break and fix)

The admin ping box built a shell command by concatenation and ran it with
`shell=True`:

```python
cmd = "ping -c 1 " + host
subprocess.run(cmd, shell=True, ...)
```

The shell reads `;` as "now run the next command", so
`host = 127.0.0.1; id; head -2 /etc/passwd` ran `id` (returning
`uid=0(root)` — the container runs as root, flaw #13) and leaked `/etc/passwd`.

Fix — hand the command as an argument list so `host` is one single argument,
and never invoke a shell at all:

```python
if not re.fullmatch(r"[A-Za-z0-9.-]+", host):
    output = "Invalid host."
else:
    result = subprocess.run(
        ["ping", "-c", "1", host],
        capture_output=True, text=True, timeout=10,
    )
```

With no shell, `;`, `|`, `&&` are just characters in a hostname. The allow-list
regex is a second wall (defence in depth): the same payload now returns
"Invalid host." and never reaches `ping`.

## Part 4 — real features still work

- `admin` / `admin123` logs in (HTTP 302) — the real password still works.
- `alice` / `alicepw` logs in (HTTP 302) and her dashboard loads.
- A plain `127.0.0.1` in the ping box still pings normally.

Full output: [after-fix.txt](class-09-evidence/after-fix.txt).

## The deeper lesson

SQL and the shell are two languages but one mistake: user text glued into a
command string. The rule is always the same — pass data as data, in its own
envelope, never as part of the command. The same bug waits at every place text
meets an interpreter (a template → stored XSS, a file path, etc.).
