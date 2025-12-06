"""Transaction model."""
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.database.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=True)
    date = Column(Date, nullable=False)
    category = Column(String(128), nullable=True)
    merchant_name = Column(String(255), nullable=True)
    description = Column(String(512), nullable=True)

    account = relationship("Account")
