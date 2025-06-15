from flask import Flask, jsonify
from consistent_hash import ConsistentHashRing

app = Flask(__name__)
ring = ConsistentHashRing(num_servers=3, slots=512, virtual_nodes=9)

@app.route('/request/<int:request_id>', methods=['GET'])
def route_request(request_id):
    server = ring.get_server_for_request(request_id)
    if server:
        return jsonify({
            "message": f"Request ID {request_id} routed to {server}",
            "status": "successful"
        }), 200
    else:
        return jsonify({
            "message": "No available server found.",
            "status": "error"
        }), 503

@app.route('/servers', methods=['GET'])
def servers():
    return jsonify({
        "server_map": ring.server_map
    }), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000)
