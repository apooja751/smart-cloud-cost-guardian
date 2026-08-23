import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.budget import Budget
from app.models.cost import CostRecord
from app.models.alert import Alert
from app.models.aws_account import AWSAccount
from app.core.logging import logger

def evaluate_budget_alerts(db: Session, aws_account_id: int):
    account = db.query(AWSAccount).filter(AWSAccount.id == aws_account_id).first()
    if not account or not account.user_id:
        return

    budgets = db.query(Budget).filter(Budget.aws_account_id == aws_account_id).all()
    now = datetime.date.today()
    first_of_month = now.replace(day=1)

    for b in budgets:
        q = db.query(func.sum(CostRecord.amount)).filter(
            CostRecord.aws_account_id == aws_account_id,
            CostRecord.date >= first_of_month
        )
        if b.service:
            q = q.filter(CostRecord.service == b.service)
        
        current_spend = float(q.scalar() or 0.0)
        if b.amount <= 0:
            continue

        pct = (current_spend / b.amount) * 100.0

        thresholds = [
            (100.0, b.threshold_100, 'Critical', 'Budget Exceeded (100% Threshold)'),
            (90.0, b.threshold_90, 'High', 'Budget Warning: 90% Threshold Reached'),
            (75.0, b.threshold_75, 'Medium', 'Budget Notice: 75% Threshold Reached'),
            (50.0, b.threshold_50, 'Low', 'Budget Update: 50% Threshold Reached')
        ]

        for limit, enabled, severity, title in thresholds:
            if pct >= limit and enabled:
                # Check if alert for this budget & threshold already sent this month
                existing = db.query(Alert).filter(
                    Alert.user_id == account.user_id,
                    Alert.aws_account_id == aws_account_id,
                    Alert.title == f'{b.name}: {title}',
                    Alert.created_at >= datetime.datetime.combine(first_of_month, datetime.time.min)
                ).first()

                if not existing:
                    alt = Alert(
                        user_id=account.user_id,
                        aws_account_id=aws_account_id,
                        type='BUDGET_THRESHOLD',
                        title=f'{b.name}: {title}',
                        message=f'Current spending is  ({pct:.1f}% of  limit) for period {b.period}.',
                        severity=severity,
                        read=False
                    )
                    db.add(alt)
                break # Log highest breached threshold
    db.commit()
