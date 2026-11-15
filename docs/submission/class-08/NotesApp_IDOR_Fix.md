# NotesApp IDOR Fix

Date: 12 November 2026

Class 8 lab, run against the local NotesApp clone. The app is served over HTTPS
at `https://localhost` under the Class 5/7 configuration, so the commands use
`curl -k` for the local self-signed certificate (equivalent to the lab's
`http://localhost:8080`).

## Predictions

Recorded before running the attack, as the lab requires:

| Question | Prediction | Result |
|---|---|---|
| As alice, what does `/api/notes/3` (not hers) return? | **Someone else's grade** | Confirmed: bob's note, grade 12.6. |
| After the fix, does that same request still work? | **No** | Confirmed: `not found` (HTTP 404). |
| After the fix, can alice still read her own note, and the teacher read any note? | **Yes** | Confirmed: alice note 1 (HTTP 200), prof.turing note 3 (HTTP 200). |

## Audit line

```text
IDOR FIX — NotesApp flaw #7 (broken access control) closed
  Proof you got in:  as alice, /api/notes/3 returned bob's grade: 12.6, "Solid work, keep it up."
  Fix:   api_notes refuses a note whose student_id is not the caller's,
         unless the caller is a teacher/admin
  Code chosen:  [x] 404 not found   [ ] 403 forbidden
  Proof it's closed:  as alice,      /api/notes/3 -> {"error":"not found"} (HTTP 404)
                      as alice,      /api/notes/1 -> her own note, grade 16.2 (HTTP 200)
                      as prof.turing,/api/notes/3 -> bob's note, grade 12.6 (HTTP 200)
```

## The bug

The handler authenticated the caller but never authorised them. It asked only
*"are you logged in?"* (`if not ident`), never *"is this note yours?"* — so any
authenticated student could read any note by changing the id in the URL. Logged
in as alice (student_id 6), one `for` loop over ids 1..10 read the whole class:
five students, ten grades. Raw output:
[before-fix-idor.txt](class-08-evidence/before-fix-idor.txt).

The note row already carries the owner (`student_id`) and `ident` already carries
the caller's `user_id` and `role`, so the fix is a direct comparison of the two.

## What changed

Added an ownership check in `api_notes` (`web/app.py`), right after the note is
fetched:

```python
    note = cur.fetchone()
    conn.close()
    if not note:
        return jsonify({"error": "not found"}), 404
    # Flaw #7 fix (IDOR / broken access control): authentication is not enough;
    # we must also check authorization. A student may read only their OWN note.
    # Teachers and admins are allowed to read any note (that is their job).
    # We return 404 (not 403) so we do not even confirm the id exists.
    if (note["student_id"] != ident["user_id"]
            and ident.get("role") not in ("teacher", "admin")):
        return jsonify({"error": "not found"}), 404
```

A student now sees only their own note; a teacher or admin may read any note.

### Why 404, not 403

Both close the hole. `403 forbidden` confirms the id exists ("you're just not
allowed"), which lets an attacker map which ids are real. `404 not found`
reveals nothing, so the attacker cannot even enumerate the objects. (403 is
accepted for this lab; this fix chose 404.)

## Evidence

After the fix, replaying the exact request that leaked bob's grade, plus the two
regression checks:

```text
### FIX: alice -> /api/notes/3 (bob's note)
{"error": "not found"}
HTTP 404

### alice -> /api/notes/1 (her own)
{"id": 1, "student": "alice", "grade": 16.2, ...}
HTTP 200

### prof.turing -> /api/notes/3 (teacher)
{"id": 3, "student": "bob", "grade": 12.6, ...}
HTTP 200
```

Walking ids 1..10 as alice after the fix, only her own notes (1, 2) return 200;
every other id returns HTTP 404. Raw output:
[after-fix-proof.txt](class-08-evidence/after-fix-proof.txt).

## The deeper lesson

`/api/notes/<id>` was one door. The same bug hides anywhere an id in a URL names
something that belongs to one user (`/invoice/<id>`, `/message/<id>`,
`/order/<id>`). The server must decide what the caller may see from their
identity, for every object — never trust that the url handed to the client is
the only one it will ask for.

[Class 8 lab](https://kristenpire.github.io/epita-security-labs/class8/read-anyones-grade/)
