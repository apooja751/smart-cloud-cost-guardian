from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.alert import Alert
from app.schemas import AlertResponse
from app.schemas.common import StandardResponse
from app.api.deps import get_current_user

router = APIRouter(prefix='/alerts', tags=['Alerts & Notifications'])

@router.get('', response_model=StandardResponse[List[AlertResponse]])
def list_alerts(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Alert).filter(Alert.user_id == current_user.id)
    if unread_only:
        query = query.filter(Alert.read == False)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    results = [AlertResponse.model_validate(a) for a in alerts]
    return StandardResponse(data=results, message='Alerts retrieved')

@router.post('/{id}/read', response_model=StandardResponse[dict])
def mark_alert_read(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == id, Alert.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail='Alert not found')
    alert.read = True
    db.commit()
    return StandardResponse(data={}, message='Alert marked as read')

@router.post('/read-all', response_model=StandardResponse[dict])
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Alert).filter(Alert.user_id == current_user.id, Alert.read == False).update({'read': True})
    db.commit()
    return StandardResponse(data={}, message='All alerts marked as read')
