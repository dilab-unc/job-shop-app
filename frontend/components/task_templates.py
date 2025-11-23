"""Task templates management UI component."""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.cache import fetch_factories, fetch_task_templates, fetch_machines, refresh_cache
from utils.ui import dataframe_or_empty
from utils.api import api_post


def render_task_templates_tab() -> None:
    """Render the task templates management tab."""
    factories = fetch_factories()
    factory_lookup = {f["name"]: f["id"] for f in factories}
    factory_name = st.selectbox(
        "Factory for templates", options=list(factory_lookup.keys()), key="task_factory"
    )
    factory_id = factory_lookup[factory_name]
    task_templates = fetch_task_templates(factory_id)
    st.markdown(f"### Task templates for {factory_name}")
    dataframe_or_empty(task_templates, "task templates")

    with st.form("create_task_template"):
        st.markdown("#### Create template")
        name = st.text_input("Template name")
        description = st.text_area("Description")
        task_type = st.text_input("Task type", help="Capability tag")
        default_duration = st.number_input(
            "Default duration (minutes)", min_value=1, value=5
        )
        machine_options = fetch_machines(factory_id)
        allowed_names = [
            st.checkbox(m["name"], key=f"template_machine_{m['id']}") for m in machine_options
        ]
        allowed_machine_ids = [
            machine["id"]
            for machine, checked in zip(machine_options, allowed_names)
            if checked
        ]
        submitted = st.form_submit_button("Create template")
        if submitted:
            payload = {
                "factory_id": factory_id,
                "name": name,
                "description": description,
                "task_type": task_type,
                "default_duration_minutes": default_duration,
                "allowed_machine_ids": allowed_machine_ids or None,
            }
            resp = api_post("/task-templates", payload)
            if resp.status_code == 201:
                st.success("Template created")
                refresh_cache()
                st.rerun()
            else:
                st.error(resp.text)

