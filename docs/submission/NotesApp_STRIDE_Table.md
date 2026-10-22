# Session 02 — NotesApp STRIDE Table

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
