from typing import Any, ClassVar
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy import Integer, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    __allow_unmapped__ = True  # Allow legacy annotations to be used alongside Mapped
    
    # Generate __tablename__ automatically based on class name
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Common columns for all models
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)