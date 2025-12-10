from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

from app.projects.enums import ProjectType, ProjectStatus


class ProjectCreateSchema(BaseModel):
    """Schema for creating a new project."""

    name: str = Field(
        ...,
        description="Name of the project",
        max_length=255,
    )

    status: ProjectStatus = Field(
        ...,
        description="Status of the project",
    )

    type: ProjectType = Field(
        ...,
        description="Type of the project",
    )

    start_date: Optional[date] = Field(
        default=None,
        description="Start date of the project",
    )

    end_date: Optional[date] = Field(
        default=None,
        description="Expected completion date of the project",
    )

    address: Optional[str] = Field(
        default=None,
        description="Address of the project location",
        max_length=500,
    )


class ProjectResponseSchema(BaseModel):
    """Schema for project response."""

    uuid: str
    name: str
    status: ProjectStatus
    type: ProjectType
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    address: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if v else None,
        }
