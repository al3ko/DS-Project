from flask import Flask, jsonify, request
from consistent_hash import ConsistentHashMap
from docker_manager import DockerManager
import requests
import random
import threading
import time

app = Flask(__name__)

# --------------------------------------------------
# Initialise Components
# --------------------------------------------------

hash_ring = ConsistentHashMap()
hash_ring.initialize()

docker_manager = DockerManager()

# Initial replicas
replicas = ["Server1", "Server2", "Server3"]

# Mapping hostname -> server id
server_ids = {
    "Server1": 1,
    "Server2": 2,
    "Server3": 3
}

# --------------------------------------------------
# Heartbeat Monitor
# --------------------------------------------------

def heartbeat_monitor():

    print("Heartbeat waiting 15 seconds...", flush=True)
    time.sleep(15)

    print("Heartbeat started.", flush=True)

    while True:

        time.sleep(5)

        current = docker_manager.list_servers()
        running = set(current)

        print("\n==============================", flush=True)
        print("Running :", current, flush=True)
        print("Replicas:", replicas, flush=True)
        print("==============================", flush=True)

        for hostname in replicas.copy():

            if hostname not in running:

                print(f"{hostname} considered DEAD!", flush=True)

                old_id = server_ids[hostname]

                replicas.remove(hostname)
                hash_ring.remove_server(old_id)
                del server_ids[hostname]

                new_name = docker_manager.random_hostname()
                new_id = max(server_ids.values(), default=0) + 1

                created = docker_manager.start_server(
                    hostname=new_name,
                    server_id=new_id
                )

                if created is not None:
                    replicas.append(created)
                    server_ids[created] = new_id
                    hash_ring.add_server(new_id)

                    print(f"Spawned replacement {created}", flush=True)


# --------------------------------------------------
# GET /rep
# --------------------------------------------------
@app.route("/rep", methods=["GET"])
def replicas_status():

    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": replicas
        },
        "status": "successful"
    }), 200

# --------------------------------------------------
# POST /add
# --------------------------------------------------
@app.route("/add", methods=["POST"])
def add_servers():

    data = request.get_json()

    print("\n========== ADD REQUEST ==========")
    print(data)
    print("=================================\n")

    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    # Sanity checks
    if len(hostnames) > n:
        return jsonify({
            "message": "Length of hostname list is more than newly added instances",
            "status": "failure"
        }), 400

    created = []

    # --------------------------------------
    # Add preferred hostnames
    # --------------------------------------
    for hostname in hostnames:

        # Skip duplicates
        if hostname in replicas:
            print(f"{hostname} already exists.")
            continue

        # Skip if Docker container already exists
        if docker_manager.exists(hostname):
            print(f"Container {hostname} already exists.")
            continue

        server_id = max(server_ids.values(), default=0) + 1

        print(f"Starting container {hostname} (Server ID {server_id})")

        docker_manager.start_server(
            hostname=hostname,
            server_id=server_id
        )

        replicas.append(hostname)
        server_ids[hostname] = server_id
        hash_ring.add_server(server_id)

        created.append(hostname)

    # --------------------------------------
    # Add remaining random servers
    # --------------------------------------
    remaining = n - len(created)

    while remaining > 0:

        hostname = docker_manager.random_hostname()

        while hostname in replicas or docker_manager.exists(hostname):
            hostname = docker_manager.random_hostname()

        server_id = max(server_ids.values(), default=0) + 1

        print(f"Starting random container {hostname} (Server ID {server_id})")

        docker_manager.start_server(
            hostname=hostname,
            server_id=server_id
        )

        replicas.append(hostname)
        server_ids[hostname] = server_id
        hash_ring.add_server(server_id)

        created.append(hostname)
        remaining -= 1

    print("Current replicas:", replicas)

    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": replicas
        },
        "status": "successful"
    }), 200

# --------------------------------------------------
# DELETE /rm
# --------------------------------------------------
@app.route("/rm", methods=["DELETE"])
def remove_servers():

    data = request.get_json()

    n = data.get("n", 0)

    hostnames = data.get("hostnames", [])

    if len(hostnames) > n:

        return jsonify({
            "message": "Length of hostname list is more than removable instances",
            "status": "failure"
        }), 400

    removable = replicas.copy()

    removed = []

    # Remove preferred servers
    for hostname in hostnames:

        if hostname in replicas:

            replicas.remove(hostname)

            docker_manager.remove_server(hostname)

            hash_ring.remove_server(server_ids[hostname])

            del server_ids[hostname]

            removed.append(hostname)

            removable.remove(hostname)

    # Remove remaining random servers
    remaining = n - len(removed)

    while remaining > 0 and removable:

        hostname = random.choice(removable)

        removable.remove(hostname)

        replicas.remove(hostname)

        docker_manager.remove_server(hostname)

        hash_ring.remove_server(server_ids[hostname])

        del server_ids[hostname]

        remaining -= 1

    return jsonify({

        "message": {

            "N": len(replicas),

            "replicas": replicas

        },

        "status": "successful"

    }), 200


# --------------------------------------------------
# Route Client Requests
# --------------------------------------------------
@app.route("/<path:endpoint>", methods=["GET"])
def route_request(endpoint):

    if endpoint != "home":

        return jsonify({

            "message": f"'{endpoint}' endpoint does not exist in server replicas",

            "status": "failure"

        }), 400

    if len(replicas) == 0:

        return jsonify({

            "message": "No replicas available",

            "status": "failure"

        }), 500

    request_id = random.randint(1, 100000)

    server_id = hash_ring.get_server(request_id)

    hostname = None

    for name, sid in server_ids.items():

        if sid == server_id:

            hostname = name
            break

    if hostname is None:

        return jsonify({

            "message": "Server not found",

            "status": "failure"

        }), 500

    try:

        response = requests.get(
            f"http://{hostname}:5000/home",
            timeout=5
        )

        return jsonify(response.json()), response.status_code

    except Exception as e:

        return jsonify({

            "message": str(e),

            "status": "failure"

        }), 500


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    monitor = threading.Thread(
        target=heartbeat_monitor,
        daemon=True
    )

    monitor.start()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
    