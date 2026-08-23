import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base

class Alert(Base):
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    aws_account_id = Column(Integer, ForeignKey('aws_accounts.id', ondelete='CASCADE'), nullable=True, index=True)
    type = Column(String(100), nullable=False)  # 'BUDGET_THRESHOLD', 'COST_ANOMALY', 'IDLE_RESOURCE', 'SECURITY_RISK'
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(50), default='Medium', nullable=False)  # 'Critical', 'High', 'Medium', 'Low', 'Info'
    read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    user = relationship('User', back_populates='alerts')
    aws_account = relationship('AWSAccount', back_populates='alerts')
