import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    aws_account_id = Column(Integer, ForeignKey('aws_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    reporting_period = Column(String(100), nullable=False)  # e.g., 'Last 30 Days', 'August 2026'
    file_path = Column(String(500), nullable=False)
    format = Column(String(20), default='PDF', nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    user = relationship('User', back_populates='reports')
    aws_account = relationship('AWSAccount', back_populates='reports')
