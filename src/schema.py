from typing import Dict, Any

from pydantic import BaseModel

class GitHubWebhookPayload(BaseModel):
    ref: str
    pusher: Dict[str, Any]
    repository: Dict[str, Any] = {}
