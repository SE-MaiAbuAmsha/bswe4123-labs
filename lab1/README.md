# Lab 1 — Setting Up and First Contact with Distribution

**Student:** Mai Abu Amsha — 120220681
**Partner:** N/A
**Setup used:** fallback — two services on localhost:8000 and localhost:8001

## Experiment 1 — First contact

- Host name printed by client: MaiAbuAmsha
- Round-trip time: 2.0 ms
- Two processes: what each knows about the other:
  The service knows only its own hostname and its own clock.
  The client knows only the URL. They share information by
  exchanging JSON messages over HTTP.

## Experiment 2 — From my machine to my partner's

- Host that answered: ...
- What changed in the code: ...
- What this says about location transparency: ...

## Experiment 3 — Latency is not zero

| Target            | p50 (ms) | p95 (ms) | max (ms) |
| ----------------- | -------- | -------- | -------- |
| localhost         | 4.2      | 6.2      | 2048.0   |
| partner's machine | 4.1      | 6.0      | 2050.2   |

- How many times slower at p50: 4.1 / 4.2 ≈ 0.98, i.e. essentially the
  same. Since both services run on the same machine (fallback), there is
  no network hop between them, so the difference is only measurement noise.
  A real partner's machine over the lab network would show a clear increase.

- Why p95 > p50, and why percentiles:
  p95 is higher because the slowest 5% of requests include occasional
  delays such as OS scheduling, garbage collection in Python, or network
  jitter. The max value (~2050 ms) is a clear outlier caused by a brief
  system pause. We report percentiles instead of the average because the
  average hides these outliers; p95 tells us what a typical user
  experiences in the worst 5% of cases.

## Experiment 4 — There is no global clock

- Three estimated offsets: 3.0 ms / 2.9 ms / 0.0 ms
- Clearly different or within noise:
  The first two runs give almost the same offset (~3 ms), and the third
  reports 0.0 ms because the whole round trip fell below the resolution
  of the Windows clock used by datetime.now(). All three values are within
  a few milliseconds, so the two clocks are effectively the same clock;
  the differences are measurement noise, not real clock skew. In the
  fallback setup both services share the same physical clock, so any
  non-zero offset comes from the midpoint assumption and from the time
  the service takes to answer.
- One situation where the midpoint assumption is wrong:
  If the server is under heavy load and takes much longer to process the
  request than the network takes to deliver it, the reply takes longer
  than the request, so the "midpoint" is not when the server read its
  clock. Asymmetric network routes (request and reply take different
  paths) also break the assumption. Finally, if the clock resolution is
  coarser than the round trip (as in run 3), the measurement collapses
  to 0 and cannot estimate the offset at all.

## Experiment 5 — Partial failure

### 5a — Stopped service (observed as timeouts)

- What the client printed:
  During the run, three requests failed:
  "request 13: no answer within 2.0 s"
  "request 14: no answer within 2.0 s"
  "request 15: no answer within 2.0 s"
  At the end it printed:
  "Succeeded: 17 of 20 Failed: {'timeout': 3}".
  The other 17 requests succeeded normally.

- What happened when the service came back:
  The requests after the interruption succeeded again, and the failure
  count stopped increasing. The client did not crash; it kept trying
  and recovered automatically once the service was responsive again.

- Observation:
  In this run the failure appeared as a timeout rather than a
  connection refused. This is because the service was not fully
  stopped at the moment of those requests; it was either still
  shutting down or restarting, so the TCP connection was accepted
  but no reply arrived within the 2 s timeout. From the client's
  point of view, a service that is slow to answer looks the same
  as a service that is down.

### 5b — Slow service

- Without timeout, client waited:
  About 6 seconds per request (the service was asked to delay 5 seconds,
  plus normal processing time). Both requests succeeded, with
  p50 = 6029.3 ms, p95 = 8794.7 ms, and max = 7053.5 ms.

- With a 2 s timeout:
  Every request printed "no answer within 2.0 s", and both failed:
  "Succeeded: 0 of 2 Failed: {'timeout': 2}".

- Difference between stopped and slow from the client's view:
  A fully stopped service usually gives "connection refused" immediately,
  because the TCP connection is rejected. A slow service keeps the
  connection open and simply does not answer within the timeout, so the
  client sees a timeout instead of a refusal. If the timeout is short,
  a slow service looks the same as a dead one; the client cannot tell
  them apart without extra information (e.g. a health endpoint or a
  longer timeout).

- Timeout you would choose, and why:
  A timeout slightly above the normal p95 (for example 1-2 seconds,
  since p95 on localhost is around 6 ms) gives enough room for normal
  jitter without waiting too long on real failures. A very short
  timeout (e.g. 50 ms) would cause false timeouts even on healthy
  requests, while a very long timeout would make failures slow to
  detect.
