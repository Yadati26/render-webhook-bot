from flask import Flask, request, jsonify
import requests
import datetime
import os
import re

app = Flask(__name__)

# ✅ Set this to your current ngrok URL
FORWARD_URL = "https://7216-192-166-246-184.ngrok-free.app/webhook"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

@app.route("/webhook", methods=["POST"])
def receive_alert():
    data = request.get_json()
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()

    # 🔐 Clean timestamp for filename use
    safe_timestamp = re.sub(r"[^\w\-]", "_", timestamp)
    log_path = os.path.join(LOG_DIR, f"{safe_timestamp}.json")

    with open(log_path, "w") as f:
        f.write(str(data))

    print(f"[RECEIVED] {timestamp}: {data}")

    try:
        r = requests.post(FORWARD_URL, json=data, timeout=5)
        print(f"[FORWARDED] Status: {r.status_code}")
        return jsonify({"status": "forwarded", "code": r.status_code}), 200
    except Exception as e:
        print(f"[ERROR] Forward failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
