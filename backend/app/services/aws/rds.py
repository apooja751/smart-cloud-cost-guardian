from typing import List, Dict, Any
import boto3
from app.services.aws.credentials import boto_config
from app.services.aws.pricing import estimate_rds_monthly_cost
from app.core.logging import logger

def discover_rds_instances(session: boto3.Session, region: str) -> List[Dict[str, Any]]:
    results = []
    try:
        rds = session.client('rds', region_name=region, config=boto_config)
        paginator = rds.get_paginator('describe_db_instances')
        for page in paginator.paginate():
            for db in page.get('DBInstances', []):
                db_id = db.get('DBInstanceIdentifier')
                instance_class = db.get('DBInstanceClass', 'db.t3.micro')
                engine = db.get('Engine', 'postgres')
                status = db.get('DBInstanceStatus', 'available')
                multi_az = db.get('MultiAZ', False)
                storage_gb = db.get('AllocatedStorage', 20)

                est_cost = estimate_rds_monthly_cost(instance_class, multi_az)

                results.append({
                    'resource_id': db_id,
                    'resource_type': 'RDS',
                    'service': 'Amazon RDS',
                    'region': region,
                    'name': db_id,
                    'state': status,
                    'estimated_monthly_cost': est_cost,
                    'metadata': {
                        'engine': engine,
                        'instance_class': instance_class,
                        'multi_az': multi_az,
                        'allocated_storage_gb': storage_gb,
                        'storage_type': db.get('StorageType', 'gp2'),
                        'endpoint': db.get('Endpoint', {}).get('Address'),
                        'publicly_accessible': db.get('PubliclyAccessible', False)
                    }
                })
    except Exception as e:
        logger.error(f'RDS discovery failed for region {region}: {e}')
    return results
