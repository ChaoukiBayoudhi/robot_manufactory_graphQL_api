import typing as t
from datetime import datetime

import strawberry
from django.utils import timezone
from strawberry import auto
from strawberry.django import type as django_type
from strawberry.scalars import JSON

from .models import (
    MaintenanceEvent,
    Prediction,
    Robot,
    Task,
    TelemetryPoint,
)


@django_type(Robot)
class RobotType:
    id: auto
    serial: str
    model: str
    capabilities: list[str]
    status: str
    location: str | None
    last_seen: datetime | None


@django_type(TelemetryPoint)
class TelemetryPointType:
    id: auto
    robot: RobotType
    timestamp: datetime
    metric_name: str
    metric_value: float
    metadata: JSON | None


@django_type(Task)
class TaskType:
    id: auto
    required_capabilities: list[str]
    status: str
    assigned_robot: RobotType | None
    priority: int
    deadline: datetime | None
    created_at: datetime


@django_type(MaintenanceEvent)
class MaintenanceEventType:
    id: auto
    robot: RobotType
    timestamp: datetime
    type: str
    notes: str


@django_type(Prediction)
class PredictionType:
    id: auto
    robot: RobotType
    timestamp: datetime
    prediction_type: str
    value: float
    model_version: str


@strawberry.type
class Query:
    @strawberry.field
    def robots(self, info, model: str | None = None) -> list[RobotType]:
        qs = Robot.objects.all()
        if model:
            qs = qs.filter(model__icontains=model)
        return list(qs)

    @strawberry.field
    def tasks(self, info, status: str | None = None) -> list[TaskType]:
        qs = Task.objects.all()
        if status:
            qs = qs.filter(status=status)
        return list(qs)


@strawberry.input
class CreateRobotInput:
    serial: str
    model: str
    capabilities: list[str] | None = None
    location: str | None = None


@strawberry.input
class CreateTaskInput:
    required_capabilities: list[str]
    priority: int = 0
    deadline: datetime | None = None
    assigned_robot_id: strawberry.ID | None = None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_robot(self, info, data: CreateRobotInput) -> RobotType:
        robot = Robot.objects.create(
            serial=data.serial,
            model=data.model,
            capabilities=data.capabilities or [],
            location=data.location or "",
        )
        return robot

    @strawberry.mutation
    def create_task(self, info, data: CreateTaskInput) -> TaskType:
        assigned_robot = None
        if data.assigned_robot_id is not None:
            assigned_robot = Robot.objects.get(pk=data.assigned_robot_id)

        task = Task.objects.create(
            required_capabilities=data.required_capabilities,
            priority=data.priority,
            deadline=data.deadline,
            assigned_robot=assigned_robot,
        )
        return task

    @strawberry.mutation
    def ingest_telemetry(
        self,
        info,
        robot_id: strawberry.ID,
        metric_name: str,
        metric_value: float,
        timestamp: datetime | None = None,
        metadata: JSON | None = None,
    ) -> TelemetryPointType:
        robot = Robot.objects.get(pk=robot_id)
        ts = timestamp or timezone.now()
        point = TelemetryPoint.objects.create(
            robot=robot,
            metric_name=metric_name,
            metric_value=metric_value,
            timestamp=ts,
            metadata=metadata or {},
        )
        return point


schema = strawberry.Schema(query=Query, mutation=Mutation)


