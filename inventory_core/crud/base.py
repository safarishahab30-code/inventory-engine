from typing import Any, Generic, Type, TypeVar, Dict, Union
from sqlalchemy.orm import Session
from pydantic import BaseModel
from inventory_core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> ModelType | None:
        return db.query(self.model).filter(self.model.id == id).first()

    def update(self, db: Session, *, id: Any, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType | None:
        db_obj = self.get(db, id)
        if not db_obj:
            return None
        
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, product_id: int) -> bool:
        obj = self.get(db, product_id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()
