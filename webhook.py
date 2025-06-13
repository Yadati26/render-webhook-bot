from flask import Flask, request, jsonify
import requests
import datetime
import os
import json

app = Flask(__name__)

FORWARD_URL = "https://2c7b-192-166-246-184.ngrok-free.app/webhook"  # Ngrok relay to your laptop

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

@app.route('/webhook', methods=['POST'])
def receive_alert():
    data = request.get_json()
    timestamp = datetime.datetime.utcnow().isoformat()
    safe_timestamp = timestamp.replace(":", "-").replace(".", "_")

    # Save to log
    log_path = os.path.join(LOG_DIR, f"{safe_timestamp}.json")
    with open(log_path, 'w') as f:
        json.dump(data, f)

    print(f"[RECEIVED] {timestamp}: {data}")

    # Forward to ngrok tunnel
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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
