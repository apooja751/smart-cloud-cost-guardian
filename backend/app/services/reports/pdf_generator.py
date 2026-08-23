import os
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.aws_account import AWSAccount
from app.models.resource import Resource
from app.models.cost import CostRecord
from app.models.recommendation import Recommendation
from app.services.health_score.calculator import calculate_cloud_health_score
from app.core.config import settings

def generate_pdf_report(db: Session, aws_account_id: int, title: str, reporting_period: str) -> str:
    account = db.query(AWSAccount).filter(AWSAccount.id == aws_account_id).first()
    os.makedirs(settings.REPORTS_STORAGE_PATH, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"SCCG_FinOps_Report_Acc_{aws_account_id}_{timestamp}.pdf"
    file_path = os.path.join(settings.REPORTS_STORAGE_PATH, filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    story = []

    story.append(Paragraph(f"<b>{title}</b>", title_style))
    acc_nm = account.account_name if account else 'Account'
    acc_id = account.account_id if account else ''
    reg = account.region if account else 'global'
    gen_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    story.append(Paragraph(
        f"<b>AWS Account:</b> {acc_nm} ({acc_id}) | <b>Region:</b> {reg} | <b>Period:</b> {reporting_period} | <b>Generated:</b> {gen_time}",
        subtitle_style
    ))
    story.append(Spacer(1, 10))

    health = calculate_cloud_health_score(db, aws_account_id)
    recs = db.query(Recommendation).filter(
        Recommendation.aws_account_id == aws_account_id,
        Recommendation.status == 'Active'
    ).all()
    total_savings = sum(r.estimated_monthly_savings for r in recs)

    now = datetime.date.today()
    first_of_month = now.replace(day=1)
    current_spend = float(db.query(func.sum(CostRecord.amount)).filter(
        CostRecord.aws_account_id == aws_account_id,
        CostRecord.date >= first_of_month
    ).scalar() or 0.0)

    kpi_data = [
        ['Current Month Spend', 'Potential Monthly Savings', 'Identified Annual Savings', 'Cloud Health Score'],
        [f"${current_spend:,.2f}", f"${total_savings:,.2f}/mo", f"${total_savings*12:,.2f}/yr", f"{health['overall_score']}/100 (Grade {health['grade']})"]
    ]
    t_kpi = Table(kpi_data, colWidths=[130, 140, 140, 130])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#0f172a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Top FinOps Cost Optimization Recommendations</b>", h2_style))
    if recs:
        rec_rows = [['Priority', 'Category', 'Recommendation Title', 'Est. Monthly Savings', 'Status']]
        for r in recs[:8]:
            rec_rows.append([
                r.severity,
                r.category,
                Paragraph(r.title, body_style),
                f"${r.estimated_monthly_savings:,.2f}",
                r.status
            ])
        t_recs = Table(rec_rows, colWidths=[65, 105, 230, 85, 55])
        t_recs.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_recs)
    else:
        story.append(Paragraph("No active optimization recommendations found. Infrastructure is well optimized.", body_style))

    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>AWS Service Cost Breakdown (Current Period)</b>", h2_style))
    services_q = db.query(
        CostRecord.service,
        func.sum(CostRecord.amount).label('total')
    ).filter(
        CostRecord.aws_account_id == aws_account_id,
        CostRecord.date >= first_of_month
    ).group_by(CostRecord.service).order_by(func.sum(CostRecord.amount).desc()).all()

    if services_q:
        svc_rows = [['AWS Service', 'Current Month Spend', '% of Total Spend']]
        total_svc = sum(float(r[1]) for r in services_q) or 1.0
        for s in services_q:
            amt = float(s[1])
            pct = (amt / total_svc) * 100.0
            svc_rows.append([s[0], f"${amt:,.2f}", f"{pct:.1f}%"])
        
        t_svc = Table(svc_rows, colWidths=[270, 135, 135])
        t_svc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_svc)

    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Resource Inventory Snapshot</b>", h2_style))
    res_list = db.query(Resource).filter(
        Resource.aws_account_id == aws_account_id
    ).order_by(Resource.estimated_monthly_cost.desc()).limit(10).all()

    if res_list:
        res_rows = [['Resource Name / ID', 'Type', 'Region', 'State', 'Est. Monthly Cost']]
        for r in res_list:
            res_rows.append([
                Paragraph(f"{r.name or r.resource_id}<br/><font size=6 color='#64748b'>{r.resource_id}</font>", body_style),
                r.resource_type,
                r.region,
                r.state,
                f"${r.estimated_monthly_cost:,.2f}"
            ])
        t_res = Table(res_rows, colWidths=[200, 75, 75, 75, 115])
        t_res.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#475569')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_res)

    doc.build(story)
    return file_path
