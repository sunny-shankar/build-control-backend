import uuid as uuid_pkg
from datetime import datetime, timezone

from sqlalchemy import DateTime, text
from sqlmodel import Column, Field, SQLModel


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
        default=datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    updated_at: datetime = Field(
        default=datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )


class SoftDeleteMixin(SQLModel):
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    def soft_delete(self):
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self):
        self.deleted_at = None


class BaseSQLModel(UUIDModel, TimestampModel, SoftDeleteMixin):
    pass
