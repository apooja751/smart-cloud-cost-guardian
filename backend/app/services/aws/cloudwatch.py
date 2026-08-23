import datetime
from datetime import timezone
from typing import List, Dict, Any, Optional
import boto3
from app.services.aws.credentials import boto_config
from app.core.logging import logger

def fetch_metric_statistics(
    session: boto3.Session,
    region: str,
    namespace: str,
    metric_name: str,
    dimension_name: str,
    dimension_value: str,
    days: int = 7
) -> List[Dict[str, Any]]:
    results = []
    try:
        cw = session.client('cloudwatch', region_name=region, config=boto_config)
        now = datetime.datetime.now(timezone.utc)
        start_time = now - datetime.timedelta(days=days)

        resp = cw.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=[{'Name': dimension_name, 'Value': dimension_value}],
            StartTime=start_time,
            EndTime=now,
            Period=86400, # 1 day aggregate
            Statistics=['Average', 'Maximum']
        )
        for dp in sorted(resp.get('Datapoints', []), key=lambda x: x['Timestamp']):
            results.append({
                'metric_name': metric_name,
                'metric_value': round(dp.get('Average', 0.0), 2),
                'max_value': round(dp.get('Maximum', 0.0), 2),
                'timestamp': dp.get('Timestamp')
            })
    except Exception as e:
        logger.warning(f'CloudWatch metric fetch failed for {metric_name} ({dimension_value}): {e}')
    return results
