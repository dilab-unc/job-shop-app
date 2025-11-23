"""Job orders management UI component."""
from datetime import date
import sys
from pathlib import Path

import httpx
import pandas as pd
import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.cache import (
    fetch_factories,
    fetch_job_orders,
    fetch_job_tasks,
    fetch_machines,
    fetch_task_templates,
    refresh_cache,
)
from utils.api import api_post, api_put, api_delete, API_URL


def render_job_orders_tab() -> None:
    """Render the job orders management tab."""
    st.title("Job Orders Management")
    
    # Factory selection at the top
    factories = fetch_factories()
    factory_lookup = {f["name"]: f["id"] for f in factories}
    factory_name = st.selectbox(
        "Select Factory", 
        options=list(factory_lookup.keys()), 
        key="jobs_factory",
        help="Choose the factory to manage job orders for"
    )
    factory_id = factory_lookup[factory_name]
    
    # Main tabs for different operations
    main_tabs = st.tabs(["📋 Job Orders List", "➕ Create New Job", "⚙️ Manage Job Tasks", "🔧 Run Solver"])
    
    with main_tabs[0]:  # Job Orders List
        st.header("Job Orders")
        jobs = fetch_job_orders(factory_id)
        
        if jobs:
            st.info(f"Found {len(jobs)} job order(s) in {factory_name}")
            df_jobs = pd.DataFrame(jobs)
            display_cols = ["name", "status", "priority", "due_date", "makespan_minutes"]
            available_cols = [col for col in display_cols if col in df_jobs.columns]
            if available_cols:
                st.dataframe(
                    df_jobs[available_cols],
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info(f"No job orders found in {factory_name}. Create one using the 'Create New Job' tab.")
    
    with main_tabs[1]:  # Create New Job
        st.header("Create New Job Order")
        with st.form("create_job_order"):
            col1, col2 = st.columns(2)
            with col1:
                job_name = st.text_input("Job Name *", help="Required: Name for this job order")
                due_date = st.date_input("Due Date", value=date.today())
            with col2:
                priority = st.number_input("Priority", value=0, help="Higher numbers = higher priority")
                status = st.selectbox("Initial Status", ["draft", "queued"], index=0)
            
            description = st.text_area("Description", height=100, help="Optional description for this job order")
            
            submitted = st.form_submit_button("Create Job Order", type="primary")
            if submitted:
                if not job_name:
                    st.error("Job name is required")
                else:
                    payload = {
                        "factory_id": factory_id,
                        "name": job_name,
                        "description": description if description else None,
                        "due_date": due_date.isoformat() if isinstance(due_date, date) else None,
                        "priority": priority,
                        "status": status,
                    }
                    resp = api_post("/job-orders", payload)
                    if resp.status_code == 201:
                        st.success(f"✅ Job order '{job_name}' created successfully!")
                        refresh_cache()
                        st.rerun()
                    else:
                        try:
                            error_detail = resp.json().get("detail", resp.text)
                        except:
                            error_detail = resp.text
                        st.error(f"❌ Failed to create job: {error_detail}")

    with main_tabs[2]:  # Manage Job Tasks
        _render_manage_job_tasks(factory_id)
    
    with main_tabs[3]:  # Run Solver
        _render_run_solver(factory_id)


def _render_manage_job_tasks(factory_id: int) -> None:
    """Render the manage job tasks section."""
    st.header("Manage Job Tasks")
    jobs = fetch_job_orders(factory_id)
    
    if not jobs:
        st.warning(f"No job orders found. Please create a job order first.")
    else:
        job_options = {job["name"]: job["id"] for job in jobs}
        job_name = st.selectbox(
            "Select Job Order", 
            options=list(job_options.keys()),
            help="Choose a job order to manage its tasks"
        )
        job_id = job_options[job_name]
        
        # Get job details
        job_details = next(j for j in jobs if j["id"] == job_id)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", job_details.get("status", "unknown").upper())
        with col2:
            st.metric("Priority", job_details.get("priority", 0))
        with col3:
            task_count = len(fetch_job_tasks(job_id))
            st.metric("Tasks", task_count)
        
        st.markdown("---")
        
        # Task management sub-tabs
        task_mgmt_tabs = st.tabs(["📋 View Tasks", "➕ Add Task", "📥 Import CSV", "✏️ Edit/Delete/Reorder"])
        
        with task_mgmt_tabs[0]:  # View Tasks
            tasks = fetch_job_tasks(job_id)
            if tasks:
                st.subheader("Current Tasks")
                df_tasks = pd.DataFrame(tasks)
                display_cols = ["sequence_index", "custom_name", "custom_duration_minutes", "machine_hint_id", "notes"]
                available_cols = [col for col in display_cols if col in df_tasks.columns]
                if available_cols:
                    st.dataframe(
                        df_tasks[available_cols].sort_values("sequence_index"),
                        use_container_width=True,
                        hide_index=True,
                    )
            else:
                st.info("No tasks found. Add tasks using the 'Add Task' or 'Import CSV' tabs.")
        
        with task_mgmt_tabs[1]:  # Add Task
            _render_add_task(factory_id, job_id, task_count)
        
        with task_mgmt_tabs[2]:  # Import CSV
            _render_csv_import(job_id)
        
        with task_mgmt_tabs[3]:  # Edit/Delete/Reorder
            _render_task_management(factory_id, job_id)


def _render_add_task(factory_id: int, job_id: int, task_count: int) -> None:
    """Render the add task form."""
    st.subheader("Add New Task")
    with st.form("add_job_task"):
        templates = fetch_task_templates(factory_id)
        template_lookup = {t["name"]: t["id"] for t in templates}
        template_name = st.selectbox(
            "Task template", options=list(template_lookup.keys())
        )
        sequence_index = st.number_input(
            "Sequence index", min_value=0, value=task_count
        )
        custom_name = st.text_input("Custom name", value=template_name)
        custom_duration = st.number_input(
            "Duration (minutes)", min_value=1, value=5
        )
        machines = fetch_machines(factory_id)
        machine_lookup = {m["name"]: m["id"] for m in machines}
        machine_name = st.selectbox(
            "Machine hint", options=list(machine_lookup.keys())
        )
        notes = st.text_area("Notes", height=60)
        submitted = st.form_submit_button("Add Task", type="primary")
        if submitted:
            payload = [
                {
                    "job_id": job_id,
                    "sequence_index": sequence_index,
                    "custom_name": custom_name,
                    "custom_duration_minutes": custom_duration,
                    "machine_hint_id": machine_lookup[machine_name],
                    "notes": notes,
                    "task_template_id": template_lookup[template_name],
                }
            ]
            resp = api_post(f"/job-orders/{job_id}/tasks", payload)
            if resp.status_code == 200:
                st.success("✅ Task added successfully!")
                refresh_cache()
                st.rerun()
            else:
                try:
                    error_detail = resp.json().get("detail", resp.text)
                except:
                    error_detail = resp.text
                st.error(f"❌ Failed to add task: {error_detail}")


def _render_csv_import(job_id: int) -> None:
    """Render the CSV import section."""
    st.subheader("Import Tasks from CSV")
    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        key=f"csv_upload_{job_id}",
        help="Upload a CSV file with task data. See format guide below.",
    )

    if uploaded_file is not None:
        col1, col2 = st.columns([3, 1])
        with col1:
            try:
                file_position = uploaded_file.tell()
                uploaded_file.seek(0)
                df_preview = pd.read_csv(uploaded_file)
                uploaded_file.seek(file_position)
                st.write("**CSV Preview:**")
                st.dataframe(df_preview.head(10), use_container_width=True)
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")

        with col2:
            if st.button("Import CSV", key=f"import_csv_{job_id}", type="primary"):
                try:
                    uploaded_file.seek(0)
                    file_content = uploaded_file.read()
                    files = {"file": (uploaded_file.name, file_content, "text/csv")}
                    resp = httpx.post(
                        f"{API_URL}/job-orders/{job_id}/import-csv",
                        files=files,
                        timeout=30.0,
                        follow_redirects=True,
                    )
                    if resp.status_code == 200:
                        imported = resp.json()
                        st.success(f"✅ Successfully imported {len(imported)} tasks!")
                        refresh_cache()
                        st.rerun()
                    else:
                        try:
                            error_detail = resp.json().get("detail", resp.text)
                        except:
                            error_detail = resp.text
                        st.error(f"❌ Import failed: {error_detail}")
                except Exception as e:
                    st.error(f"❌ Error during import: {str(e)}")

    with st.expander("📋 CSV Format Guide"):
        st.markdown("""
        **Required columns:**
        - `sequence_index`: Order of task (0-based integer)
        - `task_name`: Name of the task (string)
        - `duration_minutes`: Duration in minutes (integer > 0)

        **Optional columns:**
        - `machine_name`: Name of machine (will be looked up)
        - `machine_id`: ID of machine (alternative to machine_name)
        - `task_template_name`: Name of task template (will be looked up)
        - `task_template_id`: ID of task template (alternative to task_template_name)
        - `notes`: Additional notes (string)

        **Example CSV:**
        ```csv
        sequence_index,task_name,duration_minutes,machine_name,task_template_name,notes
        0,Cutting,3,Machine 0,Cutting,Initial cut
        1,Assembly,2,Machine 1,Assembly,Assemble parts
        2,Painting,2,Machine 2,Painting,Final paint
        ```
        """)
        sample_csv = """sequence_index,task_name,duration_minutes,machine_name,task_template_name,notes
0,Task 1,5,Machine 0,Cutting,First task
1,Task 2,3,Machine 1,Assembly,Second task
2,Task 3,4,Machine 2,Painting,Third task"""
        st.download_button(
            "📥 Download Sample CSV Template",
            sample_csv,
            file_name="job_tasks_template.csv",
            mime="text/csv",
            key=f"download_template_{job_id}",
        )


def _render_task_management(factory_id: int, job_id: int) -> None:
    """Render task edit/delete/reorder section."""
    tasks = fetch_job_tasks(job_id)
    if not tasks:
        st.info("No tasks to manage. Add tasks first.")
    else:
        edit_tab, delete_tab, reorder_tab = st.tabs(["✏️ Edit", "🗑️ Delete", "🔄 Reorder"])
        
        with edit_tab:
            _render_edit_task(factory_id, job_id, tasks)
        
        with delete_tab:
            _render_delete_task(job_id, tasks)
        
        with reorder_tab:
            _render_reorder_tasks(job_id, tasks)


def _render_edit_task(factory_id: int, job_id: int, tasks: list[dict]) -> None:
    """Render the edit task form."""
    st.markdown("**Edit a task**")
    task_options = {
        f"#{t['sequence_index']}: {t.get('custom_name', 'Unnamed')} (ID: {t['id']})": t["id"]
        for t in tasks
    }
    edit_task_id = st.selectbox(
        "Select task to edit",
        options=list(task_options.keys()),
        key=f"edit_select_{job_id}",
    )
    task_id = task_options[edit_task_id]
    task_to_edit = next(t for t in tasks if t["id"] == task_id)
    
    with st.form(f"edit_task_{task_id}"):
        templates = fetch_task_templates(factory_id)
        template_lookup = {t["name"]: t["id"] for t in templates}
        template_options = [None] + list(template_lookup.keys())
        current_template = next(
            (t["name"] for t in templates if t["id"] == task_to_edit.get("task_template_id")),
            None,
        )
        template_idx = template_options.index(current_template) if current_template in template_options else 0
        
        edit_template_name = st.selectbox(
            "Task template",
            options=template_options,
            index=template_idx,
            key=f"edit_template_{task_id}",
        )
        edit_sequence = st.number_input(
            "Sequence index",
            min_value=0,
            value=task_to_edit.get("sequence_index", 0),
            key=f"edit_seq_{task_id}",
        )
        edit_name = st.text_input(
            "Task name",
            value=task_to_edit.get("custom_name") or "",
            key=f"edit_name_{task_id}",
        )
        edit_duration = st.number_input(
            "Duration (minutes)",
            min_value=1,
            value=task_to_edit.get("custom_duration_minutes") or 1,
            key=f"edit_duration_{task_id}",
        )
        machines = fetch_machines(factory_id)
        machine_lookup = {m["name"]: m["id"] for m in machines}
        machine_options = [None] + list(machine_lookup.keys())
        current_machine = next(
            (m["name"] for m in machines if m["id"] == task_to_edit.get("machine_hint_id")),
            None,
        )
        machine_idx = machine_options.index(current_machine) if current_machine in machine_options else 0
        edit_machine_name = st.selectbox(
            "Machine hint",
            options=machine_options,
            index=machine_idx,
            key=f"edit_machine_{task_id}",
        )
        edit_notes = st.text_area(
            "Notes",
            value=task_to_edit.get("notes") or "",
            height=60,
            key=f"edit_notes_{task_id}",
        )
        submitted_edit = st.form_submit_button("Update Task", type="primary")
        
        if submitted_edit:
            payload = {
                "sequence_index": edit_sequence,
                "custom_name": edit_name,
                "custom_duration_minutes": edit_duration,
                "machine_hint_id": machine_lookup[edit_machine_name] if edit_machine_name else None,
                "task_template_id": template_lookup[edit_template_name] if edit_template_name else None,
                "notes": edit_notes or None,
            }
            resp = api_put(f"/job-orders/{job_id}/tasks/{task_id}", payload)
            if resp.status_code == 200:
                st.success("✅ Task updated successfully!")
                refresh_cache()
                st.rerun()
            else:
                try:
                    error_detail = resp.json().get("detail", resp.text)
                except:
                    error_detail = resp.text
                st.error(f"❌ Update failed: {error_detail}")


def _render_delete_task(job_id: int, tasks: list[dict]) -> None:
    """Render the delete task section."""
    st.markdown("**Delete a task**")
    delete_task_options = {
        f"#{t['sequence_index']}: {t.get('custom_name', 'Unnamed')} (ID: {t['id']})": t["id"]
        for t in tasks
    }
    delete_task_id = st.selectbox(
        "Select task to delete",
        options=list(delete_task_options.keys()),
        key=f"delete_select_{job_id}",
    )
    task_id_to_delete = delete_task_options[delete_task_id]
    task_to_delete = next(t for t in tasks if t["id"] == task_id_to_delete)
    
    st.warning(
        f"⚠️ You are about to delete: **{task_to_delete.get('custom_name', 'Unnamed')}** "
        f"(Sequence: {task_to_delete.get('sequence_index')})"
    )
    
    if st.button("Delete Task", key=f"delete_btn_{task_id_to_delete}", type="primary"):
        resp = api_delete(f"/job-orders/{job_id}/tasks/{task_id_to_delete}")
        if resp.status_code == 204:
            st.success("✅ Task deleted successfully!")
            refresh_cache()
            st.rerun()
        else:
            try:
                error_detail = resp.json().get("detail", resp.text)
            except:
                error_detail = resp.text
            st.error(f"❌ Delete failed: {error_detail}")


def _render_reorder_tasks(job_id: int, tasks: list[dict]) -> None:
    """Render the reorder tasks section."""
    st.markdown("**Reorder tasks**")
    st.info("Assign new sequence indices to reorder tasks. Lower numbers run first.")
    
    sorted_tasks = sorted(tasks, key=lambda x: x.get("sequence_index", 0))
    st.write("**Current order:**")
    for idx, task in enumerate(sorted_tasks):
        st.write(f"{idx + 1}. Sequence {task.get('sequence_index', 0)}: {task.get('custom_name', 'Unnamed')} (ID: {task['id']})")
    
    st.markdown("---")
    st.write("**Set new sequence indices:**")
    
    with st.form(f"reorder_form_{job_id}"):
        new_sequences = {}
        for task in sorted_tasks:
            task_label = f"{task.get('custom_name', 'Unnamed')} (ID: {task['id']})"
            new_seq = st.number_input(
                f"New sequence for: {task_label}",
                min_value=0,
                value=task.get("sequence_index", 0),
                key=f"reorder_seq_{task['id']}",
            )
            new_sequences[task["id"]] = new_seq
        
        submitted_reorder = st.form_submit_button("Apply New Order", type="primary")
        
        if submitted_reorder:
            seq_values = list(new_sequences.values())
            if len(seq_values) != len(set(seq_values)):
                st.error("❌ Duplicate sequence indices found. Each task must have a unique sequence index.")
            else:
                sorted_by_new_seq = sorted(new_sequences.items(), key=lambda x: x[1])
                task_order = [task_id for task_id, _ in sorted_by_new_seq]
                
                resp = api_put(f"/job-orders/{job_id}/tasks/reorder", task_order)
                if resp.status_code == 200:
                    st.success("✅ Tasks reordered successfully!")
                    refresh_cache()
                    st.rerun()
                else:
                    try:
                        error_detail = resp.json().get("detail", resp.text)
                    except:
                        error_detail = resp.text
                    st.error(f"❌ Reorder failed: {error_detail}")


def _render_run_solver(factory_id: int) -> None:
    """Render the run solver section."""
    st.header("Run Solver")
    jobs = fetch_job_orders(factory_id)
    
    if not jobs:
        st.warning(f"No job orders found. Please create a job order first.")
    else:
        job_options = {job["name"]: job["id"] for job in jobs}
        job_name = st.selectbox(
            "Select Job Order to Solve",
            options=list(job_options.keys()),
            help="Choose a job order to generate an optimal schedule"
        )
        job_id = job_options[job_name]
        
        job_details = next(j for j in jobs if j["id"] == job_id)
        tasks = fetch_job_tasks(job_id)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Job Status", job_details.get("status", "unknown").upper())
            st.metric("Task Count", len(tasks))
        with col2:
            makespan = job_details.get("makespan_minutes")
            if makespan:
                st.metric("Current Makespan", f"{makespan} min")
            else:
                st.metric("Current Makespan", "Not solved")
            st.metric("Priority", job_details.get("priority", 0))
        
        if not tasks:
            st.error("❌ This job order has no tasks. Add tasks before running the solver.")
        else:
            st.markdown("---")
            st.info("💡 The solver will find an optimal schedule that minimizes the makespan (total completion time).")
            
            if st.button("🚀 Run Solver", type="primary", use_container_width=True):
                with st.spinner("Solving... This may take a moment."):
                    resp = api_post(f"/job-orders/{job_id}/solve", None)
                    if resp.status_code in (200, 201):
                        data = resp.json()
                        status_emoji = "✅" if data.get("status") == "feasible" else "❌"
                        st.success(
                            f"{status_emoji} **Solver Status:** {data.get('solver_status', 'unknown').upper()}\n\n"
                            f"**Objective Value (Makespan):** {data.get('objective_value', 'N/A')} minutes"
                        )
                        if data.get("status") == "infeasible":
                            st.error(
                                "⚠️ **Infeasible Solution:** The solver could not find a valid schedule. "
                                "Check machine capabilities, task durations, or constraints."
                            )
                        refresh_cache()
                        st.rerun()
                    else:
                        try:
                            error_detail = resp.json().get("detail", resp.text)
                        except:
                            error_detail = resp.text
                        st.error(f"❌ Solver failed: {error_detail}")

