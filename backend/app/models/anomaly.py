import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Anomaly(Base):
    __tablename__ = 'anomalies'

    id = Column(Integer, primary_key=True, index=True)
    aws_account_id = Column(Integer, ForeignKey('aws_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    service = Column(String(100), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    expected_cost = Column(Float, nullable=False)
    actual_cost = Column(Float, nullable=False)
    deviation = Column(Float, nullable=False)  # percentage, e.g., 42.5%
    severity = Column(String(50), default='Medium', nullable=False)  # 'Critical', 'High', 'Medium', 'Low'
    status = Column(String(50), default='Detected', nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    aws_account = relationship('AWSAccount', back_populates='anomalies')
