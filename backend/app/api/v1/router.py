from fastapi import APIRouter

from .endpoints import factories, machines, task_templates, job_orders, schedules


api_router = APIRouter()

api_router.include_router(factories.router, prefix="/factories", tags=["factories"])
api_router.include_router(machines.router, prefix="/machines", tags=["machines"])
api_router.include_router(
    task_templates.router, prefix="/task-templates", tags=["task_templates"]
)
api_router.include_router(
    job_orders.router, prefix="/job-orders", tags=["job_orders"]
)
api_router.include_router(
    schedules.router, prefix="/schedules", tags=["schedules"]
)


