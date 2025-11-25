from __future__ import annotations

import csv
from io import StringIO
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, status
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import (
    JobOrder,
    JobOrderCreate,
    JobOrderRead,
    JobTask,
    JobTaskCreate,
    JobTaskRead,
    JobTaskUpdate,
    Machine,
    ScheduleRead,
    TaskTemplate,
)
from app.solver import solve_job_order, solve_job_orders


router = APIRouter()


@router.get("/", response_model=List[JobOrderRead])
def list_job_orders(session: SessionDep, factory_id: int | None = None) -> List[JobOrderRead]:
    query = select(JobOrder)
    if factory_id:
        query = query.where(JobOrder.factory_id == factory_id)
    return session.exec(query).all()


@router.post("/", response_model=JobOrderRead, status_code=status.HTTP_201_CREATED)
def create_job_order(job_in: JobOrderCreate, session: SessionDep) -> JobOrderRead:
    job = JobOrder.from_orm(job_in)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobOrderRead)
def get_job_order(job_id: int, session: SessionDep) -> JobOrderRead:
    job = session.get(JobOrder, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job order not found")
    return job


@router.get("/{job_id}/tasks", response_model=List[JobTaskRead])
def list_job_tasks(job_id: int, session: SessionDep) -> List[JobTaskRead]:
    job = session.get(JobOrder, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job order not found")
    return job.tasks


@router.post("/{job_id}/tasks", response_model=List[JobTaskRead])
def add_job_tasks(
    job_id: int, tasks_in: List[JobTaskCreate], session: SessionDep
) -> List[JobTaskRead]:
    job = session.get(JobOrder, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job order not found")

    created_tasks: List[JobTask] = []
    for payload in tasks_in:
        task = JobTask(
            job_id=job_id,
            sequence_index=payload.sequence_index,
            custom_name=payload.custom_name,
            custom_duration_minutes=payload.custom_duration_minutes,
            machine_hint_id=payload.machine_hint_id,
            notes=payload.notes,
            task_template_id=payload.task_template_id,
        )
        session.add(task)
        created_tasks.append(task)

    session.commit()
    for task in created_tasks:
        session.refresh(task)

    return created_tasks


@router.put("/{job_id}/tasks/reorder", response_model=List[JobTaskRead])
def reorder_job_tasks(
    job_id: int, task_ids: List[int], session: SessionDep
) -> List[JobTaskRead]:
    """Reorder tasks by providing a list of task IDs in the desired order."""
    job = session.get(JobOrder, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job order not found")

    # Verify all tasks belong to this job
    tasks = session.exec(select(JobTask).where(JobTask.job_id == job_id)).all()
    task_dict = {t.id: t for t in tasks}
    
    if len(task_ids) != len(tasks):
        raise HTTPException(
            status_code=400,
            detail=f"Expected {len(tasks)} task IDs, got {len(task_ids)}",
        )

    for task_id in task_ids:
        if task_id not in task_dict:
            raise HTTPException(
                status_code=400,
                detail=f"Task {task_id} does not belong to this job",
            )

    # Update sequence indices
    for new_index, task_id in enumerate(task_ids):
        task = task_dict[task_id]
        task.sequence_index = new_index
        session.add(task)

    session.commit()
    for task in tasks:
        session.refresh(task)

    # Return tasks in new order
    return [task_dict[tid] for tid in task_ids]


@router.get("/{job_id}/tasks/{task_id}", response_model=JobTaskRead)
def get_job_task(job_id: int, task_id: int, session: SessionDep) -> JobTaskRead:
    task = session.get(JobTask, task_id)
    if not task or task.job_id != job_id:
        raise HTTPException(status_code=404, detail="Job task not found")
    return task


@router.put("/{job_id}/tasks/{task_id}", response_model=JobTaskRead)
def update_job_task(
    job_id: int, task_id: int, task_update: JobTaskUpdate, session: SessionDep
) -> JobTaskRead:
    task = session.get(JobTask, task_id)
    if not task or task.job_id != job_id:
        raise HTTPException(status_code=404, detail="Job task not found")

    task.sequence_index = task_update.sequence_index
    task.custom_name = task_update.custom_name
    task.custom_duration_minutes = task_update.custom_duration_minutes
    task.machine_hint_id = task_update.machine_hint_id
    task.notes = task_update.notes
    task.task_template_id = task_update.task_template_id

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{job_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_job_task(job_id: int, task_id: int, session: SessionDep) -> None:
    task = session.get(JobTask, task_id)
    if not task or task.job_id != job_id:
        raise HTTPException(status_code=404, detail="Job task not found")

    session.delete(task)
    session.commit()
    return None


@router.post("/{job_id}/import-csv", response_model=List[JobTaskRead])
async def import_job_tasks_csv(job_id: int, file: UploadFile, session: SessionDep) -> List[JobTaskRead]:
    """Import job tasks from CSV file.
    
    Expected CSV columns:
    - sequence_index (required): Order of task in job (0-based)
    - task_name (required): Name of the task
    - duration_minutes (required): Duration in minutes
    - machine_name (optional): Name of machine (looked up by name)
    - machine_id (optional): ID of machine (alternative to machine_name)
    - task_template_name (optional): Name of task template (looked up by name)
    - task_template_id (optional): ID of task template (alternative to task_template_name)
    - notes (optional): Additional notes
    """
    job = session.get(JobOrder, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job order not found")

    content = await file.read()
    try:
        decoded = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded") from exc

    reader = csv.DictReader(StringIO(decoded))
    rows = list(reader)
    if not rows:
        raise HTTPException(status_code=400, detail="CSV file is empty")

    # Build lookup maps for machines and templates in this factory
    machines = session.exec(select(Machine).where(Machine.factory_id == job.factory_id)).all()
    machine_name_to_id = {m.name: m.id for m in machines}
    machine_id_to_obj = {m.id: m for m in machines}

    templates = session.exec(
        select(TaskTemplate).where(TaskTemplate.factory_id == job.factory_id)
    ).all()
    template_name_to_id = {t.name: t.id for t in templates}
    template_id_to_obj = {t.id: t for t in templates}

    tasks: List[JobTaskCreate] = []
    errors: List[str] = []

    for idx, row in enumerate(rows, start=2):  # Start at 2 (1 for header, 1-indexed for users)
        # Validate required fields
        if not row.get("task_name"):
            errors.append(f"Row {idx}: task_name is required")
            continue

        try:
            duration = int(row.get("duration_minutes", "0"))
            if duration <= 0:
                errors.append(f"Row {idx}: duration_minutes must be > 0")
                continue
        except (ValueError, TypeError):
            errors.append(f"Row {idx}: Invalid duration_minutes (must be integer)")
            continue

        # Parse sequence_index
        try:
            seq_idx = int(row.get("sequence_index", str(idx - 2)))
        except (ValueError, TypeError):
            errors.append(f"Row {idx}: Invalid sequence_index (must be integer)")
            continue

        # Resolve machine_id
        machine_id = None
        if row.get("machine_id"):
            try:
                machine_id = int(row["machine_id"])
                if machine_id not in machine_id_to_obj:
                    errors.append(f"Row {idx}: Machine ID {machine_id} not found in factory")
                    continue
            except (ValueError, TypeError):
                errors.append(f"Row {idx}: Invalid machine_id (must be integer)")
                continue
        elif row.get("machine_name"):
            machine_name = row["machine_name"].strip()
            if machine_name not in machine_name_to_id:
                errors.append(f"Row {idx}: Machine '{machine_name}' not found in factory")
                continue
            machine_id = machine_name_to_id[machine_name]

        # Resolve task_template_id
        task_template_id = None
        if row.get("task_template_id"):
            try:
                task_template_id = int(row["task_template_id"])
                if task_template_id not in template_id_to_obj:
                    errors.append(f"Row {idx}: Task template ID {task_template_id} not found in factory")
                    continue
            except (ValueError, TypeError):
                errors.append(f"Row {idx}: Invalid task_template_id (must be integer)")
                continue
        elif row.get("task_template_name"):
            template_name = row["task_template_name"].strip()
            if template_name not in template_name_to_id:
                errors.append(f"Row {idx}: Task template '{template_name}' not found in factory")
                continue
            task_template_id = template_name_to_id[template_name]

        tasks.append(
            JobTaskCreate(
                job_id=job_id,
                sequence_index=seq_idx,
                custom_name=row["task_name"].strip(),
                custom_duration_minutes=duration,
                machine_hint_id=machine_id,
                task_template_id=task_template_id,
                notes=row.get("notes", "").strip() or None,
            )
        )

    if errors:
        error_msg = "CSV import errors:\n" + "\n".join(f"  - {e}" for e in errors)
        raise HTTPException(status_code=400, detail=error_msg)

    if not tasks:
        raise HTTPException(status_code=400, detail="No valid tasks found in CSV")

    return add_job_tasks(job_id=job_id, tasks_in=tasks, session=session)


@router.post("/solve-batch", response_model=ScheduleRead)
def solve_jobs_batch(job_ids: List[int], session: SessionDep) -> ScheduleRead:
    """Solve multiple job orders simultaneously in a single schedule.
    
    Tasks from different job orders can run in parallel on different machines.
    Tasks within the same job order maintain their sequence constraints.
    Returns a single schedule containing all job orders.
    """
    if not job_ids:
        raise HTTPException(status_code=400, detail="At least one job order ID is required")
    
    try:
        solver_result = solve_job_orders(job_ids=job_ids, session=session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Persist the schedule (this will also persist the job order associations)
    schedule = solver_result.schedule
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    
    # Assign schedule_id to all assignments
    for assignment in solver_result.assignments:
        assignment.schedule_id = schedule.id
        session.add(assignment)
    session.commit()
    
    # Refresh to get relationships loaded
    session.refresh(schedule)
    job_order_ids = [job.id for job in schedule.job_orders]
    return {
        "id": schedule.id,
        "status": schedule.status,
        "objective_value": schedule.objective_value,
        "solver_status": schedule.solver_status,
        "job_order_ids": job_order_ids,
        "created_at": schedule.created_at,
        "updated_at": schedule.updated_at,
    }


@router.post("/{job_id}/solve", response_model=ScheduleRead)
def solve_job(job_id: int, session: SessionDep) -> ScheduleRead:
    job = session.get(JobOrder, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job order not found")

    solver_result = solve_job_order(job_id=job_id, session=session)
    schedule = solver_result.schedule
    session.add(schedule)
    session.commit()
    session.refresh(schedule)

    for assignment in solver_result.assignments:
        assignment.schedule_id = schedule.id  # assign FK after schedule persisted
        session.add(assignment)
    session.commit()
    
    # Refresh to load job_orders relationship
    session.refresh(schedule)
    job_order_ids = [job.id for job in schedule.job_orders]
    return {
        "id": schedule.id,
        "status": schedule.status,
        "objective_value": schedule.objective_value,
        "solver_status": schedule.solver_status,
        "job_order_ids": job_order_ids,
        "created_at": schedule.created_at,
        "updated_at": schedule.updated_at,
    }


