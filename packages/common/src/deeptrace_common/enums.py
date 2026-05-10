from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    INVESTIGATOR = "investigator"
    ANALYST = "analyst"
    VIEWER = "viewer"


class EntityType(str, Enum):
    EMAIL = "email"
    USERNAME = "username"
    PHONE = "phone"
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    PERSON = "person"
    ORGANIZATION = "organization"


class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"