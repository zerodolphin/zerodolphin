# app.py (Deploy this on Render)
import os
import urllib.request
import urllib.error
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Secret API key stored ONLY in Render's Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"

@app.route("/v1/chat", methods=["POST"])
def proxy_gemini():
    if not GEMINI_API_KEY:
        return jsonify({"error": "Server misconfigured: missing GEMINI_API_KEY"}), 500

    try:
        # Pass the payload directly to Gemini
        client_payload = request.get_json()
        
        req = urllib.request.Request(
            GEMINI_ENDPOINT,
            data=json.dumps(client_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return jsonify(data)

    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        return jsonify({"error": err_msg}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Render assigns dynamic PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
