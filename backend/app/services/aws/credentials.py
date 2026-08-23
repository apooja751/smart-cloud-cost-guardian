import json
import boto3
from botocore.config import Config
from typing import Optional, Dict, Any
from app.core.security import decrypt_secret
from app.core.logging import logger

boto_config = Config(
    retries={'max_attempts': 3, 'mode': 'standard'},
    connect_timeout=5,
    read_timeout=10
)

def get_boto3_session(
    connection_type: str,
    encrypted_metadata: Optional[str] = None,
    region: str = 'us-east-1',
    role_arn: Optional[str] = None,
    external_id: Optional[str] = None,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None
) -> boto3.Session:
    # If encrypted_metadata is provided, decrypt it
    if encrypted_metadata:
        try:
            raw_meta = decrypt_secret(encrypted_metadata)
            if raw_meta:
                meta = json.loads(raw_meta)
                connection_type = meta.get('connection_type', connection_type)
                role_arn = meta.get('role_arn', role_arn)
                external_id = meta.get('external_id', external_id)
                aws_access_key_id = meta.get('aws_access_key_id', aws_access_key_id)
                aws_secret_access_key = meta.get('aws_secret_access_key', aws_secret_access_key)
                region = meta.get('region', region)
        except Exception as e:
            logger.error(f'Failed to parse connection metadata: {e}')

    if connection_type == 'ROLE_ARN' and role_arn:
        sts_client = boto3.client('sts', region_name=region, config=boto_config)
        assume_kwargs = {
            'RoleArn': role_arn,
            'RoleSessionName': 'SCCGFinOpsSession',
            'DurationSeconds': 3600
        }
        if external_id:
            assume_kwargs['ExternalId'] = external_id
        assumed = sts_client.assume_role(**assume_kwargs)
        creds = assumed['Credentials']
        return boto3.Session(
            aws_access_key_id=creds['AccessKeyId'],
            aws_secret_access_key=creds['SecretAccessKey'],
            aws_session_token=creds['SessionToken'],
            region_name=region
        )
    elif connection_type == 'ACCESS_KEY' and aws_access_key_id and aws_secret_access_key:
        return boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region
        )
    else:
        # Default environment / instance profile session
        return boto3.Session(region_name=region)
