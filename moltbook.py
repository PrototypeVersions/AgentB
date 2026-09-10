import os
import requests


class MoltbookClient:
    def __init__(self):
        self.base_url = os.environ.get(
            "MOLTBOOK_BASE_URL", "https://www.moltbook.com/api/v1"
        ).rstrip("/")
        self.api_key = os.environ.get("MOLTBOOK_API_KEY", "").strip()
        self.write_enabled = os.environ.get(
            "MOLTBOOK_WRITE_ENABLED", "false"
        ).lower() == "true"

    def _headers(self, auth=False):
        headers = {"Accept": "application/json"}
        if auth:
            if not self.api_key:
                raise RuntimeError("MOLTBOOK_API_KEY is not configured")
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(self, method, path, *, auth=False, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = requests.request(
            method,
            url,
            headers={**self._headers(auth=auth), **kwargs.pop("headers", {})},
            timeout=30,
            **kwargs,
        )
        response.raise_for_status()
        if not response.content:
            return {}
        return response.json()

    def get_feed(self, limit=20, sort="new"):
        return self._request(
            "GET", "feed", params={"limit": limit, "sort": sort}, auth=False
        )

    def get_post(self, post_id):
        return self._request("GET", f"posts/{post_id}", auth=False)

    def get_comments(self, post_id, limit=50, sort="new"):
        return self._request(
            "GET",
            f"posts/{post_id}/comments",
            params={"limit": limit, "sort": sort},
            auth=False,
        )

    def create_post(self, submolt, title, content):
        self._ensure_writes()
        return self._request(
            "POST",
            "posts",
            auth=True,
            json={"submolt": submolt, "title": title, "content": content},
        )

    def create_comment(self, post_id, content, parent_id=None):
        self._ensure_writes()
        body = {"content": content}
        if parent_id:
            body["parent_id"] = parent_id
        return self._request(
            "POST",
            f"posts/{post_id}/comments",
            auth=True,
            json=body,
        )

    def setup_owner_email(self, email):
        self._ensure_writes()
        return self._request(
            "POST",
            "agents/me/setup-owner-email",
            auth=True,
            json={"email": email},
        )

    def _ensure_writes(self):
        if not self.write_enabled:
            raise RuntimeError(
                "Moltbook writes are disabled. Set MOLTBOOK_WRITE_ENABLED=true to enable them."
            )
