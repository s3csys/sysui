from typing import Any
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime


class BaseModel:
    # Generate __tablename__ automatically based on class name
    # but only if __tablename__ is not explicitly defined
    @declared_attr
    def __tablename__(cls) -> str:
        # Check if __tablename__ is explicitly defined in the class
        if '__tablename__' in cls.__dict__:
            return cls.__dict__['__tablename__']
        return cls.__name__.lower()
    
    # Common columns for all models
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


Base = declarative_base(cls=BaseModel)