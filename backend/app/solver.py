from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from ortools.sat.python import cp_model
from sqlmodel import Session, select

from .models import JobOrder, JobTask, Machine, ScheduledTask, Schedule


@dataclass
class SolverResult:
    schedule: Schedule
    assignments: List[ScheduledTask]


def solve_job_order(job_id: int, session: Session) -> SolverResult:
    """Translate a job order into a CP-SAT model and persist the schedule."""
    job: JobOrder | None = session.get(JobOrder, job_id)
    if not job:
        raise ValueError("Job order not found")

    tasks = (
        session.exec(
            select(JobTask).where(JobTask.job_id == job_id).order_by(JobTask.sequence_index)
        ).all()
        or []
    )
    if not tasks:
        raise ValueError("Job order has no tasks to schedule")

    machines = session.exec(
        select(Machine).where(Machine.factory_id == job.factory_id)
    ).all()
    machine_lookup = {machine.id: machine for machine in machines}

    model = cp_model.CpModel()
    horizon = 0
    for task in tasks:
        duration = task.custom_duration_minutes or (
            task.task_template.default_duration_minutes if task.task_template else 0
        )
        horizon += duration
    if horizon == 0:
        raise ValueError("Tasks must have duration > 0")

    all_tasks = {}
    machine_to_intervals: dict[int, list] = {}

    for task in tasks:
        duration = task.custom_duration_minutes or (
            task.task_template.default_duration_minutes if task.task_template else 0
        )
        if duration <= 0:
            raise ValueError(f"Task {task.id} is missing a positive duration")

        machine_id = task.machine_hint_id or (
            task.task_template.allowed_machine_ids[0]
            if task.task_template and task.task_template.allowed_machine_ids
            else None
        )
        if not machine_id:
            raise ValueError(f"Task {task.id} has no machine hint or allowed machines")
        if machine_id not in machine_lookup:
            raise ValueError(f"Machine {machine_id} is not available in factory")

        suffix = f"{task.id}"
        start = model.NewIntVar(0, horizon, f"start_{suffix}")
        end = model.NewIntVar(0, horizon, f"end_{suffix}")
        interval = model.NewIntervalVar(start, duration, end, f"interval_{suffix}")

        all_tasks[task.id] = (start, end, interval, duration, machine_id)
        machine_to_intervals.setdefault(machine_id, []).append(interval)

    for machine_id, intervals in machine_to_intervals.items():
        model.AddNoOverlap(intervals)

    sorted_task_ids = [task.id for task in tasks]
    for prev, nxt in zip(sorted_task_ids, sorted_task_ids[1:]):
        model.Add(all_tasks[nxt][0] >= all_tasks[prev][1])

    obj_var = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(obj_var, [all_tasks[task_id][1] for task_id in sorted_task_ids])
    model.Minimize(obj_var)

    solver = cp_model.CpSolver()
    solver_status = solver.Solve(model)

    status_map = {
        cp_model.OPTIMAL: "optimal",
        cp_model.FEASIBLE: "feasible",
        cp_model.INFEASIBLE: "infeasible",
        cp_model.MODEL_INVALID: "invalid",
        cp_model.UNKNOWN: "unknown",
    }
    status_str = status_map.get(solver_status, "unknown")

    schedule = Schedule(
        job_id=job_id,
        status="feasible" if solver_status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else "infeasible",
        objective_value=int(solver.ObjectiveValue())
        if solver_status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        else None,
        solver_status=status_str,
        solver_metadata={
            "status": status_str,
            "conflicts": solver.NumConflicts(),
            "branches": solver.NumBranches(),
            "wall_time": solver.WallTime(),
        },
    )

    assignments: List[ScheduledTask] = []
    if schedule.status == "feasible":
        start_time = datetime.utcnow()
        for task_id, (start, end, _, duration, machine_id) in all_tasks.items():
            assignments.append(
                ScheduledTask(
                    job_task_id=task_id,
                    machine_id=machine_id,
                    start_time=start_time + timedelta(minutes=int(solver.Value(start))),
                    end_time=start_time + timedelta(minutes=int(solver.Value(end))),
                )
            )

    return SolverResult(schedule=schedule, assignments=assignments)


