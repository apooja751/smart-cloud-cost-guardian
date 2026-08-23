import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class CostRecord(Base):
    __tablename__ = 'cost_records'

    id = Column(Integer, primary_key=True, index=True)
    aws_account_id = Column(Integer, ForeignKey('aws_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    service = Column(String(100), nullable=False, index=True)
    region = Column(String(50), nullable=False)
    resource_identifier = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='USD', nullable=False)
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    aws_account = relationship('AWSAccount', back_populates='cost_records')
