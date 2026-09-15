import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.models.user import User
from app.models.aws_account import AWSAccount
from app.models.cost import CostRecord
from app.models.recommendation import Recommendation
from app.models.forecast import Forecast
from app.schemas import CostSummaryResponse, DailyCostItem, ServiceCostItem
from app.schemas.common import StandardResponse
from app.services.health_score.calculator import calculate_cloud_health_score
from app.api.deps import get_current_user

router = APIRouter(prefix='/costs', tags=['Cost Analysis'])

@router.get('/summary', response_model=StandardResponse[CostSummaryResponse])
def get_cost_summary(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    acc_query = db.query(AWSAccount)
    if current_user.role != 'ADMIN':
        acc_query = acc_query.filter(AWSAccount.user_id == current_user.id)
    if account_id:
        acc_query = acc_query.filter(AWSAccount.id == account_id)
    account = acc_query.first()

    if not account:
        return StandardResponse(
            data=CostSummaryResponse(
                current_month_cost=0.0,
                previous_month_cost=0.0,
                cost_change_percentage=0.0,
                forecasted_monthly_cost=0.0,
                potential_monthly_savings=0.0,
                cloud_health_score=100,
                currency='USD'
            ),
            message='No connected accounts'
        )

    target_acc_id = account.id

    now = datetime.date.today()
    first_of_month = now.replace(day=1)
    prev_month_start = (first_of_month - datetime.timedelta(days=28)).replace(day=1)

    current_spend = float(db.query(func.sum(CostRecord.amount)).filter(
        CostRecord.aws_account_id == target_acc_id,
        CostRecord.date >= first_of_month
    ).scalar() or 0.0)

    prev_spend = float(db.query(func.sum(CostRecord.amount)).filter(
        CostRecord.aws_account_id == target_acc_id,
        CostRecord.date >= prev_month_start,
        CostRecord.date < first_of_month
    ).scalar() or 0.0)

    change_pct = round(((current_spend - prev_spend) / prev_spend * 100.0), 2) if prev_spend > 0 else 0.0

    active_recs = db.query(Recommendation).filter(
        Recommendation.aws_account_id == target_acc_id,
        Recommendation.status == 'Active'
    ).all()
    potential_savings = round(sum(r.estimated_monthly_savings for r in active_recs), 2)

    forecast_sum = float(db.query(func.sum(Forecast.predicted_amount)).filter(
        Forecast.aws_account_id == target_acc_id
    ).scalar() or (current_spend * 1.05))

    health = calculate_cloud_health_score(db, target_acc_id)

    return StandardResponse(
        data=CostSummaryResponse(
            current_month_cost=round(current_spend, 2),
            previous_month_cost=round(prev_spend, 2),
            cost_change_percentage=change_pct,
            forecasted_monthly_cost=round(forecast_sum, 2),
            potential_monthly_savings=potential_savings,
            cloud_health_score=health['overall_score'],
            currency='USD'
        ),
        message='Cost summary calculated'
    )

@router.get('/daily', response_model=StandardResponse[List[DailyCostItem]])
def get_daily_costs(
    account_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    acc = db.query(AWSAccount)
    if current_user.role != 'ADMIN':
        acc = acc.filter(AWSAccount.user_id == current_user.id)
    if account_id:
        acc = acc.filter(AWSAccount.id == account_id)
    account = acc.first()

    if not account:
        return StandardResponse(data=[], message='No account')

    start_date = datetime.date.today() - datetime.timedelta(days=days)
    records = db.query(
        CostRecord.date,
        func.sum(CostRecord.amount).label('total')
    ).filter(
        CostRecord.aws_account_id == account.id,
        CostRecord.date >= start_date
    ).group_by(CostRecord.date).order_by(CostRecord.date.asc()).all()

    results = [DailyCostItem(date=str(r[0]), amount=round(float(r[1]), 2)) for r in records]
    return StandardResponse(data=results, message='Daily costs retrieved')

@router.get('/services', response_model=StandardResponse[List[ServiceCostItem]])
def get_service_costs(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    acc = db.query(AWSAccount)
    if current_user.role != 'ADMIN':
        acc = acc.filter(AWSAccount.user_id == current_user.id)
    if account_id:
        acc = acc.filter(AWSAccount.id == account_id)
    account = acc.first()

    if not account:
        return StandardResponse(data=[], message='No account')

    first_of_month = datetime.date.today().replace(day=1)
    services_q = db.query(
        CostRecord.service,
        func.sum(CostRecord.amount).label('total')
    ).filter(
        CostRecord.aws_account_id == account.id,
        CostRecord.date >= first_of_month
    ).group_by(CostRecord.service).order_by(func.sum(CostRecord.amount).desc()).all()

    total = sum(float(r[1]) for r in services_q) or 1.0
    results = [
        ServiceCostItem(
            service=r[0],
            amount=round(float(r[1]), 2),
            percentage=round((float(r[1]) / total) * 100.0, 1)
        ) for r in services_q
    ]
    return StandardResponse(data=results, message='Service costs retrieved')
