import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Forecast(Base):
    __tablename__ = 'forecasts'

    id = Column(Integer, primary_key=True, index=True)
    aws_account_id = Column(Integer, ForeignKey('aws_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    forecast_date = Column(Date, nullable=False, index=True)
    predicted_amount = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    model = Column(String(100), default='Linear+Trend', nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    aws_account = relationship('AWSAccount', back_populates='forecasts')
