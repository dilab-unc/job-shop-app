from datetime import datetime, timedelta

from sqlmodel import select

from .database import init_db, session_scope
from .models import Factory, JobOrder, JobTask, Machine, TaskTemplate

SAMPLE_FACTORY_NAME = "Demo Factory"


def seed_sample_data() -> None:
    """Populate the database with demo factory, machines, templates, and a job order."""
    init_db()

    with session_scope() as session:
        factory = session.exec(
            select(Factory).where(Factory.name == SAMPLE_FACTORY_NAME)
        ).first()
        if not factory:
            factory = Factory(
                name=SAMPLE_FACTORY_NAME,
                description="Reference factory mirroring the Google OR-Tools job shop example.",
            )
            session.add(factory)
            session.flush()

        machines_payload = [
            {
                "name": "Machine 0",
                "description": "Handles cutting/rough prep tasks.",
                "capabilities": ["cut", "prep"],
            },
            {
                "name": "Machine 1",
                "description": "Assembly and finishing station.",
                "capabilities": ["assemble", "finish"],
            },
            {
                "name": "Machine 2",
                "description": "Paint / coating booth.",
                "capabilities": ["paint", "coat"],
            },
        ]

        for payload in machines_payload:
            exists = session.exec(
                select(Machine).where(
                    Machine.factory_id == factory.id,
                    Machine.name == payload["name"],
                )
            ).first()
            if not exists:
                session.add(
                    Machine(
                        factory_id=factory.id,
                        name=payload["name"],
                        description=payload["description"],
                        capabilities=payload["capabilities"],
                    )
                )
        session.flush()

        machines = session.exec(
            select(Machine).where(Machine.factory_id == factory.id)
        ).all()
        machine_by_name = {machine.name: machine for machine in machines}

        templates_payload = [
            {
                "name": "Cutting",
                "task_type": "cut",
                "default_duration_minutes": 3,
                "allowed_machines": ["Machine 0"],
            },
            {
                "name": "Assembly",
                "task_type": "assemble",
                "default_duration_minutes": 2,
                "allowed_machines": ["Machine 1"],
            },
            {
                "name": "Painting",
                "task_type": "paint",
                "default_duration_minutes": 2,
                "allowed_machines": ["Machine 2"],
            },
        ]

        for payload in templates_payload:
            exists = session.exec(
                select(TaskTemplate).where(
                    TaskTemplate.factory_id == factory.id,
                    TaskTemplate.name == payload["name"],
                )
            ).first()
            if exists:
                continue

            allowed_ids = [
                machine_by_name[name].id
                for name in payload["allowed_machines"]
                if name in machine_by_name
            ]
            session.add(
                TaskTemplate(
                    factory_id=factory.id,
                    name=payload["name"],
                    description=f"{payload['name']} task",
                    task_type=payload["task_type"],
                    default_duration_minutes=payload["default_duration_minutes"],
                    allowed_machine_ids=allowed_ids,
                )
            )
        session.flush()

        templates = session.exec(
            select(TaskTemplate).where(TaskTemplate.factory_id == factory.id)
        ).all()
        template_by_name = {template.name: template for template in templates}

        job_orders_payload = [
            {
                "name": "Sample Job 0",
                "tasks": [
                    ("Cutting", "Machine 0", 3),
                    ("Assembly", "Machine 1", 2),
                    ("Painting", "Machine 2", 2),
                ],
            },
            {
                "name": "Sample Job 1",
                "tasks": [
                    ("Cutting", "Machine 0", 2),
                    ("Painting", "Machine 2", 1),
                    ("Assembly", "Machine 1", 4),
                ],
            },
            {
                "name": "Sample Job 2",
                "tasks": [
                    ("Assembly", "Machine 1", 4),
                    ("Painting", "Machine 2", 3),
                ],
            },
        ]

        for payload in job_orders_payload:
            job_exists = session.exec(
                select(JobOrder).where(
                    JobOrder.factory_id == factory.id, JobOrder.name == payload["name"]
                )
            ).first()
            if job_exists:
                continue

            job = JobOrder(
                factory_id=factory.id,
                name=payload["name"],
                description="Auto-seeded demo job order.",
                due_date=datetime.utcnow() + timedelta(days=7),
                status="draft",
            )
            session.add(job)
            session.flush()

            for idx, (template_name, machine_name, duration) in enumerate(payload["tasks"]):
                template = template_by_name[template_name]
                machine = machine_by_name[machine_name]
                session.add(
                    JobTask(
                        job_id=job.id,
                        sequence_index=idx,
                        task_template_id=template.id,
                        custom_name=f"{template_name} #{idx+1}",
                        custom_duration_minutes=duration,
                        machine_hint_id=machine.id,
                    )
                )

        print("✅ Sample data seeded. Run `uvicorn app.main:app --reload` and hit /api endpoints.")


if __name__ == "__main__":
    seed_sample_data()

