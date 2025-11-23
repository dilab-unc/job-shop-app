"""Machines management UI component."""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.cache import fetch_factories, fetch_machines, refresh_cache
from utils.ui import dataframe_or_empty
from utils.api import api_post


def render_machines_tab() -> None:
    """Render the machines management tab."""
    factories = fetch_factories()
    factory_lookup = {f["name"]: f["id"] for f in factories}
    factory_name = st.selectbox(
        "Select factory", options=list(factory_lookup.keys())
    )
    factory_id = factory_lookup[factory_name]
    machines = fetch_machines(factory_id)
    st.markdown(f"### Machines in {factory_name}")
    dataframe_or_empty(machines, "machines")

    with st.form("create_machine"):
        st.markdown("#### Add Machine")
        name = st.text_input("Machine name")
        description = st.text_area("Description", height=80)
        capabilities_text = st.text_input("Capabilities (comma separated)")
        max_parallel_jobs = st.number_input(
            "Max parallel jobs", min_value=1, max_value=5, value=1
        )
        submitted = st.form_submit_button("Create Machine")
        if submitted:
            payload = {
                "factory_id": factory_id,
                "name": name,
                "description": description,
                "max_parallel_jobs": max_parallel_jobs,
                "capabilities": [
                    cap.strip() for cap in capabilities_text.split(",") if cap.strip()
                ],
            }
            resp = api_post("/machines", payload)
            if resp.status_code == 201:
                st.success("Machine created")
                refresh_cache()
                st.rerun()
            else:
                st.error(resp.text)

