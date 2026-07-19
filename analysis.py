import asyncio
import aiohttp
from collections import Counter
import matplotlib.pyplot as plt

URL = "http://localhost:5000/home"
NUM_REQUESTS = 10000


async def fetch(session):
    async with session.get(URL) as response:
        data = await response.json()

        # Your server returns:
        # {
        #     "count": 89,
        #     "server": "1"
        # }

        return data["server"]


async def main():

    async with aiohttp.ClientSession() as session:

        tasks = [fetch(session) for _ in range(NUM_REQUESTS)]

        results = await asyncio.gather(*tasks)

    counts = Counter(results)

    print("\n========== RESULTS ==========")

    for server in sorted(counts.keys()):
        print(f"Server {server}: {counts[server]} requests")

    print("=============================\n")

    # Create bar chart
    plt.figure(figsize=(8, 5))

    plt.bar(
        list(counts.keys()),
        list(counts.values())
    )

    plt.title("Load Distribution Across 3 Servers (10000 Requests)")
    plt.xlabel("Server")
    plt.ylabel("Requests Handled")

    # Put values above each bar
    for x, y in zip(counts.keys(), counts.values()):
        plt.text(x, y + 50, str(y), ha="center")

    plt.tight_layout()

    plt.savefig("A1_bar_chart.png", dpi=300)

    print("Graph saved as A1_bar_chart.png")


if __name__ == "__main__":
    asyncio.run(main())