import requests
import random
import docker
import re
import time

from flask import Flask, jsonify, request

from consistent_hash import ConsistentHashRing
from docker_utils import spawn_new_server, remove_server_container, extract_container_name

app = Flask(__name__)
HSLOTS = 512
K = 9
servers = ["server1:5000", "server2:5000", "server3:5000"]
hash_ring = ConsistentHashRing(servers, HSLOTS, K)
docker_client = docker.from_env()

def wait_for_server_ready(server_addr, timeout=10, interval=0.5):
    """Wait until the server at server_addr responds to /heartbeat, or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            res = requests.get(f"http://{server_addr}/heartbeat", timeout=2)
            if res.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(interval)
    return False

@app.route("/rep", methods=["GET"])
def get_replicas():
    """Get server replicas being handled by the load balancer."""
    return jsonify({"message": {"N": len(servers), "replicas": servers, "status": "successful"}}), 200

@app.route("/add", methods=["POST"])
def add_servers():
    """Add a server."""
    global hash_ring
    data = request.json
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    # Validate n and hostnames
    if not isinstance(n, int) or n <= 0 or len(hostnames) > n:
        return jsonify({"message": "Error: Invalid n or hostname list length exceeds n", "status": "failure"}), 400

    # Validate server names
    for server_name in hostnames:
        if not server_name:
            return jsonify({"message": "Error: Server name cannot be empty", "status": "failure"}), 400
        if server_name in servers:
            return jsonify({"message": f"Error: '{server_name}' already exists in the hash ring", "status": "failure"}), 400
        if not re.match(r'^[a-zA-Z0-9]+$', server_name):
            return jsonify({"message": f"Error: '{server_name}' is not a valid server name", "status": "failure"}), 400

    # Add new servers
    new_servers = []
    for i in range(n):
        if i < len(hostnames):
            server_name = hostnames[i]
        else:
            server_name = None
        server_name = spawn_new_server(docker_client, server_name)
        
        # Wait for the new server to be ready
        if wait_for_server_ready(server_name):
            servers.append(server_name)
            new_servers.append(server_name)
        else:
            print(f"[ERROR] New server {server_name} did not become ready in time.")

    # Rebuild hash ring
    hash_ring = ConsistentHashRing(servers, HSLOTS, K)
    return jsonify({"message": {"N": len(servers), "replicas": servers, "added": new_servers, "status": "successful"}}), 200

@app.route("/rm", methods=["DELETE"])
def remove_servers():
    """Remove a server."""
    global hash_ring
    data = request.json
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    # Validate n and hostnames
    if not isinstance(n, int) or n <= 0 or n > len(servers) or len(hostnames) > n:
        return jsonify({"message": "Error: Invalid n or hostname list length exceeds n", "status": "failure"}), 400

    # Remove servers
    remove_list = hostnames[:n] if hostnames else [s for s in servers[:n]]
    actually_removed = []
    for server in remove_list:
        if server in servers:
            container_name = extract_container_name(server)
            remove_server_container(docker_client, container_name)
            servers.remove(server)
            actually_removed.append(server)
            n -= 1
    while n > 0 and servers:
        server = random.choice(servers)
        container_name = extract_container_name(server)
        remove_server_container(docker_client, container_name)
        servers.remove(server)
        actually_removed.append(server)
        n -= 1

    # Rebuild hash ring
    hash_ring = ConsistentHashRing(servers, HSLOTS, K)
    return jsonify({"message": {"N": len(servers), "replicas": servers, "removed": actually_removed, "status": "successful"}}), 200


def is_server_alive(server):
    """Checks if a server is active by sending a heartbeat to it."""
    try:
        res = requests.get(f"http://{server}/heartbeat", timeout=2)
        return res.status_code == 200
    except requests.RequestException:
        return False

@app.route("/<path:path>", methods=["GET"])
def route_request(path):
    """Route an incoming request to a server."""
    global hash_ring

    if path != "home":
        return jsonify({"message": f"Error: '{path}' endpoint not supported", "status": "failure"}), 400

    # Try to route the request to a healthy server
    routing_attempts = len(servers)
    for _ in range(routing_attempts):
        request_id = random.randint(100000, 999999)
        server = hash_ring.get_server_for_request(request_id)

        # If server is found and is healthy, route the request to it
        if server and server in servers:
            if is_server_alive(server):
                try:
                    response = requests.get(f"http://{server}/{path}", timeout=3)
                    return jsonify(response.json()), response.status_code
                except requests.RequestException:
                    time.sleep(0.5)
                    continue
            else:
                # Remove dead server
                print(f"[FAILURE DETECTED] Removing dead server: {server}")
                servers.remove(server)

                # Extract container name and ensure it's stopped/removed
                container_name = extract_container_name(server)
                remove_server_container(docker_client, container_name)

                # Replace dead server with a new server container
                new_server = spawn_new_server(docker_client)
                
                # Wait for the new server to be ready
                if wait_for_server_ready(new_server):
                    servers.append(new_server)
                    print(f"[RECOVERY] Spawned and verified replacement server: {new_server}")
                    # Rebuild hash ring with updated servers list
                    hash_ring = ConsistentHashRing(servers, HSLOTS, K)
                else:
                    print(f"[RECOVERY] Replacement server {new_server} did not become ready in time.")

    return jsonify({"message": "Error: No healthy server found", "status": "failure"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)