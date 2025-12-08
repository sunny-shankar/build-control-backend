from typing import Optional
import uuid as uuid_pkg
from datetime import datetime, timezone

from sqlalchemy import text
from sqlmodel import Field, SQLModel


class UUIDModel(SQLModel):
    uuid: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
        sa_column_kwargs={"server_default": text("gen_random_uuid()"), "unique": True},
    )


class TimestampModel(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )


class SoftDeleteMixin(SQLModel):
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self):
        self.deleted_at = None


class BaseSQLModel(UUIDModel, TimestampModel, SoftDeleteMixin):
    pass
