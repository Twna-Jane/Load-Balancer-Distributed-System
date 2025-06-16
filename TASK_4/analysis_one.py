"""Asynchronous execution and counting of requests using aiohttp and asyncio."""

import asyncio
import aiohttp
import matplotlib.pyplot as plt
from collections import Counter

NUM_REQUESTS = 10000
URL = "http://localhost:5000/home"

async def fetch(session, url=URL):
    """Gets a response from the server URL, returning the server id."""
    try:
        async with session.get(url) as response:
            data = await response.json()
            message = data.get("message", "")
            server_id = message.split()[-1].split(":")[0]
            return server_id
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


async def count_requests_per_server():
    """Counts the number of requests handled by each server."""
    counter = Counter()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url=URL) for _ in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)
        for server in results:
            if server is not None:
                counter[server] += 1

    return counter


async def main():
    """Plots a bar chart showing the number of requests per server."""
    requests_count = await count_requests_per_server()
    servers = sorted(requests_count.keys())
    counts = list(requests_count.values())

    plt.bar(servers, counts)
    plt.title("Request distribution Across Servers")
    plt.xlabel("Servers")
    plt.ylabel("Requests")
    plt.savefig("figures/analysis_one.png")


if __name__ == "__main__":
    asyncio.run(main())