# Project 1 — NotesApp STRIDE Table and Risk Analysis

**S:** Spoofing · **T:** Tampering · **R:** Repudiation · **I:** Information disclosure · **D:** Denial of service · **E:** Elevation of privilege

**●:** Threat identified · **—:** No entry

| Flow | S | T | R | I | D | E | Threat scenario |
|---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| 01 | ● | ● | — | ● | ● | ● | Stolen teacher or admin credentials enable impersonation; crafted login fields affect authentication; HTTP exposes credentials; repeated attempts consume service capacity. |
| 02 | — | ● | — | ● | — | ● | The login query concatenates form input into SQL, allowing the query to be changed and authentication or database data to be exposed. |
| 03 | — | — | — | — | — | — | — |
| 04 | ● | ● | — | ● | — | ● | A stolen or forged session cookie can transfer another user's identity and privileges. |
| 05 | ● | — | — | ● | — | — | A stolen student session opens the student's grade page. |
| 06 | — | — | — | — | — | — | — |
| 07 | — | — | — | — | — | — | — |
| 08 | — | ● | — | ● | — | — | Unescaped comments can alter the grade page and expose the API token embedded in it. |
| 09 | ● | ● | — | ● | — | ● | An unsigned token can impersonate a user; changing the note ID can request another student's grade. |
| 10 | — | — | — | ● | — | ● | The note query checks the ID but not its owner, allowing another student's record to be selected. |
| 11 | — | — | — | — | — | — | — |
| 12 | — | — | — | ● | — | — | The JSON response can disclose another student's grade details. |
| 13 | ● | — | — | ● | — | ● | A stolen teacher session gives access to teacher data and grade controls. |
| 14 | — | — | — | ● | — | ● | Queries are not limited to the current teacher's classes, so other classes' grades are selected. |
| 15 | — | — | — | — | — | — | — |
| 16 | — | ● | — | ● | — | — | The page displays grades from all classes, and unescaped comments can alter the page. |
| 17 | ● | ● | ● | — | — | ● | A forged teacher request or changed note ID can alter grades outside the teacher's classes; the write lacks a complete audit trail. |
| 18 | — | ● | ● | — | — | ● | The database write checks a note ID but not class ownership; the log omits the old and new values. |
| 19 | — | ● | — | ● | — | ● | Changing `class_id` requests an export of another teacher's class. |
| 20 | — | — | — | ● | — | ● | The export query is not scoped to the current teacher. |
| 21 | — | — | — | — | — | — | — |
| 22 | — | — | — | ● | — | — | The CSV response can disclose an entire class's grades or all grades. |
| 23 | ● | — | — | ● | — | ● | A stolen admin session gives access to user lists and management controls. |
| 24 | — | — | — | — | — | — | — |
| 25 | — | — | — | — | — | — | — |
| 26 | — | — | — | ● | — | — | A stolen admin session receives the usernames and roles shown on this page. |
| 27 | ● | ● | ● | — | — | ● | A forged admin request can create or delete users; role fields can be changed; the operation lacks a separate audit record. |
| 28 | — | ● | ● | — | — | ● | Creating a privileged user or deleting a user changes account permissions without a separate operation log. |

## Risk assessment

Related flows are grouped by risk. Likelihood and impact are scored from 1 (low) to 5 (high). Risk score = likelihood × impact.

| Risk | Flows | STRIDE | Threat | Likelihood | Impact | Score |
|:---:|:---|:---:|---|---:|---:|---:|
| R01 | 01, 05, 13, 23 | S, I, E | Plain HTTP can expose credentials and let an attacker use a student, teacher, or admin account. | 3 | 4 | 12 |
| R02 | 01 | D | Repeated login attempts can consume application and database capacity. | 4 | 2 | 8 |
| R03 | 01–02 | T, I, E | Concatenated login SQL lets crafted input change the query and bypass authentication or expose database data. | 5 | 5 | 25 |
| R04 | 04–05, 13, 17, 23, 26–27 | S, T, I, E | A stolen or forged session cookie lets an attacker act as another user, including a teacher or admin. | 4 | 5 | 20 |
| R05 | 08, 16 | T, I | An unescaped stored comment can change the grade page and expose its embedded API token. | 4 | 4 | 16 |
| R06 | 09 | S, I, E | The API accepts an unsigned JWT, so a forged token can claim another identity. | 5 | 4 | 20 |
| R07 | 09–10, 12 | T, I, E | Changing a note ID retrieves another student's grade because ownership is not checked. | 4 | 4 | 16 |
| R08 | 14, 16 | I, E | A teacher can view notes from classes they do not teach because the query has no teacher scope. | 4 | 3 | 12 |
| R09 | 17–18 | T, E | A teacher can change another class's grade by supplying its note ID because the write has no class ownership check. | 4 | 4 | 16 |
| R10 | 17–18 | R | The grade-write log records the username but omits old and new values and the new record's ID, so disputed changes cannot be fully reconstructed. | 4 | 2 | 8 |
| R11 | 19–20, 22 | T, I, E | A changed or omitted `class_id` can export grades outside the teacher's classes. | 4 | 4 | 16 |
| R12 | 17–18, 27–28 | S, T, E | A CSRF request can make a logged-in teacher write grades or a logged-in admin create or delete users because these state-changing forms have no CSRF check. | 3 | 4 | 12 |
| R13 | 27–28 | R | User creation and deletion lack a separate audit record, making disputed operations hard to trace. | 4 | 2 | 8 |

## Top three risks and fixes

| Priority | Risk | Score | Fix |
|---:|:---:|---:|---|
| 1 | R03 — login SQL injection | 25 | Replace string-concatenated login SQL with a parameterized query for both username and password. |
| 2 | R04 — session impersonation | 20 | Use a strong deployment-specific Flask session secret outside source code, and protect session cookies with HTTPS, `Secure`, and `HttpOnly`. |
| 3 | R06 — forged API identity | 20 | Reject `alg:none`, require a verified JWT signature, and check that the authenticated user may read the requested note. |
