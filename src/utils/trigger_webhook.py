# webhook_trigger.py
import hmac
import hashlib
import json, os
import requests

from dotenv import load_dotenv
load_dotenv()

URL = os.environ.get("WEBSITE_URL")

def trigger_github_webhook():
    GITHUB_SECRET = b'ThisIsASecretForAfricanVoices123456!@#'

    payload = {
        "ref": "refs/heads/main",
        "pusher": {"name": "abumafrim"},
        "repository": {"full_name": "abumafrim/dsn-voice"}
    }

    body = json.dumps(payload).encode("utf-8")
    signature = "sha256=" + hmac.new(GITHUB_SECRET, body, hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "x-hub-signature-256": signature
    }

    print("This is the payload:", payload)

    response = requests.post(URL, headers=headers, data=body)
    
    try:
        return {"status": response.status_code, "response": response.json()}
    except Exception:
        return {"status": response.status_code, "raw_response": response.text}
