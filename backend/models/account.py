"""Bank account model."""
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.database.db import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plaid_account_id = Column(String(128), nullable=False)
    institution_name = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    mask = Column(String(16), nullable=True)
    subtype = Column(String(64), nullable=True)
    balance_available = Column(Float, nullable=True)
    balance_current = Column(Float, nullable=True)
    currency = Column(String(8), nullable=True)
    encrypted_access_token = Column(String(512), nullable=False)

    user = relationship("User", backref="accounts")
    transactions = relationship("Transaction", cascade="all, delete-orphan", backref="account")
