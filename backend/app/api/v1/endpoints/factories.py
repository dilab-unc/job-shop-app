from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.models import Factory, FactoryCreate, FactoryRead
from app.api.deps import SessionDep


router = APIRouter()


@router.get("/", response_model=List[FactoryRead])
def list_factories(session: SessionDep) -> List[FactoryRead]:
    return session.exec(select(Factory)).all()


@router.post(
    "/", response_model=FactoryRead, status_code=status.HTTP_201_CREATED
)
def create_factory(factory_in: FactoryCreate, session: SessionDep) -> FactoryRead:
    factory = Factory.from_orm(factory_in)
    session.add(factory)
    session.commit()
    session.refresh(factory)
    return factory


@router.get("/{factory_id}", response_model=FactoryRead)
def get_factory(factory_id: int, session: SessionDep) -> FactoryRead:
    factory = session.get(Factory, factory_id)
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")
    return factory


