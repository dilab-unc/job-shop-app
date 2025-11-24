"""API client utilities for communicating with the FastAPI backend."""
import os
from typing import Any

import httpx
import streamlit as st


def get_api_url() -> str:
    """Get API URL from environment variable or Streamlit secrets.
    
    Reads dynamically to ensure we get the latest value in production.
    """
    # First try environment variable (for production)
    api_url = os.getenv("API_URL", "").strip()
    
    # If not found, try Streamlit secrets (for local dev)
    if not api_url:
        try:
            api_url = st.secrets.get("API_URL", "").strip()
        except (FileNotFoundError, AttributeError, KeyError):
            pass
    
    # Fallback to localhost
    if not api_url:
        api_url = "http://localhost:8000/api"
    
    # If API_URL is just a hostname (no protocol), assume https://
    if api_url and not api_url.startswith(("http://", "https://")):
        api_url = f"https://{api_url}"
    
    # Remove trailing slash from API_URL
    if api_url and api_url.endswith("/"):
        api_url = api_url.rstrip("/")
    
    return api_url


def api_get(path: str, params: dict | None = None) -> list[dict[str, Any]]:
    """Make a GET request to the API."""
    api_url = get_api_url()
    url = f"{api_url}{path}"
    try:
        resp = httpx.get(url, params=params, timeout=10.0, follow_redirects=True)
        resp.raise_for_status()
        return resp.json()
    except httpx.ConnectError as e:
        # Debug: Show what we're trying to connect to
        env_api_url = os.getenv("API_URL", "NOT SET")
        error_msg = (
            f"❌ **Connection Error**: Cannot connect to backend at `{url}`\n\n"
            f"**API_URL from environment**: `{env_api_url}`\n"
            f"**Resolved API_URL**: `{api_url}`\n\n"
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
    api_url = get_api_url()
    return httpx.post(
        f"{api_url}{path}", json=payload, timeout=10.0, follow_redirects=True
    )


def api_put(path: str, payload: dict | list | None = None) -> httpx.Response:
    """Make a PUT request to the API."""
    api_url = get_api_url()
    return httpx.put(
        f"{api_url}{path}", json=payload, timeout=10.0, follow_redirects=True
    )


def api_delete(path: str) -> httpx.Response:
    """Make a DELETE request to the API."""
    api_url = get_api_url()
    return httpx.delete(f"{api_url}{path}", timeout=10.0, follow_redirects=True)

