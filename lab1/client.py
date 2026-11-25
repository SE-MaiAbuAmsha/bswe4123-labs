"""Lab 1 - call the service once and compare clocks."""
import sys
from datetime import datetime, timezone

import httpx

base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

with httpx.Client(timeout=5.0) as client:
    client.get(f"{base_url}/info")
    t_send = datetime.now(timezone.utc)
    response = client.get(f"{base_url}/info")
    t_receive = datetime.now(timezone.utc)

data = response.json()
server_time = datetime.fromisoformat(data["server_time"])
round_trip_ms = (t_receive - t_send).total_seconds() * 1000
midpoint = t_send + (t_receive - t_send) / 2
offset_ms = (server_time - midpoint).total_seconds() * 1000

print(f"Answered by host : {data['host']}")
print(f"Round trip : {round_trip_ms:.1f} ms")
print(f"Server clock : {server_time.isoformat()}")
print(f"My clock (mid) : {midpoint.isoformat()}")
print(f"Estimated offset : {offset_ms:.1f} ms (server minus me)")