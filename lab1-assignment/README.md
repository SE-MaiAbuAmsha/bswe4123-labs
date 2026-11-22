
# Lab 1 Assignment: Service Health Monitor 
## Overview This repository contains a Python-based health monitor for microservices in a distributed system setup. 
## Step 3: Monitor Output &amp; Observations 
### Output Log:
 ```text 
 --- Health Check Round at 10:00:00 --- 
 Service Port 8001: UP (12.4 ms) Service Port 8002: UP (10.1 ms) Service Port 8003: UP (14.5 ms) 
 --- Health Check Round at 10:00:06 --- 
 Service Port 8001: DOWN (1 consecutive failure) Service Port 8002: UP (11.0 ms) Service Port 8003: UP (14.5 ms) 
 --- Health Check Round at 10:00:20 --- 
 Service Port 8001: UP (13.0 ms) Service Port 8002: UP (10.5 ms) Service Port 8003: SLOW (812.3 ms)