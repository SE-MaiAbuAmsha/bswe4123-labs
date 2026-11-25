import socket
import time
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Lab 1 Info Service")


@app.get("/info")
def info(delay: float = 0.0):
    """Return the host name and the server's clock.

    delay: seconds to wait before answering (used to simulate a slow server).
    """
    if delay > 0:
        time.sleep(delay)
    return {
        "host": socket.gethostname(),
        "server_time": datetime.now(timezone.utc).isoformat(),
    }
