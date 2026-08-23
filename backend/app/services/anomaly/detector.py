import datetime
from typing import List
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.cost import CostRecord
from app.models.anomaly import Anomaly
from app.models.alert import Alert
from app.models.aws_account import AWSAccount
from app.core.logging import logger

def detect_cost_anomalies(db: Session, aws_account_id: int) -> List[Anomaly]:
    # Query daily costs per service for the last 45 days
    records = db.query(
        CostRecord.service,
        CostRecord.date,
        CostRecord.amount
    ).filter(
        CostRecord.aws_account_id == aws_account_id
    ).order_by(CostRecord.date.asc()).all()

    if len(records) < 10:
        return []

    df = pd.DataFrame([{'service': r[0], 'date': r[1], 'amount': float(r[2])} for r in records])
    detected = []
    account = db.query(AWSAccount).filter(AWSAccount.id == aws_account_id).first()

    for service, group in df.groupby('service'):
        if len(group) < 7:
            continue
        
        group = group.sort_values('date')
        # Calculate 14-day rolling mean & std
        rolling_mean = group['amount'].rolling(window=14, min_periods=5).mean()
        rolling_std = group['amount'].rolling(window=14, min_periods=5).std().fillna(1.0)

        for i in range(len(group)):
            row = group.iloc[i]
            mean_val = rolling_mean.iloc[i]
            std_val = rolling_std.iloc[i]
            actual = row['amount']
            dt = row['date']

            if pd.isna(mean_val) or mean_val <= 0.5:
                continue

            # If actual > mean + 2.5 * std or percentage increase > 50% with absolute increase > 
            diff = actual - mean_val
            pct_dev = (diff / mean_val) * 100.0

            if diff > 15.0 and (actual > mean_val + (2.2 * std_val) or pct_dev > 50.0):
                severity = 'Critical' if pct_dev > 150.0 else 'High' if pct_dev > 75.0 else 'Medium'
                
                # Check if already logged
                existing = db.query(Anomaly).filter(
                    Anomaly.aws_account_id == aws_account_id,
                    Anomaly.service == service,
                    Anomaly.date == dt
                ).first()

                if not existing:
                    anom = Anomaly(
                        aws_account_id=aws_account_id,
                        service=service,
                        date=dt,
                        expected_cost=round(mean_val, 2),
                        actual_cost=round(actual, 2),
                        deviation=round(pct_dev, 2),
                        severity=severity,
                        status='Detected'
                    )
                    db.add(anom)
                    detected.append(anom)

                    # Trigger alert for this anomaly
                    if account and account.user_id:
                        alt = Alert(
                            user_id=account.user_id,
                            aws_account_id=aws_account_id,
                            type='COST_ANOMALY',
                            title=f'Cost Surge Detected on {service}',
                            message=f'Spend surged to  (+{pct_dev:.1f}% deviation from expected ) on {dt}.',
                            severity=severity,
                            read=False
                        )
                        db.add(alt)

    db.commit()
    logger.info(f'Anomaly detection found {len(detected)} new anomalies for AWS Account #{aws_account_id}.')
    return detected
