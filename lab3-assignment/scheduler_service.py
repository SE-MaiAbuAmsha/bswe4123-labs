import os
import time
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Exam Scheduler Service")

ROOM_SERVICE_URL = os.getenv("ROOM_SERVICE_URL", "http://localhost:8001")
TIMEOUT = float(os.getenv("SCHEDULER_TIMEOUT", "2.0"))
MAX_RETRIES = int(os.getenv("SCHEDULER_RETRIES", "3"))

class ExamRequest(BaseModel):
    exam_id: str = Field(examples=["EXAM1"])
    course_code: str = Field(examples=["BSWE4321"])
    day: str = Field(examples=["2026-12-01"])
    start_hour: int = Field(ge=8, le=19)
    end_hour: int = Field(ge=9, le=20)
    students: int = Field(ge=1)

@app.get("/config")
def get_config():
    return {
        "room_service_url": ROOM_SERVICE_URL,
        "timeout_seconds": TIMEOUT,
        "max_retries": MAX_RETRIES
    }

def fetch_with_retry(method: str, url: str, **kwargs):
    delay = 0.5
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = httpx.request(method, url, timeout=TIMEOUT, **kwargs)
            if response.status_code in [404, 409]:
                return response
            response.raise_for_status()
            return response
        except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError) as e:
            if attempt == MAX_RETRIES:
                raise HTTPException(503, "Room Booking Service is unavailable after retries")
            print(f"Retry {attempt+1} in {delay}s due to: {type(e).__name__}")
            time.sleep(delay)
            delay *= 2 

@app.post("/exams", status_code=201)
def schedule_exam(req: ExamRequest):
    rooms_resp = fetch_with_retry("GET", f"{ROOM_SERVICE_URL}/rooms")
    rooms = rooms_resp.json()

    available_rooms = [r for r in rooms if r["capacity"] >= req.students]
    available_rooms.sort(key=lambda r: r["capacity"])

    for room in available_rooms:
        booking_id = f"exam-{req.exam_id}"
        payload = {
            "room_id": room["id"],
            "date": req.day,
            "start_hour": req.start_hour,
            "end_hour": req.end_hour,
            "purpose": f"Exam {req.course_code}"
        }
        resp = fetch_with_retry("PUT", f"{ROOM_SERVICE_URL}/bookings/{booking_id}", json=payload)
        
        if resp.status_code in [200, 201]:
            return {"message": "Exam booked", "room": room["id"], "booking_id": booking_id}
        elif resp.status_code == 409:
            continue
            
    raise HTTPException(409, "No free room is large enough for this exam")