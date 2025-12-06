"""User model."""
from sqlalchemy import Column, Integer, String

from backend.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=True)
