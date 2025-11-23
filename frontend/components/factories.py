"""Factories management UI component."""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.cache import fetch_factories, refresh_cache
from utils.ui import dataframe_or_empty
from utils.api import api_post


def render_factories_tab() -> None:
    """Render the factories management tab."""
    st.subheader("Factories")
    factories = fetch_factories()
    dataframe_or_empty(factories, "factories")

    with st.form("create_factory"):
        st.markdown("### Create Factory")
        name = st.text_input("Name", key="factory_name")
        description = st.text_area("Description", key="factory_desc")
        submitted = st.form_submit_button("Create Factory")
        if submitted:
            if not name:
                st.error("Name is required")
            else:
                resp = api_post(
                    "/factories", {"name": name, "description": description}
                )
                if resp.status_code == 201:
                    st.success("Factory created")
                    refresh_cache()
                    st.rerun()
                else:
                    st.error(resp.text)

