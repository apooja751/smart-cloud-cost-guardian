from typing import List, Dict, Any
import boto3
from app.services.aws.credentials import boto_config
from app.services.aws.pricing import estimate_ec2_monthly_cost
from app.core.logging import logger

def discover_ec2_instances(session: boto3.Session, region: str) -> List[Dict[str, Any]]:
    results = []
    try:
        ec2 = session.client('ec2', region_name=region, config=boto_config)
        paginator = ec2.get_paginator('describe_instances')
        for page in paginator.paginate():
            for res in page.get('Reservations', []):
                for inst in res.get('Instances', []):
                    instance_id = inst.get('InstanceId')
                    instance_type = inst.get('InstanceType', 't3.micro')
                    state = inst.get('State', {}).get('Name', 'unknown')
                    launch_time = inst.get('LaunchTime').isoformat() if inst.get('LaunchTime') else None
                    tags = {t.get('Key'): t.get('Value') for t in inst.get('Tags', [])}
                    name = tags.get('Name', instance_id)

                    est_cost = estimate_ec2_monthly_cost(instance_type) if state == 'running' else 0.0

                    results.append({
                        'resource_id': instance_id,
                        'resource_type': 'EC2',
                        'service': 'Amazon EC2',
                        'region': region,
                        'name': name,
                        'state': state,
                        'estimated_monthly_cost': est_cost,
                        'metadata': {
                            'instance_type': instance_type,
                            'launch_time': launch_time,
                            'public_ip': inst.get('PublicIpAddress'),
                            'private_ip': inst.get('PrivateIpAddress'),
                            'availability_zone': inst.get('Placement', {}).get('AvailabilityZone'),
                            'tags': tags,
                            'block_devices': [bd.get('Ebs', {}).get('VolumeId') for bd in inst.get('BlockDeviceMappings', [])]
                        }
                    })
    except Exception as e:
        logger.error(f'EC2 discovery failed for region {region}: {e}')
    return results
