import datetime
from datetime import timezone
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.aws_account import AWSAccount
from app.models.resource import Resource
from app.models.resource_metric import ResourceMetric
from app.models.recommendation import Recommendation
from app.services.recommendations.rules import (
    evaluate_idle_ec2,
    evaluate_stopped_ec2,
    evaluate_unattached_ebs,
    evaluate_old_snapshots,
    evaluate_unused_elastic_ip,
    evaluate_low_traffic_elb,
    evaluate_underutilized_rds,
    evaluate_s3_lifecycle
)
from app.core.logging import logger

def run_recommendation_engine(db: Session, aws_account_id: int) -> List[Recommendation]:
    account = db.query(AWSAccount).filter(AWSAccount.id == aws_account_id).first()
    if not account:
        return []

    # Query resources for this account
    resources = db.query(Resource).filter(Resource.aws_account_id == aws_account_id).all()
    generated_recs = []

    # Map average CPU utilization per resource
    cpu_metrics = db.query(
        ResourceMetric.resource_id,
        func.avg(ResourceMetric.metric_value).label('avg_cpu')
    ).filter(
        ResourceMetric.metric_name == 'CPUUtilization'
    ).group_by(ResourceMetric.resource_id).all()
    cpu_map = {r_id: float(avg_val) for r_id, avg_val in cpu_metrics}

    evaluators = [
        lambda r: evaluate_idle_ec2(r, cpu_map.get(r.id)),
        lambda r: evaluate_stopped_ec2(r),
        lambda r: evaluate_unattached_ebs(r),
        lambda r: evaluate_old_snapshots(r),
        lambda r: evaluate_unused_elastic_ip(r),
        lambda r: evaluate_low_traffic_elb(r),
        lambda r: evaluate_underutilized_rds(r, cpu_map.get(r.id)),
        lambda r: evaluate_s3_lifecycle(r)
    ]

    for res in resources:
        for ev in evaluators:
            rec_dict = ev(res)
            if rec_dict:
                # Check if recommendation already exists for this resource & title
                existing = db.query(Recommendation).filter(
                    Recommendation.aws_account_id == aws_account_id,
                    Recommendation.resource_id == res.id,
                    Recommendation.title == rec_dict['title']
                ).first()

                if not existing:
                    rec = Recommendation(
                        aws_account_id=aws_account_id,
                        resource_id=res.id,
                        category=rec_dict['category'],
                        title=rec_dict['title'],
                        description=rec_dict['description'],
                        evidence=rec_dict['evidence'],
                        estimated_monthly_savings=rec_dict['estimated_monthly_savings'],
                        estimated_yearly_savings=rec_dict['estimated_yearly_savings'],
                        confidence=rec_dict['confidence'],
                        severity=rec_dict['severity'],
                        status='Active',
                        action_notes=rec_dict.get('action_notes')
                    )
                    db.add(rec)
                    generated_recs.append(rec)
                else:
                    # Update savings and evidence
                    existing.estimated_monthly_savings = rec_dict['estimated_monthly_savings']
                    existing.estimated_yearly_savings = rec_dict['estimated_yearly_savings']
                    existing.evidence = rec_dict['evidence']
                    existing.updated_at = datetime.datetime.now(timezone.utc)
                    generated_recs.append(existing)

    db.commit()
    logger.info(f'Recommendation engine generated {len(generated_recs)} recommendations for AWS Account #{aws_account_id}.')
    return generated_recs
