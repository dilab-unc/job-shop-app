from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, JSON
from sqlmodel import Field, Relationship, SQLModel


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_type=DateTime(timezone=False),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_type=DateTime(timezone=False),
    )


class FactoryBase(SQLModel):
    name: str
    description: Optional[str] = None


class Factory(TimestampMixin, FactoryBase, table=True):
    __tablename__ = "factories"

    id: Optional[int] = Field(default=None, primary_key=True)

    machines: list["Machine"] = Relationship(back_populates="factory")
    task_templates: list["TaskTemplate"] = Relationship(back_populates="factory")
    job_orders: list["JobOrder"] = Relationship(back_populates="factory")


class FactoryCreate(FactoryBase):
    pass


class FactoryRead(FactoryBase):
    id: int
    created_at: datetime
    updated_at: datetime


class MachineBase(SQLModel):
    name: str
    description: Optional[str] = None
    capabilities: list[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False, default=list)
    )
    max_parallel_jobs: int = 1


class Machine(TimestampMixin, MachineBase, table=True):
    __tablename__ = "machines"

    id: Optional[int] = Field(default=None, primary_key=True)
    factory_id: int = Field(foreign_key="factories.id", nullable=False)

    factory: Optional[Factory] = Relationship(back_populates="machines")
    scheduled_tasks: list["ScheduledTask"] = Relationship(back_populates="machine")


class MachineCreate(MachineBase):
    factory_id: int


class MachineRead(MachineBase):
    id: int
    factory_id: int
    created_at: datetime
    updated_at: datetime


class TaskTemplateBase(SQLModel):
    name: str
    description: Optional[str] = None
    task_type: str
    default_duration_minutes: int
    allowed_machine_ids: Optional[list[int]] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )


class TaskTemplate(TimestampMixin, TaskTemplateBase, table=True):
    __tablename__ = "task_templates"

    id: Optional[int] = Field(default=None, primary_key=True)
    factory_id: int = Field(foreign_key="factories.id", nullable=False)

    factory: Optional[Factory] = Relationship(back_populates="task_templates")
    job_tasks: list["JobTask"] = Relationship(back_populates="task_template")


class TaskTemplateCreate(TaskTemplateBase):
    factory_id: int


class TaskTemplateRead(TaskTemplateBase):
    id: int
    factory_id: int
    created_at: datetime
    updated_at: datetime


class JobOrderBase(SQLModel):
    name: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = 0
    status: str = "draft"
    makespan_minutes: Optional[int] = None
    solver_metadata: Optional[dict] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )


class JobOrder(TimestampMixin, JobOrderBase, table=True):
    __tablename__ = "job_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    factory_id: int = Field(foreign_key="factories.id", nullable=False)

    factory: Optional[Factory] = Relationship(back_populates="job_orders")
    tasks: list["JobTask"] = Relationship(
        back_populates="job_order", sa_relationship_kwargs={"order_by": "JobTask.sequence_index"}
    )
    schedules: list["Schedule"] = Relationship(back_populates="job_order")


class JobOrderCreate(JobOrderBase):
    factory_id: int


class JobOrderRead(JobOrderBase):
    id: int
    factory_id: int
    created_at: datetime
    updated_at: datetime


class JobTaskBase(SQLModel):
    sequence_index: int
    custom_name: Optional[str] = None
    custom_duration_minutes: Optional[int] = None
    machine_hint_id: Optional[int] = None
    notes: Optional[str] = None


class JobTask(TimestampMixin, JobTaskBase, table=True):
    __tablename__ = "job_tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job_orders.id", nullable=False)
    task_template_id: Optional[int] = Field(
        default=None, foreign_key="task_templates.id"
    )

    job_order: Optional[JobOrder] = Relationship(back_populates="tasks")
    task_template: Optional[TaskTemplate] = Relationship(back_populates="job_tasks")
    scheduled_tasks: list["ScheduledTask"] = Relationship(back_populates="job_task")


class JobTaskCreate(JobTaskBase):
    job_id: int
    task_template_id: Optional[int] = None


class JobTaskUpdate(JobTaskBase):
    task_template_id: Optional[int] = None


class JobTaskRead(JobTaskBase):
    id: int
    job_id: int
    task_template_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class ScheduleBase(SQLModel):
    status: str = "pending"
    objective_value: Optional[int] = None
    solver_status: Optional[str] = None


class Schedule(TimestampMixin, ScheduleBase, table=True):
    __tablename__ = "schedules"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job_orders.id", nullable=False)

    job_order: Optional[JobOrder] = Relationship(back_populates="schedules")
    assignments: list["ScheduledTask"] = Relationship(back_populates="schedule")


class ScheduleRead(ScheduleBase):
    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime


class ScheduledTaskBase(SQLModel):
    start_time: datetime
    end_time: datetime


class ScheduledTask(TimestampMixin, ScheduledTaskBase, table=True):
    __tablename__ = "scheduled_tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    schedule_id: int = Field(foreign_key="schedules.id", nullable=False)
    job_task_id: int = Field(foreign_key="job_tasks.id", nullable=False)
    machine_id: int = Field(foreign_key="machines.id", nullable=False)

    schedule: Optional[Schedule] = Relationship(back_populates="assignments")
    job_task: Optional[JobTask] = Relationship(back_populates="scheduled_tasks")
    machine: Optional[Machine] = Relationship(back_populates="scheduled_tasks")


class ScheduledTaskRead(ScheduledTaskBase):
    id: int
    schedule_id: int
    job_task_id: int
    machine_id: int
    created_at: datetime
    updated_at: datetime


