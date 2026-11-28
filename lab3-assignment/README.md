# Lab Assignment 3: Exam Scheduler Service

**Student:** Mai Abu Amsha - 120220681

## 1. Commands to Run Both Services

To run the Room Booking Service (with an optional delay):

```powershell
$env:ROOM_DELAY="0"; uvicorn room_service:app --port 8001
```

To run the Exam Scheduler Service (with custom timeout and retries):

```powershell
$env:SCHEDULER_TIMEOUT="2.0"; uvicorn scheduler_service:app --port 8002
```

## 2. Retry Test Log

During the retry test, the Scheduler was running while the Room Booking Service was restarted. The Scheduler printed the following logs, proving the exponential backoff retry mechanism works:

```
Retry 1 in 0.5s due to: ReadTimeout
Retry 2 in 1.0s due to: ReadTimeout
Retry 3 in 2.0s due to: ReadTimeout
```

## 3. Delay vs Timeout Table (Step 4)

| ROOM_DELAY | SCHEDULER_TIMEOUT | Status Code             | Time Measured | Explanation                                                                                                                                                                                        |
| :--------- | :---------------- | :---------------------- | :------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 3.0 s      | 1.0 s             | 503 Service Unavailable | 13.95 s       | The Scheduler timed out and retried 3 times. The total time includes the failed timeouts (1s each) + exponential backoff (0.5s + 1s + 2s) + processing.                                            |
| 3.0 s      | 5.0 s             | 201 Created             | 12.49 s       | The Scheduler waited for the Room Service. The time includes the full delay (3s to fetch rooms + 3s to book). The 5s timeout was enough for each individual request, so no retries were triggered. |

### Explanations of the Trade-off:

Short Timeout (1s): Fails fast. It frees up the Scheduler's resources quickly, but it causes false failures when the downstream service is just a bit slow. This triggers unnecessary retries, making the client wait even longer.

Long Timeout (5s): Succeeds even with a slow service, but ties up the Scheduler's resources for a long time. If the service is truly dead, the client waits too long before getting an error.

The sweet spot is a timeout slightly larger than the p95 response time of the downstream service.

## 4. Why is the booking request safe to retry? (Step 3)

The booking request is safe to retry because the Scheduler uses the PUT method with a specific booking_id derived from the exam_id (e.g., exam-EX1).

PUT is idempotent: if the Room Service receives the exact same PUT /bookings/exam-EX1 request twice, it will just overwrite the existing booking with the same data and return 200 OK. It will not create a duplicate booking. Therefore, if the network drops the reply and the Scheduler retries, no double-booking will occur.
