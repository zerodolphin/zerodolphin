# app.py (Deploy to Render)
import os
import time
import json
import urllib.request
import urllib.error
from flask import Flask, request, jsonify

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "ZeroDolphin Gateway Engine",
        "endpoint": "/v1/chat"
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/v1/chat", methods=["POST"])
def proxy_gemini():
    if not GEMINI_API_KEY:
        return jsonify({"error": "Server misconfigured: missing GEMINI_API_KEY on Render."}), 500

    try:
        client_payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": f"Invalid JSON payload received: {str(e)}"}), 400

    req = urllib.request.Request(
        GEMINI_ENDPOINT,
        data=json.dumps(client_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    max_retries = 5
    retry_delay = 3

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return jsonify(data)

        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            if e.code in [429, 503] and attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            
            return jsonify({
                "error": "Upstream Gemini Error",
                "code": e.code,
                "message": err_body
            }), e.code

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            return jsonify({"error": f"Gateway Exception: {str(e)}"}), 500

    return jsonify({"error": "Gateway timeout / rate limit exceeded."}), 503

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
