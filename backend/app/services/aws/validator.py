import boto3
from typing import Dict, Any, List
from app.services.aws.credentials import get_boto3_session, boto_config
from app.core.logging import logger

def validate_aws_connection(
    connection_type: str,
    region: str = 'us-east-1',
    role_arn: str = None,
    external_id: str = None,
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    demo_mode: bool = False
) -> Dict[str, Any]:
    if demo_mode:
        return {
            'connected': True,
            'account_id': '123456789012',
            'validated_permissions': [
                'sts:GetCallerIdentity',
                'ec2:DescribeInstances',
                'ec2:DescribeVolumes',
                'ec2:DescribeSnapshots',
                'ec2:DescribeAddresses',
                's3:ListAllMyBuckets',
                'rds:DescribeDBInstances',
                'lambda:ListFunctions',
                'elasticloadbalancing:DescribeLoadBalancers',
                'cloudwatch:GetMetricData',
                'ce:GetCostAndUsage',
                'budgets:ViewBudget'
            ],
            'missing_permissions': [],
            'message': 'Demo Mode AWS connection validated successfully.'
        }

    validated = []
    missing = []
    account_id = 'UNKNOWN'

    try:
        session = get_boto3_session(
            connection_type=connection_type,
            region=region,
            role_arn=role_arn,
            external_id=external_id,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
    except Exception as e:
        logger.error(f'AWS Session creation failed: {e}')
        return {
            'connected': False,
            'account_id': None,
            'validated_permissions': [],
            'missing_permissions': ['Authentication Credentials'],
            'message': f'Failed to authenticate with AWS credentials: {str(e)}'
        }

    # 1. Test STS Caller Identity
    try:
        sts = session.client('sts', config=boto_config)
        ident = sts.get_caller_identity()
        account_id = ident.get('Account', 'UNKNOWN')
        validated.append('sts:GetCallerIdentity')
    except Exception as e:
        return {
            'connected': False,
            'account_id': None,
            'validated_permissions': [],
            'missing_permissions': ['sts:GetCallerIdentity'],
            'message': f'STS identity validation failed: {str(e)}'
        }

    # 2. Test EC2 DescribeInstances
    try:
        ec2 = session.client('ec2', region_name=region, config=boto_config)
        ec2.describe_instances(MaxResults=5)
        validated.append('ec2:DescribeInstances')
    except Exception as e:
        missing.append('ec2:DescribeInstances')

    # 3. Test S3 ListBuckets
    try:
        s3 = session.client('s3', region_name=region, config=boto_config)
        s3.list_buckets()
        validated.append('s3:ListAllMyBuckets')
    except Exception as e:
        missing.append('s3:ListAllMyBuckets')

    # 4. Test CloudWatch ListMetrics
    try:
        cw = session.client('cloudwatch', region_name=region, config=boto_config)
        cw.list_metrics(Namespace='AWS/EC2')
        validated.append('cloudwatch:ListMetrics')
    except Exception as e:
        missing.append('cloudwatch:ListMetrics')

    # 5. Test Cost Explorer
    try:
        ce = session.client('ce', region_name='us-east-1', config=boto_config)
        import datetime
        today = datetime.date.today()
        start = (today - datetime.timedelta(days=2)).isoformat()
        end = (today - datetime.timedelta(days=1)).isoformat()
        ce.get_cost_and_usage(
            TimePeriod={'Start': start, 'End': end},
            Granularity='DAILY',
            Metrics=['UnblendedCost']
        )
        validated.append('ce:GetCostAndUsage')
    except Exception as e:
        missing.append('ce:GetCostAndUsage')

    connected = len(validated) > 0 and 'sts:GetCallerIdentity' in validated
    msg = 'AWS Connection validated successfully' if not missing else f'Connected with some missing permissions: {missing}'

    return {
        'connected': connected,
        'account_id': account_id,
        'validated_permissions': validated,
        'missing_permissions': missing,
        'message': msg
    }
