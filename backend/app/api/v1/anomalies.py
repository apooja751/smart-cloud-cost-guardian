from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.aws_account import AWSAccount
from app.models.anomaly import Anomaly
from app.schemas import AnomalyResponse
from app.schemas.common import StandardResponse
from app.api.deps import get_current_user

router = APIRouter(prefix='/anomalies', tags=['Cost Anomalies'])

@router.get('', response_model=StandardResponse[List[AnomalyResponse]])
def list_anomalies(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Anomaly).join(AWSAccount).filter(AWSAccount.user_id == current_user.id)
    if account_id:
        query = query.filter(Anomaly.aws_account_id == account_id)
    
    anomalies = query.order_by(Anomaly.date.desc()).all()
    results = [
        AnomalyResponse(
            id=a.id,
            aws_account_id=a.aws_account_id,
            service=a.service,
            date=str(a.date),
            expected_cost=a.expected_cost,
            actual_cost=a.actual_cost,
            deviation_percentage=a.deviation,
            severity=a.severity,
            status=a.status,
            created_at=a.created_at
        ) for a in anomalies
    ]
    return StandardResponse(data=results, message='Anomalies retrieved')
