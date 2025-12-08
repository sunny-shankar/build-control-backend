"""
Base Repository Pattern Implementation for SQLModel with Async Support
Provides generic CRUD operations and filtering capabilities.
"""

from typing import Generic, Optional, TypeVar, List, Any, Type, Dict

from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession


from app.common.models import BaseSQLModel, SoftDeleteMixin

# Generic type variable bound to SQLModel
T = TypeVar("T", bound=BaseSQLModel)


class BaseRepository(Generic[T]):
    """
    Base repository class providing generic CRUD operations for SQLModel.
    Supports soft delete, filtering, pagination, and async operations.
    """

    def __init__(self, session: AsyncSession, model: Type[T]):
        """
        Initialize repository with async session and model class.

        Args:
            session: AsyncSession instance for database operations
            model: SQLModel class to perform operations on
        """
        self.session = session
        self.model = model

    # ==================== CREATE OPERATIONS ====================

    async def create(self, obj_in: T) -> T:
        """
        Create a new record in the database.

        Args:
            obj_in: Model instance to create

        Returns:
            Created model instance with generated UUID and timestamps
        """
        self.session.add(obj_in)
        await self.session.commit()
        await self.session.refresh(obj_in)
        return obj_in

    async def create_bulk(self, objects: List[T]) -> List[T]:
        """
        Create multiple records in a single transaction.

        Args:
            objects: List of model instances to create

        Returns:
            List of created model instances
        """
        self.session.add_all(objects)
        await self.session.commit()

        # Refresh all objects to populate generated fields
        for obj in objects:
            await self.session.refresh(obj)

        return objects

    # ==================== READ OPERATIONS ====================

    async def get(self, uuid: UUID) -> Optional[T]:
        """
        Fetch a single record by UUID, excluding soft-deleted records.

        Args:
            uuid: Primary key UUID

        Returns:
            Model instance or None if not found
        """
        query = select(self.model).where(self.model.uuid == uuid)

        # Exclude soft-deleted records if model supports soft delete
        if issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> List[T]:
        """
        Fetch all records with pagination support.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            include_deleted: Include soft-deleted records

        Returns:
            List of model instances
        """
        query = select(self.model)

        # Exclude soft-deleted records by default
        if not include_deleted and issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_at.is_(None))

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        **filters: Any,
    ) -> List[T]:
        """
        Fetch records with custom filters and pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Include soft-deleted records
            **filters: Column filters (e.g., status='active', user_id=123)

        Returns:
            List of filtered model instances

        Example:
            users = await repo.get_by_filters(status='active', skip=0, limit=10)
        """
        query = select(self.model)

        # Apply filters
        filter_conditions = []
        for key, value in filters.items():
            if hasattr(self.model, key):
                filter_conditions.append(getattr(self.model, key) == value)

        if filter_conditions:
            query = query.where(and_(*filter_conditions))

        # Exclude soft-deleted records by default
        if not include_deleted and issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_at.is_(None))

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def exists(self, **filters: Any) -> bool:
        """
        Check if a record exists matching the given filters.

        Args:
            **filters: Column filters

        Returns:
            True if record exists, False otherwise
        """
        query = select(func.count(self.model.uuid))

        filter_conditions = []
        for key, value in filters.items():
            if hasattr(self.model, key):
                filter_conditions.append(getattr(self.model, key) == value)

        if filter_conditions:
            query = query.where(and_(*filter_conditions))

        result = await self.session.execute(query)
        count = result.scalar()
        return count > 0

    # ==================== UPDATE OPERATIONS ====================

    async def update(self, uuid: UUID, obj_in: Dict[str, Any] | T) -> Optional[T]:
        """
        Update an existing record by UUID.

        Args:
            uuid: Primary key UUID
            obj_in: Dictionary of fields to update or model instance

        Returns:
            Updated model instance or None if not found
        """
        db_obj = await self.get(uuid)
        if not db_obj:
            return None

        # Convert dict to SQLModel update format
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Prevent updating uuid and created_at
        update_data.pop("uuid", None)
        update_data.pop("created_at", None)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update_bulk(self, updates: List[tuple[UUID, Dict[str, Any]]]) -> List[T]:
        """
        Update multiple records in a single transaction.

        Args:
            updates: List of tuples containing (uuid, update_dict)

        Returns:
            List of updated model instances

        Example:
            updates = [
                (uuid1, {'status': 'active'}),
                (uuid2, {'status': 'inactive'}),
            ]
            await repo.update_bulk(updates)
        """
        updated_objects = []

        for uuid, update_data in updates:
            obj = await self.update(uuid, update_data)
            if obj:
                updated_objects.append(obj)

        return updated_objects

    # ==================== DELETE OPERATIONS ====================

    async def delete(self, uuid: UUID) -> bool:
        """
        Permanently delete a record by UUID.

        Args:
            uuid: Primary key UUID

        Returns:
            True if deleted, False if not found
        """
        obj = await self.get(uuid)
        if not obj:
            return False

        await self.session.delete(obj)
        await self.session.commit()
        return True

    async def delete_bulk(self, uuids: List[UUID]) -> int:
        """
        Permanently delete multiple records.

        Args:
            uuids: List of UUIDs to delete

        Returns:
            Number of deleted records
        """
        query = select(self.model).where(self.model.uuid.in_(uuids))
        result = await self.session.execute(query)
        objects = result.scalars().all()

        for obj in objects:
            await self.session.delete(obj)

        await self.session.commit()
        return len(objects)

    async def soft_delete(self, uuid: UUID) -> Optional[T]:
        """
        Soft delete a record by UUID (sets deleted_at timestamp).
        Only works with models that inherit from SoftDeleteMixin.

        Args:
            uuid: Primary key UUID

        Returns:
            Updated model instance or None if not found
        """
        if not issubclass(self.model, SoftDeleteMixin):
            raise TypeError(f"{self.model.__name__} does not support soft delete")

        obj = await self.get(uuid)
        if not obj:
            return None

        obj.soft_delete()
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def soft_delete_bulk(self, uuids: List[UUID]) -> int:
        """
        Soft delete multiple records.

        Args:
            uuids: List of UUIDs to soft delete

        Returns:
            Number of soft-deleted records
        """
        if not issubclass(self.model, SoftDeleteMixin):
            raise TypeError(f"{self.model.__name__} does not support soft delete")

        query = select(self.model).where(
            and_(
                self.model.uuid.in_(uuids),
                self.model.deleted_at.is_(None),
            )
        )

        result = await self.session.execute(query)
        objects = result.scalars().all()

        for obj in objects:
            obj.soft_delete()

        await self.session.commit()
        return len(objects)

    async def restore(self, uuid: UUID) -> Optional[T]:
        """
        Restore a soft-deleted record (sets deleted_at to None).

        Args:
            uuid: Primary key UUID

        Returns:
            Restored model instance or None if not found
        """
        if not issubclass(self.model, SoftDeleteMixin):
            raise TypeError(f"{self.model.__name__} does not support soft delete")

        # Query including deleted records
        query = select(self.model).where(self.model.uuid == uuid)
        result = await self.session.execute(query)
        obj = result.scalar_one_or_none()

        if not obj:
            return None

        obj.restore()
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def restore_bulk(self, uuids: List[UUID]) -> int:
        """
        Restore multiple soft-deleted records.

        Args:
            uuids: List of UUIDs to restore

        Returns:
            Number of restored records
        """
        if not issubclass(self.model, SoftDeleteMixin):
            raise TypeError(f"{self.model.__name__} does not support soft delete")

        query = select(self.model).where(
            and_(
                self.model.uuid.in_(uuids),
                self.model.deleted_at.isnot(None),
            )
        )

        result = await self.session.execute(query)
        objects = result.scalars().all()

        for obj in objects:
            obj.restore()

        await self.session.commit()
        return len(objects)

    # ==================== UTILITY OPERATIONS ====================

    async def count(self, include_deleted: bool = False) -> int:
        """
        Get total count of records.

        Args:
            include_deleted: Include soft-deleted records

        Returns:
            Total record count
        """
        query = select(func.count(self.model.uuid))

        if not include_deleted and issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def count_by_filters(
        self, include_deleted: bool = False, **filters: Any
    ) -> int:
        """
        Get count of records matching filters.

        Args:
            include_deleted: Include soft-deleted records
            **filters: Column filters

        Returns:
            Record count matching filters
        """
        query = select(func.count(self.model.uuid))

        filter_conditions = []
        for key, value in filters.items():
            if hasattr(self.model, key):
                filter_conditions.append(getattr(self.model, key) == value)

        if filter_conditions:
            query = query.where(and_(*filter_conditions))

        if not include_deleted and issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar() or 0
