from django.db import models


class RobotStatus(models.TextChoices):
    IDLE = "IDLE", "Idle"
    ACTIVE = "ACTIVE", "Active"
    OFFLINE = "OFFLINE", "Offline"
    ERROR = "ERROR", "Error"
    MAINTENANCE = "MAINTENANCE", "Under maintenance"


class TaskStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ASSIGNED = "ASSIGNED", "Assigned"
    RUNNING = "RUNNING", "Running"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class MaintenanceType(models.TextChoices):
    PREVENTIVE = "PREVENTIVE", "Preventive"
    CORRECTIVE = "CORRECTIVE", "Corrective"
    INSPECTION = "INSPECTION", "Inspection"
    CALIBRATION = "CALIBRATION", "Calibration"


class PredictionType(models.TextChoices):
    ANOMALY_SCORE = "ANOMALY_SCORE", "Anomaly score"
    RUL = "RUL", "Remaining useful life"


class UserRole(models.TextChoices):
    PRODUCTION_MANAGER = "PRODUCTION_MANAGER", "Production manager"
    OPERATOR = "OPERATOR", "Operator"
    MAINTENANCE_ENGINEER = "MAINTENANCE_ENGINEER", "Maintenance engineer"
    AUDITOR = "AUDITOR", "Auditor / Analytics"
    ADMIN = "ADMIN", "Administrator"


