from typing import List, Dict, Any
import datetime
from datetime import timezone
import boto3
from app.services.aws.credentials import boto_config
from app.services.aws.pricing import estimate_snapshot_monthly_cost
from app.core.logging import logger

def discover_ebs_snapshots(session: boto3.Session, region: str) -> List[Dict[str, Any]]:
    results = []
    try:
        ec2 = session.client('ec2', region_name=region, config=boto_config)
        # Only query self-owned snapshots
        snaps = ec2.describe_snapshots(OwnerIds=['self']).get('Snapshots', [])
        now = datetime.datetime.now(timezone.utc)

        for s in snaps:
            snap_id = s.get('SnapshotId')
            volume_id = s.get('VolumeId')
            volume_size = s.get('VolumeSize', 0)
            start_time = s.get('StartTime')
            age_days = (now - start_time).days if start_time else 0
            tags = {t.get('Key'): t.get('Value') for t in s.get('Tags', [])}
            name = tags.get('Name', snap_id)

            est_cost = estimate_snapshot_monthly_cost(volume_size)

            results.append({
                'resource_id': snap_id,
                'resource_type': 'Snapshot',
                'service': 'Amazon EBS',
                'region': region,
                'name': name,
                'state': s.get('State', 'completed'),
                'estimated_monthly_cost': est_cost,
                'metadata': {
                    'volume_id': volume_id,
                    'volume_size_gb': volume_size,
                    'age_days': age_days,
                    'start_time': start_time.isoformat() if start_time else None,
                    'description': s.get('Description'),
                    'tags': tags
                }
            })
    except Exception as e:
        logger.error(f'Snapshots discovery failed for region {region}: {e}')
    return results
