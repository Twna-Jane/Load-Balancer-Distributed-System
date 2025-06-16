from consistent_hash import ConsistentHashRing

import matplotlib.pyplot as plt
import asyncio
import aiohttp
from collections import Counter
import random

NUM_REQUESTS = 100
SERVER_RANGE = range(2, 7)
AVERAGES = []

async def fetch(ring):
    """Gets the server for a particular request."""
    request_id = random.randint(100000, 999999)
    server = ring.get_server_for_request(request_id)
    return server


async def run_simulation(num_servers):
    """Creates a hash ring and simulates async requests for a set number of servers."""
    ring = ConsistentHashRing(num_servers=num_servers, slots=512, virtual_nodes=9)
    counter = Counter()

    # Count requests per server
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(ring) for _ in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)
        for server in results:
            counter[server] += 1

    loads = list(counter.values())
    avg_load = sum(loads) / num_servers
    return avg_load


async def main():
    """Plots the average load against number of servers N."""
    for N in SERVER_RANGE:
        avg = await run_simulation(N)
        print(f"N={N}, Avg load: {avg:.2f}")
        AVERAGES.append(avg)

    plt.plot(list(SERVER_RANGE), AVERAGES, marker='o')
    plt.title("Avg Load against Number of Servers")
    plt.xlabel("Servers (N)")
    plt.ylabel("Avg Load")
    plt.grid()
    plt.savefig("figures/analysis_two.png")

if __name__ == "__main__":
    asyncio.run(main())