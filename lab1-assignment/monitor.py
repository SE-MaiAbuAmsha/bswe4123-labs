import time

import httpx

SERVICES = [
    "http://localhost:8000/info",
    "http://localhost:8001/info",
    "http://localhost:8002/info",
]
TIMEOUT = 1.0
FAIL_THRESHOLD = 3
SLOW_MS = 500.0

fail_counters = {url: 0 for url in SERVICES}


def check_services() -> None:
    print(f"\n--- Health Check Round at {time.strftime('%H:%M:%S')} ---")
    with httpx.Client(timeout=TIMEOUT) as client:
        for url in SERVICES:
            port = url.split(":")[-1].split("/")[0]
            try:
                start = time.time()
                response = client.get(url)
                elapsed_ms = (time.time() - start) * 1000

                if response.status_code == 200:
                    fail_counters[url] = 0
                    if elapsed_ms > SLOW_MS:
                        print(f"Service Port {port}: SLOW ({elapsed_ms:.1f} ms)")
                    else:
                        print(f"Service Port {port}: UP ({elapsed_ms:.1f} ms)")
                else:
                    fail_counters[url] += 1
                    print(f"Service Port {port}: DOWN (HTTP {response.status_code})")
            except Exception:
                fail_counters[url] += 1
                if fail_counters[url] >= FAIL_THRESHOLD:
                    print(
                        f"Service Port {port}: DOWN "
                        f"({fail_counters[url]} consecutive failures)"
                    )
                else:
                    print(
                        f"Service Port {port}: WARNING "
                        f"(Failed {fail_counters[url]}/{FAIL_THRESHOLD})"
                    )


if __name__ == "__main__":
    try:
        while True:
            check_services()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
