"""Admin endpoints for database management."""
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import (
    Factory,
    JobOrder,
    JobTask,
    Machine,
    Schedule,
    ScheduleJobOrder,
    ScheduledTask,
    TaskTemplate,
)
from app.seed import seed_sample_data

router = APIRouter()


@router.post("/seed", status_code=status.HTTP_200_OK)
def seed_database(session: SessionDep) -> dict:
    """Seed the database with sample data.
    
    This endpoint runs the seed script to populate the database with:
    - Demo Factory
    - 3 Machines (Machine 0, Machine 1, Machine 2)
    - 3 Task Templates (Cutting, Assembly, Painting)
    - 3 Sample Job Orders
    
    The seed script is idempotent - it won't create duplicates if data already exists.
    """
    try:
        # The seed function uses its own session_scope, so we don't need the session parameter
        # but we keep it for consistency with other endpoints
        seed_sample_data()
        return {
            "status": "success",
            "message": "Sample data seeded successfully. Check /api/factories to see the demo factory."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed database: {str(e)}"
        )


@router.delete("/clear", status_code=status.HTTP_200_OK)
def clear_database(session: SessionDep) -> dict:
    """Clear all data from the database.
    
    WARNING: This will delete ALL data including:
    - All factories
    - All machines
    - All task templates
    - All job orders and tasks
    - All schedules and scheduled tasks
    
    This action cannot be undone!
    """
    try:
        # Delete in order to respect foreign key constraints
        # Start with dependent tables first
        
        # Delete scheduled tasks
        scheduled_tasks = session.exec(select(ScheduledTask)).all()
        for task in scheduled_tasks:
            session.delete(task)
        
        # Delete schedule-job associations
        schedule_jobs = session.exec(select(ScheduleJobOrder)).all()
        for sj in schedule_jobs:
            session.delete(sj)
        
        # Delete schedules
        schedules = session.exec(select(Schedule)).all()
        for schedule in schedules:
            session.delete(schedule)
        
        # Delete job tasks
        job_tasks = session.exec(select(JobTask)).all()
        for task in job_tasks:
            session.delete(task)
        
        # Delete job orders
        job_orders = session.exec(select(JobOrder)).all()
        for job in job_orders:
            session.delete(job)
        
        # Delete task templates
        templates = session.exec(select(TaskTemplate)).all()
        for template in templates:
            session.delete(template)
        
        # Delete machines
        machines = session.exec(select(Machine)).all()
        for machine in machines:
            session.delete(machine)
        
        # Delete factories (last, as other tables depend on it)
        factories = session.exec(select(Factory)).all()
        for factory in factories:
            session.delete(factory)
        
        session.commit()
        
        counts = {
            "factories": len(factories),
            "machines": len(machines),
            "task_templates": len(templates),
            "job_orders": len(job_orders),
            "job_tasks": len(job_tasks),
            "schedules": len(schedules),
            "scheduled_tasks": len(scheduled_tasks),
        }
        
        return {
            "status": "success",
            "message": "Database cleared successfully.",
            "deleted": counts
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear database: {str(e)}"
        )

