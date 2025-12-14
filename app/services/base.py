from typing import TypeVar, Generic, Type, List, Optional, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base service with common CRUD operations.
    Implements Repository pattern for database access.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> ModelType:
        """Get a single record by ID"""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise HTTPException(
                status_code=404, detail=f"{self.model.__name__} not found"
            )
        return obj

    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination"""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, id: int, obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record"""
        db_obj = self.get(db, id)
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> None:
        """Delete a record"""
        obj = self.get(db, id)
        db.delete(obj)
        db.commit()

    def exists(self, db: Session, **filters) -> bool:
        """Check if a record exists with given filters"""
        query = db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.first() is not None


class SlugUniqueService(BaseService[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Extended base service that validates slug uniqueness.
    Template Method pattern: extends create behavior.
    """

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create with slug uniqueness validation"""
        obj_data = obj_in.model_dump()
        
        # Validate slug uniqueness
        if "slug" in obj_data and self.exists(db, slug=obj_data["slug"]):
            raise HTTPException(
                status_code=400,
                detail=f"{self.model.__name__} with this slug already exists",
            )
        
        return super().create(db, obj_in)
