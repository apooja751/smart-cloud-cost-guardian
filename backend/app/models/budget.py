import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base

class Budget(Base):
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True, index=True)
    aws_account_id = Column(Integer, ForeignKey('aws_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='USD', nullable=False)
    period = Column(String(50), default='MONTHLY', nullable=False)  # 'MONTHLY', 'QUARTERLY'
    service = Column(String(100), nullable=True)
    threshold_50 = Column(Boolean, default=True, nullable=False)
    threshold_75 = Column(Boolean, default=True, nullable=False)
    threshold_90 = Column(Boolean, default=True, nullable=False)
    threshold_100 = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    aws_account = relationship('AWSAccount', back_populates='budgets')
