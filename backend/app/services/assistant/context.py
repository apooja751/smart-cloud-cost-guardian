import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.aws_account import AWSAccount
from app.models.resource import Resource
from app.models.cost import CostRecord
from app.models.recommendation import Recommendation
from app.models.budget import Budget
from app.models.anomaly import Anomaly
from app.services.health_score.calculator import calculate_cloud_health_score

def gather_finops_context(db: Session, aws_account_id: int) -> dict:
    account = db.query(AWSAccount).filter(AWSAccount.id == aws_account_id).first()
    if not account:
        return {}

    now = datetime.date.today()
    first_of_month = now.replace(day=1)
    prev_month_start = (first_of_month - datetime.timedelta(days=28)).replace(day=1)

    current_spend = float(db.query(func.sum(CostRecord.amount)).filter(
        CostRecord.aws_account_id == aws_account_id,
        CostRecord.date >= first_of_month
    ).scalar() or 0.0)

    prev_spend = float(db.query(func.sum(CostRecord.amount)).filter(
        CostRecord.aws_account_id == aws_account_id,
        CostRecord.date >= prev_month_start,
        CostRecord.date < first_of_month
    ).scalar() or 0.0)

    top_services_q = db.query(
        CostRecord.service,
        func.sum(CostRecord.amount).label('total')
    ).filter(
        CostRecord.aws_account_id == aws_account_id,
        CostRecord.date >= first_of_month
    ).group_by(CostRecord.service).order_by(func.sum(CostRecord.amount).desc()).limit(5).all()
    top_services = [{'service': r[0], 'amount': round(float(r[1]), 2)} for r in top_services_q]

    top_resources = db.query(Resource).filter(
        Resource.aws_account_id == aws_account_id
    ).order_by(Resource.estimated_monthly_cost.desc()).limit(5).all()
    expensive_resources = [{
        'name': r.name or r.resource_id,
        'type': r.resource_type,
        'cost': r.estimated_monthly_cost,
        'state': r.state
    } for r in top_resources]

    active_recs = db.query(Recommendation).filter(
        Recommendation.aws_account_id == aws_account_id,
        Recommendation.status == 'Active'
    ).order_by(Recommendation.estimated_monthly_savings.desc()).all()
    total_savings = sum(r.estimated_monthly_savings for r in active_recs)

    recs_summary = [{
        'title': r.title,
        'category': r.category,
        'monthly_savings': r.estimated_monthly_savings,
        'severity': r.severity,
        'evidence': r.evidence
    } for r in active_recs[:6]]

    health = calculate_cloud_health_score(db, aws_account_id)

    budgets = db.query(Budget).filter(Budget.aws_account_id == aws_account_id).all()
    budget_summary = [{
        'name': b.name,
        'amount': b.amount,
        'period': b.period
    } for b in budgets]

    anomalies = db.query(Anomaly).filter(
        Anomaly.aws_account_id == aws_account_id
    ).order_by(Anomaly.date.desc()).limit(3).all()
    anomalies_summary = [{
        'service': a.service,
        'date': str(a.date),
        'deviation': f'+{a.deviation:.1f}%',
        'actual': a.actual_cost,
        'expected': a.expected_cost
    } for a in anomalies]

    return {
        'account_name': account.account_name,
        'account_id': account.account_id,
        'region': account.region,
        'current_month_spend': round(current_spend, 2),
        'previous_month_spend': round(prev_spend, 2),
        'top_services': top_services,
        'expensive_resources': expensive_resources,
        'potential_monthly_savings': round(total_savings, 2),
        'recommendations': recs_summary,
        'cloud_health_score': health['overall_score'],
        'cloud_health_grade': health['grade'],
        'health_explanations': health['explanations'],
        'budgets': budget_summary,
        'recent_anomalies': anomalies_summary
    }
