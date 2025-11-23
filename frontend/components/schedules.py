"""Schedules visualization UI component."""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.cache import fetch_schedules, refresh_cache
from utils.ui import dataframe_or_empty
from utils.api import api_get


def render_schedules_tab() -> None:
    """Render the schedules visualization tab."""
    schedules = fetch_schedules()
    st.markdown("### Schedules")
    dataframe_or_empty(schedules, "schedules")

    if schedules:
        schedule_lookup = {
            f"Schedule {s['id']} (Job: {s['job_id']}, Status: {s.get('status', 'unknown')})": s["id"]
            for s in schedules
        }
        sel = st.selectbox("Select schedule to visualize", options=list(schedule_lookup.keys()))
        schedule_id = schedule_lookup[sel]

        # Get schedule details
        schedule = next(s for s in schedules if s["id"] == schedule_id)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", schedule.get("status", "unknown").upper())
        with col2:
            obj_val = schedule.get("objective_value")
            if obj_val is not None:
                st.metric("Makespan (minutes)", obj_val)
            else:
                st.metric("Makespan", "N/A")
        with col3:
            solver_status = schedule.get("solver_status", "unknown")
            st.metric("Solver Status", solver_status.upper())

        # Show infeasibility message if needed
        if schedule.get("status") == "infeasible":
            st.error(
                f"⚠️ This schedule is infeasible. Solver status: {solver_status}. "
                "Check machine capabilities, task durations, or constraints."
            )

        # Fetch Gantt data
        try:
            gantt_data = api_get(f"/schedules/{schedule_id}/gantt")
            
            if gantt_data:
                # Create Gantt chart
                df = pd.DataFrame(gantt_data)
                df["start_time"] = pd.to_datetime(df["start_time"])
                df["end_time"] = pd.to_datetime(df["end_time"])

                # Create Gantt chart using Plotly
                fig = px.timeline(
                    df,
                    x_start="start_time",
                    x_end="end_time",
                    y="machine_name",
                    color="job_name",
                    hover_data=["task_name", "duration_minutes"],
                    labels={
                        "machine_name": "Machine",
                        "start_time": "Start Time",
                        "end_time": "End Time",
                        "job_name": "Job",
                    },
                    title=f"Gantt Chart - Schedule {schedule_id}",
                )
                fig.update_yaxes(autorange="reversed")  # Machines at top
                fig.update_layout(
                    height=max(400, len(df["machine_name"].unique()) * 60),
                    xaxis_title="Time",
                    yaxis_title="Machine",
                    hovermode="closest",
                )
                st.plotly_chart(fig, use_container_width=True)

                # Show task details table
                st.markdown("#### Task Details")
                display_df = df[
                    ["task_name", "machine_name", "start_time", "end_time", "duration_minutes"]
                ].copy()
                display_df["start_time"] = display_df["start_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
                display_df["end_time"] = display_df["end_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
                display_df.columns = ["Task", "Machine", "Start", "End", "Duration (min)"]
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No scheduled tasks found for this schedule.")
        except Exception as e:
            st.error(f"Error loading Gantt data: {str(e)}")
            # Fallback to simple task list
            resp = api_get(f"/schedules/{schedule_id}/tasks")
            st.write("#### Scheduled tasks")
            dataframe_or_empty(resp, "scheduled tasks")

