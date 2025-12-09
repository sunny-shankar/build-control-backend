import uuid as uuid_pkg
from datetime import datetime

from sqlalchemy import text
from sqlmodel import Field, SQLModel
from app.utils.datetime import now_utc_naive


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
        default_factory=now_utc_naive,
    )

    updated_at: datetime = Field(
        default_factory=now_utc_naive,
    )


class SoftDeleteMixin(SQLModel):
    deleted_at: datetime | None = Field(default=None)

    def soft_delete(self):
        self.deleted_at = now_utc_naive()

    def restore(self):
        self.deleted_at = None


class BaseSQLModel(UUIDModel, TimestampModel, SoftDeleteMixin):
    pass
