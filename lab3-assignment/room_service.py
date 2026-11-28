import os
import asyncio
from fastapi import FastAPI, HTTPException, Response, Request
from pydantic import BaseModel, Field
from typing import Dict

app = FastAPI(title="Room Booking Service")
DELAY = float(os.getenv("ROOM_DELAY", "0"))

@app.middleware("http")
async def slow_down(request: Request, call_next):
    if DELAY > 0:
        await asyncio.sleep(DELAY)
    return await call_next(request)

class Room(BaseModel):
    id: str = Field(min_length=1, max_length=10, examples=["B205"])
    building: str = Field(min_length=1, examples=["Engineering"])
    capacity: int = Field(ge=1, examples=[4])

class Booking(BaseModel):
    room_id: str
    date: str = Field(examples=["2026-12-01"])
    start_hour: int = Field(ge=8, le=19)
    end_hour: int = Field(ge=9, le=20)
    purpose: str = Field(min_length=1)

rooms: Dict[str, Room] = {}
bookings: Dict[str, Booking] = {}

@app.post("/rooms", status_code=201)
def create_room(room: Room):
    if room.id in rooms:
        raise HTTPException(409, f"Room {room.id} already exists")
    rooms[room.id] = room
    return room

@app.get("/rooms")
def list_rooms():
    return list(rooms.values())

@app.put("/bookings/{booking_id}")
def create_or_update_booking(booking_id: str, booking: Booking, response: Response):
    if booking.end_hour <= booking.start_hour:
        raise HTTPException(422, "end_hour must be greater than start_hour")
    
    if booking.room_id not in rooms:
        raise HTTPException(404, f"Room {booking.room_id} does not exist")
    
    if booking_id in bookings and bookings[booking_id] == booking:
        response.status_code = 200
        return booking
            
    for b_id, existing in bookings.items():
        if b_id == booking_id:
            continue
        if existing.room_id == booking.room_id and existing.date == booking.date:
            if max(booking.start_hour, existing.start_hour) < min(booking.end_hour, existing.end_hour):
                raise HTTPException(409, "Booking time overlaps with an existing reservation")
    
    response.status_code = 200 if booking_id in bookings else 201
    bookings[booking_id] = booking
    return booking