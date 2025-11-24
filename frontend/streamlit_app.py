"""Main Streamlit application entry point."""
import os
import sys
from pathlib import Path

import streamlit as st

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from components import factories, job_orders, machines, schedules, task_templates
from utils.api import get_api_url


def main() -> None:
    st.set_page_config(page_title="Job Shop App", layout="wide")
    st.title("Job Shop Scheduler")
    
    # Debug: Show API_URL in sidebar (only in production/debug mode)
    if os.getenv("DEBUG", "false").lower() == "true" or os.getenv("API_URL"):
        with st.sidebar:
            st.caption("🔧 Debug Info")
            api_url = get_api_url()
            env_api_url = os.getenv("API_URL", "NOT SET")
            st.text(f"API_URL (env): {env_api_url}")
            st.text(f"API_URL (resolved): {api_url}")

    (
        tab_factories,
        tab_machines,
        tab_tasks,
        tab_jobs,
        tab_schedules,
    ) = st.tabs(["Factories", "Machines", "Task Templates", "Job Orders", "Schedules"])

    with tab_factories:
        factories.render_factories_tab()

    with tab_machines:
        machines.render_machines_tab()

    with tab_tasks:
        task_templates.render_task_templates_tab()

    with tab_jobs:
        job_orders.render_job_orders_tab()

    with tab_schedules:
        schedules.render_schedules_tab()


if __name__ == "__main__":
    main()

