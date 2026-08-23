from typing import List, Dict, Any
import boto3
from app.services.aws.credentials import boto_config
from app.core.logging import logger

def discover_elastic_ips(session: boto3.Session, region: str) -> List[Dict[str, Any]]:
    results = []
    try:
        ec2 = session.client('ec2', region_name=region, config=boto_config)
        addresses = ec2.describe_addresses().get('Addresses', [])
        for addr in addresses:
            alloc_id = addr.get('AllocationId', addr.get('PublicIp'))
            public_ip = addr.get('PublicIp')
            instance_id = addr.get('InstanceId')
            association_id = addr.get('AssociationId')
            state = 'associated' if (instance_id or association_id) else 'unassociated'

            # Unassociated Elastic IPs cost ~.65/mo (.005/hr) in AWS
            est_cost = 3.65 if state == 'unassociated' else 0.0

            results.append({
                'resource_id': alloc_id,
                'resource_type': 'ElasticIP',
                'service': 'Amazon VPC',
                'region': region,
                'name': f'EIP {public_ip}',
                'state': state,
                'estimated_monthly_cost': est_cost,
                'metadata': {
                    'public_ip': public_ip,
                    'allocation_id': alloc_id,
                    'instance_id': instance_id,
                    'network_interface_id': addr.get('NetworkInterfaceId')
                }
            })
    except Exception as e:
        logger.error(f'Elastic IP discovery failed for region {region}: {e}')
    return results
