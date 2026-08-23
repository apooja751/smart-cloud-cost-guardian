import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.resource import Resource
from app.models.resource_metric import ResourceMetric
from app.models.cost import CostRecord
from app.models.recommendation import Recommendation
from app.models.budget import Budget
from app.models.anomaly import Anomaly

def calculate_cloud_health_score(db: Session, aws_account_id: int) -> dict:
    explanations = []

    # 1. Cost Efficiency (Max 25 pts)
    # Ratio of potential savings to total monthly cost. If savings = 0%, score = 25. If savings >= 50% of spend, score = 5.
    now = datetime.date.today()
    first_of_month = now.replace(day=1)
    
    monthly_cost_q = db.query(func.sum(CostRecord.amount)).filter(
        CostRecord.aws_account_id == aws_account_id,
        CostRecord.date >= first_of_month
    ).scalar() or 0.0

    active_recs = db.query(Recommendation).filter(
        Recommendation.aws_account_id == aws_account_id,
        Recommendation.status == 'Active'
    ).all()
    potential_savings = sum(r.estimated_monthly_savings for r in active_recs)

    if monthly_cost_q > 0:
        waste_ratio = min(1.0, potential_savings / (monthly_cost_q + 1e-5))
        cost_eff_pts = round(max(5.0, 25.0 * (1.0 - (waste_ratio * 0.8))), 1)
    else:
        cost_eff_pts = 25.0
    
    if cost_eff_pts >= 22:
        explanations.append('High cost efficiency: Minimal unoptimized cloud waste detected.')
    else:
        explanations.append(f'Cost efficiency score ({cost_eff_pts}/25): /mo in identified potential optimization savings.')

    # 2. Resource Utilization (Max 25 pts)
    # Average CPU utilization across active compute & database instances
    avg_cpu_metrics = db.query(func.avg(ResourceMetric.metric_value)).filter(
        ResourceMetric.resource_id.in_(
            db.query(Resource.id).filter(
                Resource.aws_account_id == aws_account_id,
                Resource.resource_type.in_(['EC2', 'RDS'])
            )
        ),
        ResourceMetric.metric_name == 'CPUUtilization'
    ).scalar() or 50.0

    # Healthy CPU is between 25% and 80%. Penalize heavily if < 10% (idle) or > 90% (risk)
    if 25.0 <= avg_cpu_metrics <= 80.0:
        util_pts = 25.0
    elif avg_cpu_metrics < 25.0:
        util_pts = round(max(8.0, 25.0 * (avg_cpu_metrics / 25.0)), 1)
    else:
        util_pts = 20.0
    explanations.append(f'Resource utilization ({util_pts}/25): Fleet average compute/database utilization is {avg_cpu_metrics:.1f}%.')

    # 3. Optimization Opportunities (Max 20 pts)
    # Critical and High severity recommendations reduce points
    critical_recs = [r for r in active_recs if r.severity in ['Critical', 'High']]
    opt_pts = max(4.0, 20.0 - (len(critical_recs) * 3.0) - (len(active_recs) * 0.5))
    opt_pts = round(opt_pts, 1)
    explanations.append(f'Optimization backlog ({opt_pts}/20): {len(active_recs)} active recommendations ({len(critical_recs)} high-priority).')

    # 4. Budget Adherence (Max 20 pts)
    budgets = db.query(Budget).filter(Budget.aws_account_id == aws_account_id).all()
    budget_pts = 20.0
    if budgets:
        for b in budgets:
            if b.amount > 0 and monthly_cost_q > b.amount:
                budget_pts -= 8.0 # Exceeded
            elif b.amount > 0 and monthly_cost_q > (b.amount * 0.9):
                budget_pts -= 4.0 # > 90%
        budget_pts = max(5.0, budget_pts)
        explanations.append(f'Budget adherence ({budget_pts}/20): Current monthly spend is tracking within budget thresholds.')
    else:
        budget_pts = 18.0
        explanations.append('Budget adherence (18/20): No strict budget limits defined.')

    # 5. Anomaly Cleanliness (Max 10 pts)
    recent_anomalies = db.query(Anomaly).filter(
        Anomaly.aws_account_id == aws_account_id,
        Anomaly.date >= (now - datetime.timedelta(days=14))
    ).count()
    anomaly_pts = max(2.0, 10.0 - (recent_anomalies * 3.0))
    if recent_anomalies > 0:
        explanations.append(f'Anomaly health ({anomaly_pts}/10): {recent_anomalies} cost spikes detected in the last 14 days.')
    else:
        explanations.append('Anomaly health (10/10): Zero unexpected cost anomalies detected in the last 14 days.')

    overall_score = int(round(cost_eff_pts + util_pts + opt_pts + budget_pts + anomaly_pts))
    overall_score = max(0, min(100, overall_score))

    grade = 'A' if overall_score >= 90 else 'B' if overall_score >= 75 else 'C' if overall_score >= 60 else 'D' if overall_score >= 40 else 'F'

    return {
        'overall_score': overall_score,
        'grade': grade,
        'breakdown': {
            'cost_efficiency': cost_eff_pts,
            'resource_utilization': util_pts,
            'optimization_opportunities': opt_pts,
            'budget_adherence': budget_pts,
            'anomaly_health': anomaly_pts
        },
        'explanations': explanations
    }
