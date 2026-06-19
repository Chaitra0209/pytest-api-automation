"""
utils/api_client.py

A thin wrapper around requests.Session.
Centralises base_url so tests never hardcode it.
Think of this like a 'Page Object' in Selenium — but for APIs.
"""

import requests


class APIClient:
    """Reusable HTTP client for the Restful-Booker API."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.session.get(f"{self.base_url}{endpoint}", **kwargs)

    def post(self, endpoint: str, payload: dict, **kwargs) -> requests.Response:
        return self.session.post(f"{self.base_url}{endpoint}", json=payload, **kwargs)

    def put(self, endpoint: str, payload: dict, **kwargs) -> requests.Response:
        return self.session.put(f"{self.base_url}{endpoint}", json=payload, **kwargs)

    def patch(self, endpoint: str, payload: dict, **kwargs) -> requests.Response:
        return self.session.patch(f"{self.base_url}{endpoint}", json=payload, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.session.delete(f"{self.base_url}{endpoint}", **kwargs)

    def close(self):
        self.session.close()
