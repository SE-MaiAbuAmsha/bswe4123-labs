import time
import sys
from fastapi import FastAPI
import uvicorn

app = FastAPI()
start_time = time.time()

@app.get("/health")
def health(delay: float = 0.0):
    if delay > 0:
        time.sleep(delay)
    uptime = time.time() - start_time
    return {"status": "ok", "uptime_seconds": round(uptime, 2)}

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    uvicorn.run(app, host="127.0.0.1", port=port)