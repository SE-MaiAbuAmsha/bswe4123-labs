# Lab 2 - Courses REST Service Report

**Student:** Mai Abu Amsha - 120220681

## Experiment 1: Browser

- POST (success): 201
- GET (success): 200
- GET (not found): 404
- PUT (success): 200
- POST (invalid): 422
- DELETE (success): 204
- Who rejected the invalid data? Pydantic (due to the `Field` rules in the `Course` model, specifically `credits: int = Field(ge=1, le=6)`).

## Experiment 2: Client

```text
POST /courses                      -> 409 {"detail":"Course BSWE4321 already exists"}
GET /courses/BSWE4321              -> 200 {"code":"BSWE4321","title":"Distributed Software Systems","credits":2,"capacity":45}
GET /courses/XYZ999                -> 404 {"detail":"Course XYZ999 not found"}
PUT /courses/BSWE4321 (cap 45)     -> 200 {"code":"BSWE4321","title":"Distributed Software Systems","credits":2,"capacity":45}
GET /courses                       -> 200 [{"code":"BSWE4321","title":"Distributed Software Systems","credits":2,"capacity":45},{"code":"PHYS200","title":"Physics","credits":3,"capacity":30}]
POST /courses (invalid data)       -> 422 {"detail":[{"type":"int_parsing","loc":["body","credits"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"two"},{"type":"greater_than_equal","loc":["body","capacity"],"msg":"Input should be greater than or equal to 1","input":0,"ctx":{"ge":1}}]}
DELETE /courses/BSWE4321           -> 204 (no body)
GET /courses/BSWE4321              -> 404 {"detail":"Course BSWE4321 not found"}
```

## Experiment 3: Idempotency

| Method | 1st status | 2nd status | Server state changed by the 2nd call?     |
| ------ | ---------- | ---------- | ----------------------------------------- |
| POST   | 201        | 409        | No (rejected because it already exists)   |
| PUT    | 200        | 200        | No (overwritten with the exact same data) |
| DELETE | 204        | 404        | No (the course was already deleted)       |

- Which methods are idempotent here? PUT and DELETE are idempotent in terms of server state. POST is not idempotent.
- If server generated a new ID for POST: two identical POST requests would create two different courses (double booking), which is very dangerous for a payment system as the user would be charged twice.

## Experiment 4: State

- What did port 8001 answer? It returned an empty list `[]`. Each process has its own isolated memory, so the data created on port 8000 was not visible on port 8001.
- What was left on port 8000 after the restart? Nothing (empty list). The in-memory dictionary was destroyed when the process stopped.
- Why can't they share work? Because the service lacks a central Data Tier (like a database). The current implementation keeps state inside the RAM of a single process, so it is lost on restart and cannot be shared across multiple instances.

## Challenge: Enrollments

- Successfully implemented and tested the POST, GET, and DELETE operations for enrollments.
- Tested constraints: 201 on success, 409 on full capacity or duplicate, 404 on unknown course or student.
- See the attached screenshot `enrollment_student.png` for the Swagger UI evidence.
