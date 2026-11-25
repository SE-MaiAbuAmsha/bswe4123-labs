# Lab Assignment 2: Campus Room Booking Service

**Student:** Mai Abu Amsha - 120220681

## 1. API Design Table

| Operation             | Method   | URI                      | Request Body                                                                                      | Success Code             | Error Codes & Triggers                                                                                                                         |
| :-------------------- | :------- | :----------------------- | :------------------------------------------------------------------------------------------------ | :----------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| Create Room           | `POST`   | `/rooms`                 | `{"id": "B205", "building": "IT", "capacity": 30}`                                                | `201 Created`            | `409 Conflict` (Room exists), `422 Unprocessable` (Invalid data)                                                                               |
| Get Room              | `GET`    | `/rooms/{room_id}`       | None                                                                                              | `200 OK`                 | `404 Not Found` (Unknown room)                                                                                                                 |
| Create/Update Booking | `PUT`    | `/bookings/{booking_id}` | `{"room_id": "B205", "date": "2026-12-01", "start_hour": 10, "end_hour": 12, "purpose": "Study"}` | `200 OK` / `201 Created` | `404 Not Found` (Room doesn't exist), `409 Conflict` (Overlapping booking), `422 Unprocessable` (end_hour <= start_hour or hours out of range) |
| Get Booking           | `GET`    | `/bookings/{booking_id}` | None                                                                                              | `200 OK`                 | `404 Not Found` (Booking doesn't exist)                                                                                                        |
| Delete Booking        | `DELETE` | `/bookings/{booking_id}` | None                                                                                              | `204 No Content`         | `404 Not Found` (Booking doesn't exist)                                                                                                        |

## 2. Test Execution Output (`test_bookings.py`)

```text
--- 1. Testing Room Operations ---
POST /rooms (Create B205)                     -> Status: 201 | Body: {"id":"B205","building":"IT Faculty","capacity":30}
POST /rooms (Duplicate - expect 409)          -> Status: 409 | Body: {"detail":"Room B205 already exists"}
GET /rooms/B205 (Success)                     -> Status: 200 | Body: {"id":"B205","building":"IT Faculty","capacity":30}
GET /rooms/XYZ (Non-existent - expect 404)    -> Status: 404 | Body: {"detail":"Room XYZ not found"}

--- 2. Testing Booking & Validation Operations ---
PUT /bookings/b1 (Invalid Time - expect 422)  -> Status: 422 | Body: {"detail":"end_hour must be greater than start_hour"}
PUT /bookings/b1 (Unknown Room - expect 404)  -> Status: 404 | Body: {"detail":"Room NO_ROOM does not exist"}
PUT /bookings/b1 (Create Booking b1)          -> Status: 201 | Body: {"room_id":"B205","date":"2026-12-01","start_hour":10,"end_hour":12,"purpose":"Study Group"}
PUT /bookings/b2 (Adjacent 12-14 - Success)   -> Status: 201 | Body: {"room_id":"B205","date":"2026-12-01","start_hour":12,"end_hour":14,"purpose":"Lab Session"}
PUT /bookings/b3 (Overlap 11-13 - expect 409) -> Status: 409 | Body: {"detail":"Booking time overlaps with an existing reservation"}

--- 3. Testing Idempotency (Safe Retry) ---
PUT /bookings/b1 (Attempt 1)                  -> Status: 200 | Body: {"room_id":"B205","date":"2026-12-01","start_hour":10,"end_hour":12,"purpose":"Study Group"}
PUT /bookings/b1 (Attempt 2 - Retry)          -> Status: 200 | Body: {"room_id":"B205","date":"2026-12-01","start_hour":10,"end_hour":12,"purpose":"Study Group"}
```

## 3. Safe Retry (Idempotency) Design - Step 4

To make booking creation safe to retry, I used the PUT method and allowed the client to choose the booking_id in the URL.

How it works:

If the app sends PUT /bookings/b1 for the first time, the server creates the booking and returns 201 Created.

If the reply is lost and the app sends the exact same PUT /bookings/b1 request again, the server checks if the booking exists. Since the data is identical, the server does not create a duplicate. It simply returns 200 OK with the existing booking.

In the test output (Section 3), you can see PUT /bookings/b1 (Attempt 1) returns 200, and PUT /bookings/b1 (Attempt 2 - Retry) also returns 200. The server state does not change, and no second booking is created. This proves the operation is idempotent and safe to retry.
