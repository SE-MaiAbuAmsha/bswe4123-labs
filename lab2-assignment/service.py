from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from typing import Dict, List

app = FastAPI(title="Campus Room Booking Service")

# 1. Models
class Room(BaseModel):
    id: str = Field(min_length=2, max_length=10, examples=["B205"])
    building: str = Field(min_length=2, examples=["Engineering"])
    capacity: int = Field(ge=1, examples=[4])

class Booking(BaseModel):
    room_id: str
    date: str = Field(examples=["2026-12-01"])
    start_hour: int = Field(ge=8, le=19, description="Start hour (8 to 19)")
    end_hour: int = Field(ge=9, le=20, description="End hour (9 to 20)")
    purpose: str = Field(min_length=3, examples=["Study Group"])

# Data storage (in-memory)
rooms: Dict[str, Room] = {}
bookings: Dict[str, Booking] = {}

# 2. Rooms Endpoints
@app.post("/rooms", status_code=201)
def create_room(room: Room):
    if room.id in rooms:
        raise HTTPException(status_code=409, detail=f"Room {room.id} already exists")
    rooms[room.id] = room
    return room

@app.get("/rooms/{room_id}")
def get_room(room_id: str):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    return rooms[room_id]

@app.get("/rooms")
def list_rooms():
    return list(rooms.values())

# Helper: Check time overlap
def check_overlap(new_b: Booking, ignore_id: str = None):
    for b_id, existing in bookings.items():
        if b_id == ignore_id:
            continue
        if existing.room_id == new_b.room_id and existing.date == new_b.date:
            # Overlap condition: max(start1, start2) < min(end1, end2)
            if max(new_b.start_hour, existing.start_hour) < min(new_b.end_hour, existing.end_hour):
                return True
    return False

# 3. Bookings Endpoints (Idempotent PUT)
@app.put("/bookings/{booking_id}")
def create_or_update_booking(booking_id: str, booking: Booking, response: Response):
    # Validate end_hour > start_hour
    if booking.end_hour <= booking.start_hour:
        raise HTTPException(status_code=422, detail="end_hour must be greater than start_hour")
    
    # Check if room exists
    if booking.room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"Room {booking.room_id} does not exist")
    
    # Check if idempotently repeating exact same request
    if booking_id in bookings:
        existing = bookings[booking_id]
        if existing == booking:
            response.status_code = 200
            return booking  # Return existing booking without error (Safe retry)
            
    # Check time overlap with other bookings
    if check_overlap(booking, ignore_id=booking_id):
        raise HTTPException(status_code=409, detail="Booking time overlaps with an existing reservation")
    
    response.status_code = 200 if booking_id in bookings else 201
    bookings[booking_id] = booking
    return booking

@app.get("/bookings/{booking_id}")
def get_booking(booking_id: str):
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    return bookings[booking_id]

@app.delete("/bookings/{booking_id}", status_code=204)
def delete_booking(booking_id: str):
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    del bookings[booking_id]
    return Response(status_code=204)
