import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.aws_account import AWSAccount
from app.models.resource import Resource
from app.schemas import ResourceResponse, ResourceDetailResponse, ResourceMetricResponse
from app.schemas.common import StandardResponse
from app.api.deps import get_current_user

router = APIRouter(prefix='/resources', tags=['Resource Inventory'])

@router.get('', response_model=StandardResponse[List[ResourceResponse]])
def list_resources(
    account_id: Optional[int] = None,
    service: Optional[str] = None,
    resource_type: Optional[str] = None,
    state: Optional[str] = None,
    region: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Resource).join(AWSAccount)
    if current_user.role != 'ADMIN':
        query = query.filter(AWSAccount.user_id == current_user.id)

    if account_id:
        query = query.filter(Resource.aws_account_id == account_id)
    if service:
        query = query.filter(Resource.service == service)
    if resource_type:
        query = query.filter(Resource.resource_type == resource_type)
    if state:
        query = query.filter(Resource.state == state)
    if region:
        query = query.filter(Resource.region == region)
    if search:
        search_filter = f"%{search}%"
        query = query.filter((Resource.name.ilike(search_filter)) | (Resource.resource_id.ilike(search_filter)))

    resources = query.order_by(Resource.estimated_monthly_cost.desc()).offset(offset).limit(limit).all()

    results = []
    for r in resources:
        meta = {}
        if r.metadata_json:
            try:
                meta = json.loads(r.metadata_json)
            except Exception:
                meta = {}
        resp = ResourceResponse(
            id=r.id,
            aws_account_id=r.aws_account_id,
            resource_id=r.resource_id,
            resource_type=r.resource_type,
            service=r.service,
            region=r.region,
            name=r.name,
            state=r.state,
            estimated_monthly_cost=r.estimated_monthly_cost,
            metadata=meta,
            last_seen_at=r.last_seen_at,
            recommendations_count=len(r.recommendations)
        )
        results.append(resp)

    return StandardResponse(data=results, message='Resources retrieved')

@router.get('/summary', response_model=StandardResponse[dict])
def get_resource_summary(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Resource).join(AWSAccount)
    if current_user.role != 'ADMIN':
        query = query.filter(AWSAccount.user_id == current_user.id)
    if account_id:
        query = query.filter(Resource.aws_account_id == account_id)
    
    all_res = query.all()
    type_counts = {}
    service_costs = {}
    total_est_cost = 0.0

    for r in all_res:
        type_counts[r.resource_type] = type_counts.get(r.resource_type, 0) + 1
        service_costs[r.service] = service_costs.get(r.service, 0.0) + r.estimated_monthly_cost
        total_est_cost += r.estimated_monthly_cost

    return StandardResponse(
        data={
            'total_resources': len(all_res),
            'total_estimated_monthly_cost': round(total_est_cost, 2),
            'resource_counts_by_type': type_counts,
            'cost_by_service': {k: round(v, 2) for k, v in service_costs.items()}
        },
        message='Resource summary calculated'
    )

@router.get('/{id}', response_model=StandardResponse[ResourceDetailResponse])
def get_resource_detail(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Resource).join(AWSAccount).filter(Resource.id == id)
    if current_user.role != 'ADMIN':
        query = query.filter(AWSAccount.user_id == current_user.id)
    r = query.first()
    if not r:
        raise HTTPException(status_code=404, detail='Resource not found')
    
    meta = {}
    if r.metadata_json:
        try:
            meta = json.loads(r.metadata_json)
        except Exception:
            meta = {}
    resp = ResourceDetailResponse(
        id=r.id,
        aws_account_id=r.aws_account_id,
        resource_id=r.resource_id,
        resource_type=r.resource_type,
        service=r.service,
        region=r.region,
        name=r.name,
        state=r.state,
        estimated_monthly_cost=r.estimated_monthly_cost,
        metadata=meta,
        last_seen_at=r.last_seen_at,
        recommendations_count=len(r.recommendations),
        metrics=[ResourceMetricResponse.model_validate(m) for m in sorted(r.metrics, key=lambda x: x.timestamp)],
        recommendations=[
            {
                'id': rec.id,
                'title': rec.title,
                'category': rec.category,
                'monthly_savings': rec.estimated_monthly_savings,
                'severity': rec.severity,
                'evidence': rec.evidence,
                'status': rec.status
            } for rec in r.recommendations
        ]
    )
    return StandardResponse(data=resp, message='Resource details retrieved')
