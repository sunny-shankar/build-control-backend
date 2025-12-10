from typing import Optional
from datetime import date
from uuid import UUID

from sqlmodel import Field

from app.common.models import BaseSQLModel
from app.projects.enums import ProjectType, ProjectStatus


class Project(BaseSQLModel, table=True):
    __tablename__ = "projects"

    # Required fields
    name: str = Field(
        nullable=False,
        index=True,
        max_length=255,
        description="Name of the project",
    )

    status: ProjectStatus = Field(
        nullable=False,
        index=True,
        description="Status of the project",
    )

    type: ProjectType = Field(
        nullable=False,
        index=True,
        description="Type of the project",
    )

    # Optional fields
    start_date: Optional[date] = Field(
        default=None,
        nullable=True,
        description="Start date of the project",
    )

    end_date: Optional[date] = Field(
        default=None,
        nullable=True,
        description="Expected completion date of the project",
    )

    address: Optional[str] = Field(
        default=None,
        nullable=True,
        max_length=500,
        description="Address of the project location",
    )

    user_id: UUID = Field(
        nullable=False,
        index=True,
        foreign_key="users.uuid",
        description="ID of the user who owns this project",
    )
