from typing import List, Dict, Any
import boto3
from app.services.aws.credentials import boto_config
from app.core.logging import logger

def discover_lambda_functions(session: boto3.Session, region: str) -> List[Dict[str, Any]]:
    results = []
    try:
        lam = session.client('lambda', region_name=region, config=boto_config)
        paginator = lam.get_paginator('list_functions')
        for page in paginator.paginate():
            for fn in page.get('Functions', []):
                fn_name = fn.get('FunctionName')
                runtime = fn.get('Runtime', 'python3.11')
                memory = fn.get('MemorySize', 128)
                timeout = fn.get('Timeout', 3)
                last_modified = fn.get('LastModified')

                results.append({
                    'resource_id': fn_name,
                    'resource_type': 'Lambda',
                    'service': 'AWS Lambda',
                    'region': region,
                    'name': fn_name,
                    'state': 'active',
                    'estimated_monthly_cost': 5.00,
                    'metadata': {
                        'runtime': runtime,
                        'memory_mb': memory,
                        'timeout_seconds': timeout,
                        'last_modified': last_modified,
                        'arn': fn.get('FunctionArn')
                    }
                })
    except Exception as e:
        logger.error(f'Lambda discovery failed for region {region}: {e}')
    return results
