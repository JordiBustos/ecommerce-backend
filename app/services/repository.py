"""
Repository Pattern Implementation
Provides reusable database query patterns to reduce code duplication.
Implements generic repository with common query operations.
"""

from typing import TypeVar, Generic, Type, List, Optional, Any, Callable
from sqlalchemy.orm import Session
from fastapi import HTTPException


ModelType = TypeVar("ModelType")


class EntityRepository(Generic[ModelType]):
    """
    Generic repository pattern for database entities.
    Provides common database operations to eliminate repeated query logic.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize repository with model class.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    def get_by_id(self, db: Session, entity_id: int) -> Optional[ModelType]:
        """
        Get entity by ID.
        
        Args:
            db: Database session
            entity_id: ID of the entity
        
        Returns:
            Entity or None if not found
        """
        return db.query(self.model).filter(self.model.id == entity_id).first()
    
    def get_by_id_or_404(self, db: Session, entity_id: int, error_msg: Optional[str] = None) -> ModelType:
        """
        Get entity by ID or raise 404.
        
        Args:
            db: Database session
            entity_id: ID of the entity
            error_msg: Custom error message
        
        Returns:
            Entity
        
        Raises:
            HTTPException: 404 if not found
        """
        entity = self.get_by_id(db, entity_id)
        if not entity:
            msg = error_msg or f"{self.model.__name__} not found"
            raise HTTPException(status_code=404, detail=msg)
        return entity
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get all entities with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of entities
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def get_by_field(
        self,
        db: Session,
        field_name: str,
        field_value: Any,
        skip: int = 0,
        limit: Optional[int] = None
    ) -> List[ModelType]:
        """
        Get entities by a specific field value.
        
        Args:
            db: Database session
            field_name: Name of the field to filter by
            field_value: Value to filter for
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of matching entities
        """
        query = db.query(self.model).filter(
            getattr(self.model, field_name) == field_value
        ).offset(skip)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_first_by_field(
        self,
        db: Session,
        field_name: str,
        field_value: Any
    ) -> Optional[ModelType]:
        """
        Get first entity matching a field value.
        
        Args:
            db: Database session
            field_name: Name of the field to filter by
            field_value: Value to filter for
        
        Returns:
            Entity or None
        """
        return db.query(self.model).filter(
            getattr(self.model, field_name) == field_value
        ).first()
    
    def exists(self, db: Session, entity_id: int) -> bool:
        """
        Check if entity exists.
        
        Args:
            db: Database session
            entity_id: ID of the entity
        
        Returns:
            True if exists, False otherwise
        """
        return db.query(self.model).filter(self.model.id == entity_id).count() > 0
    
    def exists_by_field(self, db: Session, field_name: str, field_value: Any) -> bool:
        """
        Check if entity exists with specific field value.
        
        Args:
            db: Database session
            field_name: Name of the field
            field_value: Value to check
        
        Returns:
            True if exists, False otherwise
        """
        return db.query(self.model).filter(
            getattr(self.model, field_name) == field_value
        ).count() > 0
    
    def create(self, db: Session, entity_data: dict) -> ModelType:
        """
        Create a new entity.
        
        Args:
            db: Database session
            entity_data: Dictionary of entity data
        
        Returns:
            Created entity
        """
        entity = self.model(**entity_data)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity
    
    def update(self, db: Session, entity_id: int, update_data: dict) -> ModelType:
        """
        Update an existing entity.
        
        Args:
            db: Database session
            entity_id: ID of the entity to update
            update_data: Dictionary of fields to update
        
        Returns:
            Updated entity
        """
        entity = self.get_by_id_or_404(db, entity_id)
        
        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        
        db.commit()
        db.refresh(entity)
        return entity
    
    def delete(self, db: Session, entity_id: int) -> None:
        """
        Delete an entity.
        
        Args:
            db: Database session
            entity_id: ID of the entity to delete
        """
        entity = self.get_by_id_or_404(db, entity_id)
        db.delete(entity)
        db.commit()
    
    def count(self, db: Session) -> int:
        """
        Count total entities.
        
        Args:
            db: Database session
        
        Returns:
            Total count
        """
        return db.query(self.model).count()
    
    def count_by_field(self, db: Session, field_name: str, field_value: Any) -> int:
        """
        Count entities matching a field value.
        
        Args:
            db: Database session
            field_name: Name of the field
            field_value: Value to filter for
        
        Returns:
            Count of matching entities
        """
        return db.query(self.model).filter(
            getattr(self.model, field_name) == field_value
        ).count()
    
    def filter_by(
        self,
        db: Session,
        filters: dict,
        skip: int = 0,
        limit: Optional[int] = None
    ) -> List[ModelType]:
        """
        Filter entities by multiple fields.
        
        Args:
            db: Database session
            filters: Dictionary of field_name: value pairs
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of matching entities
        """
        query = db.query(self.model)
        
        for field_name, field_value in filters.items():
            if hasattr(self.model, field_name):
                query = query.filter(getattr(self.model, field_name) == field_value)
        
        query = query.offset(skip)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()


class UserOwnedEntityRepository(EntityRepository[ModelType]):
    """
    Extended repository for user-owned entities.
    Adds methods for filtering by user ownership.
    """
    
    def get_by_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get all entities belonging to a user.
        
        Args:
            db: Database session
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of user's entities
        """
        return self.get_by_field(db, "user_id", user_id, skip, limit)
    
    def get_user_entity_or_404(
        self,
        db: Session,
        entity_id: int,
        user_id: int
    ) -> ModelType:
        """
        Get entity belonging to user or raise 404/403.
        
        Args:
            db: Database session
            entity_id: ID of the entity
            user_id: ID of the user
        
        Returns:
            Entity
        
        Raises:
            HTTPException: 404 if not found, 403 if not owned by user
        """
        entity = self.get_by_id_or_404(db, entity_id)
        
        if entity.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail=f"Not authorized to access this {self.model.__name__.lower()}"
            )
        
        return entity
    
    def count_by_user(self, db: Session, user_id: int) -> int:
        """
        Count entities belonging to a user.
        
        Args:
            db: Database session
            user_id: ID of the user
        
        Returns:
            Count of user's entities
        """
        return self.count_by_field(db, "user_id", user_id)
