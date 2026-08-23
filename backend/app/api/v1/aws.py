import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.aws_account import AWSAccount
from app.models.audit_log import AuditLog
from app.schemas import (
    AWSAccountConnect,
    AWSAccountResponse,
    AWSTestConnectionRequest,
    AWSTestConnectionResponse
)
from app.schemas.common import StandardResponse
from app.core.security import encrypt_secret
from app.services.aws.validator import validate_aws_connection
from app.services.aws.collector import synchronize_aws_account
from app.api.deps import get_current_user

router = APIRouter(prefix='/aws', tags=['AWS Integration'])

@router.post('/test-connection', response_model=StandardResponse[AWSTestConnectionResponse])
def test_connection(req: AWSTestConnectionRequest):
    result = validate_aws_connection(
        connection_type=req.connection_type,
        region=req.region,
        role_arn=req.role_arn,
        external_id=req.external_id,
        aws_access_key_id=req.aws_access_key_id,
        aws_secret_access_key=req.aws_secret_access_key,
        demo_mode=req.demo_mode
    )
    return StandardResponse(data=AWSTestConnectionResponse(**result), message=result['message'])

@router.post('/connect', response_model=StandardResponse[AWSAccountResponse])
def connect_account(
    req: AWSAccountConnect,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meta = {
        'connection_type': req.connection_type,
        'role_arn': req.role_arn,
        'external_id': req.external_id,
        'aws_access_key_id': req.aws_access_key_id,
        'aws_secret_access_key': req.aws_secret_access_key,
        'region': req.region
    }
    enc_meta = encrypt_secret(json.dumps(meta)) if req.connection_type != 'DEMO' else None

    account = db.query(AWSAccount).filter(
        AWSAccount.user_id == current_user.id,
        AWSAccount.account_id == req.account_id
    ).first()

    if not account:
        account = AWSAccount(
            user_id=current_user.id,
            account_id=req.account_id,
            account_name=req.account_name,
            region=req.region,
            connection_type=req.connection_type,
            encrypted_connection_metadata=enc_meta,
            status='Synchronizing'
        )
        db.add(account)
    else:
        account.account_name = req.account_name
        account.region = req.region
        account.connection_type = req.connection_type
        account.encrypted_connection_metadata = enc_meta
        account.status = 'Synchronizing'
    db.commit()
    db.refresh(account)

    audit = AuditLog(
        user_id=current_user.id,
        action='AWS_ACCOUNT_CONNECTED',
        resource_type='AWS_ACCOUNT',
        resource_id=req.account_id,
        metadata_json=json.dumps({'account_name': req.account_name, 'region': req.region, 'type': req.connection_type})
    )
    db.add(audit)
    db.commit()

    background_tasks.add_task(synchronize_aws_account, db, account.id)

    resp = AWSAccountResponse.model_validate(account)
    resp.discovered_resources_count = len(account.resources)
    return StandardResponse(data=resp, message='AWS account connected. Initial synchronization started in background.')

@router.get('/accounts', response_model=StandardResponse[List[AWSAccountResponse]])
def list_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    accounts = db.query(AWSAccount).filter(AWSAccount.user_id == current_user.id).all()
    results = []
    for acc in accounts:
        item = AWSAccountResponse.model_validate(acc)
        item.discovered_resources_count = len(acc.resources)
        results.append(item)
    return StandardResponse(data=results, message='AWS accounts retrieved')

@router.get('/accounts/{id}', response_model=StandardResponse[AWSAccountResponse])
def get_account(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    acc = db.query(AWSAccount).filter(AWSAccount.id == id, AWSAccount.user_id == current_user.id).first()
    if not acc:
        raise HTTPException(status_code=404, detail='AWS account not found')
    resp = AWSAccountResponse.model_validate(acc)
    resp.discovered_resources_count = len(acc.resources)
    return StandardResponse(data=resp, message='Account retrieved')

@router.delete('/accounts/{id}', response_model=StandardResponse[dict])
def disconnect_account(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    acc = db.query(AWSAccount).filter(AWSAccount.id == id, AWSAccount.user_id == current_user.id).first()
    if not acc:
        raise HTTPException(status_code=404, detail='AWS account not found')
    
    acc_id = acc.account_id
    db.delete(acc)
    db.commit()

    audit = AuditLog(
        user_id=current_user.id,
        action='AWS_ACCOUNT_DISCONNECTED',
        resource_type='AWS_ACCOUNT',
        resource_id=acc_id,
        metadata_json='{}'
    )
    db.add(audit)
    db.commit()

    return StandardResponse(data={}, message='AWS account disconnected successfully')

@router.post('/sync/{id}', response_model=StandardResponse[dict])
def sync_account_now(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    acc = db.query(AWSAccount).filter(AWSAccount.id == id, AWSAccount.user_id == current_user.id).first()
    if not acc:
        raise HTTPException(status_code=404, detail='AWS account not found')
    
    res = synchronize_aws_account(db, acc.id)
    return StandardResponse(data=res, message=res.get('message', 'Synchronization complete'))
