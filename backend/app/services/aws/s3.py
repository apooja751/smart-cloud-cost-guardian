from typing import List, Dict, Any
import boto3
from app.services.aws.credentials import boto_config
from app.core.logging import logger

def discover_s3_buckets(session: boto3.Session, default_region: str = 'us-east-1') -> List[Dict[str, Any]]:
    results = []
    try:
        s3 = session.client('s3', region_name=default_region, config=boto_config)
        buckets = s3.list_buckets().get('Buckets', [])

        for b in buckets:
            b_name = b.get('Name')
            creation_date = b.get('CreationDate').isoformat() if b.get('CreationDate') else None

            # Get bucket location
            region = default_region
            try:
                loc = s3.get_bucket_location(Bucket=b_name).get('LocationConstraint')
                if loc:
                    region = loc
            except Exception:
                pass

            # Check lifecycle configuration
            has_lifecycle = False
            try:
                lc = s3.get_bucket_lifecycle_configuration(Bucket=b_name)
                if lc.get('Rules'):
                    has_lifecycle = True
            except Exception:
                has_lifecycle = False

            # Check tagging
            tags = {}
            try:
                tag_set = s3.get_bucket_tagging(Bucket=b_name).get('TagSet', [])
                tags = {t.get('Key'): t.get('Value') for t in tag_set}
            except Exception:
                pass

            # Base placeholder cost (will be refined by Cost Explorer if available)
            est_cost = 15.00

            results.append({
                'resource_id': b_name,
                'resource_type': 'S3',
                'service': 'Amazon S3',
                'region': region,
                'name': b_name,
                'state': 'active',
                'estimated_monthly_cost': est_cost,
                'metadata': {
                    'creation_date': creation_date,
                    'has_lifecycle_rules': has_lifecycle,
                    'tags': tags
                }
            })
    except Exception as e:
        logger.error(f'S3 discovery failed: {e}')
    return results
