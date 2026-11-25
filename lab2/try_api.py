"""Lab 2 - call every operation of the Courses Service and show what happens."""
import sys
import httpx

base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
course = {"code": "BSWE4321", "title": "Distributed Software Systems", "credits": 2, "capacity": 40}

def show(label, response):
    body = response.text if response.content else "(no body)"
    print(f"{label:<34} -> {response.status_code} {body}")

with httpx.Client(base_url=base, timeout=5.0) as client:
    show("POST /courses", client.post("/courses", json=course))
    show("GET /courses/BSWE4321", client.get("/courses/BSWE4321"))
    show("GET /courses/XYZ999", client.get("/courses/XYZ999"))

    course["capacity"] = 45
    show("PUT /courses/BSWE4321 (cap 45)", client.put("/courses/BSWE4321", json=course))
    show("GET /courses", client.get("/courses"))

    bad = {"code": "BAD1", "title": "Broken", "credits": "two", "capacity": 0}
    show("POST /courses (invalid data)", client.post("/courses", json=bad))

    show("DELETE /courses/BSWE4321", client.delete("/courses/BSWE4321"))
    show("GET /courses/BSWE4321", client.get("/courses/BSWE4321"))