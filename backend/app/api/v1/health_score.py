from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.aws_account import AWSAccount
from app.schemas import HealthScoreResponse
from app.schemas.common import StandardResponse
from app.services.health_score.calculator import calculate_cloud_health_score
from app.api.deps import get_current_user

router = APIRouter(prefix='/health-score', tags=['Cloud Health Score'])

@router.get('', response_model=StandardResponse[HealthScoreResponse])
def get_health_score(
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
        raise HTTPException(status_code=404, detail='No AWS account found')

    result = calculate_cloud_health_score(db, account.id)
    return StandardResponse(data=HealthScoreResponse(**result), message='Cloud Health Score calculated')
