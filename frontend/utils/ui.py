"""UI utility functions."""
from typing import Any

import pandas as pd
import streamlit as st


def dataframe_or_empty(data: list[dict[str, Any]], caption: str) -> None:
    """Display a dataframe or an info message if empty."""
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info(f"No {caption} found yet.")

