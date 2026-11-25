"""Lab 2 - send the same request twice and compare (idempotency)."""
import sys
import httpx

base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
method = sys.argv[2].lower() if len(sys.argv) > 2 else "post"
course = {"code": "BSWE4123", "title": "Distributed Systems Lab", "credits": 1, "capacity": 25}

with httpx.Client(base_url=base, timeout=5.0) as client:
    for attempt in (1, 2):
        if method == "post":
            r = client.post("/courses", json=course)
        elif method == "put":
            r = client.put("/courses/BSWE4123", json=course)
        else:
            r = client.delete("/courses/BSWE4123")
        print(f"{method.upper()} attempt {attempt}: status {r.status_code}")
        print("Courses now on the server:", [c["code"] for c in client.get("/courses").json()])