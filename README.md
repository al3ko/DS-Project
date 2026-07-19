# Distributed Systems Programming Project

## Group Members

| Name | Registration Number |
|------|----------------------|
| Alex Ngigi | 162437 |
| Joseph Manene | 169648 |

---

# Overview

This project implements a custom software load balancer using Docker containers and Consistent Hashing. The load balancer distributes incoming client requests among multiple backend server containers while maintaining balanced request allocation. The system also includes automatic failure detection and recovery through a heartbeat mechanism.

---

# Project Structure

```text
load-balancer/
│
├── load_balancer/                     
│   ├── app.py                         
│   ├── consistent_hash.py             
│   ├── docker_manager.py              
│   ├── heartbeat.py                   
│   ├── Dockerfile                     
│   ├── requirements.txt               
│   ├── test_docker.py                 
│   ├── .venv/
│   └── __pycache__/
│
├── server/                            
│   ├── app.py                         
│   ├── Dockerfile                     
│   ├── requirements.txt               
│   └── .venv/
│
├── analysis.py                        # A-1 Performance analysis
├── analysis_A2.py                     # A-2 Scalability analysis
├── docker-compose.yml                 # Multi-container deployment
├── Makefile                           # Automation commands
├── README.md                          # Project documentation
├── .gitignore                         # Git ignore rules
├── A1_bar_chart.png                   # Load distribution graph
└── A2_line_chart.png                  # Scalability graph
```

---

# Design Choices

## 1. Consistent Hashing

The load balancer uses a consistent hashing ring to determine which backend server should receive a request.

### Advantages

- Minimal remapping when servers are added or removed
- Balanced request allocation
- Scalable architecture
- Reduced disruption during scaling

---

## 2. Docker Containers

Each backend server runs as an independent Docker container.

### Benefits

- Lightweight virtualization
- Isolated execution environment
- Easy deployment
- Easy replacement after failure
- Simple scalability

---

## 3. Heartbeat Monitoring

A background heartbeat thread continuously monitors all backend servers every five seconds.

If a server fails, the load balancer automatically:

1. Detects the missing container.
2. Removes the failed server from the replica list.
3. Removes the server from the consistent hash ring.
4. Launches a replacement Docker container.
5. Adds the new server back into the hash ring.

This provides automatic fault recovery without interrupting client requests.

---

## 4. REST API

The load balancer exposes the following REST endpoints.

| Endpoint | Method | Description |
|-----------|----------|------------------------------|
| `/rep` | GET | Returns the current replicas |
| `/add` | POST | Adds new replicas |
| `/rm` | DELETE | Removes replicas |
| `/home` | GET | Routes client requests |

---

# Assumptions

The implementation assumes:

- Docker Engine is installed.
- Docker Compose is installed.
- Python 3.11 or later is available.
- All containers belong to the same Docker network.
- Backend servers expose port 5000.
- Every backend server implements the `/home` endpoint.
- Every backend server responds to `/heartbeat`.

---

# Testing

The following tests were successfully performed.

## Replica Endpoint

```http
GET /rep
```

Returns the current number of active replicas.

---

## Add Endpoint

```http
POST /add
```

Successfully launches new Docker server containers and updates the consistent hash ring.

---

## Remove Endpoint

```http
DELETE /rm
```

Successfully removes selected server containers while updating the replica list and hash ring.

---

## Load Balancing

```http
GET /home
```

Routes client requests to backend servers using consistent hashing.

---

## Failure Recovery

When a backend container is manually removed

```bash
docker rm -f Server2
```

the heartbeat thread automatically detects the failure and launches a replacement server.

---

# Performance Analysis

## A-1 Load Distribution Across Three Servers

A total of **10,000 asynchronous requests** were sent to the load balancer using **three backend servers**.

### Result

![A1](A1_bar_chart.png)

### Observed Request Distribution

| Server | Requests |
|----------|----------|
| Server 1 | 8392 |
| Server 2 | 473 |
| Server 3 | 1135 |

### Observation

The requests were **not evenly distributed** across the three backend servers.

Although all 10,000 requests were successfully processed, Server 1 handled a significantly larger percentage of the workload than Servers 2 and 3.

This indicates that while the consistent hashing implementation correctly routes requests, the current hash function produces an uneven distribution of virtual nodes on the hash ring. Consequently, one server receives a much larger share of requests.

A better hash function or the use of additional virtual nodes would improve load balancing while still preserving the benefits of consistent hashing.

---

## A-2 Scalability Analysis

The number of backend replicas was increased from **2 to 6**.

For each configuration, **10,000 client requests** were generated.

### Result

![A2](A2_line_chart.png)

| Number of Replicas | Average Requests per Server |
|--------------------|-----------------------------|
| 2 | 5000 |
| 3 | 3333 |
| 4 | 2500 |
| 5 | 2000 |
| 6 | 1667 |

### Observation

The average number of requests handled by each server decreases almost linearly as additional replicas are introduced.

This demonstrates that the system scales effectively because the workload is shared among a larger number of backend servers.

Adding more replicas reduces the processing burden on individual servers, resulting in improved scalability and increased capacity to handle client requests.

---

## A-3 Fault Tolerance

The heartbeat mechanism was tested by manually terminating one backend server.

Example:

```bash
docker rm -f Server2
```

The heartbeat monitor detected the failed server within a few seconds.

It then automatically:

- Removed the failed server from the replica list.
- Updated the consistent hash ring.
- Created a replacement Docker container.
- Added the replacement server back into the hash ring.
- Continued serving incoming client requests.

### Observation

The recovery process required no manual intervention.

Client requests continued successfully after the replacement server joined the cluster, demonstrating that the implementation provides automatic fault tolerance and high availability.

---

## A-4 Modified Hash Functions

The hash functions **H(i)** and **Φ(i,j)** were modified by changing the hashing constants used in the consistent hashing implementation.

The experiments in **A-1** and **A-2** were then repeated.

### Observation

Changing the hash functions altered the distribution of requests across backend servers.

Some hash functions produced a more balanced distribution while others resulted in greater imbalance.

However, the scalability trend remained unchanged.

As additional replicas were introduced, the average load handled by each server continued to decrease almost linearly.

This demonstrates that overall system scalability depends primarily on the number of available replicas, while the quality of the hash function determines how evenly the requests are distributed among those replicas.

---

# Conclusion

The project successfully demonstrates the implementation of a Docker-based software load balancer featuring:

- Consistent Hashing
- Dynamic server addition
- Dynamic server removal
- Automatic heartbeat monitoring
- Automatic server failure recovery
- Docker container orchestration
- REST-based request routing
- Performance evaluation
- Scalability with increasing replicas

The heartbeat mechanism ensures high availability by automatically replacing failed servers, while consistent hashing minimizes disruption whenever servers join or leave the cluster. Experimental evaluation confirms that the system scales effectively as the number of backend replicas increases, although the choice of hash function has a significant impact on the quality of load distribution.