from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.aws_account import AWSAccount
from app.schemas import ForecastResponse
from app.schemas.common import StandardResponse
from app.services.forecasting.forecaster import generate_cost_forecast
from app.api.deps import get_current_user

router = APIRouter(prefix='/forecast', tags=['Cost Forecasting'])

@router.get('', response_model=StandardResponse[ForecastResponse])
def get_forecast(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    acc = db.query(AWSAccount).filter(AWSAccount.user_id == current_user.id)
    if account_id:
        acc = acc.filter(AWSAccount.id == account_id)
    account = acc.first()

    if not account:
        raise HTTPException(status_code=404, detail='No AWS account found')

    result = generate_cost_forecast(db, account.id)
    return StandardResponse(data=ForecastResponse(**result), message='Cost forecast calculated')

@router.post('/generate', response_model=StandardResponse[ForecastResponse])
def trigger_forecast_generation(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    acc = db.query(AWSAccount).filter(AWSAccount.user_id == current_user.id)
    if account_id:
        acc = acc.filter(AWSAccount.id == account_id)
    account = acc.first()

    if not account:
        raise HTTPException(status_code=404, detail='No AWS account found')

    result = generate_cost_forecast(db, account.id)
    return StandardResponse(data=ForecastResponse(**result), message='Cost forecast regenerated')
