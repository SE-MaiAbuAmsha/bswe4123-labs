with open("service.py", "w", encoding="utf-8") as f:
    f.write("""import time
from fastapi import FastAPI
import uvicorn
import sys
app = FastAPI()
start\_time = time.time()
DELAY = 0.0
    @app.get("/health")
    def health():
    if DELAY &gt; 0:
      time.sleep(DELAY)
      uptime = time.time() - start\_time
      return {"status": "ok", "uptime\_seconds": round(uptime, 2)}
      if \_\_name\_\_ == "\_\_main\_\_":
      port = int(sys.argv[1]) if len(sys.argv) &gt; 1 else 8001
      uvicorn.run(app, host="127.0.0.1", port=port)
      """)
   
print("✅ service.py fixed!")

