from typing import List, Dict, Any
import boto3
from app.services.aws.credentials import boto_config
from app.services.aws.pricing import estimate_ebs_monthly_cost
from app.core.logging import logger

def discover_ebs_volumes(session: boto3.Session, region: str) -> List[Dict[str, Any]]:
    results = []
    try:
        ec2 = session.client('ec2', region_name=region, config=boto_config)
        paginator = ec2.get_paginator('describe_volumes')
        for page in paginator.paginate():
            for vol in page.get('Volumes', []):
                vol_id = vol.get('VolumeId')
                size = vol.get('Size', 0)
                vol_type = vol.get('VolumeType', 'gp3')
                state = vol.get('State', 'unknown')
                create_time = vol.get('CreateTime').isoformat() if vol.get('CreateTime') else None
                tags = {t.get('Key'): t.get('Value') for t in vol.get('Tags', [])}
                name = tags.get('Name', vol_id)

                attachments = vol.get('Attachments', [])
                attached_instance = attachments[0].get('InstanceId') if attachments else None

                est_cost = estimate_ebs_monthly_cost(vol_type, size)

                results.append({
                    'resource_id': vol_id,
                    'resource_type': 'EBS',
                    'service': 'Amazon EBS',
                    'region': region,
                    'name': name,
                    'state': state, # 'available' = unattached, 'in-use' = attached
                    'estimated_monthly_cost': est_cost,
                    'metadata': {
                        'size_gb': size,
                        'volume_type': vol_type,
                        'attached_instance': attached_instance,
                        'create_time': create_time,
                        'iops': vol.get('Iops'),
                        'encrypted': vol.get('Encrypted', False),
                        'tags': tags
                    }
                })
    except Exception as e:
        logger.error(f'EBS discovery failed for region {region}: {e}')
    return results
