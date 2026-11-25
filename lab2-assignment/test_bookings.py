import httpx

BASE_URL = "http://127.0.0.1:8000"

def log(label, resp):
    body = resp.text if resp.content else "(empty)"
    print(f"{label:<45} -> Status: {resp.status_code} | Body: {body}")

with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
    print("--- 1. Testing Room Operations ---")
    room_data = {"id": "B205", "building": "IT Faculty", "capacity": 30}
    log("POST /rooms (Create B205)", client.post("/rooms", json=room_data))
    log("POST /rooms (Duplicate - expect 409)", client.post("/rooms", json=room_data))
    log("GET /rooms/B205 (Success)", client.get("/rooms/B205"))
    log("GET /rooms/XYZ (Non-existent - expect 404)", client.get("/rooms/XYZ"))

    print("\n--- 2. Testing Booking & Validation Operations ---")
    invalid_time = {"room_id": "B205", "date": "2026-12-01", "start_hour": 14, "end_hour": 10, "purpose": "Study"}
    log("PUT /bookings/b1 (Invalid Time - expect 422)", client.put("/bookings/b1", json=invalid_time))

    unknown_room = {"room_id": "NO_ROOM", "date": "2026-12-01", "start_hour": 10, "end_hour": 12, "purpose": "Study"}
    log("PUT /bookings/b1 (Unknown Room - expect 404)", client.put("/bookings/b1", json=unknown_room))

    valid_b1 = {"room_id": "B205", "date": "2026-12-01", "start_hour": 10, "end_hour": 12, "purpose": "Study Group"}
    log("PUT /bookings/b1 (Create Booking b1)", client.put("/bookings/b1", json=valid_b1))

    valid_b2 = {"room_id": "B205", "date": "2026-12-01", "start_hour": 12, "end_hour": 14, "purpose": "Lab Session"}
    log("PUT /bookings/b2 (Adjacent 12-14 - Success)", client.put("/bookings/b2", json=valid_b2))

    overlap_b3 = {"room_id": "B205", "date": "2026-12-01", "start_hour": 11, "end_hour": 13, "purpose": "Meeting"}
    log("PUT /bookings/b3 (Overlap 11-13 - expect 409)", client.put("/bookings/b3", json=overlap_b3))

    print("\n--- 3. Testing Idempotency (Safe Retry) ---")
    log("PUT /bookings/b1 (Attempt 1)", client.put("/bookings/b1", json=valid_b1))
    log("PUT /bookings/b1 (Attempt 2 - Retry)", client.put("/bookings/b1", json=valid_b1))