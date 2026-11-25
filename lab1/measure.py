"""Lab 1 - send many requests and measure response times."""
import statistics
import sys
import time

import httpx

base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
timeout_arg = sys.argv[3] if len(sys.argv) > 3 else "2"
timeout = None if timeout_arg.lower() == "none" else float(timeout_arg)
delay = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0

times_ms = []
failures = {}

with httpx.Client(timeout=timeout) as client:
    for i in range(1, n + 1):
        start = time.perf_counter()
        try:
            client.get(f"{base_url}/info", params={"delay": delay}).raise_for_status()
            times_ms.append((time.perf_counter() - start) * 1000)
        except httpx.TimeoutException:
            failures["timeout"] = failures.get("timeout", 0) + 1
            print(f"request {i}: no answer within {timeout} s")
        except httpx.ConnectError:
            failures["connection refused"] = failures.get("connection refused", 0) + 1
            print(f"request {i}: cannot connect (is the service running?)")
        time.sleep(0.5)

print(f"\nSucceeded: {len(times_ms)} of {n} Failed: {failures or 0}")
if len(times_ms) == 1:
    print(f"time = {times_ms[0]:.1f} ms")
elif len(times_ms) >= 2:
    cuts = statistics.quantiles(times_ms, n=100)
    print(f"p50 = {statistics.median(times_ms):.1f} ms")
    print(f"p95 = {cuts[94]:.1f} ms max = {max(times_ms):.1f} ms")