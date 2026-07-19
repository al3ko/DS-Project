# Distributed Systems Programming Project

## Group Members

- Alex Ngigi - 162437
- Joseph Manene - 169648
---
## Overview

This project implements a custom software load balancer using Docker containers and Consistent Hashing. The load balancer distributes incoming client requests among multiple backend server containers while maintaining balanced request allocation. The system also includes automatic failure detection and recovery through a heartbeat mechanism.

---

# Project Structure

```
load-balancer/
│
├── app.py
├── consistent_hash.py
├── docker_manager.py
├── analysis.py
├── analysis_A2.py
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
│
└── server/
      ├── app.py
      └── Dockerfile
```

---

# Design Choices

### 1. Consistent Hashing

The load balancer uses a consistent hashing ring to determine which backend server should receive a request.

Advantages:

- minimal remapping when servers are added or removed
- balanced request allocation
- scalable architecture

---

### 2. Docker Containers

Each backend server runs as an independent Docker container.

Benefits:

- lightweight
- isolated
- easy deployment
- easy replacement after failure

---

### 3. Heartbeat Monitoring

A background thread continuously checks running server containers every 5 seconds.

If a server disappears:

1. remove it from the hash ring
2. remove it from the replica list
3. launch a replacement server
4. add the replacement back into the hash ring

This provides automatic fault recovery.

---

### 4. REST API

The load balancer exposes the following endpoints.

| Endpoint | Method | Description |
|-----------|----------|------------------------------|
| /rep | GET | View replicas |
| /add | POST | Add new replicas |
| /rm | DELETE | Remove replicas |
| /home | GET | Forward client request |

---

# Assumptions

The implementation assumes:

- Docker Engine is installed
- Docker Compose is installed
- Python 3.11+
- All containers are connected to the same Docker network
- Backend servers expose port 5000
- Every backend server responds to `/home`
- Every backend server responds to `/heartbeat`

---

# Testing

The following tests were performed.

### Replica Endpoint

```
GET /rep
```

Returns the current number of replicas.

---

### Add Endpoint

```
POST /add
```

Successfully launches additional Docker containers.

---

### Remove Endpoint

```
DELETE /rm
```

Successfully removes containers and updates the hash ring.

---

### Load Balancing

```
GET /home
```

Routes incoming requests to backend servers.

---

### Failure Recovery

When a backend container is manually removed using

```
docker rm -f Server2
```

the heartbeat thread automatically detects the failure and launches a replacement server.

---

# Performance Analysis

## A-1 Load Distribution Across Three Servers

10000 asynchronous requests were sent to the load balancer using three backend servers.

### Result

Insert the generated bar chart here.

![A1](A1_bar_chart.png)

Observed request distribution

| Server | Requests |
|----------|----------|
| Server 1 | 8392 |
| Server 2 | 473 |
| Server 3 | 1135 |

### Observation

The requests were not evenly distributed across the three servers.

One server handled significantly more requests than the others. This indicates that the current hash function does not provide a perfectly uniform distribution.

Although all requests were successfully processed, the workload imbalance suggests that the hash function can still be improved.

---

## A-2 Scalability Analysis

The number of replicas was increased from 2 to 6.

For each configuration, 10000 requests were generated.

### Result

Insert the generated line chart here.

![A2](A2_line_chart.png)

| Replicas | Average Requests per Server |
|------------|----------------------------|
| 2 | 5000 |
| 3 | 3333 |
| 4 | 2500 |
| 5 | 2000 |
| 6 | 1667 |

### Observation

The average load per server decreases almost linearly as additional replicas are introduced.

This demonstrates that the system scales well because the workload is shared among more backend servers.

Increasing the number of replicas reduces the processing burden on each individual server.

---

## A-3 Fault Tolerance

The heartbeat mechanism was tested by manually terminating one backend server.

Example

```
docker rm -f Server2
```

The load balancer detected the missing server within a few seconds.

It automatically

- removed the failed server
- updated the consistent hash ring
- launched a replacement container
- continued serving requests

### Observation

The recovery process required no manual intervention.

Client requests continued successfully after the replacement server joined the cluster.

This demonstrates that the implementation is fault tolerant.

---

## A-4 Modified Hash Functions

The hash functions H(i) and Φ(i,j) were modified by changing the hashing constants.

The experiments in A-1 and A-2 were repeated.

### Observation

Changing the hash function altered how requests were distributed across the servers.

Some hash functions produced a more balanced distribution while others increased the imbalance.

However, the scalability trend remained unchanged.

Increasing the number of replicas continued to reduce the average load handled by each server.

This confirms that system scalability depends mainly on the number of replicas, while the choice of hash function primarily affects load distribution quality.

---

# Conclusion

The project successfully implements

- Consistent Hashing
- Dynamic server addition
- Dynamic server removal
- Automatic failure recovery
- Docker container orchestration
- Request routing
- Scalability with increasing replicas

The heartbeat mechanism ensures high availability while the consistent hashing strategy minimizes disruption when servers join or leave the system.