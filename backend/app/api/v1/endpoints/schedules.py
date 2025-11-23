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
    query = select(Schedule)
    if job_id:
        query = query.where(Schedule.job_id == job_id)
    return session.exec(query).all()


@router.get("/{schedule_id}", response_model=ScheduleRead)
def get_schedule(schedule_id: int, session: SessionDep) -> ScheduleRead:
    schedule = session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.get("/{schedule_id}/tasks", response_model=List[ScheduledTaskRead])
def get_schedule_tasks(schedule_id: int, session: SessionDep) -> List[ScheduledTaskRead]:
    schedule = session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule.assignments


@router.get("/{schedule_id}/gantt", response_model=List[Dict[str, Any]])
def get_schedule_gantt_data(schedule_id: int, session: SessionDep) -> List[Dict[str, Any]]:
    """Get enriched schedule data for Gantt chart visualization."""
    schedule = session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    job_order = session.get(JobOrder, schedule.job_id)
    if not job_order:
        raise HTTPException(status_code=404, detail="Job order not found")

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
        else:
            task_name = f"Task {task.job_task_id}"

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
                "job_id": schedule.job_id,
                "job_name": job_order.name,
            }
        )

    return gantt_data


