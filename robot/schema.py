"""
Strawberry GraphQL Schema for Robot Fleet Management API

================================================================================
STRAWBERRY GRAPHQL OVERVIEW
================================================================================

Strawberry GraphQL is a Python library that allows you to create GraphQL APIs
using Python type hints and decorators. It automatically generates GraphQL
schemas from your Python classes and functions.

KEY CONCEPTS:
-------------

1. TYPES (@strawberry.type):
   - Define the structure of data that can be returned from queries
   - Similar to Python dataclasses, but for GraphQL
   - Each field becomes a queryable property in GraphQL

2. INPUT TYPES (@strawberry.input):
   - Define the structure of data that can be sent to mutations
   - Used for creating/updating resources
   - Cannot have relationships (only scalar values)

3. QUERIES (@strawberry.field):
   - Read operations - fetch data without modifying it
   - Defined as methods in a Query class decorated with @strawberry.type
   - Each method becomes a queryable field in GraphQL

4. MUTATIONS (@strawberry.mutation):
   - Write operations - create, update, or delete data
   - Defined as methods in a Mutation class decorated with @strawberry.type
   - Each method becomes a mutation in GraphQL

5. DJANGO INTEGRATION (@django_type):
   - Automatically maps Django models to GraphQL types
   - Handles field resolution from Django ORM
   - Uses 'auto' to automatically expose model fields

6. SCHEMA:
   - Combines all queries and mutations into a single GraphQL schema
   - Exposed via HTTP endpoint (configured in urls.py)

HOW IT WORKS:
-------------
1. Client sends a GraphQL query/mutation as JSON
2. Strawberry parses the request and calls the appropriate resolver function
3. Resolver function queries Django ORM and returns data
4. Strawberry serializes the response back to JSON
5. Client receives the requested data

EXAMPLE QUERY:
--------------
{
  robots {
    id
    serial
    model
    status
  }
}

This query calls the 'robots' method in the Query class, which returns
a list of RobotType objects. GraphQL automatically serializes only the
requested fields (id, serial, model, status).
"""

import typing as t
from datetime import datetime, timedelta
from decimal import Decimal
from functools import reduce

import strawberry
from django.db.models import Avg, Count, Max, Min, Q, Sum
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


# ============================================================================
# GRAPHQL OUTPUT TYPES (Object Types)
# ============================================================================
# These types define the structure of data returned from queries.
# They use @django_type decorator to automatically map Django model fields
# to GraphQL fields.

@django_type(Robot)
class RobotType:
    """
    GraphQL type representing a Robot.
    
    @django_type(Robot) decorator:
    - Automatically maps the Django Robot model to a GraphQL type
    - Exposes all model fields as GraphQL fields
    - Handles relationships and field resolution automatically
    
    'auto' keyword:
    - Tells Strawberry to automatically expose the Django model field
    - Works for simple fields (id, created_at, updated_at)
    - For relationships, you can explicitly define the type (e.g., robot: RobotType)
    
    This type can be used in queries like:
    {
      robots {
        id
        serial
        model
        capabilities
        status
      }
    }
    """
    id: auto  # Automatically maps to Robot.id (primary key)
    serial: str  # Robot serial number
    model: str  # Robot model name
    capabilities: list[str]  # List of robot capabilities (e.g., ["welding", "pick-place"])
    status: str  # Current status (IDLE, ACTIVE, OFFLINE, etc.)
    location: str | None  # Optional location string
    last_seen: datetime | None  # Optional timestamp of last communication
    created_at: auto  # Automatically maps to Robot.created_at
    updated_at: auto  # Automatically maps to Robot.updated_at


@django_type(TelemetryPoint)
class TelemetryPointType:
    """
    GraphQL type representing a telemetry data point.
    
    This type includes a relationship to RobotType, which GraphQL will
    automatically resolve when queried. For example:
    {
      telemetryPoints {
        id
        metricName
        metricValue
        robot {
          id
          serial
          model
        }
      }
    }
    """
    id: auto
    robot: RobotType  # Foreign key relationship - GraphQL will resolve this automatically
    timestamp: datetime  # When the telemetry was recorded
    metric_name: str  # Name of the metric (e.g., "temperature", "vibration")
    metric_value: float  # The actual metric value
    metadata: JSON | None  # Optional JSON metadata (sensor info, flags, etc.)


@django_type(Task)
class TaskType:
    """
    GraphQL type representing a production task.
    
    Tasks can be assigned to robots, and this relationship is exposed
    as an optional RobotType field.
    """
    id: auto
    required_capabilities: list[str]  # Capabilities needed to complete this task
    status: str  # Task status (PENDING, ASSIGNED, RUNNING, COMPLETED, etc.)
    assigned_robot: RobotType | None  # Optional robot assigned to this task
    priority: int  # Task priority (higher = more important)
    deadline: datetime | None  # Optional deadline for task completion
    created_at: datetime  # When the task was created


@django_type(MaintenanceEvent)
class MaintenanceEventType:
    """
    GraphQL type representing a maintenance event.
    
    Tracks maintenance performed on robots, including type, cost, and notes.
    """
    id: auto
    robot: RobotType  # Robot that was maintained
    timestamp: datetime  # When maintenance occurred
    type: str  # Type of maintenance (PREVENTIVE, CORRECTIVE, INSPECTION, etc.)
    notes: str  # Maintenance notes/description
    cost: Decimal | None  # Optional cost of maintenance


@django_type(Prediction)
class PredictionType:
    """
    GraphQL type representing a predictive maintenance prediction.
    
    Stores ML model predictions like anomaly scores or remaining useful life (RUL).
    """
    id: auto
    robot: RobotType  # Robot the prediction is for
    timestamp: datetime  # When the prediction was made
    prediction_type: str  # Type of prediction (ANOMALY_SCORE, RUL, etc.)
    value: float  # The prediction value
    model_version: str  # Version of the ML model that made the prediction


# ============================================================================
# CUSTOM GRAPHQL TYPES (Not directly mapped from Django models)
# ============================================================================
# These types are created specifically for GraphQL and don't have direct
# Django model equivalents. They're used for computed/aggregated data.

@strawberry.type
class RobotStatistics:
    """
    Custom GraphQL type for robot statistics.
    
    @strawberry.type (without @django_type):
    - Creates a GraphQL type that doesn't map to a Django model
    - Used for computed/aggregated data
    - Fields must be explicitly defined (no 'auto' keyword)
    
    This type is returned by the robot_statistics query which aggregates
    data from multiple sources.
    """
    total_robots: int  # Total number of robots in the system
    robots_by_status: JSON  # Dictionary mapping status to count
    average_tasks_per_robot: float  # Average number of tasks per robot
    robots_with_maintenance: int  # Number of robots that have maintenance records


@strawberry.type
class TelemetryStatistics:
    """
    Custom GraphQL type for telemetry statistics.
    
    Used to return aggregated statistics about telemetry data,
    such as average, min, max values, and count.
    """
    count: int  # Total number of telemetry points
    average_value: float  # Average metric value
    min_value: float  # Minimum metric value
    max_value: float  # Maximum metric value
    latest_timestamp: datetime | None  # Timestamp of the most recent data point


# ============================================================================
# INPUT TYPES (For Mutations)
# ============================================================================
# Input types define the structure of data sent TO the API (for creating/updating).
# They use @strawberry.input decorator and cannot have relationships.

@strawberry.input
class CreateRobotInput:
    """
    Input type for creating a new robot.
    
    @strawberry.input decorator:
    - Defines the structure of data that can be sent in mutations
    - Similar to @strawberry.type but specifically for input
    - Cannot have relationships (only scalar values and lists)
    - Used as parameters in mutation methods
    
    Example mutation usage:
    mutation {
      createRobot(data: {
        serial: "RBT-001"
        model: "WeldingBot-3000"
        capabilities: ["welding"]
        location: "Factory Floor A"
      }) {
        id
        serial
      }
    }
    """
    serial: str  # Required: robot serial number (must be unique)
    model: str  # Required: robot model name
    capabilities: list[str] | None = None  # Optional: list of capabilities
    location: str | None = None  # Optional: robot location
    status: str | None = None  # Optional: initial status (defaults to "IDLE")
    firmware_version: str | None = None  # Optional: firmware version


@strawberry.input
class UpdateRobotInput:
    """
    Input type for updating an existing robot.
    
    All fields are optional except 'id', allowing partial updates.
    Only provided fields will be updated.
    """
    id: strawberry.ID  # Required: ID of robot to update
    serial: str | None = None  # Optional: new serial number
    model: str | None = None  # Optional: new model
    capabilities: list[str] | None = None  # Optional: new capabilities
    location: str | None = None  # Optional: new location
    status: str | None = None  # Optional: new status
    firmware_version: str | None = None  # Optional: new firmware version
    last_seen: datetime | None = None  # Optional: update last seen timestamp


@strawberry.input
class CreateTaskInput:
    """
    Input type for creating a new task.
    
    Tasks require capabilities and can optionally be assigned to a robot.
    """
    required_capabilities: list[str]  # Required: capabilities needed for this task
    priority: int = 0  # Optional: task priority (defaults to 0)
    deadline: datetime | None = None  # Optional: task deadline
    assigned_robot_id: strawberry.ID | None = None  # Optional: ID of assigned robot
    status: str | None = None  # Optional: initial status (defaults to "PENDING")


@strawberry.input
class UpdateTaskInput:
    """Input type for updating an existing task."""
    id: strawberry.ID
    required_capabilities: list[str] | None = None
    priority: int | None = None
    deadline: datetime | None = None
    assigned_robot_id: strawberry.ID | None = None
    status: str | None = None


@strawberry.input
class CreateTelemetryInput:
    """
    Input type for creating a telemetry data point.
    
    Used by robots to send sensor data to the API.
    """
    robot_id: strawberry.ID  # Required: ID of robot sending telemetry
    metric_name: str  # Required: name of the metric (e.g., "temperature")
    metric_value: float  # Required: the metric value
    timestamp: datetime | None = None  # Optional: timestamp (defaults to now)
    metadata: JSON | None = None  # Optional: additional metadata as JSON


@strawberry.input
class UpdateTelemetryInput:
    """Input type for updating an existing telemetry point."""
    id: strawberry.ID
    metric_name: str | None = None
    metric_value: float | None = None
    timestamp: datetime | None = None
    metadata: JSON | None = None


@strawberry.input
class CreateMaintenanceEventInput:
    """Input type for creating a maintenance event."""
    robot_id: strawberry.ID
    type: str  # Type of maintenance (PREVENTIVE, CORRECTIVE, etc.)
    notes: str | None = None
    cost: Decimal | None = None
    timestamp: datetime | None = None


@strawberry.input
class UpdateMaintenanceEventInput:
    """Input type for updating an existing maintenance event."""
    id: strawberry.ID
    type: str | None = None
    notes: str | None = None
    cost: Decimal | None = None
    timestamp: datetime | None = None


@strawberry.input
class CreatePredictionInput:
    """Input type for creating a predictive maintenance prediction."""
    robot_id: strawberry.ID
    prediction_type: str  # Type of prediction (ANOMALY_SCORE, RUL, etc.)
    value: float  # The prediction value
    model_version: str  # Version of the ML model
    timestamp: datetime | None = None


@strawberry.input
class UpdatePredictionInput:
    """Input type for updating an existing prediction."""
    id: strawberry.ID
    prediction_type: str | None = None
    value: float | None = None
    model_version: str | None = None
    timestamp: datetime | None = None


# ============================================================================
# QUERIES (Read Operations)
# ============================================================================
# Queries are read-only operations that fetch data without modifying it.
# All query methods are defined in a class decorated with @strawberry.type.

@strawberry.type
class Query:
    """
    GraphQL Query type - defines all read operations.
    
    @strawberry.type decorator on Query class:
    - Marks this class as the root Query type in GraphQL
    - All methods decorated with @strawberry.field become queryable fields
    - This is the entry point for all GraphQL queries
    
    @strawberry.field decorator:
    - Marks a method as a queryable field in GraphQL
    - Method parameters become GraphQL query arguments
    - Return type determines the GraphQL return type
    - The 'info' parameter contains request context (user, request, etc.)
    
    Example query:
    {
      robots(status: "ACTIVE") {
        id
        serial
        model
      }
    }
    
    This calls the 'robots' method with status="ACTIVE" and returns
    only the requested fields (id, serial, model).
    """
    
    # ========== Robot Queries ==========
    
    @strawberry.field
    def robots(
        self,
        info,
        model: str | None = None,
        status: str | None = None,
        location: str | None = None,
        serial: str | None = None,
    ) -> list[RobotType]:
        """
        Get all robots with optional filtering.
        
        Parameters:
        - info: GraphQL context (contains request, user, etc.)
        - model: Optional filter by model name (case-insensitive partial match)
        - status: Optional filter by status (exact match)
        - location: Optional filter by location (case-insensitive partial match)
        - serial: Optional filter by serial number (case-insensitive partial match)
        
        Returns: List of RobotType objects matching the filters
        
        GraphQL query example:
        {
          robots(status: "ACTIVE", model: "Welding") {
            id
            serial
            model
            status
          }
        }
        """
        qs = Robot.objects.all()  # Start with all robots
        
        # Apply filters if provided (Django ORM filtering)
        if model:
            qs = qs.filter(model__icontains=model)  # Case-insensitive contains
        if status:
            qs = qs.filter(status=status)  # Exact match
        if location:
            qs = qs.filter(location__icontains=location)
        if serial:
            qs = qs.filter(serial__icontains=serial)
        
        return list(qs)  # Convert QuerySet to list for GraphQL
    
    @strawberry.field
    def robot(self, info, id: strawberry.ID) -> RobotType | None:
        """
        Get a single robot by ID.
        
        strawberry.ID:
        - Special type for GraphQL ID scalars
        - Automatically converts between string and integer IDs
        - Used for primary keys and foreign keys
        
        Returns None if robot doesn't exist (GraphQL handles null gracefully).
        """
        try:
            return Robot.objects.get(pk=id)
        except Robot.DoesNotExist:
            return None
    
    @strawberry.field
    def robot_by_serial(self, info, serial: str) -> RobotType | None:
        """Get a robot by serial number (alternative lookup method)."""
        try:
            return Robot.objects.get(serial=serial)
        except Robot.DoesNotExist:
            return None

@django_type(Robot)
class RobotType:
    id: auto
    serial: str
    model: str
    capabilities: list[str]
    status: str
    location: str | None
    last_seen: datetime | None
    created_at: auto
    updated_at: auto


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
    cost: Decimal | None


@django_type(Prediction)
class PredictionType:
    id: auto
    robot: RobotType
    timestamp: datetime
    prediction_type: str
    value: float
    model_version: str


# ==================== STATISTICS TYPES ====================

@strawberry.type
class RobotStatistics:
    total_robots: int
    robots_by_status: JSON
    average_tasks_per_robot: float
    robots_with_maintenance: int


@strawberry.type
class TelemetryStatistics:
    count: int
    average_value: float
    min_value: float
    max_value: float
    latest_timestamp: datetime | None


# ==================== INPUT TYPES ====================

@strawberry.input
class CreateRobotInput:
    serial: str
    model: str
    capabilities: list[str] | None = None
    location: str | None = None
    status: str | None = None
    firmware_version: str | None = None


@strawberry.input
class UpdateRobotInput:
    id: strawberry.ID
    serial: str | None = None
    model: str | None = None
    capabilities: list[str] | None = None
    location: str | None = None
    status: str | None = None
    firmware_version: str | None = None
    last_seen: datetime | None = None


@strawberry.input
class CreateTaskInput:
    required_capabilities: list[str]
    priority: int = 0
    deadline: datetime | None = None
    assigned_robot_id: strawberry.ID | None = None
    status: str | None = None


@strawberry.input
class UpdateTaskInput:
    id: strawberry.ID
    required_capabilities: list[str] | None = None
    priority: int | None = None
    deadline: datetime | None = None
    assigned_robot_id: strawberry.ID | None = None
    status: str | None = None


@strawberry.input
class CreateTelemetryInput:
    robot_id: strawberry.ID
    metric_name: str
    metric_value: float
    timestamp: datetime | None = None
    metadata: JSON | None = None


@strawberry.input
class UpdateTelemetryInput:
    id: strawberry.ID
    metric_name: str | None = None
    metric_value: float | None = None
    timestamp: datetime | None = None
    metadata: JSON | None = None


@strawberry.input
class CreateMaintenanceEventInput:
    robot_id: strawberry.ID
    type: str
    notes: str | None = None
    cost: Decimal | None = None
    timestamp: datetime | None = None


@strawberry.input
class UpdateMaintenanceEventInput:
    id: strawberry.ID
    type: str | None = None
    notes: str | None = None
    cost: Decimal | None = None
    timestamp: datetime | None = None


@strawberry.input
class CreatePredictionInput:
    robot_id: strawberry.ID
    prediction_type: str
    value: float
    model_version: str
    timestamp: datetime | None = None


@strawberry.input
class UpdatePredictionInput:
    id: strawberry.ID
    prediction_type: str | None = None
    value: float | None = None
    model_version: str | None = None
    timestamp: datetime | None = None


# ==================== QUERIES ====================

@strawberry.type
class Query:
    # ========== Robot Queries ==========
    
    @strawberry.field
    def robots(
        self,
        info,
        model: str | None = None,
        status: str | None = None,
        location: str | None = None,
        serial: str | None = None,
    ) -> list[RobotType]:
        """Get all robots with optional filtering"""
        qs = Robot.objects.all()
        
        if model:
            qs = qs.filter(model__icontains=model)
        if status:
            qs = qs.filter(status=status)
        if location:
            qs = qs.filter(location__icontains=location)
        if serial:
            qs = qs.filter(serial__icontains=serial)
        
        return list(qs)
    
    @strawberry.field
    def robot(self, info, id: strawberry.ID) -> RobotType | None:
        """Get a single robot by ID"""
        try:
            return Robot.objects.get(pk=id)
        except Robot.DoesNotExist:
            return None
    
    @strawberry.field
    def robot_by_serial(self, info, serial: str) -> RobotType | None:
        """Get a robot by serial number"""
        try:
            return Robot.objects.get(serial=serial)
        except Robot.DoesNotExist:
            return None
    
    # ========== Task Queries ==========
    
    @strawberry.field
    def tasks(
        self,
        info,
        status: str | None = None,
        priority_min: int | None = None,
        priority_max: int | None = None,
        robot_id: strawberry.ID | None = None,
        has_deadline: bool | None = None,
    ) -> list[TaskType]:
        """
        Get all tasks with optional filtering.
        
        Demonstrates range filtering (priority_min/priority_max) and
        boolean filtering (has_deadline).
        
        Note: We check 'is not None' for numeric/boolean filters to
        distinguish between "not provided" and "provided as 0/False".
        """
        qs = Task.objects.all()
        
        if status:
            qs = qs.filter(status=status)
        if priority_min is not None:  # Allows filtering by priority >= min
            qs = qs.filter(priority__gte=priority_min)
        if priority_max is not None:  # Allows filtering by priority <= max
            qs = qs.filter(priority__lte=priority_max)
        if robot_id:
            qs = qs.filter(assigned_robot_id=robot_id)
        if has_deadline is not None:
            if has_deadline:
                qs = qs.exclude(deadline__isnull=True)  # Has deadline
            else:
                qs = qs.filter(deadline__isnull=True)  # No deadline
        
        return list(qs)
    
    @strawberry.field
    def task(self, info, id: strawberry.ID) -> TaskType | None:
        """Get a single task by ID"""
        try:
            return Task.objects.get(pk=id)
        except Task.DoesNotExist:
            return None
    
    # ========== Telemetry Queries ==========
    
    @strawberry.field
    def telemetry_points(
        self,
        info,
        robot_id: strawberry.ID | None = None,
        metric_name: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int | None = 100,
    ) -> list[TelemetryPointType]:
        """Get telemetry points with optional filtering"""
        qs = TelemetryPoint.objects.all()
        
        if robot_id:
            qs = qs.filter(robot_id=robot_id)
        if metric_name:
            qs = qs.filter(metric_name=metric_name)
        if start_date:
            qs = qs.filter(timestamp__gte=start_date)
        if end_date:
            qs = qs.filter(timestamp__lte=end_date)
        
        qs = qs.order_by("-timestamp")
        
        if limit:
            qs = qs[:limit]
        
        return list(qs)
    
    @strawberry.field
    def telemetry_point(self, info, id: strawberry.ID) -> TelemetryPointType | None:
        """Get a single telemetry point by ID"""
        try:
            return TelemetryPoint.objects.get(pk=id)
        except TelemetryPoint.DoesNotExist:
            return None
    
    @strawberry.field
    def telemetry_statistics(
        self,
        info,
        robot_id: strawberry.ID | None = None,
        metric_name: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> TelemetryStatistics | None:
        """
        Get statistics for telemetry data using Django aggregation.
        
        Demonstrates:
        - Using Django ORM aggregate() for computed values
        - Returning custom types (TelemetryStatistics) instead of models
        - Handling empty result sets (returns None)
        
        Django aggregation functions:
        - Count(): Count of records
        - Avg(): Average value
        - Min()/Max(): Minimum/maximum values
        - Sum(): Sum of values (not used here)
        """
        qs = TelemetryPoint.objects.all()
        
        if robot_id:
            qs = qs.filter(robot_id=robot_id)
        if metric_name:
            qs = qs.filter(metric_name=metric_name)
        if start_date:
            qs = qs.filter(timestamp__gte=start_date)
        if end_date:
            qs = qs.filter(timestamp__lte=end_date)
        
        if not qs.exists():
            return None  # No data to aggregate
        
        # Aggregate computes statistics in the database (efficient)
        stats = qs.aggregate(
            count=Count("id"),  # Total count
            avg=Avg("metric_value"),  # Average value
            min=Min("metric_value"),  # Minimum value
            max=Max("metric_value"),  # Maximum value
            latest=Max("timestamp"),  # Most recent timestamp
        )
        
        # Create and return custom type (not a Django model)
        return TelemetryStatistics(
            count=stats["count"],
            average_value=float(stats["avg"] or 0),
            min_value=float(stats["min"] or 0),
            max_value=float(stats["max"] or 0),
            latest_timestamp=stats["latest"],
        )
    
    # ========== Maintenance Event Queries ==========
    
    @strawberry.field
    def maintenance_events(
        self,
        info,
        robot_id: strawberry.ID | None = None,
        type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[MaintenanceEventType]:
        """Get maintenance events with optional filtering"""
        qs = MaintenanceEvent.objects.all()
        
        if robot_id:
            qs = qs.filter(robot_id=robot_id)
        if type:
            qs = qs.filter(type=type)
        if start_date:
            qs = qs.filter(timestamp__gte=start_date)
        if end_date:
            qs = qs.filter(timestamp__lte=end_date)
        
        return list(qs.order_by("-timestamp"))
    
    @strawberry.field
    def maintenance_event(self, info, id: strawberry.ID) -> MaintenanceEventType | None:
        """Get a single maintenance event by ID"""
        try:
            return MaintenanceEvent.objects.get(pk=id)
        except MaintenanceEvent.DoesNotExist:
            return None
    
    # ========== Prediction Queries ==========
    
    @strawberry.field
    def predictions(
        self,
        info,
        robot_id: strawberry.ID | None = None,
        prediction_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[PredictionType]:
        """Get predictions with optional filtering"""
        qs = Prediction.objects.all()
        
        if robot_id:
            qs = qs.filter(robot_id=robot_id)
        if prediction_type:
            qs = qs.filter(prediction_type=prediction_type)
        if start_date:
            qs = qs.filter(timestamp__gte=start_date)
        if end_date:
            qs = qs.filter(timestamp__lte=end_date)
        
        return list(qs.order_by("-timestamp"))
    
    @strawberry.field
    def prediction(self, info, id: strawberry.ID) -> PredictionType | None:
        """Get a single prediction by ID"""
        try:
            return Prediction.objects.get(pk=id)
        except Prediction.DoesNotExist:
            return None
    
    # ========== Complex Queries ==========
    
    @strawberry.field
    def robot_with_details(self, info, id: strawberry.ID) -> RobotType | None:
        """
        Get robot with all related data using prefetch_related.
        
        prefetch_related():
        - Optimizes database queries by fetching related objects in advance
        - Prevents N+1 query problem (one query per related object)
        - When GraphQL requests related data, it's already loaded
        
        Example: If query requests robot.tasks, robot.telemetry, etc.,
        all are fetched in optimized queries instead of one per relationship.
        """
        try:
            return Robot.objects.prefetch_related(
                "assigned_tasks",  # Prefetch all tasks assigned to this robot
                "telemetry_points",  # Prefetch all telemetry for this robot
                "maintenance_events",  # Prefetch all maintenance events
                "predictions",  # Prefetch all predictions
            ).get(pk=id)
        except Robot.DoesNotExist:
            return None
    
    @strawberry.field
    def robots_by_capability(self, info, capability: str) -> list[RobotType]:
        """
        Get robots that have a specific capability.
        
        Demonstrates JSON field querying:
        - capabilities is a JSONField in Django
        - capabilities__contains checks if the list contains the value
        - Useful for filtering on array/list fields stored as JSON
        """
        return list(Robot.objects.filter(capabilities__contains=[capability]))
    
    @strawberry.field
    def high_priority_tasks(self, info, min_priority: int = 5) -> list[TaskType]:
        """
        Get tasks with priority >= min_priority.
        
        Demonstrates:
        - Default parameter values in GraphQL queries
        - Ordering results (order_by("-priority") = descending)
        """
        return list(Task.objects.filter(priority__gte=min_priority).order_by("-priority"))
    
    @strawberry.field
    def overdue_tasks(self, info) -> list[TaskType]:
        """
        Get tasks that are past their deadline and not completed.
        
        Demonstrates:
        - Date/time comparisons (deadline__lt=now)
        - Filtering by multiple status values (status__in)
        - Complex business logic in queries
        """
        now = timezone.now()
        return list(
            Task.objects.filter(
                deadline__lt=now,  # Deadline is in the past
                status__in=["PENDING", "ASSIGNED", "RUNNING"],  # Not completed
            ).order_by("deadline")  # Order by deadline (earliest first)
        )
    
    @strawberry.field
    def robot_statistics(self, info) -> RobotStatistics:
        """
        Get overall robot statistics.
        
        Demonstrates:
        - Complex aggregations and annotations
        - Accessing Django model metadata (choices)
        - Returning custom computed types
        - Multiple database queries combined into one response
        
        Django annotations:
        - annotate() adds computed fields to each object in a queryset
        - Here we count tasks per robot, then aggregate those counts
        """
        total = Robot.objects.count()
        
        # Count by status - iterate through all possible status choices
        status_counts = {}
        for status, _ in Robot._meta.get_field("status").choices:
            status_counts[status] = Robot.objects.filter(status=status).count()
        
        # Average tasks per robot using annotation
        # First, annotate each robot with its task count
        robots_with_tasks = Robot.objects.annotate(
            task_count=Count("assigned_tasks")  # Add task_count field to each robot
        ).filter(task_count__gt=0)  # Only robots with tasks
        
        if robots_with_tasks.exists():
            # Then aggregate to get the average
            avg_tasks = robots_with_tasks.aggregate(avg=Avg("task_count"))["avg"] or 0
        else:
            avg_tasks = 0.0
        
        # Robots with maintenance (using reverse relationship)
        robots_with_maintenance = Robot.objects.filter(
            maintenance_events__isnull=False  # Has at least one maintenance event
        ).distinct().count()  # Count distinct robots (avoid duplicates)
        
        return RobotStatistics(
            total_robots=total,
            robots_by_status=status_counts,
            average_tasks_per_robot=float(avg_tasks),
            robots_with_maintenance=robots_with_maintenance,
        )
    
    @strawberry.field
    def search_robots(
        self,
        info,
        search_term: str,
    ) -> list[RobotType]:
        """
        Search robots by serial, model, or location.
        
        Demonstrates:
        - Using Django Q objects for complex OR queries
        - Case-insensitive search across multiple fields
        - Q(condition1) | Q(condition2) = OR logic
        - Q(condition1) & Q(condition2) = AND logic
        """
        return list(
            Robot.objects.filter(
                Q(serial__icontains=search_term)  # Search in serial
                | Q(model__icontains=search_term)  # OR search in model
                | Q(location__icontains=search_term)  # OR search in location
            )
        )
    
    # ========== Lambda Expression Examples ==========
    # 
    # LAMBDA EXPRESSIONS IN PYTHON - QUICK REFERENCE:
    # ------------------------------------------------
    # Lambda expressions are anonymous (unnamed) functions in Python.
    # 
    # Syntax: lambda arguments: expression
    # 
    # Common use cases with built-in functions:
    # 1. filter(lambda x: condition, iterable) - Filter elements matching condition
    # 2. map(lambda x: transform(x), iterable) - Transform each element
    # 3. sorted(iterable, key=lambda x: sort_key) - Sort by computed key
    # 4. reduce(lambda acc, x: operation, iterable, initial) - Aggregate values
    # 5. List comprehensions: [lambda x: f(x) for x in iterable]
    # 
    # When to use lambda:
    # - Short, simple functions used once
    # - As arguments to higher-order functions (filter, map, sorted, etc.)
    # - For inline transformations and filtering
    # 
    # When NOT to use lambda:
    # - Complex logic (use regular functions instead)
    # - Functions used multiple times (define once, reuse)
    # - When readability suffers (lambda can be less clear)
    # 
    # In GraphQL/Django context:
    # - Use for post-processing data after database queries
    # - For complex filtering that's hard to express in Django ORM
    # - For computed values and transformations
    # - Note: Database queries (Django ORM) are usually more efficient than
    #   Python-side filtering with lambda for large datasets
    
    @strawberry.field
    def robots_with_high_telemetry_count(
        self,
        info,
        min_telemetry_points: int = 10,
    ) -> list[RobotType]:
        """
        Get robots that have at least N telemetry points using lambda expressions.
        
        LAMBDA EXPRESSIONS IN PYTHON:
        -----------------------------
        Lambda expressions are anonymous functions defined with the 'lambda' keyword.
        Syntax: lambda arguments: expression
        
        This example demonstrates:
        1. Fetching robots with their telemetry counts (using annotate)
        2. Converting QuerySet to list
        3. Using filter() with lambda to filter Python list in memory
        4. Lambda: lambda r: r.telemetry_count >= min_telemetry_points
        
        Why use lambda here?
        - Sometimes complex filtering logic is easier to express in Python
        - Can combine multiple conditions that are hard to express in Django ORM
        - Useful for post-processing data after database query
        
        Note: For large datasets, prefer Django ORM filtering (more efficient).
        Lambda filtering is done in Python memory, not in the database.
        """
        # First, get robots with annotated telemetry count (database query)
        robots = list(
            Robot.objects.annotate(
                telemetry_count=Count("telemetry_points")
            )
        )
        
        # Use lambda with filter() to filter in Python memory
        # lambda r: r.telemetry_count >= min_telemetry_points
        # This creates an anonymous function that checks if telemetry_count >= min
        filtered_robots = list(
            filter(
                lambda r: r.telemetry_count >= min_telemetry_points,
                robots
            )
        )
        
        return filtered_robots
    
    @strawberry.field
    def robots_sorted_by_capability_count(
        self,
        info,
        reverse: bool = False,
    ) -> list[RobotType]:
        """
        Get all robots sorted by number of capabilities using lambda.
        
        Demonstrates:
        - Using lambda with sorted() for custom sorting
        - Sorting by computed property (length of capabilities list)
        - Lambda: lambda r: len(r.capabilities)
        
        sorted() with lambda:
        - sorted(iterable, key=lambda x: expression, reverse=bool)
        - 'key' function determines the value to sort by
        - Lambda extracts the sorting key from each element
        """
        robots = list(Robot.objects.all())
        
        # Sort using lambda to extract sorting key
        # lambda r: len(r.capabilities) - returns number of capabilities for each robot
        sorted_robots = sorted(
            robots,
            key=lambda r: len(r.capabilities),  # Sort by capability count
            reverse=reverse  # True = descending, False = ascending
        )
        
        return sorted_robots
    
    @strawberry.field
    def robots_with_recent_activity(
        self,
        info,
        hours: int = 24,
    ) -> list[RobotType]:
        """
        Get robots that have been active in the last N hours using lambda.
        
        Demonstrates:
        - Combining Django ORM filtering with Python lambda filtering
        - Using lambda with filter() for complex time-based logic
        - Lambda with conditional expressions
        """
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        # Get robots with recent telemetry or tasks
        robots = list(
            Robot.objects.prefetch_related("telemetry_points", "assigned_tasks")
        )
        
        # Use lambda to filter robots with recent activity
        # Lambda checks if robot has telemetry or tasks in the time window
        active_robots = list(
            filter(
                lambda r: (
                    # Has recent telemetry (last telemetry point within time window)
                    any(
                        tp.timestamp >= cutoff_time
                        for tp in r.telemetry_points.all()[:1]  # Check most recent
                    )
                    or
                    # Has recent tasks (task created within time window)
                    any(
                        task.created_at >= cutoff_time
                        for task in r.assigned_tasks.all()[:1]  # Check most recent
                    )
                    or
                    # Was seen recently
                    (r.last_seen and r.last_seen >= cutoff_time)
                ),
                robots
            )
        )
        
        return active_robots
    
    @strawberry.field
    def telemetry_anomalies(
        self,
        info,
        robot_id: strawberry.ID | None = None,
        metric_name: str = "temperature",
        threshold_multiplier: float = 2.0,
    ) -> list[TelemetryPointType]:
        """
        Find telemetry points that are anomalies (outliers) using lambda.
        
        Demonstrates:
        - Using lambda with map() to transform data
        - Using lambda with filter() for complex conditions
        - Statistical anomaly detection in Python
        
        Lambda with map():
        - map(lambda x: expression, iterable) - applies function to each element
        - Here we use it to extract metric values
        
        Algorithm:
        1. Get all telemetry points for the metric
        2. Calculate average value using lambda and reduce()
        3. Filter points that deviate significantly from average
        """
        qs = TelemetryPoint.objects.filter(metric_name=metric_name)
        
        if robot_id:
            qs = qs.filter(robot_id=robot_id)
        
        points = list(qs)
        
        if not points:
            return []
        
        # Use lambda with map() to extract metric values
        # lambda p: p.metric_value - extracts the value from each point
        values = list(map(lambda p: p.metric_value, points))
        
        # Calculate average using reduce() with lambda
        # reduce(lambda acc, x: acc + x, values, 0) - sums all values
        # Then divide by count to get average
        total = reduce(lambda acc, x: acc + x, values, 0)
        average = total / len(values) if values else 0
        
        # Calculate threshold (points beyond this are anomalies)
        threshold = average * threshold_multiplier
        
        # Use lambda with filter() to find anomalies
        # Lambda checks if value deviates significantly from average
        anomalies = list(
            filter(
                lambda p: abs(p.metric_value - average) > threshold,
                points
            )
        )
        
        return anomalies
    
    @strawberry.field
    def tasks_by_urgency_score(
        self,
        info,
        min_score: float = 0.5,
    ) -> list[TaskType]:
        """
        Get tasks sorted by urgency score (computed using lambda).
        
        Demonstrates:
        - Using lambda to compute a score for each task
        - Sorting by computed value
        - Complex business logic in Python
        
        Urgency score formula:
        - Higher priority = higher score
        - Closer deadline = higher score
        - Combines both factors using lambda
        """
        now = timezone.now()
        tasks = list(Task.objects.all())
        
        # Define urgency calculation as a lambda function
        # This lambda takes a task and returns an urgency score
        calculate_urgency = lambda t: (
            # Priority component (normalized to 0-1, assuming max priority is 10)
            min(1.0, t.priority / 10.0) * 0.6
            +
            # Deadline component (closer deadline = higher score)
            (
                # Hours until deadline (inverse relationship: fewer hours = higher score)
                max(0.0, min(0.4, 0.4 / max(1, (t.deadline - now).total_seconds() / 3600)))
                if t.deadline and t.deadline > now
                else 0.0  # Past deadline gets 0 for deadline component
            )
        )
        
        # Filter tasks with minimum urgency score using lambda
        urgent_tasks = list(
            filter(
                lambda t: calculate_urgency(t) >= min_score,
                tasks
            )
        )
        
        # Sort by urgency score (descending) using lambda
        sorted_tasks = sorted(
            urgent_tasks,
            key=lambda t: calculate_urgency(t),  # Sort by computed urgency
            reverse=True  # Highest urgency first
        )
        
        return sorted_tasks


# ============================================================================
# MUTATIONS (Write Operations)
# ============================================================================
# Mutations are write operations that create, update, or delete data.
# All mutation methods are defined in a class decorated with @strawberry.type.

@strawberry.type
class Mutation:
    """
    GraphQL Mutation type - defines all write operations.
    
    @strawberry.type decorator on Mutation class:
    - Marks this class as the root Mutation type in GraphQL
    - All methods decorated with @strawberry.mutation become mutations
    - This is the entry point for all GraphQL mutations
    
    @strawberry.mutation decorator:
    - Marks a method as a mutation in GraphQL
    - Mutations can modify data (create, update, delete)
    - Method parameters become mutation arguments
    - Return type determines what data is returned after mutation
    
    Example mutation:
    mutation {
      createRobot(data: {
        serial: "RBT-001"
        model: "WeldingBot"
        capabilities: ["welding"]
      }) {
        id
        serial
        model
      }
    }
    
    This calls create_robot() with the input data, creates the robot,
    and returns the specified fields.
    """
    
    # ========== Robot Mutations ==========
    
    @strawberry.mutation
    def create_robot(self, info, data: CreateRobotInput) -> RobotType:
        """
        Create a new robot.
        
        Mutations typically:
        1. Accept input data (CreateRobotInput)
        2. Create/update/delete using Django ORM
        3. Return the created/updated object (or boolean for deletes)
        
        The 'info' parameter contains:
        - request: HTTP request object
        - context: Custom context data
        - user: Authenticated user (if authentication is enabled)
        
        Django objects.create():
        - Creates and saves a new database record in one operation
        - Returns the created object
        """
        robot = Robot.objects.create(
            serial=data.serial,
            model=data.model,
            capabilities=data.capabilities or [],  # Default to empty list if None
            location=data.location or "",  # Default to empty string if None
            status=data.status or "IDLE",  # Default to "IDLE" if None
            firmware_version=data.firmware_version or "",
        )
        return robot  # Return the created robot (GraphQL will serialize it)
    
    @strawberry.mutation
    def update_robot(self, info, data: UpdateRobotInput) -> RobotType:
        """
        Update an existing robot (partial update).
        
        Demonstrates partial updates:
        - Only provided fields are updated
        - Check 'is not None' to distinguish between "not provided" and "provided as None"
        - This allows clients to update only specific fields
        
        Django save():
        - Saves changes to the database
        - Updates the updated_at timestamp (if auto_now=True)
        """
        robot = Robot.objects.get(pk=data.id)  # Get existing robot
        
        # Update only fields that were provided (not None)
        if data.serial is not None:
            robot.serial = data.serial
        if data.model is not None:
            robot.model = data.model
        if data.capabilities is not None:
            robot.capabilities = data.capabilities
        if data.location is not None:
            robot.location = data.location
        if data.status is not None:
            robot.status = data.status
        if data.firmware_version is not None:
            robot.firmware_version = data.firmware_version
        if data.last_seen is not None:
            robot.last_seen = data.last_seen
        
        robot.save()  # Persist changes to database
        return robot  # Return updated robot
    
    @strawberry.mutation
    def delete_robot(self, info, id: strawberry.ID) -> bool:
        """
        Delete a robot.
        
        Returns boolean to indicate success/failure.
        GraphQL clients can check this to confirm deletion.
        
        Django delete():
        - Removes the record from the database
        - Can raise DoesNotExist if record doesn't exist
        """
        try:
            Robot.objects.get(pk=id).delete()  # Get and delete in one operation
            return True  # Success
        except Robot.DoesNotExist:
            return False  # Robot not found
    
    # ========== Task Mutations ==========
    
    @strawberry.mutation
    def create_task(self, info, data: CreateTaskInput) -> TaskType:
        """Create a new task"""
        assigned_robot = None
        if data.assigned_robot_id is not None:
            assigned_robot = Robot.objects.get(pk=data.assigned_robot_id)
        
        task = Task.objects.create(
            required_capabilities=data.required_capabilities,
            priority=data.priority,
            deadline=data.deadline,
            assigned_robot=assigned_robot,
            status=data.status or "PENDING",
        )
        return task
    
    @strawberry.mutation
    def update_task(self, info, data: UpdateTaskInput) -> TaskType:
        """Update an existing task"""
        task = Task.objects.get(pk=data.id)
        
        if data.required_capabilities is not None:
            task.required_capabilities = data.required_capabilities
        if data.priority is not None:
            task.priority = data.priority
        if data.deadline is not None:
            task.deadline = data.deadline
        if data.assigned_robot_id is not None:
            if data.assigned_robot_id:
                task.assigned_robot = Robot.objects.get(pk=data.assigned_robot_id)
            else:
                task.assigned_robot = None
        if data.status is not None:
            task.status = data.status
        
        task.save()
        return task
    
    @strawberry.mutation
    def delete_task(self, info, id: strawberry.ID) -> bool:
        """Delete a task"""
        try:
            Task.objects.get(pk=id).delete()
            return True
        except Task.DoesNotExist:
            return False
    
    # ========== Telemetry Mutations ==========
    
    @strawberry.mutation
    def create_telemetry(self, info, data: CreateTelemetryInput) -> TelemetryPointType:
        """
        Create a new telemetry point (ingest telemetry data).
        
        This is typically called by robots/edge devices to send sensor data.
        Demonstrates:
        - Resolving foreign key relationships (robot_id -> Robot object)
        - Default timestamp handling (uses current time if not provided)
        - JSON metadata storage
        
        This mutation is called frequently (high throughput), so it should
        be optimized for performance in production.
        """
        robot = Robot.objects.get(pk=data.robot_id)  # Resolve robot from ID
        ts = data.timestamp or timezone.now()  # Use provided timestamp or current time
        
        point = TelemetryPoint.objects.create(
            robot=robot,
            metric_name=data.metric_name,
            metric_value=data.metric_value,
            timestamp=ts,
            metadata=data.metadata or {},  # Default to empty dict if None
        )
        return point
    
    @strawberry.mutation
    def update_telemetry(self, info, data: UpdateTelemetryInput) -> TelemetryPointType:
        """Update an existing telemetry point"""
        point = TelemetryPoint.objects.get(pk=data.id)
        
        if data.metric_name is not None:
            point.metric_name = data.metric_name
        if data.metric_value is not None:
            point.metric_value = data.metric_value
        if data.timestamp is not None:
            point.timestamp = data.timestamp
        if data.metadata is not None:
            point.metadata = data.metadata
        
        point.save()
        return point
    
    @strawberry.mutation
    def delete_telemetry(self, info, id: strawberry.ID) -> bool:
        """Delete a telemetry point"""
        try:
            TelemetryPoint.objects.get(pk=id).delete()
            return True
        except TelemetryPoint.DoesNotExist:
            return False
    
    # ========== Maintenance Event Mutations ==========
    
    @strawberry.mutation
    def create_maintenance_event(
        self, info, data: CreateMaintenanceEventInput
    ) -> MaintenanceEventType:
        """Create a new maintenance event"""
        robot = Robot.objects.get(pk=data.robot_id)
        ts = data.timestamp or timezone.now()
        
        event = MaintenanceEvent.objects.create(
            robot=robot,
            type=data.type,
            notes=data.notes or "",
            cost=data.cost,
            timestamp=ts,
        )
        return event
    
    @strawberry.mutation
    def update_maintenance_event(
        self, info, data: UpdateMaintenanceEventInput
    ) -> MaintenanceEventType:
        """Update an existing maintenance event"""
        event = MaintenanceEvent.objects.get(pk=data.id)
        
        if data.type is not None:
            event.type = data.type
        if data.notes is not None:
            event.notes = data.notes
        if data.cost is not None:
            event.cost = data.cost
        if data.timestamp is not None:
            event.timestamp = data.timestamp
        
        event.save()
        return event
    
    @strawberry.mutation
    def delete_maintenance_event(self, info, id: strawberry.ID) -> bool:
        """Delete a maintenance event"""
        try:
            MaintenanceEvent.objects.get(pk=id).delete()
            return True
        except MaintenanceEvent.DoesNotExist:
            return False
    
    # ========== Prediction Mutations ==========
    
    @strawberry.mutation
    def create_prediction(self, info, data: CreatePredictionInput) -> PredictionType:
        """Create a new prediction"""
        robot = Robot.objects.get(pk=data.robot_id)
        ts = data.timestamp or timezone.now()
        
        prediction = Prediction.objects.create(
            robot=robot,
            prediction_type=data.prediction_type,
            value=data.value,
            model_version=data.model_version,
            timestamp=ts,
        )
        return prediction
    
    @strawberry.mutation
    def update_prediction(self, info, data: UpdatePredictionInput) -> PredictionType:
        """Update an existing prediction"""
        prediction = Prediction.objects.get(pk=data.id)
        
        if data.prediction_type is not None:
            prediction.prediction_type = data.prediction_type
        if data.value is not None:
            prediction.value = data.value
        if data.model_version is not None:
            prediction.model_version = data.model_version
        if data.timestamp is not None:
            prediction.timestamp = data.timestamp
        
        prediction.save()
        return prediction
    
    @strawberry.mutation
    def delete_prediction(self, info, id: strawberry.ID) -> bool:
        """Delete a prediction"""
        try:
            Prediction.objects.get(pk=id).delete()
            return True
        except Prediction.DoesNotExist:
            return False
    
    # ========== Lambda Expression Examples in Mutations ==========
    
    @strawberry.mutation
    def bulk_update_robot_statuses(
        self,
        info,
        robot_ids: list[strawberry.ID],
        new_status: str,
    ) -> list[RobotType]:
        """
        Update status of multiple robots using lambda expressions.
        
        Demonstrates:
        - Using lambda with map() to transform/update multiple objects
        - Batch operations with lambda
        - Functional programming approach to mutations
        
        Lambda with map():
        - map(lambda r: expression, robots) - applies function to each robot
        - Here we update status and save each robot
        - Returns list of updated robots
        """
        # Get all robots at once
        robots = list(Robot.objects.filter(pk__in=robot_ids))
        
        # Use lambda with map() to update each robot's status
        # lambda r: (setattr(r, 'status', new_status), r.save(), r)[2]
        # This lambda:
        # 1. Sets the status attribute
        # 2. Saves the robot
        # 3. Returns the robot object (using tuple indexing [2])
        updated_robots = list(
            map(
                lambda r: (
                    setattr(r, 'status', new_status),  # Update status
                    r.save(),  # Save to database
                    r  # Return robot object
                )[2],  # Return the robot (third element of tuple)
                robots
            )
        )
        
        return updated_robots
    
    @strawberry.mutation
    def create_robots_from_templates(
        self,
        info,
        templates: list[CreateRobotInput],
        location_prefix: str = "Factory",
    ) -> list[RobotType]:
        """
        Create multiple robots from templates using lambda.
        
        Demonstrates:
        - Using lambda with map() to create multiple objects
        - Transforming input data with lambda
        - Batch creation operations
        
        This mutation takes a list of robot templates and creates all of them.
        Lambda is used to transform each template into a Robot object.
        """
        # Use lambda with map() to create robots from templates
        # lambda t: Robot.objects.create(...) - creates a robot for each template
        created_robots = list(
            map(
                lambda t: Robot.objects.create(
                    serial=t.serial,
                    model=t.model,
                    capabilities=t.capabilities or [],
                    location=f"{location_prefix} - {t.location}" if t.location else location_prefix,
                    status=t.status or "IDLE",
                    firmware_version=t.firmware_version or "",
                ),
                templates
            )
        )
        
        return created_robots
    
    @strawberry.mutation
    def assign_tasks_to_robots_by_capability(
        self,
        info,
        task_ids: list[strawberry.ID],
    ) -> list[TaskType]:
        """
        Automatically assign tasks to robots based on capability matching using lambda.
        
        Demonstrates:
        - Complex business logic with lambda expressions
        - Using lambda with filter() to find matching robots
        - Using lambda with map() to update tasks
        - Multi-step algorithm with functional programming
        
        Algorithm:
        1. Get all tasks and available robots
        2. For each task, find robots with matching capabilities (using lambda filter)
        3. Assign task to first available robot (using lambda map)
        4. Return updated tasks
        """
        tasks = list(Task.objects.filter(pk__in=task_ids, status="PENDING"))
        available_robots = list(
            Robot.objects.filter(status__in=["IDLE", "ACTIVE"])
        )
        
        def assign_task(task: Task) -> Task:
            """Helper function to assign a task to a suitable robot."""
            # Use lambda with filter() to find robots with matching capabilities
            # Lambda checks if robot has ALL required capabilities
            matching_robots = list(
                filter(
                    lambda r: all(
                        cap in r.capabilities
                        for cap in task.required_capabilities
                    ),
                    available_robots
                )
            )
            
            if matching_robots:
                # Assign to first available robot
                # Use lambda with min() to find robot with least tasks
                best_robot = min(
                    matching_robots,
                    key=lambda r: r.assigned_tasks.filter(
                        status__in=["PENDING", "ASSIGNED", "RUNNING"]
                    ).count()
                )
                task.assigned_robot = best_robot
                task.status = "ASSIGNED"
                task.save()
            
            return task
        
        # Use lambda with map() to assign all tasks
        # map(lambda t: assign_task(t), tasks) - applies assignment to each task
        assigned_tasks = list(map(lambda t: assign_task(t), tasks))
        
        return assigned_tasks
    
    @strawberry.mutation
    def cleanup_old_telemetry(
        self,
        info,
        days_to_keep: int = 30,
        metric_names: list[str] | None = None,
    ) -> int:
        """
        Delete old telemetry points using lambda for filtering.
        
        Demonstrates:
        - Using lambda with filter() to identify records to delete
        - Bulk delete operations
        - Date-based cleanup logic
        
        Returns: Number of deleted telemetry points
        """
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        qs = TelemetryPoint.objects.filter(timestamp__lt=cutoff_date)
        
        if metric_names:
            qs = qs.filter(metric_name__in=metric_names)
        
        # Get all old points
        old_points = list(qs)
        
        # Use lambda with filter() for additional Python-side filtering if needed
        # (Example: could filter by metadata conditions)
        points_to_delete = list(
            filter(
                lambda p: (
                    # Could add complex conditions here
                    # For example: p.metadata.get('retention', 'standard') == 'short'
                    True  # For now, delete all old points
                ),
                old_points
            )
        )
        
        # Extract IDs using lambda with map()
        ids_to_delete = list(map(lambda p: p.id, points_to_delete))
        
        # Bulk delete
        deleted_count = TelemetryPoint.objects.filter(pk__in=ids_to_delete).delete()[0]
        
        return deleted_count




# ============================================================================
# SCHEMA DEFINITION
# ============================================================================
# The schema combines all queries and mutations into a single GraphQL schema.
# This is what gets exposed via the HTTP endpoint.

schema = strawberry.Schema(query=Query, mutation=Mutation)
"""
GraphQL Schema Definition

strawberry.Schema:
- Combines the Query and Mutation classes into a complete GraphQL schema
- This schema is used by the GraphQL endpoint (configured in urls.py)
- Automatically generates GraphQL type definitions from Python classes
- Handles request parsing, validation, and response serialization

How it works:
1. Client sends GraphQL query/mutation as JSON to /graphql endpoint
2. Strawberry parses the request and validates it against the schema
3. Strawberry calls the appropriate resolver (Query or Mutation method)
4. Resolver executes Django ORM queries and returns Python objects
5. Strawberry serializes the response to JSON matching the requested fields
6. Client receives only the data they requested

Example request:
POST /graphql
{
  "query": "{
    robots(status: \"ACTIVE\") {
      id
      serial
      model
    }
  }"
}

This will:
1. Call Query.robots(status="ACTIVE")
2. Execute Robot.objects.filter(status="ACTIVE")
3. Return only id, serial, and model fields (not all fields)
4. Serialize to JSON and return to client

The schema is registered in urls.py:
path("graphql/", GraphQLView.as_view(schema=schema))
"""
