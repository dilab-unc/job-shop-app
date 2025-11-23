from typing import List

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import TaskTemplate, TaskTemplateCreate, TaskTemplateRead


router = APIRouter()


@router.get("/", response_model=List[TaskTemplateRead])
def list_task_templates(
    session: SessionDep, factory_id: int | None = Query(default=None)
) -> List[TaskTemplateRead]:
    query = select(TaskTemplate)
    if factory_id:
        query = query.where(TaskTemplate.factory_id == factory_id)
    return session.exec(query).all()


@router.post(
    "/", response_model=TaskTemplateRead, status_code=status.HTTP_201_CREATED
)
def create_task_template(
    template_in: TaskTemplateCreate, session: SessionDep
) -> TaskTemplateRead:
    template = TaskTemplate.from_orm(template_in)
    session.add(template)
    session.commit()
    session.refresh(template)
    return template


@router.get("/{template_id}", response_model=TaskTemplateRead)
def get_task_template(template_id: int, session: SessionDep) -> TaskTemplateRead:
    template = session.get(TaskTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Task template not found")
    return template


