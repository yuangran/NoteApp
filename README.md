# NotesApp

- **Name:** Yu Angran
- **English name:** Terry
- **Student ID:** 2023900899

A small grades application used throughout the Computer Security course. Teachers
record grades and comments for their classes, students read their own grades, and an
admin manages users and classes.

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

Start the application:

```
docker compose up --build
```

The first start builds the image, launches PostgreSQL, and loads the seed data
automatically. NotesApp encrypts the seeded comments before serving requests.
When it is ready, open:

```
http://localhost:8080
```

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
- Docker Compose (`web` and `db` services)

## Reset

```
docker compose down -v   # wipes the database volume
docker compose up        # reloads the seed data
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
docker compose up --build
```

A plain `docker compose up` would keep running the old image.
