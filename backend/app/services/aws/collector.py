import json
import datetime
from datetime import timezone
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.aws_account import AWSAccount
from app.models.resource import Resource
from app.models.cost import CostRecord
from app.services.aws.credentials import get_boto3_session
from app.services.aws.ec2 import discover_ec2_instances
from app.services.aws.ebs import discover_ebs_volumes
from app.services.aws.elastic_ip import discover_elastic_ips
from app.services.aws.snapshots import discover_ebs_snapshots
from app.services.aws.s3 import discover_s3_buckets
from app.services.aws.rds import discover_rds_instances
from app.services.aws.lambda_svc import discover_lambda_functions
from app.services.aws.elb import discover_load_balancers
from app.services.aws.cost_explorer import fetch_cost_explorer_data
from app.services.recommendations.engine import run_recommendation_engine
from app.services.forecasting.forecaster import generate_cost_forecast
from app.services.anomaly.detector import detect_cost_anomalies
from app.services.notifications.dispatcher import evaluate_budget_alerts
from app.database.seed_demo import seed_demo_data
from app.core.logging import logger

def synchronize_aws_account(db: Session, aws_account_id: int) -> Dict[str, Any]:
    account = db.query(AWSAccount).filter(AWSAccount.id == aws_account_id).first()
    if not account:
        return {'success': False, 'message': 'Account not found'}

    account.status = 'Synchronizing'
    db.commit()

    try:
        if account.connection_type == 'DEMO':
            seed_demo_data(db)
            account.status = 'Connected'
            account.last_sync_at = datetime.datetime.now(timezone.utc)
            db.commit()

            # Run analytical intelligence
            run_recommendation_engine(db, aws_account_id)
            generate_cost_forecast(db, aws_account_id)
            detect_cost_anomalies(db, aws_account_id)
            evaluate_budget_alerts(db, aws_account_id)

            return {'success': True, 'message': 'Demo AWS account synchronized successfully.'}

        # Real AWS Sync
        session = get_boto3_session(
            connection_type=account.connection_type,
            encrypted_metadata=account.encrypted_connection_metadata,
            region=account.region
        )

        all_resources = []
        # Run discoverers with non-blocking error boundaries
        discoverers = [
            ('EC2', lambda: discover_ec2_instances(session, account.region)),
            ('EBS', lambda: discover_ebs_volumes(session, account.region)),
            ('EIP', lambda: discover_elastic_ips(session, account.region)),
            ('Snapshots', lambda: discover_ebs_snapshots(session, account.region)),
            ('S3', lambda: discover_s3_buckets(session, account.region)),
            ('RDS', lambda: discover_rds_instances(session, account.region)),
            ('Lambda', lambda: discover_lambda_functions(session, account.region)),
            ('ELB', lambda: discover_load_balancers(session, account.region)),
        ]

        for svc_name, fn in discoverers:
            try:
                res_list = fn()
                all_resources.extend(res_list)
            except Exception as e:
                logger.error(f'Service discovery error on {svc_name}: {e}')

        now = datetime.datetime.now(timezone.utc)

        # Upsert discovered resources in DB
        for item in all_resources:
            r = db.query(Resource).filter(
                Resource.aws_account_id == account.id,
                Resource.resource_id == item['resource_id']
            ).first()

            if not r:
                r = Resource(
                    aws_account_id=account.id,
                    resource_id=item['resource_id'],
                    resource_type=item['resource_type'],
                    service=item['service'],
                    region=item['region'],
                    name=item['name'],
                    state=item['state'],
                    metadata_json=json.dumps(item.get('metadata', {})),
                    estimated_monthly_cost=item.get('estimated_monthly_cost', 0.0),
                    first_seen_at=now,
                    last_seen_at=now
                )
                db.add(r)
            else:
                r.state = item['state']
                r.name = item['name']
                r.metadata_json = json.dumps(item.get('metadata', {}))
                r.estimated_monthly_cost = item.get('estimated_monthly_cost', r.estimated_monthly_cost)
                r.last_seen_at = now
        db.commit()

        # Cost Explorer Sync
        try:
            costs = fetch_cost_explorer_data(session, days=30)
            for c in costs:
                cr = db.query(CostRecord).filter(
                    CostRecord.aws_account_id == account.id,
                    CostRecord.service == c['service'],
                    CostRecord.date == c['date']
                ).first()
                if not cr:
                    cr = CostRecord(
                        aws_account_id=account.id,
                        service=c['service'],
                        region=c['region'],
                        amount=c['amount'],
                        currency=c['currency'],
                        date=c['date']
                    )
                    db.add(cr)
                else:
                    cr.amount = c['amount']
            db.commit()
        except Exception as e:
            logger.warning(f'Cost Explorer sync error: {e}')

        # Run FinOps analytics
        run_recommendation_engine(db, account.id)
        generate_cost_forecast(db, account.id)
        detect_cost_anomalies(db, account.id)
        evaluate_budget_alerts(db, account.id)

        account.status = 'Connected'
        account.last_sync_at = datetime.datetime.now(timezone.utc)
        db.commit()

        return {'success': True, 'discovered_count': len(all_resources), 'message': f'Discovered {len(all_resources)} AWS resources.'}

    except Exception as e:
        logger.error(f'Full sync failed for account #{aws_account_id}: {e}')
        account.status = 'Failed'
        db.commit()
        return {'success': False, 'message': f'Synchronization failed: {str(e)}'}
