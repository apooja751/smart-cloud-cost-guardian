import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.models.user import User
from app.models.aws_account import AWSAccount
from app.models.budget import Budget
from app.models.cost import CostRecord
from app.schemas import BudgetCreate, BudgetResponse
from app.schemas.common import StandardResponse
from app.api.deps import get_current_user

router = APIRouter(prefix='/budgets', tags=['Budget Management'])

@router.get('', response_model=StandardResponse[List[BudgetResponse]])
def list_budgets(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Budget).join(AWSAccount).filter(AWSAccount.user_id == current_user.id)
    if account_id:
        query = query.filter(Budget.aws_account_id == account_id)
    budgets = query.all()

    first_of_month = datetime.date.today().replace(day=1)
    results = []

    for b in budgets:
        q = db.query(func.sum(CostRecord.amount)).filter(
            CostRecord.aws_account_id == b.aws_account_id,
            CostRecord.date >= first_of_month
        )
        if b.service:
            q = q.filter(CostRecord.service == b.service)
        current_spend = float(q.scalar() or 0.0)
        pct = round((current_spend / b.amount) * 100.0, 1) if b.amount > 0 else 0.0
        status = 'EXCEEDED' if pct >= 100.0 else 'WARNING' if pct >= 90.0 else 'OK'

        resp = BudgetResponse(
            id=b.id,
            aws_account_id=b.aws_account_id,
            name=b.name,
            amount=b.amount,
            currency=b.currency,
            period=b.period,
            service=b.service,
            current_spend=round(current_spend, 2),
            spent_percentage=pct,
            status=status,
            threshold_50=b.threshold_50,
            threshold_75=b.threshold_75,
            threshold_90=b.threshold_90,
            threshold_100=b.threshold_100,
            created_at=b.created_at
        )
        results.append(resp)

    return StandardResponse(data=results, message='Budgets retrieved')

@router.post('', response_model=StandardResponse[BudgetResponse])
def create_budget(req: BudgetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    acc = db.query(AWSAccount).filter(AWSAccount.id == req.aws_account_id, AWSAccount.user_id == current_user.id).first()
    if not acc:
        raise HTTPException(status_code=404, detail='AWS account not found')

    b = Budget(
        aws_account_id=req.aws_account_id,
        name=req.name,
        amount=req.amount,
        currency=req.currency,
        period=req.period,
        service=req.service,
        threshold_50=req.threshold_50,
        threshold_75=req.threshold_75,
        threshold_90=req.threshold_90,
        threshold_100=req.threshold_100
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    resp = BudgetResponse.model_validate(b)
    resp.current_spend = 0.0
    resp.spent_percentage = 0.0
    resp.status = 'OK'
    return StandardResponse(data=resp, message='Budget created successfully')

@router.delete('/{id}', response_model=StandardResponse[dict])
def delete_budget(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    b = db.query(Budget).join(AWSAccount).filter(Budget.id == id, AWSAccount.user_id == current_user.id).first()
    if not b:
        raise HTTPException(status_code=404, detail='Budget not found')
    db.delete(b)
    db.commit()
    return StandardResponse(data={}, message='Budget deleted successfully')
