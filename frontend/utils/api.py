"""API client utilities for communicating with the FastAPI backend."""
import os
from typing import Any

import httpx
import streamlit as st

# Read API_URL from environment variable (for production) or Streamlit secrets (for local dev)
API_URL = os.getenv("API_URL", "").strip()
if not API_URL:
    try:
        API_URL = st.secrets.get("API_URL", "http://localhost:8000/api")
    except (FileNotFoundError, AttributeError, KeyError):
        API_URL = "http://localhost:8000/api"

# If API_URL is just a hostname (no protocol), assume https://
if API_URL and not API_URL.startswith(("http://", "https://")):
    API_URL = f"https://{API_URL}"

# Remove trailing slash from API_URL
if API_URL and API_URL.endswith("/"):
    API_URL = API_URL.rstrip("/")


def api_get(path: str, params: dict | None = None) -> list[dict[str, Any]]:
    """Make a GET request to the API."""
    url = f"{API_URL}{path}"
    try:
        resp = httpx.get(url, params=params, timeout=10.0, follow_redirects=True)
        resp.raise_for_status()
        return resp.json()
    except httpx.ConnectError as e:
        error_msg = (
            f"❌ **Connection Error**: Cannot connect to backend at `{url}`\n\n"
            f"**Current API_URL**: `{API_URL}`\n\n"
            f"**To fix this:**\n"
            f"1. Check that your backend service is running on Render\n"
            f"2. In Render dashboard → Frontend service → Environment tab\n"
            f"3. Set `API_URL` to your backend URL + `/api`\n"
            f"   Example: `https://jobshop-backend.onrender.com/api`\n"
            f"4. Save and redeploy the frontend service"
        )
        st.error(error_msg)
        raise ConnectionError(error_msg) from e


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

