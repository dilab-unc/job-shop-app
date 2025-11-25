from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import (
    JobOrder,
    JobTask,
    Machine,
    Schedule,
    ScheduleRead,
    ScheduledTask,
    ScheduledTaskRead,
    TaskTemplate,
)


router = APIRouter()


@router.get("/", response_model=List[ScheduleRead])
def list_schedules(session: SessionDep, job_id: int | None = None) -> List[ScheduleRead]:
    """List all schedules, optionally filtered by job order ID."""
    from sqlalchemy.orm import aliased
    from app.models import ScheduleJobOrder
    
    query = select(Schedule)
    if job_id:
        # Filter schedules that contain this job order
        query = query.join(ScheduleJobOrder).where(ScheduleJobOrder.job_order_id == job_id)
    schedules = session.exec(query).all()
    
    # Convert to ScheduleRead with job_order_ids
    result = []
    for schedule in schedules:
        # Refresh to load job_orders relationship
        session.refresh(schedule)
        job_order_ids = [job.id for job in schedule.job_orders]
        result.append({
            "id": schedule.id,
            "status": schedule.status,
            "objective_value": schedule.objective_value,
            "solver_status": schedule.solver_status,
            "job_order_ids": job_order_ids,
            "created_at": schedule.created_at,
            "updated_at": schedule.updated_at,
        })
    return result


@router.get("/{schedule_id}", response_model=ScheduleRead)
def get_schedule(schedule_id: int, session: SessionDep) -> ScheduleRead:
    schedule = session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
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


@router.get("/{schedule_id}/tasks", response_model=List[ScheduledTaskRead])
def get_schedule_tasks(schedule_id: int, session: SessionDep) -> List[ScheduledTaskRead]:
    schedule = session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule.assignments


@router.get("/{schedule_id}/gantt", response_model=List[Dict[str, Any]])
def get_schedule_gantt_data(schedule_id: int, session: SessionDep) -> List[Dict[str, Any]]:
    """Get enriched schedule data for Gantt chart visualization.
    
    Returns data for all tasks from all job orders in the schedule.
    """
    schedule = session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Refresh to load job_orders relationship
    session.refresh(schedule)
    
    # Create lookup for job orders
    job_order_lookup = {job.id: job for job in schedule.job_orders}

    gantt_data = []
    for task in schedule.assignments:
        # Load job task with template relationship
        job_task = session.exec(
            select(JobTask).where(JobTask.id == task.job_task_id)
        ).first()
        machine = session.get(Machine, task.machine_id)

        # Get task name
        if job_task:
            if job_task.custom_name:
                task_name = job_task.custom_name
            elif job_task.task_template_id:
                template = session.get(TaskTemplate, job_task.task_template_id)
                task_name = template.name if template else f"Task {task.job_task_id}"
            else:
                task_name = f"Task {task.job_task_id}"
            
            # Get job order info
            job_order = job_order_lookup.get(job_task.job_id)
            job_name = job_order.name if job_order else f"Job {job_task.job_id}"
            job_id = job_task.job_id
        else:
            task_name = f"Task {task.job_task_id}"
            job_name = "Unknown Job"
            job_id = None

        machine_name = machine.name if machine else f"Machine {task.machine_id}"

        gantt_data.append(
            {
                "task_id": task.id,
                "job_task_id": task.job_task_id,
                "task_name": task_name,
                "machine_id": task.machine_id,
                "machine_name": machine_name,
                "start_time": task.start_time.isoformat(),
                "end_time": task.end_time.isoformat(),
                "duration_minutes": int((task.end_time - task.start_time).total_seconds() / 60),
                "job_id": job_id,
                "job_name": job_name,
            }
        )

    return gantt_data


