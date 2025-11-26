from django.conf import settings
from django.db import models
from django.utils import timezone

from .enumerations import (
    MaintenanceType,
    PredictionType,
    RobotStatus,
    TaskStatus,
    UserRole,
)


class Robot(models.Model):
    serial = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=100)
    capabilities = models.JSONField(default=list, blank=True)
    kinematics_profile = models.TextField(blank=True)
    firmware_version = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20, choices=RobotStatus.choices, default=RobotStatus.IDLE
    )
    safety_envelope = models.JSONField(blank=True, null=True)
    calibration_notes = models.TextField(blank=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["serial"]
        verbose_name = "Robot"
        verbose_name_plural = "Robots"

    def __str__(self) -> str:
        return f"{self.serial} ({self.model})"


class TelemetryPoint(models.Model):
    robot = models.ForeignKey(
        Robot, related_name="telemetry_points", on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    metric_name = models.CharField(max_length=100, db_index=True)
    metric_value = models.FloatField()
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Telemetry point"
        verbose_name_plural = "Telemetry points"
        indexes = [
            models.Index(fields=["robot", "timestamp"]),
            models.Index(fields=["metric_name", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.robot.serial} {self.metric_name}={self.metric_value} @ {self.timestamp.isoformat()}"


class Task(models.Model):
    required_capabilities = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=20, choices=TaskStatus.choices, default=TaskStatus.PENDING
    )
    assigned_robot = models.ForeignKey(
        Robot,
        related_name="assigned_tasks",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    priority = models.IntegerField(default=0, help_text="Higher number = higher priority")
    deadline = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-priority", "deadline", "created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self) -> str:
        base = f"Task #{self.pk}"
        if self.assigned_robot:
            base += f" -> {self.assigned_robot.serial}"
        return base


class MaintenanceEvent(models.Model):
    robot = models.ForeignKey(
        Robot, related_name="maintenance_events", on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(default=timezone.now)
    type = models.CharField(
        max_length=20, choices=MaintenanceType.choices, default=MaintenanceType.INSPECTION
    )
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="performed_maintenance",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Maintenance event"
        verbose_name_plural = "Maintenance events"

    def __str__(self) -> str:
        return f"{self.type} on {self.robot.serial} @ {self.timestamp.isoformat()}"


class Prediction(models.Model):
    robot = models.ForeignKey(
        Robot, related_name="predictions", on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(default=timezone.now)
    prediction_type = models.CharField(
        max_length=30,
        choices=PredictionType.choices,
        default=PredictionType.ANOMALY_SCORE,
    )
    value = models.FloatField()
    model_version = models.CharField(max_length=100)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Prediction"
        verbose_name_plural = "Predictions"
        indexes = [
            models.Index(fields=["robot", "prediction_type", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.prediction_type}={self.value} ({self.robot.serial})"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="profile", on_delete=models.CASCADE
    )
    role = models.CharField(
        max_length=40, choices=UserRole.choices, default=UserRole.OPERATOR
    )
    contact = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "User profile"
        verbose_name_plural = "User profiles"

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="audit_logs",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    action = models.CharField(max_length=255)
    target_type = models.CharField(max_length=100)
    target_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(blank=True, null=True)
    correlation_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit log entry"
        verbose_name_plural = "Audit log entries"
        indexes = [
            models.Index(fields=["target_type", "target_id"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} on {self.target_type}({self.target_id})"

