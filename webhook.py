from flask import Flask, request, jsonify
import requests
import datetime
import os
import json

app = Flask(__name__)

FORWARD_URL = "http://localhost:5000/webhook"  # Your local Flask bot

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

@app.route('/webhook', methods=['POST'])
def receive_alert():
    data = request.get_json()
    # Safe filename timestamp
    timestamp = datetime.datetime.utcnow().isoformat()
    safe_timestamp = timestamp.replace(":", "-").replace(".", "_")

    # Save to log
    log_path = os.path.join(LOG_DIR, f"{safe_timestamp}.json")
    with open(log_path, 'w') as f:
        json.dump(data, f)

    print(f"[RECEIVED] {timestamp}: {data}")
    
    # Forward to local bot
    try:
        r = requests.post(FORWARD_URL, json=data, timeout=2)
        print(f"[FORWARDED] Status: {r.status_code}")
        return jsonify({"status": "forwarded"}), 200
    except Exception as e:
        print(f"[ERROR] Failed to forward: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def index():
    return "Webhook relay is live."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
