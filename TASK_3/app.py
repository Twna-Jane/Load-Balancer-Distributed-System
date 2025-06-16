from flask import Flask, jsonify, request
import requests
from consistent_hash import ConsistentHashRing
import random

app = Flask(__name__)
N = 3  # Initial number of servers
HSLOTS = 512
K = 9
servers = ["server1:5000", "server2:5000", "server3:5000"]
hash_ring = ConsistentHashRing(N, HSLOTS, K)

@app.route("/rep", methods=["GET"])
def get_replicas():
    return jsonify({"message": {"N": len(servers), "replicas": servers, "status": "successful"}}), 200

@app.route("/add", methods=["POST"])
def add_servers():
    data = request.json
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    if not isinstance(n, int) or n <= 0 or len(hostnames) > n:
        return jsonify({"message": "Error: Invalid n or hostname list length exceeds n", "status": "failure"}), 400

    new_servers = hostnames[:n] if hostnames else [f"server{random.randint(100, 999)}:5000" for _ in range(n)]
    servers.extend(new_servers)

    # Update hash ring with new number of servers
    new_hash_ring = ConsistentHashRing(len(servers), HSLOTS, K)
    new_hash_ring._initialize_ring()  # Reinitialize with updated server count
    global hash_ring
    
    hash_ring = new_hash_ring  # Replace the old ring
    return jsonify({"message": {"N": len(servers), "replicas": servers, "status": "successful"}}), 200

@app.route("/rm", methods=["DELETE"])
def remove_servers():
    data = request.json
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    if not isinstance(n, int) or n <= 0 or n > len(servers) or len(hostnames) > n:
        return jsonify({"message": "Error: Invalid n or hostname list length exceeds n", "status": "failure"}), 400

    remove_list = hostnames[:n] if hostnames else [s for s in servers[:n]]
    for server in remove_list:
        if server in servers:
            servers.remove(server)
            n -= 1
    
    # Randomly remove servers if n > 0
    while n > 0:
        servers.remove(random.choice(servers))
        n -= 1

    # Update hash ring with new number of servers
    new_hash_ring = ConsistentHashRing(len(servers), HSLOTS, K)
    new_hash_ring._initialize_ring()  # Reinitialize with updated server count
    global hash_ring
    hash_ring = new_hash_ring  # Replace the old ring

    return jsonify({"message": {"N": len(servers), "replicas": servers, "status": "successful"}}), 200

@app.route("/<path:path>", methods=["GET"])
def route_request(path):
    if path != "home":
        return jsonify({"message": f"Error: '{path}' endpoint not supported", "status": "failure"}), 400

    request_id = random.randint(100000, 999999)
    server_id = hash_ring.get_server_for_request(request_id)
    
    if not server_id:
        return jsonify({"message": "Error: No available server", "status": "failure"}), 500
    
    # Convert Server-0 to server1:5000
    server_num = int(server_id.split('-')[1]) + 1  # Server-0 -> 1, Server-1 -> 2, etc.
    server = f"server{server_num}:5000" if server_num <= len(servers) else None

    if not server or server not in servers:
        return jsonify({"message": f"Error: Server {server_id} not found", "status": "failure"}), 500
    try:
        response = requests.get(f"http://{server}/{path}", timeout=2)
        return jsonify(response.json()), response.status_code
    except requests.RequestException:
        return jsonify({"message": f"Error routing to {server}", "status": "failure"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)