import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class AWSAccount(Base):
    __tablename__ = 'aws_accounts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    account_id = Column(String(50), nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    region = Column(String(50), default='us-east-1', nullable=False)
    connection_type = Column(String(50), default='ROLE_ARN', nullable=False)  # 'ROLE_ARN', 'ACCESS_KEY', 'DEMO'
    encrypted_connection_metadata = Column(Text, nullable=True)
    status = Column(String(50), default='Connected', nullable=False)  # 'Connected', 'Failed', 'Permission Error', 'Synchronizing', 'Disconnected'
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    user = relationship('User', back_populates='aws_accounts')
    resources = relationship('Resource', back_populates='aws_account', cascade='all, delete-orphan')
    cost_records = relationship('CostRecord', back_populates='aws_account', cascade='all, delete-orphan')
    recommendations = relationship('Recommendation', back_populates='aws_account', cascade='all, delete-orphan')
    budgets = relationship('Budget', back_populates='aws_account', cascade='all, delete-orphan')
    alerts = relationship('Alert', back_populates='aws_account', cascade='all, delete-orphan')
    forecasts = relationship('Forecast', back_populates='aws_account', cascade='all, delete-orphan')
    anomalies = relationship('Anomaly', back_populates='aws_account', cascade='all, delete-orphan')
    reports = relationship('Report', back_populates='aws_account', cascade='all, delete-orphan')
