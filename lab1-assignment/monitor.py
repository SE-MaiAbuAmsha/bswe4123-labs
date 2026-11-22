import time
import httpx 
SERVICES = [ "[suspicious link removed]", "[suspicious link removed]", "[suspicious link removed]" ] 
TIMEOUT = 1.0
FAIL\_THRESHOLD = 3 
fail\_counters = {url: 0 for url in SERVICES}
def check\_services():
    print(f"\\n--- Health Check Round at {time.strftime('%H:%M:%S')} ---")
    with httpx.Client(timeout=TIMEOUT) as client: 
        for url in SERVICES:
            port = url.split(":")[-1].split("/")[0] 
            try: start = time.time()
                response = client.get(url)
                elapsed\_ms = (time.time() - start) \* 1000
                if response.status\_code == 200:
                    fail\_counters[url] = 0
                    if elapsed\_ms &gt; 500:
                        print(f"Service Port {port}: SLOW ({elapsed\_ms:.1f} ms)")
                        else:
                            print(f"Service Port {port}: UP ({elapsed\_ms:.1f} ms)") 
                        else:
                            print(f"Service Port {port}: DOWN (HTTP {response.status\_code})") 
                        except Exception: fail\_counters[url] += 1
                            if fail\_counters[url] &gt;= FAIL\_THRESHOLD:
                                print(f"Service Port {port}: DOWN ({fail\_counters[url]} consecutive failures)") 
                                else:
                                    print(f"Service Port {port}: WARNING (Failed {fail\_counters[url]}/{FAIL\_THRESHOLD})") 
                                    if \_\_name\_\_ == "\_\_main\_\_":
                                        try:
                                            while True:
                                                check\_services() time.sleep(2) 
                                                except KeyboardInterrupt: print("\\nMonitor stopped.")