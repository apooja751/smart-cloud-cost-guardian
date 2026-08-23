import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.base import Base

class Resource(Base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True, index=True)
    aws_account_id = Column(Integer, ForeignKey('aws_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    resource_id = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)  # 'EC2', 'EBS', 'S3', 'RDS', 'Lambda', 'ELB', 'ElasticIP', 'Snapshot'
    service = Column(String(100), nullable=False, index=True)
    region = Column(String(50), nullable=False)
    name = Column(String(255), nullable=True)
    state = Column(String(50), nullable=True)  # 'running', 'stopped', 'available', 'in-use', 'active'
    metadata_json = Column(Text, nullable=True)  # JSON serialized metadata
    estimated_monthly_cost = Column(Float, default=0.0, nullable=False)
    first_seen_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    last_seen_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    aws_account = relationship('AWSAccount', back_populates='resources')
    metrics = relationship('ResourceMetric', back_populates='resource', cascade='all, delete-orphan')
    recommendations = relationship('Recommendation', back_populates='resource', cascade='all, delete-orphan')
