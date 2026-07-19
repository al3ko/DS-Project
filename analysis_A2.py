import asyncio
import aiohttp
import requests
import matplotlib.pyplot as plt

URL = "http://localhost:5000/home"

TOTAL_REQUESTS = 10000


async def fetch(session):
    async with session.get(URL) as r:
        return await r.json()


async def run_requests():

    async with aiohttp.ClientSession() as session:

        tasks = [fetch(session) for _ in range(TOTAL_REQUESTS)]

        results = await asyncio.gather(*tasks)

    return results


server_counts = []
average_load = []


for N in range(2, 7):

    print(f"\n========== Testing N = {N} ==========")

    # -------------------------------
    # Reset to 3 replicas first
    # -------------------------------
    requests.delete(
        "http://localhost:5000/rm",
        json={"n": 10, "hostnames": []}
    )

    requests.post(
        "http://localhost:5000/add",
        json={"n": 3, "hostnames": ["Server1", "Server2", "Server3"]}
    )

    # -------------------------------
    # Adjust number of replicas
    # -------------------------------
    if N > 3:

        requests.post(
            "http://localhost:5000/add",
            json={"n": N-3, "hostnames": []}
        )

    elif N < 3:

        requests.delete(
            "http://localhost:5000/rm",
            json={"n": 3-N, "hostnames": []}
        )

    # -------------------------------
    # Launch 10,000 requests
    # -------------------------------
    responses = asyncio.run(run_requests())

    counts = {}

    for r in responses:
        sid = r["server"]
        counts[sid] = counts.get(sid, 0) + 1

    print(counts)

    avg = sum(counts.values()) / len(counts)

    server_counts.append(N)
    average_load.append(avg)

print("\nFinished!")

plt.figure(figsize=(8,5))
plt.plot(server_counts, average_load, marker='o', linewidth=2)

plt.title("Average Server Load vs Number of Replicas")
plt.xlabel("Number of Replicas (N)")
plt.ylabel("Average Requests per Server")

plt.grid(True)

plt.savefig("A2_line_chart.png", dpi=300)

print("\nSaved graph as A2_line_chart.png")