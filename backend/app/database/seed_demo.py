import json
import random
import datetime
from datetime import timezone
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.aws_account import AWSAccount
from app.models.resource import Resource
from app.models.resource_metric import ResourceMetric
from app.models.cost import CostRecord
from app.models.recommendation import Recommendation
from app.models.budget import Budget
from app.models.alert import Alert
from app.models.forecast import Forecast
from app.models.anomaly import Anomaly
from app.core.security import get_password_hash
from app.core.logging import logger

def seed_demo_data(db: Session) -> Dict[str, Any]:
    # 1. Check or create default admin/user
    admin = db.query(User).filter(User.email == 'admin@guardian.io').first()
    if not admin:
        admin = User(
            name='Cloud FinOps Admin',
            email='admin@guardian.io',
            password_hash=get_password_hash('Admin@123456'),
            role='ADMIN',
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    demo_user = db.query(User).filter(User.email == 'demo@guardian.io').first()
    if not demo_user:
        demo_user = User(
            name='FinOps Lead Engineer',
            email='demo@guardian.io',
            password_hash=get_password_hash('Demo@123456'),
            role='USER',
            is_active=True
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

    target_user = demo_user

    # 2. Check or create demo AWS Account
    aws_acc = db.query(AWSAccount).filter(AWSAccount.user_id == target_user.id, AWSAccount.account_id == '123456789012').first()
    if not aws_acc:
        aws_acc = AWSAccount(
            user_id=target_user.id,
            account_id='123456789012',
            account_name='Production & Staging Main AWS',
            region='us-east-1',
            connection_type='DEMO',
            status='Connected',
            last_sync_at=datetime.datetime.now(timezone.utc)
        )
        db.add(aws_acc)
        db.commit()
        db.refresh(aws_acc)

    # Clean existing data for this demo account to avoid stale duplicates
    db.query(ResourceMetric).filter(ResourceMetric.resource_id.in_([r.id for r in aws_acc.resources])).delete(synchronize_session=False)
    db.query(Recommendation).filter(Recommendation.aws_account_id == aws_acc.id).delete(synchronize_session=False)
    db.query(Resource).filter(Resource.aws_account_id == aws_acc.id).delete(synchronize_session=False)
    db.query(CostRecord).filter(CostRecord.aws_account_id == aws_acc.id).delete(synchronize_session=False)
    db.query(Budget).filter(Budget.aws_account_id == aws_acc.id).delete(synchronize_session=False)
    db.query(Alert).filter(Alert.aws_account_id == aws_acc.id).delete(synchronize_session=False)
    db.query(Forecast).filter(Forecast.aws_account_id == aws_acc.id).delete(synchronize_session=False)
    db.query(Anomaly).filter(Anomaly.aws_account_id == aws_acc.id).delete(synchronize_session=False)
    db.commit()

    now = datetime.datetime.now(timezone.utc)

    # 3. Seed Realistic Cloud Resources
    resources_spec = [
        # Idle EC2 instances (Waste)
        {
            'resource_id': 'i-0a89f3c1d2e4a1101', 'resource_type': 'EC2', 'service': 'Amazon EC2', 'region': 'us-east-1',
            'name': 'staging-api-server-legacy', 'state': 'running', 'estimated_monthly_cost': 242.94, # m5.xlarge
            'metadata': {'instance_type': 'm5.xlarge', 'az': 'us-east-1a', 'avg_cpu': 2.1, 'tags': {'Env': 'Staging', 'Team': 'Backend'}}
        },
        {
            'resource_id': 'i-0b78e2d4f5c6a2202', 'resource_type': 'EC2', 'service': 'Amazon EC2', 'region': 'us-east-1',
            'name': 'analytics-worker-idle', 'state': 'running', 'estimated_monthly_cost': 280.32, # c5.2xlarge
            'metadata': {'instance_type': 'c5.2xlarge', 'az': 'us-east-1b', 'avg_cpu': 1.8, 'tags': {'Env': 'Dev', 'Project': 'BatchAnalytics'}}
        },
        # Active Normal EC2 instances
        {
            'resource_id': 'i-0c12d3e4f5a6b3303', 'resource_type': 'EC2', 'service': 'Amazon EC2', 'region': 'us-east-1',
            'name': 'prod-k8s-worker-node-1', 'state': 'running', 'estimated_monthly_cost': 140.16, # m5.large
            'metadata': {'instance_type': 'm5.large', 'az': 'us-east-1a', 'avg_cpu': 68.4, 'tags': {'Env': 'Production', 'Cluster': 'EKS-Core'}}
        },
        {
            'resource_id': 'i-0d23e4f5a6b7c4404', 'resource_type': 'EC2', 'service': 'Amazon EC2', 'region': 'us-east-1',
            'name': 'prod-k8s-worker-node-2', 'state': 'running', 'estimated_monthly_cost': 140.16, # m5.large
            'metadata': {'instance_type': 'm5.large', 'az': 'us-east-1b', 'avg_cpu': 72.1, 'tags': {'Env': 'Production', 'Cluster': 'EKS-Core'}}
        },
        # Stopped EC2 instance incurring EBS cost (Waste)
        {
            'resource_id': 'i-0e34f5a6b7c8d5505', 'resource_type': 'EC2', 'service': 'Amazon EC2', 'region': 'us-east-1',
            'name': 'temp-migration-host-2025', 'state': 'stopped', 'estimated_monthly_cost': 40.00, # storage cost
            'metadata': {'instance_type': 'r5.large', 'stopped_days': 45, 'tags': {'Owner': 'David', 'Note': 'Migration finished in Dec'}}
        },
        # Unattached EBS Volumes (Waste)
        {
            'resource_id': 'vol-08492048f0293a11', 'resource_type': 'EBS', 'service': 'Amazon EBS', 'region': 'us-east-1',
            'name': 'unattached-analytics-dump-gp3', 'state': 'available', 'estimated_monthly_cost': 80.00, # 1000GB gp3
            'metadata': {'size_gb': 1000, 'volume_type': 'gp3', 'attached_instance': None, 'unattached_days': 62}
        },
        {
            'resource_id': 'vol-0938472918392b22', 'resource_type': 'EBS', 'service': 'Amazon EBS', 'region': 'us-east-1',
            'name': 'old-db-backup-volume-io1', 'state': 'available', 'estimated_monthly_cost': 62.50, # 500GB io1
            'metadata': {'size_gb': 500, 'volume_type': 'io1', 'attached_instance': None, 'unattached_days': 88}
        },
        # Active attached EBS
        {
            'resource_id': 'vol-0123456789abcdef0', 'resource_type': 'EBS', 'service': 'Amazon EBS', 'region': 'us-east-1',
            'name': 'prod-k8s-root-vol-1', 'state': 'in-use', 'estimated_monthly_cost': 16.00,
            'metadata': {'size_gb': 200, 'volume_type': 'gp3', 'attached_instance': 'i-0c12d3e4f5a6b3303'}
        },
        # Old Snapshots (Waste)
        {
            'resource_id': 'snap-0192837465abc123', 'resource_type': 'Snapshot', 'service': 'Amazon EBS', 'region': 'us-east-1',
            'name': 'pre-upgrade-db-backup-snapshot', 'state': 'completed', 'estimated_monthly_cost': 50.00,
            'metadata': {'volume_size_gb': 1000, 'age_days': 140, 'description': 'Pre-upgrade snapshot from old RDS'}
        },
        {
            'resource_id': 'snap-0827364519def456', 'resource_type': 'Snapshot', 'service': 'Amazon EBS', 'region': 'us-east-1',
            'name': 'archive-scratch-disk-snap', 'state': 'completed', 'estimated_monthly_cost': 25.00,
            'metadata': {'volume_size_gb': 500, 'age_days': 95, 'description': 'Scratch disk snapshot'}
        },
        # Unused Elastic IP (Waste)
        {
            'resource_id': 'eipalloc-0a1b2c3d4e5f6071', 'resource_type': 'ElasticIP', 'service': 'Amazon VPC', 'region': 'us-east-1',
            'name': 'EIP 54.210.88.192', 'state': 'unassociated', 'estimated_monthly_cost': 3.65,
            'metadata': {'public_ip': '54.210.88.192', 'allocation_id': 'eipalloc-0a1b2c3d4e5f6071'}
        },
        # S3 Buckets (Waste: Missing Lifecycle on big bucket)
        {
            'resource_id': 'sccg-corporate-datalake-logs-raw', 'resource_type': 'S3', 'service': 'Amazon S3', 'region': 'us-east-1',
            'name': 'sccg-corporate-datalake-logs-raw', 'state': 'active', 'estimated_monthly_cost': 345.00,
            'metadata': {'size_gb': 15000, 'has_lifecycle_rules': False, 'storage_class': 'STANDARD'}
        },
        {
            'resource_id': 'sccg-prod-app-assets-cdn', 'resource_type': 'S3', 'service': 'Amazon S3', 'region': 'us-east-1',
            'name': 'sccg-prod-app-assets-cdn', 'state': 'active', 'estimated_monthly_cost': 45.00,
            'metadata': {'size_gb': 2000, 'has_lifecycle_rules': True, 'storage_class': 'STANDARD'}
        },
        # RDS Instances (Waste: Overprovisioned dev DB)
        {
            'resource_id': 'staging-postgres-cluster', 'resource_type': 'RDS', 'service': 'Amazon RDS', 'region': 'us-east-1',
            'name': 'staging-postgres-cluster', 'state': 'available', 'estimated_monthly_cost': 519.76, # db.r5.2xlarge Multi-AZ
            'metadata': {'instance_class': 'db.r5.2xlarge', 'engine': 'postgres', 'multi_az': True, 'avg_cpu': 4.2, 'avg_connections': 3}
        },
        {
            'resource_id': 'prod-aurora-postgres-primary', 'resource_type': 'RDS', 'service': 'Amazon RDS', 'region': 'us-east-1',
            'name': 'prod-aurora-postgres-primary', 'state': 'available', 'estimated_monthly_cost': 350.40,
            'metadata': {'instance_class': 'db.r5.large', 'engine': 'aurora-postgresql', 'multi_az': True, 'avg_cpu': 65.0, 'avg_connections': 180}
        },
        # Low Traffic Load Balancer (Waste)
        {
            'resource_id': 'alb-internal-dev-gateway', 'resource_type': 'ELB', 'service': 'Elastic Load Balancing', 'region': 'us-east-1',
            'name': 'alb-internal-dev-gateway', 'state': 'active', 'estimated_monthly_cost': 24.50,
            'metadata': {'type': 'application', 'target_count': 0, 'healthy_target_count': 0, 'req_count_7d': 12}
        },
        # Lambda Functions
        {
            'resource_id': 'payment-webhook-processor', 'resource_type': 'Lambda', 'service': 'AWS Lambda', 'region': 'us-east-1',
            'name': 'payment-webhook-processor', 'state': 'active', 'estimated_monthly_cost': 12.40,
            'metadata': {'runtime': 'python3.11', 'memory_mb': 1024, 'timeout_seconds': 30, 'avg_duration_ms': 85}
        }
    ]

    db_resources = []
    for spec in resources_spec:
        res = Resource(
            aws_account_id=aws_acc.id,
            resource_id=spec['resource_id'],
            resource_type=spec['resource_type'],
            service=spec['service'],
            region=spec['region'],
            name=spec['name'],
            state=spec['state'],
            estimated_monthly_cost=spec['estimated_monthly_cost'],
            metadata_json=json.dumps(spec['metadata']),
            first_seen_at=now - datetime.timedelta(days=90),
            last_seen_at=now
        )
        db.add(res)
        db_resources.append(res)
    db.commit()

    # 4. Seed CloudWatch Utilization Metrics for Resources
    for res in db_resources:
        meta = json.loads(res.metadata_json or '{}')
        if res.resource_type == 'EC2':
            avg_cpu = meta.get('avg_cpu', 50.0)
            for i in range(14):
                ts = now - datetime.timedelta(days=14 - i)
                val = max(0.5, avg_cpu + random.uniform(-1.5, 1.5))
                m = ResourceMetric(
                    resource_id=res.id,
                    metric_name='CPUUtilization',
                    metric_value=round(val, 2),
                    timestamp=ts
                )
                db.add(m)
        elif res.resource_type == 'RDS':
            avg_cpu = meta.get('avg_cpu', 40.0)
            for i in range(14):
                ts = now - datetime.timedelta(days=14 - i)
                val = max(1.0, avg_cpu + random.uniform(-2.0, 2.0))
                m = ResourceMetric(
                    resource_id=res.id,
                    metric_name='CPUUtilization',
                    metric_value=round(val, 2),
                    timestamp=ts
                )
                db.add(m)
    db.commit()

    # 5. Seed Historical 90-Day Cost Records with Service Breakdown and deliberate recent spike for Anomaly Detection
    services_base_cost = {
        'Amazon Elastic Compute Cloud - Compute': 28.50,
        'Amazon Relational Database Service': 29.00,
        'Amazon Simple Storage Service': 13.00,
        'Amazon Elastic Block Store': 7.50,
        'Elastic Load Balancing': 1.60,
        'AWS Lambda': 0.80,
        'Amazon VPC': 0.40
    }

    start_date = (now - datetime.timedelta(days=60)).date()
    today_date = now.date()

    curr_date = start_date
    while curr_date <= today_date:
        day_offset = (curr_date - start_date).days
        growth_factor = 1.0 + (day_offset * 0.002) # Gentle 0.2% daily growth
        
        for svc, base in services_base_cost.items():
            daily_amount = base * growth_factor * random.uniform(0.95, 1.05)

            # Insert deliberate cost anomaly 4 days ago on EC2 (e.g., untagged batch runaway)
            if curr_date == (today_date - datetime.timedelta(days=4)) and 'Elastic Compute Cloud' in svc:
                daily_amount = base * 2.85 # +185% anomaly spike!

            cr = CostRecord(
                aws_account_id=aws_acc.id,
                service=svc,
                region='us-east-1',
                amount=round(daily_amount, 2),
                currency='USD',
                date=curr_date
            )
            db.add(cr)
        curr_date += datetime.timedelta(days=1)
    db.commit()

    # 6. Seed Budgets
    b1 = Budget(
        aws_account_id=aws_acc.id,
        name='Monthly Total AWS Spend Target',
        amount=2800.00,
        currency='USD',
        period='MONTHLY',
        threshold_50=True,
        threshold_75=True,
        threshold_90=True,
        threshold_100=True
    )
    b2 = Budget(
        aws_account_id=aws_acc.id,
        name='EC2 Compute Budget Guardrail',
        amount=1100.00,
        currency='USD',
        period='MONTHLY',
        service='Amazon Elastic Compute Cloud - Compute',
        threshold_50=True,
        threshold_75=True,
        threshold_90=True,
        threshold_100=True
    )
    db.add_all([b1, b2])
    db.commit()

    # 7. Seed Initial Alerts
    a1 = Alert(
        user_id=target_user.id,
        aws_account_id=aws_acc.id,
        type='COST_ANOMALY',
        title='Cost Anomaly Detected on EC2 Compute',
        message='Daily spend on Amazon EC2 surged to .22 (185% above the 14-day baseline of .50). Review active batch workers.',
        severity='High',
        read=False,
        created_at=now - datetime.timedelta(days=4)
    )
    a2 = Alert(
        user_id=target_user.id,
        aws_account_id=aws_acc.id,
        type='BUDGET_THRESHOLD',
        title='Monthly Total AWS Spend reached 85% of Budget',
        message='Current monthly spending has reached ,380.50 of your ,800.00 budget target.',
        severity='Medium',
        read=False,
        created_at=now - datetime.timedelta(days=1)
    )
    a3 = Alert(
        user_id=target_user.id,
        aws_account_id=aws_acc.id,
        type='IDLE_RESOURCE',
        title='Multiple Unattached EBS Volumes Incurring Charges',
        message='Discovered 2 unattached EBS volumes (1,500 GB total) costing .50/month in idle state.',
        severity='High',
        read=False,
        created_at=now - datetime.timedelta(hours=6)
    )
    db.add_all([a1, a2, a3])
    db.commit()

    # Automatically run recommendation engine to populate FinOps findings
    from app.services.recommendations.engine import run_recommendation_engine
    run_recommendation_engine(db, aws_acc.id)

    logger.info('Demo dataset seeded successfully.')
    return {'status': 'success', 'user_email': target_user.email, 'account_id': aws_acc.account_id}
