from flask import Flask, jsonify
import os

app = Flask(__name__)

# Get the unique server ID from an environment variable.
# If not provided, default to "Unknown".
SERVER_ID = os.getenv("SERVER_ID", "Unknown")
REQUEST_COUNT = 0

@app.route("/home", methods=["GET"])
def home():
    global REQUEST_COUNT

    REQUEST_COUNT += 1

    return jsonify({
        "server": SERVER_ID,
        "count": REQUEST_COUNT
    })


@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    return "", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)