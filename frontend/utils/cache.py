"""Cache management utilities for Streamlit."""
from typing import Any

import streamlit as st

from .api import api_get


@st.cache_data(ttl=30)
def fetch_factories() -> list[dict[str, Any]]:
    """Fetch all factories from the API."""
    return api_get("/factories")


@st.cache_data(ttl=30)
def fetch_machines(factory_id: int | None = None) -> list[dict[str, Any]]:
    """Fetch machines from the API, optionally filtered by factory."""
    params = {"factory_id": factory_id} if factory_id else None
    return api_get("/machines", params=params)


@st.cache_data(ttl=30)
def fetch_task_templates(factory_id: int | None = None) -> list[dict[str, Any]]:
    """Fetch task templates from the API, optionally filtered by factory."""
    params = {"factory_id": factory_id} if factory_id else None
    return api_get("/task-templates", params=params)


@st.cache_data(ttl=30)
def fetch_job_orders(factory_id: int | None = None) -> list[dict[str, Any]]:
    """Fetch job orders from the API, optionally filtered by factory."""
    params = {"factory_id": factory_id} if factory_id else None
    return api_get("/job-orders", params=params)


@st.cache_data(ttl=30)
def fetch_job_tasks(job_id: int) -> list[dict[str, Any]]:
    """Fetch tasks for a specific job order."""
    return api_get(f"/job-orders/{job_id}/tasks")


@st.cache_data(ttl=30)
def fetch_schedules(job_id: int | None = None) -> list[dict[str, Any]]:
    """Fetch schedules from the API, optionally filtered by job."""
    params = {"job_id": job_id} if job_id else None
    return api_get("/schedules", params=params)


def refresh_cache() -> None:
    """Clear all cached data to force refresh."""
    fetch_factories.clear()
    fetch_machines.clear()
    fetch_task_templates.clear()
    fetch_job_orders.clear()
    fetch_job_tasks.clear()
    fetch_schedules.clear()

