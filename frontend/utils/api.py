"""API client utilities for communicating with the FastAPI backend."""
from typing import Any

import httpx
import streamlit as st

try:
    API_URL = st.secrets.get("API_URL", "http://localhost:8000/api")
except (FileNotFoundError, AttributeError):
    API_URL = "http://localhost:8000/api"


def api_get(path: str, params: dict | None = None) -> list[dict[str, Any]]:
    """Make a GET request to the API."""
    resp = httpx.get(
        f"{API_URL}{path}", params=params, timeout=10.0, follow_redirects=True
    )
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, payload: dict | list | None = None) -> httpx.Response:
    """Make a POST request to the API."""
    return httpx.post(
        f"{API_URL}{path}", json=payload, timeout=10.0, follow_redirects=True
    )


def api_put(path: str, payload: dict | list | None = None) -> httpx.Response:
    """Make a PUT request to the API."""
    return httpx.put(
        f"{API_URL}{path}", json=payload, timeout=10.0, follow_redirects=True
    )


def api_delete(path: str) -> httpx.Response:
    """Make a DELETE request to the API."""
    return httpx.delete(f"{API_URL}{path}", timeout=10.0, follow_redirects=True)

