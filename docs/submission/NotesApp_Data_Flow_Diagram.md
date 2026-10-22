# Session 02 — NotesApp Numbered Data Flow Diagram

Model baseline: upstream NotesApp commit [`1c83e42`](https://github.com/KristenPire/NoteApp/commit/1c83e422429c4b784411701ffd797b5ab5f397dc) (Session 02).

- **TB1:** Browser ↔ Flask application
- **TB2:** Flask application ↔ PostgreSQL database

## A. Login and student grade views

[SVG diagram](diagrams/login-and-student.svg)

```mermaid
sequenceDiagram
    actor B as Browser (any role)
    actor S as Student browser
    participant F as Flask application
    participant D as PostgreSQL
    Note over B,F: TB1: browser / application
    Note over F,D: TB2: application / database
    B->>F: 01 POST /login (username, password)
    F->>D: 02 Query users for login
    D-->>F: 03 User ID, username, role
    F-->>B: 04 Session cookie and role redirect
    S->>F: 05 GET /dashboard (session cookie)
    F->>D: 06 Query this student's grades
    D-->>F: 07 Student's grades and comments
    F-->>S: 08 Grade page HTML and API token
    S->>F: 09 GET /api/notes/id (Bearer token)
    F->>D: 10 Query one note by note ID
    D-->>F: 11 Note, student and class data
    F-->>S: 12 JSON grade detail
```

## B. Teacher grade management and export

[SVG diagram](diagrams/teacher.svg)

```mermaid
sequenceDiagram
    actor T as Teacher browser
    participant F as Flask application
    participant D as PostgreSQL
    Note over T,F: TB1: browser / application
    Note over F,D: TB2: application / database
    T->>F: 13 GET /teacher (session cookie)
    F->>D: 14 Query classes, notes and students
    D-->>F: 15 Class, grade and student records
    F-->>T: 16 Teacher page HTML
    T->>F: 17 POST /grades (IDs, grade, comment)
    F->>D: 18 INSERT or UPDATE notes
    T->>F: 19 GET /export.csv?class_id=...
    F->>D: 20 Query grades for the selected class
    D-->>F: 21 Export rows
    F-->>T: 22 CSV file
```

## C. Administrator user management

[SVG diagram](diagrams/admin.svg)

```mermaid
sequenceDiagram
    actor A as Admin browser
    participant F as Flask application
    participant D as PostgreSQL
    Note over A,F: TB1: browser / application
    Note over F,D: TB2: application / database
    A->>F: 23 GET /admin (session cookie)
    F->>D: 24 Query users and classes
    D-->>F: 25 User, role and class records
    F-->>A: 26 Admin page HTML
    A->>F: 27 POST /admin/users (create or delete user)
    F->>D: 28 INSERT or DELETE users
```

## Numbered flow list

| No. | Sender → Receiver | Boundary | Data crossing |
|---:|---|---|---|
| 01 | Browser → Flask | TB1 | `POST /login`: username and password. |
| 02 | Flask → PostgreSQL | TB2 | Login query against `users`. |
| 03 | PostgreSQL → Flask | TB2 | Matched user ID, username and role. |
| 04 | Flask → Browser | TB1 | Login result, session cookie and role redirect. |
| 05 | Student browser → Flask | TB1 | `GET /dashboard` with session cookie. |
| 06 | Flask → PostgreSQL | TB2 | Query `notes` and `classes` using the session user ID. |
| 07 | PostgreSQL → Flask | TB2 | The student's class names, grades, comments and note IDs. |
| 08 | Flask → Student browser | TB1 | Grade page HTML and an API token embedded in the page. |
| 09 | Student browser → Flask | TB1 | `GET /api/notes/<id>` with note ID and Bearer token. |
| 10 | Flask → PostgreSQL | TB2 | Query one `notes` record by note ID, joined with student and class data. |
| 11 | PostgreSQL → Flask | TB2 | One grade, comment, student and class record. |
| 12 | Flask → Student browser | TB1 | JSON response with grade details. |
| 13 | Teacher browser → Flask | TB1 | `GET /teacher` with session cookie. |
| 14 | Flask → PostgreSQL | TB2 | Queries for classes, notes and student usernames. |
| 15 | PostgreSQL → Flask | TB2 | Class, grade, comment and student records. |
| 16 | Flask → Teacher browser | TB1 | Teacher page HTML with classes, grades and grade form. |
| 17 | Teacher browser → Flask | TB1 | `POST /grades`: note ID, student ID, class ID, grade and comment. |
| 18 | Flask → PostgreSQL | TB2 | `INSERT` or `UPDATE` on `notes`. |
| 19 | Teacher browser → Flask | TB1 | `GET /export.csv` with optional `class_id`. |
| 20 | Flask → PostgreSQL | TB2 | Query grades for one class or all classes. |
| 21 | PostgreSQL → Flask | TB2 | Student, class, grade and comment rows for export. |
| 22 | Flask → Teacher browser | TB1 | CSV file containing those rows. |
| 23 | Admin browser → Flask | TB1 | `GET /admin` with session cookie. |
| 24 | Flask → PostgreSQL | TB2 | Queries for users and classes. |
| 25 | PostgreSQL → Flask | TB2 | User IDs, usernames, roles and class records. |
| 26 | Flask → Admin browser | TB1 | Admin page HTML with user and class lists. |
| 27 | Admin browser → Flask | TB1 | `POST /admin/users`: create-user fields or target user ID for deletion. |
| 28 | Flask → PostgreSQL | TB2 | `INSERT` or `DELETE` on `users`. |
