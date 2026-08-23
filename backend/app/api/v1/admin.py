import json
import datetime
from datetime import timezone
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db
from app.models.user import User
from app.models.aws_account import AWSAccount
from app.models.resource import Resource
from app.models.audit_log import AuditLog
from app.schemas import UserResponse, AuditLogResponse, SystemHealthResponse
from app.schemas.common import StandardResponse
from app.services.scheduler.sync_scheduler import scheduler
from app.api.deps import get_current_admin_user

router = APIRouter(prefix='/admin', tags=['Admin Portal'])

@router.get('/users', response_model=StandardResponse[List[UserResponse]])
def list_system_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    results = [UserResponse.model_validate(u) for u in users]
    return StandardResponse(data=results, message='Users retrieved')

@router.get('/audit-logs', response_model=StandardResponse[List[AuditLogResponse]])
def list_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    results = []
    for l in logs:
        item = AuditLogResponse(
            id=l.id,
            user_id=l.user_id,
            user_email=l.user.email if l.user else None,
            action=l.action,
            resource_type=l.resource_type,
            resource_id=l.resource_id,
            metadata=json.loads(l.metadata_json or '{}'),
            ip_address=l.ip_address,
            created_at=l.created_at
        )
        results.append(item)
    return StandardResponse(data=results, message='Audit logs retrieved')

@router.get('/system-health', response_model=StandardResponse[SystemHealthResponse])
def get_system_health(db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    db_ok = True
    try:
        db.execute(text('SELECT 1'))
    except Exception:
        db_ok = False

    active_users = db.query(User).filter(User.is_active == True).count()
    connected_accounts = db.query(AWSAccount).count()
    total_resources = db.query(Resource).count()

    health = SystemHealthResponse(
        status='HEALTHY' if db_ok else 'DEGRADED',
        database_connected=db_ok,
        scheduler_running=scheduler.running,
        active_users=active_users,
        connected_accounts=connected_accounts,
        total_resources=total_resources,
        timestamp=datetime.datetime.now(timezone.utc)
    )
    return StandardResponse(data=health, message='System health operational')
