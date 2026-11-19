# Submission reports

| Assignment | Location | Contents |
|---|---|---|
| Session 02 and Project 1 | [session-02-project-1/](session-02-project-1/) | Data-flow diagram, STRIDE table, SVG diagrams |
| Session 03: comment encryption | [`web/comment_crypto.py`](../../web/comment_crypto.py) | AES-GCM code (no separate English report) |
| Class 4: grade export integrity | [`web/export_integrity.py`](../../web/export_integrity.py) | HMAC code (no separate English report) |
| Class 5: HTTPS and passwords | [class-05/](class-05/) | Transit and password audit PDFs; local Markdown notes and capture evidence are not committed |
| Class 6: JWT forgery | [class-06/](class-06/) | Report (Markdown/PDF) and evidence |
| Class 7: JWT fix | [class-07/](class-07/) | Report (Markdown/PDF), audit line, fixed `verify_jwt`, and evidence |
| Class 8: IDOR fix | [class-08/](class-08/) | Report (Markdown/PDF), audit line, fixed `api_notes` ownership check, and before/after evidence |
| Class 9: injection fix | [class-09/](class-09/) | Report (Markdown/PDF), audit line, fixed `login` (parameterised) and `admin_ping` (no shell), and before/after evidence |
| Class 10: stored XSS fix | [class-10/](class-10/) | Report (Markdown/PDF), audit line, `autoescape false` removed from `dashboard.html` and `teacher.html`, and before/after evidence |
| Class 11: CSRF fix | [class-11/](class-11/) | Report (Markdown/PDF), audit line, per-session CSRF token in `app.py`, hidden `csrf_token` field in `teacher.html` (1 form) + `admin.html` (3 forms), and before/after evidence (curl + browser screenshots) |
