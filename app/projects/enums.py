from enum import Enum


class ProjectType(str, Enum):
    """Enum for project types."""

    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    OTHERS = "others"


class ProjectStatus(str, Enum):
    """Enum for project statuses."""

    ONGOING = "ongoing"
    COMPLETED = "completed"
    NOT_STARTED = "not_started"
    ON_HOLD = "on_hold"
