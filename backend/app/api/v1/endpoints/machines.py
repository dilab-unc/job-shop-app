from typing import List

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import Machine, MachineCreate, MachineRead


router = APIRouter()


@router.get("/", response_model=List[MachineRead])
def list_machines(
    session: SessionDep, factory_id: int | None = Query(default=None)
) -> List[MachineRead]:
    query = select(Machine)
    if factory_id:
        query = query.where(Machine.factory_id == factory_id)
    return session.exec(query).all()


@router.post(
    "/", response_model=MachineRead, status_code=status.HTTP_201_CREATED
)
def create_machine(machine_in: MachineCreate, session: SessionDep) -> MachineRead:
    machine = Machine.from_orm(machine_in)
    session.add(machine)
    session.commit()
    session.refresh(machine)
    return machine


@router.get("/{machine_id}", response_model=MachineRead)
def get_machine(machine_id: int, session: SessionDep) -> MachineRead:
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine


