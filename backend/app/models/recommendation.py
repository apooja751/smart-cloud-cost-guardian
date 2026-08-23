import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.base import Base

class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True, index=True)
    aws_account_id = Column(Integer, ForeignKey('aws_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    resource_id = Column(Integer, ForeignKey('resources.id', ondelete='SET NULL'), nullable=True, index=True)
    category = Column(String(100), nullable=False, index=True)  # 'Idle Compute', 'Unattached Storage', 'Old Snapshots', 'Unused Network', 'Rightsizing', 'Storage Lifecycle', 'Serverless'
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=False)
    estimated_monthly_savings = Column(Float, default=0.0, nullable=False)
    estimated_yearly_savings = Column(Float, default=0.0, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)  # 0.0 to 1.0 (or percentage 0-100)
    severity = Column(String(50), default='Medium', nullable=False)  # 'Critical', 'High', 'Medium', 'Low'
    status = Column(String(50), default='Active', nullable=False)  # 'Active', 'Reviewed', 'Dismissed', 'Snoozed'
    action_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    aws_account = relationship('AWSAccount', back_populates='recommendations')
    resource = relationship('Resource', back_populates='recommendations')
