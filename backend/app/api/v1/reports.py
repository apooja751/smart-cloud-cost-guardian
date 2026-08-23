import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.aws_account import AWSAccount
from app.models.report import Report
from app.models.audit_log import AuditLog
from app.schemas import ReportGenerateRequest, ReportResponse
from app.schemas.common import StandardResponse
from app.services.reports.pdf_generator import generate_pdf_report
from app.api.deps import get_current_user

router = APIRouter(prefix='/reports', tags=['FinOps Reports'])

@router.post('/generate', response_model=StandardResponse[ReportResponse])
def generate_report(
    req: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    acc = db.query(AWSAccount).filter(AWSAccount.id == req.aws_account_id, AWSAccount.user_id == current_user.id).first()
    if not acc:
        raise HTTPException(status_code=404, detail='AWS account not found')

    pdf_path = generate_pdf_report(db, acc.id, req.title, req.reporting_period)

    report = Report(
        user_id=current_user.id,
        aws_account_id=acc.id,
        title=req.title,
        reporting_period=req.reporting_period,
        file_path=pdf_path,
        format='PDF'
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    audit = AuditLog(
        user_id=current_user.id,
        action='REPORT_GENERATED',
        resource_type='REPORT',
        resource_id=str(report.id),
        metadata_json='{}'
    )
    db.add(audit)
    db.commit()

    resp = ReportResponse(
        id=report.id,
        aws_account_id=report.aws_account_id,
        title=report.title,
        reporting_period=report.reporting_period,
        format=report.format,
        download_url=f'/api/v1/reports/{report.id}/download',
        created_at=report.created_at
    )
    return StandardResponse(data=resp, message='PDF Report generated successfully')

@router.get('', response_model=StandardResponse[List[ReportResponse]])
def list_reports(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Report).filter(Report.user_id == current_user.id)
    if account_id:
        query = query.filter(Report.aws_account_id == account_id)
    
    reports = query.order_by(Report.created_at.desc()).all()
    results = [
        ReportResponse(
            id=r.id,
            aws_account_id=r.aws_account_id,
            title=r.title,
            reporting_period=r.reporting_period,
            format=r.format,
            download_url=f'/api/v1/reports/{r.id}/download',
            created_at=r.created_at
        ) for r in reports
    ]
    return StandardResponse(data=results, message='Reports retrieved')

@router.get('/{id}/download')
def download_report(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    r = db.query(Report).filter(Report.id == id, Report.user_id == current_user.id).first()
    if not r or not os.path.exists(r.file_path):
        raise HTTPException(status_code=404, detail='Report file not found')
    
    return FileResponse(
        path=r.file_path,
        filename=os.path.basename(r.file_path),
        media_type='application/pdf'
    )
