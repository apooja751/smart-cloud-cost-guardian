import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class ResourceMetric(Base):
    __tablename__ = 'resource_metrics'

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey('resources.id', ondelete='CASCADE'), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)  # 'CPUUtilization', 'NetworkIn', 'NetworkOut', 'DatabaseConnections', 'Invocations'
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False, index=True)

    resource = relationship('Resource', back_populates='metrics')
