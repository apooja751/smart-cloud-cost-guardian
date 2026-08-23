from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.aws_account import AWSAccount
from app.models.recommendation import Recommendation
from app.schemas import RecommendationResponse, RecommendationActionRequest
from app.schemas.common import StandardResponse
from app.api.deps import get_current_user

router = APIRouter(prefix='/recommendations', tags=['FinOps Recommendations'])

@router.get('', response_model=StandardResponse[List[RecommendationResponse]])
def list_recommendations(
    account_id: Optional[int] = None,
    status: Optional[str] = 'Active',
    category: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Recommendation).join(AWSAccount).filter(AWSAccount.user_id == current_user.id)

    if account_id:
        query = query.filter(Recommendation.aws_account_id == account_id)
    if status and status != 'ALL':
        query = query.filter(Recommendation.status == status)
    if category:
        query = query.filter(Recommendation.category == category)
    if severity:
        query = query.filter(Recommendation.severity == severity)

    recs = query.order_by(Recommendation.estimated_monthly_savings.desc()).all()
    results = [RecommendationResponse.model_validate(r) for r in recs]
    return StandardResponse(data=results, message='Recommendations retrieved')

@router.get('/{id}', response_model=StandardResponse[RecommendationResponse])
def get_recommendation(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rec = db.query(Recommendation).join(AWSAccount).filter(Recommendation.id == id, AWSAccount.user_id == current_user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail='Recommendation not found')
    return StandardResponse(data=RecommendationResponse.model_validate(rec), message='Recommendation detail')

@router.post('/{id}/action', response_model=StandardResponse[RecommendationResponse])
def update_recommendation_action(
    id: int,
    req: RecommendationActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = db.query(Recommendation).join(AWSAccount).filter(Recommendation.id == id, AWSAccount.user_id == current_user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail='Recommendation not found')
    
    status_map = {
        'REVIEW': 'Reviewed',
        'DISMISS': 'Dismissed',
        'SNOOZE': 'Snoozed',
        'ACTIVE': 'Active'
    }
    rec.status = status_map.get(req.action.upper(), 'Reviewed')
    if req.notes:
        rec.action_notes = req.notes
    db.commit()
    db.refresh(rec)
    return StandardResponse(data=RecommendationResponse.model_validate(rec), message=f'Recommendation marked as {rec.status}')
