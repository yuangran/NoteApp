# NotesApp Stored XSS Fix

Date: 18 November 2026

Class 10 lab ("Your words run in someone else's browser"), run against the local
NotesApp clone. The app is served over HTTPS at `https://localhost` under the
Class 5/7 configuration, so the commands use `curl -k` for the local self-signed
certificate (the local equivalent of the lab's `http://localhost:8080`), and the
stack is rebuilt with
`docker compose -f docker-compose.yml -f docker-compose.https.yml up -d --build`.

One flaw is exercised and then closed:

- **Flaw #10: stored XSS** in the grade comment, shown on the student dashboard
  and on the teacher page.

## Audit line

```text
STORED XSS FIX: NotesApp flaw #10 closed

Break:    prof.turing posts note_id=1, grade=16.2, comment =
            <script>alert('XSS: runs as ...')</script>
          -> live <script> in alice's /dashboard (line 42)
             and on /teacher; the alert fires in Chrome as alice
Fix:      autoescape false wrapper removed in dashboard.html and
          teacher.html -> <td>{{ n.comment }}</td>
Closed:   same payload re-posted -> alice gets
            &lt;script&gt;alert(&#39;XSS: ...)&lt;/script&gt;
          shown as text, no alert
Real use: "score < 10 on part 1 & 2, see me" -> sent as
            score &lt; 10 on part 1 &amp; 2, see me
          and displayed correctly
```

## The bug

Jinja2 escapes every `{{ ... }}` by default. Both templates turned that off for the
comment cell only:

```html
<td>{% autoescape false %}{{ n.comment }}{% endautoescape %}</td>
```

The comment was therefore written into the page as HTML, so the browser treated a
`<script>` in it as code. The attack is *stored*: the teacher writes it once with
`POST /grades`, the database keeps it, and it runs for every later reader of that
note. Here that means the student alice on `/dashboard`, and the teacher on `/teacher`.

The Session 03 AES-GCM comment encryption does not help. It protects the comment
at rest. `dashboard()` and `teacher()` decrypt it before rendering, so the
template gets the original text. Encryption protects storage; escaping protects
output.

## Part 1: plant and trigger (the break)

1. Log in as `prof.turing` / `teach123` with `curl -k -c teacher.jar`.
2. `POST /grades` with `note_id=1` (alice's Mathematics note), `grade=16.2`, and
   the comment `<script>alert('XSS: runs as '+document.title+' for alice')</script>`.
3. Log in as `alice` / `alicepw` with `curl -k -c alice.jar`, fetch `/dashboard`.

**Prediction:** the browser runs the script, because the template marks the
comment as trusted HTML.

**Result:** the raw tag is in alice's HTML:

```html
<td><script>alert('XSS: runs as '+document.title+' for alice')</script></td>
```

Opening `https://localhost/dashboard` as alice in Chrome showed the alert dialog.
This is the lab checkpoint. The same live tag was also on the teacher page.

Because the script runs inside alice's page and session, it could also call
`/grades` or `/api/notes/...` as her. The Flask session cookie is `HttpOnly`, so
`document.cookie` cannot read it directly. That does not stop the script from
making requests as alice.

Full output: [before-fix.txt](class-10-evidence/before-fix.txt).

## Part 2: restore escaping (the fix)

[`web/templates/dashboard.html`](../../../web/templates/dashboard.html) and
[`web/templates/teacher.html`](../../../web/templates/teacher.html):

```html
<!-- before -->
<td>{% autoescape false %}{{ n.comment }}{% endautoescape %}</td>

<!-- after -->
<td>{{ n.comment }}</td>
```

Only the wrapper goes; `{{ n.comment }}` stays. A search of `web/templates` and
`web/app.py` found no other `autoescape false`, `|safe`, or `Markup`.

No filter on the word "script" was added. A blocklist misses
`<img src=x onerror=...>`, `<svg onload=...>`, mixed case, and many other
variants. Escaping covers all of them because it changes every `<` into `&lt;`,
whatever follows it.

## Part 3: prove the attack is dead

After rebuilding, the same payload was posted again as the teacher. Alice's
dashboard now contains:

```html
<td>&lt;script&gt;alert(&#39;XSS: runs as &#39;+document.title+&#39; for alice&#39;)&lt;/script&gt;</td>
```

`grep "<script>alert"` finds nothing on `/dashboard` or `/teacher`. The browser
shows the payload as plain text, and no alert fires.

## Part 4: normal comments still work

The teacher posted `grade=11.0` with the comment
`score < 10 on part 1 & 2, see me`. The HTML sent to alice is:

```html
<td>score &lt; 10 on part 1 &amp; 2, see me</td>
```

The browser displays exactly `score < 10 on part 1 & 2, see me`. Escaping keeps
the characters; it only stops them from being read as markup.

Full output: [after-fix.txt](class-10-evidence/after-fix.txt). The existing
`unittest` suite still passes (7 tests).

## If rich text were really needed

Keep autoescape on and sanitise the comment on the server with an allow-list
(for example `bleach.clean(comment, tags=["b", "i", "a"], attributes={"a": ["href"]})`),
then mark only that sanitised output as safe. Never turn escaping off for raw input.

## The deeper lesson

Class 9 was injection on the way *in*: user text glued into SQL or a shell
command. Class 10 is the same injection on the way *out*: user text glued into
HTML, where the browser is the interpreter. The rule is the same: data stays
data, and escaping is on by default and never turned off for user input.
