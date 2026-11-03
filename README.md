# NotesApp

- **Name:** Yu Angran
- **English name:** Terry
- **Student ID:** 2023900899

A small grades application used throughout the Computer Security course. Teachers
record grades and comments for their classes, students read their own grades, and an
admin manages users and classes.

## Coursework

| Assignment | Files |
|---|---|
| Session 02 and Project 1 | [Data-flow diagram](docs/submission/session-02-project-1/NotesApp_Data_Flow_Diagram.md), [STRIDE and risk analysis](docs/submission/session-02-project-1/NotesApp_STRIDE_Table.md) |
| Session 03: comment encryption | [AES-GCM storage](web/comment_crypto.py) |
| Class 4: grade export integrity | [HMAC generation and verification](web/export_integrity.py) |
| Class 5: HTTPS and passwords | [Transit audit](docs/submission/class-05/NotesApp_Transit_Audit.pdf), [password audit](docs/submission/class-05/NotesApp_Password_Audit.pdf) |
| Class 6: JWT forgery | [Unsigned and signed token forgery](docs/submission/class-06/NotesApp_JWT_Forgery.md), [PDF](docs/submission/class-06/NotesApp_JWT_Forgery.pdf) |

Report folders are indexed in [docs/submission/README.md](docs/submission/README.md).

## Run it

You need Docker with the Compose plugin. Run these commands from the repository root.
Store a base64-encoded 32-byte AES-GCM key in `.env` as `NOTESAPP_COMMENT_KEY`.
Reuse the same key on later starts to decrypt the stored comments. `.env` is ignored
by Git.

If `NOTESAPP_COMMENT_KEY` is not yet configured, generate it once:

```
python3 -c 'import base64, secrets; print("NOTESAPP_COMMENT_KEY=" + base64.b64encode(secrets.token_bytes(32)).decode())' >> .env
```

Set a separate 32-byte HMAC key for grade exports. If `NOTESAPP_EXPORT_HMAC_KEY`
is not yet configured, generate it once:

```
python3 -c 'import base64, secrets; print("NOTESAPP_EXPORT_HMAC_KEY=" + base64.b64encode(secrets.token_bytes(32)).decode())' >> .env
```

Generate the local certificate and start HTTPS using the commands in
[Class 5: HTTPS and password storage](#class-5-https-and-password-storage) below.
The first start builds the image, launches PostgreSQL, and loads the seed data
automatically. NotesApp encrypts the seeded comments before serving requests.

## Grade export integrity

Use the teacher page's **export CSV** link to download `grades.csv`. The file ends
with `# HMAC: <SHA-256 HMAC>`, computed over the UTF-8 CSV body, including its CRLF
line endings. The HMAC line is excluded from the calculation.

Verify a downloaded file with the server's key:

```
docker compose exec -T web python export_integrity.py < grades.csv
```

The command prints `CHECK PASSED` and exits with status 0 for an unchanged file.
Editing a grade or comment makes it print `CHECK FAILED` and exit with status 1.

Run the integrity checks:

```
docker compose exec -T web python -m unittest discover -s tests -v
```

## Test accounts

| Role    | Username      | Password   |
|---------|---------------|------------|
| Student | `alice`       | `alicepw`  |
| Teacher | `prof.turing` | `teach123` |
| Admin   | `admin`       | `admin123` |

(There are ~30 students in total; each student's password is their username + `pw`,
e.g. `bob` / `bobpw`.)

## Stack

- Python 3.11 + Flask (server-rendered Jinja2 pages and a small JSON API)
- PostgreSQL 15
- Docker Compose (`web`, `db`, and the HTTPS `nginx` service)

## Class 5: HTTPS and password storage

Generate the local certificate:

```sh
mkdir -p nginx/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/notesapp.key -out nginx/certs/notesapp.crt \
  -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

Start NotesApp with nginx:

```sh
docker compose -f docker-compose.yml -f docker-compose.https.yml up -d --build
```

Open `https://localhost`. Nginx terminates TLS on port 443, redirects port 80 to
HTTPS, and forwards requests to `web:5000` inside Docker. The HTTPS overlay removes
the web service's published port 8080.

The local certificate is self-signed. Review its issuer in the browser's
certificate viewer and confirm the local certificate warning to open the app.

Passwords upgrade to Argon2id on successful login. The first successful login for
a legacy account replaces its plaintext password with a salted Argon2 hash.
Subsequent logins verify that hash.

Run the password dictionary exercise from the repository root:

```sh
python3 crack/make_dump.py
python3 crack/crack.py
```

The dictionary is from the course's
[common-passwords.txt](https://kristenpire.github.io/epita-security-labs/class5/assets/common-passwords.txt).
Run the hash-speed measurement in the web container:

```sh
docker compose -f docker-compose.yml -f docker-compose.https.yml exec -T web python - < crack/benchmark.py
```

Audit reports:

- [Transit audit (Lab 1)](docs/submission/class-05/NotesApp_Transit_Audit.pdf)
- [Password audit (Lab 2)](docs/submission/class-05/NotesApp_Password_Audit.pdf)

## Reset

```
docker compose -f docker-compose.yml -f docker-compose.https.yml down -v   # wipes the database volume
docker compose -f docker-compose.yml -f docker-compose.https.yml up -d --build
```

## Updating your fork

The course repository is sometimes updated. Your fork does **not** update by itself.
To pull the latest changes into your fork:

**Easiest (GitHub website):** open your fork, and if it says *"This branch is behind
KristenPire/NoteApp"*, click **Sync fork → Update branch**. Then, in your local clone:

```
git pull
```

**Command line (keeps your own commits):**

```
git remote add upstream https://github.com/KristenPire/NoteApp.git   # once
git fetch upstream
git merge upstream/main
git push
```

Then **rebuild**, because the app code is baked into the Docker image:

```
docker compose -f docker-compose.yml -f docker-compose.https.yml up -d --build
```

A plain `docker compose up` would keep running the old image.
