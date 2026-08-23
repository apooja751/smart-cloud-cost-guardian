import datetime
from datetime import timezone
from typing import List, Dict, Any
import boto3
from app.services.aws.credentials import boto_config
from app.core.logging import logger

def fetch_cost_explorer_data(session: boto3.Session, days: int = 30) -> List[Dict[str, Any]]:
    records = []
    try:
        ce = session.client('ce', region_name='us-east-1', config=boto_config)
        today = datetime.date.today()
        start = (today - datetime.timedelta(days=days)).isoformat()
        end = today.isoformat()

        response = ce.get_cost_and_usage(
            TimePeriod={'Start': start, 'End': end},
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ]
        )

        for result_by_time in response.get('ResultsByTime', []):
            time_str = result_by_time.get('TimePeriod', {}).get('Start')
            record_date = datetime.date.fromisoformat(time_str)
            for group in result_by_time.get('Groups', []):
                service_name = group.get('Keys', ['Other'])[0]
                metrics = group.get('Metrics', {}).get('UnblendedCost', {})
                amount = float(metrics.get('Amount', 0.0))
                currency = metrics.get('Unit', 'USD')
                if amount > 0.001:
                    records.append({
                        'service': service_name,
                        'region': 'global',
                        'amount': round(amount, 4),
                        'currency': currency,
                        'date': record_date
                    })
    except Exception as e:
        logger.error(f'Cost Explorer data collection failed: {e}')
    return records
