import hmac
import hashlib
import json
import requests

# === CONFIGURATION ===
GITHUB_SECRET = b'ThisIsASecretForAfricanVoices123456!@#'  # must match your .env
URL = "http://localhost:8000/github-webhook"

# === Simulated Payload ===
payload = {
    "ref": "refs/heads/main",
    "pusher": {"name": "abumafrim"},
    "repository": {"full_name": "abumafrim/dsn-voice"}
}

# === Encode and Sign ===
body = json.dumps(payload).encode("utf-8")
signature = "sha256=" + hmac.new(GITHUB_SECRET, body, hashlib.sha256).hexdigest()

# === Send Request ===
headers = {
    "Content-Type": "application/json",
    "x-hub-signature-256": signature
}

response = requests.post(URL, headers=headers, data=body)

# === Print Results ===
print("Status:", response.status_code)
try:
    print("Response:", response.json())
except Exception:
    print("Raw response:", response.text)



# curl -X POST http://localhost:8000/github-webhook \
#   -H "Content-Type: application/json" \
#   -H "x-hub-signature-256: sha256=b2807bde7016d45e4124d15d99362e14c673e36f9463cff0cad8d09e6a00f203" \
#   -d '{ "ref": "refs/heads/main", "pusher": {"name": "abumafrim"}, "repository": {"full_name": "abumafrim/dsn-voice"} }'
