# NotesApp CSRF Fix

Date: 19 November 2026

Class 11 lab ("Requests you never meant to send"), run against the local
NotesApp clone. One flaw is exercised and then closed:

- **Flaw #11: cross-site request forgery (CSRF)** on every state-changing POST
  (`/grades`, `/admin/users`, `/admin/ping`). The server accepted any request
  that carried a valid session cookie, without checking that the request came
  from one of its own forms.

## Local setup note (why port 8080, not HTTPS)

Classes 5–10 run this app over the HTTPS overlay at `https://localhost`
(nginx + TLS), which is what `.env`'s `COMPOSE_FILE` selects by default. This
class is the one exception: the attack page is served over plain HTTP on
`http://localhost:9000`, and the target must be same-site so the browser
attaches the session cookie to the forged POST. Browsers treat `http://` and
`https://` origins as different sites, so pointing the attack at
`https://localhost` would make the request genuinely cross-site and the cookie
(under the new `SameSite=Lax`) would be dropped for the wrong reason — hiding
the flaw instead of demonstrating it. So for this class the stack is brought up
on plain HTTP at `http://localhost:8080`, exactly as the lab's commands expect:

```sh
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

After the class, the default HTTPS stack is restored with
`docker compose up -d --build`. Both attack page (`:9000`) and NotesApp
(`:8080`) are `localhost`, i.e. the same site, so the browser still sends the
cookie — which is the whole point of the attack.

## Audit line

```text
CSRF FIX — NotesApp flaw #11 closed

  Break:  logged in as prof.turing, opened localhost:9000/prize.html
          note 10 became -> 19.5, "Changed by Eve's page."

  Fix:    per-session token (secrets.token_urlsafe), checked on every POST,
          hidden csrf_token field in teacher.html (1 form) + admin.html (3 forms)

  Closed: same page now -> 400 Bad Request, grade unchanged

  Real use still works: teacher saves a grade [x]  admin adds a user [x]  admin ping [x]
                        (also admin delete user [x] — the 4th form)
```

## The bug

A login sets a Flask session cookie. After that the browser attaches that cookie
to **every** request to `localhost:8080` on its own — including a request that a
different page told it to send. The three POST handlers only asked
"`login_required(...)`?" — i.e. "is the cookie valid and the role right?" They
never asked "did this request originate from my own form?"

So any external page that makes the victim's browser issue
`POST /grades` has that write accepted as the teacher. A valid cookie proves
**who** the browser belongs to, not **what the user meant to do**.

## Part 1: the server trusts the cookie alone (the break, curl)

Logged in as the Mathematics teacher and kept the cookie, then sent a grade
change with only that cookie — no form, no NotesApp page — and even a spoofed
`Origin: http://evil.example` header:

```sh
curl -s -c teacher.jar -d "username=prof.turing&password=teach123" \
     http://localhost:8080/login -o /dev/null
curl -s -b teacher.jar -H "Origin: http://evil.example" \
     -d "note_id=10&grade=20&comment=Perfect work." \
     http://localhost:8080/grades -o /dev/null -w "forged request HTTP %{http_code}\n"
```

Result: `forged request HTTP 302` — accepted. Eve's Mathematics grade (note 10)
became `20.0` / "Perfect work.", confirmed from her own dashboard. The server
never looked at the request's origin. Full transcript:
[`class-11-evidence/before-fix.txt`](class-11-evidence/before-fix.txt).

## Part 2: do it for real — a page the teacher only opens

A real attacker never has the cookie; she makes the victim's browser send the
request. The attack page
([`class-11-evidence/prize.html`](class-11-evidence/prize.html)) is a hidden form
that auto-submits on load:

```html
<form id="f" action="http://localhost:8080/grades" method="POST">
  <input type="hidden" name="note_id" value="10">
  <input type="hidden" name="grade"   value="19.5">
  <input type="hidden" name="comment" value="Changed by Eve's page.">
</form>
<script>document.getElementById("f").submit();</script>
```

Served on a second origin (`python3 -m http.server 9000`). Logged in as
`prof.turing` in the browser, then opened `http://localhost:9000/prize.html` and
clicked nothing on NotesApp. The page flashed and the browser landed back on the
NotesApp teacher page with note 10 now `19.5` / "Changed by Eve's page." — the
teacher's own browser attached the cookie and sent the write.
Screenshot: [`class-11-evidence/part2-break-browser.jpg`](class-11-evidence/part2-break-browser.jpg).

## Part 3: the fix — a secret stamp on every real form

The fix is not "check the `Origin` header" and not "hope the browser blocks it".
The server must demand proof that the request came from one of its own pages: a
per-session secret token that only NotesApp's pages print and that another site
can never read (the same-origin policy stops Eve's page from reading NotesApp's
HTML). Three pieces, all in [`web/app.py`](../../../web/app.py) and the templates.

**3a — one random secret per session** (after `app.secret_key = SECRET_KEY`):

```python
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"   # defence in depth (browser seatbelt)

def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]

app.jinja_env.globals["csrf_token"] = csrf_token
```

**3b — check it on every POST** (a `before_request` hook):

```python
@app.before_request
def check_csrf():
    if request.method == "POST" and request.endpoint != "login":
        expected = session.get("csrf")
        sent = request.form.get("csrf_token", "")
        if not expected or not hmac.compare_digest(sent, expected):
            abort(400, "CSRF token missing or wrong")
```

The `not expected or` guard makes it **fail closed**: a session with no token
yet must refuse, otherwise an empty submitted value would compare `"" == ""` and
the forgery would pass. Login is exempt so a user with no session can still sign
in. (`hmac` and `abort` were already imported for earlier labs; only
`import secrets` is new.)

**3c — print the stamp in every real form.** A hidden input added as the first
line inside each `<form method="post" …>`:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

Four forms in total: [`web/templates/teacher.html`](../../../web/templates/teacher.html)
(the grade form) and [`web/templates/admin.html`](../../../web/templates/admin.html)
(delete, create, ping).

## Part 4: prove it — forged refused, real form works

**Forged request refused.** Logged in fresh (the new cookie holds no token yet),
then replayed Part 1's forged POST:

```text
forged request HTTP 400
```

**Real teacher form still works.** Fetched `/teacher` with the cookie jar,
extracted the hidden token, and posted it back to reset note 10 to `9.1`:

```sh
TOKEN=$(curl -s -b teacher.jar -c teacher.jar http://localhost:8080/teacher \
        | grep -o 'name="csrf_token" value="[^"]*"' | head -1 | cut -d'"' -f4)
curl -s -b teacher.jar \
     --data-urlencode "note_id=10" --data-urlencode "grade=9.1" \
     --data-urlencode "comment=Very strong final exam." \
     --data-urlencode "csrf_token=$TOKEN" \
     http://localhost:8080/grades -o /dev/null -w "real form HTTP %{http_code}\n"
```

Result: `real form HTTP 302` — saved; Eve's grade is back to `9.1`. Full
transcript: [`class-11-evidence/after-fix.txt`](class-11-evidence/after-fix.txt).

**Browser checks** (logged in normally, so the session holds a token):

- Reopening `http://localhost:9000/prize.html` as the teacher now lands on
  **Bad Request — CSRF token missing or wrong**; note 10 does not change.
  Screenshot: [`class-11-evidence/part4-forged-refused-browser.jpg`](class-11-evidence/part4-forged-refused-browser.jpg).
- All four real forms still work: teacher saved a grade (302); admin created the
  user `csrf_test_user`, pinged `127.0.0.1` ("64 bytes from 127.0.0.1"), and
  deleted `csrf_test_user` again. Screenshot of add-user + ping:
  [`class-11-evidence/part4-admin-realuse-browser.jpg`](class-11-evidence/part4-admin-realuse-browser.jpg).

## A possible hardening (not required)

`secrets.token_urlsafe` only ever returns ASCII, so `hmac.compare_digest(sent,
expected)` is fine for the stored token. But `sent` comes from the attacker; if
it contained a non-ASCII character, `compare_digest` on two `str` values raises
`TypeError` (→ HTTP 500) instead of a clean 400. The write is still blocked, so
this is cosmetic, but comparing the UTF-8 **bytes**
(`hmac.compare_digest(sent.encode(), expected.encode())`) would always return a
tidy 400. The lab's reference solution uses the `str` form, so this submission
keeps it for alignment and notes the edge case here.

## The deeper lesson

A cookie says **who** the browser belongs to; it says nothing about whether that
person chose to send this request. For anything that changes data, the server
must also check **intent** — a secret only its own pages hold. `SameSite=Lax`
helps, but it is the browser's seatbelt; the server must not depend on it alone.
(Flask-WTF's `CSRFProtect` provides the same protection as a one-line library
drop-in.)
