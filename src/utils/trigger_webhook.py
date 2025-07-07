import hmac
import hashlib
import json, os
import requests

from dotenv import load_dotenv
load_dotenv()

URL = os.environ.get("WEBSITE_URL")
GITHUB_SECRET = os.getenv("GITHUB_TOKEN")

print("🌐 URL ENV value loaded:", URL)


def trigger_github_webhook():
    payload = {
        "ref": "refs/heads/main",
        "pusher": {"name": "abumafrim"},
        "repository": {"full_name": "abumafrim/dsn-voice"}
    }

    body = json.dumps(payload).encode("utf-8")
    signature = "sha256=" + hmac.new(GITHUB_SECRET.encode(), body, hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "x-hub-signature-256": signature
    }

    print("📦 Payload:", payload)
    print("🔐 Signature:", signature)
    print("📡 URL:", URL)

    try:
        response = requests.post(URL, headers=headers, data=body, timeout=10)
        response.raise_for_status()
        return {"status": response.status_code, "response": response.json()}
    except Exception as e:
        print("❌ Error sending webhook:", e)
        return {"status": "failed", "error": str(e)}
