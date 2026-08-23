from typing import List, Dict, Any
import boto3
from app.services.aws.credentials import boto_config
from app.services.aws.pricing import estimate_alb_monthly_cost
from app.core.logging import logger

def discover_load_balancers(session: boto3.Session, region: str) -> List[Dict[str, Any]]:
    results = []
    try:
        elbv2 = session.client('elbv2', region_name=region, config=boto_config)
        paginator = elbv2.get_paginator('describe_load_balancers')
        for page in paginator.paginate():
            for lb in page.get('LoadBalancers', []):
                lb_name = lb.get('LoadBalancerName')
                lb_arn = lb.get('LoadBalancerArn')
                lb_type = lb.get('Type', 'application')
                state = lb.get('State', {}).get('Code', 'active')

                # Check target groups and target health
                target_count = 0
                healthy_targets = 0
                try:
                    tg_resp = elbv2.describe_target_groups(LoadBalancerArn=lb_arn)
                    for tg in tg_resp.get('TargetGroups', []):
                        tg_arn = tg.get('TargetGroupArn')
                        th_resp = elbv2.describe_target_health(TargetGroupArn=tg_arn)
                        target_count += len(th_resp.get('TargetHealthDescriptions', []))
                        for th in th_resp.get('TargetHealthDescriptions', []):
                            if th.get('TargetHealth', {}).get('State') == 'healthy':
                                healthy_targets += 1
                except Exception:
                    pass

                est_cost = estimate_alb_monthly_cost()

                results.append({
                    'resource_id': lb_name,
                    'resource_type': 'ELB',
                    'service': 'Elastic Load Balancing',
                    'region': region,
                    'name': lb_name,
                    'state': state,
                    'estimated_monthly_cost': est_cost,
                    'metadata': {
                        'type': lb_type,
                        'arn': lb_arn,
                        'dns_name': lb.get('DNSName'),
                        'target_count': target_count,
                        'healthy_target_count': healthy_targets,
                        'scheme': lb.get('Scheme')
                    }
                })
    except Exception as e:
        logger.error(f'ELB discovery failed for region {region}: {e}')
    return results
