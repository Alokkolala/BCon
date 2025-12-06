"""Payment model tracking transfers and bill payments."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.database.db import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    from_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    payee_name = Column(String(255), nullable=True)
    payee_account = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=True)
    type = Column(String(32), nullable=False)  # transfer | bill
    status = Column(String(32), nullable=False, default="pending")
    confirmation_code = Column(String(64), nullable=True)
    note = Column(String(512), nullable=True)
    provider = Column(String(64), nullable=True)
    error_message = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User")
    from_account = relationship("Account", foreign_keys=[from_account_id])
    to_account = relationship("Account", foreign_keys=[to_account_id])
