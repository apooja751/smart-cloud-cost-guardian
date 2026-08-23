import json
import datetime
from typing import List, Dict, Any, Optional
from app.models.resource import Resource

def evaluate_idle_ec2(resource: Resource, avg_cpu: Optional[float]) -> Optional[Dict[str, Any]]:
    if resource.resource_type != 'EC2' or resource.state != 'running':
        return None
    
    meta = json.loads(resource.metadata_json or '{}')
    cpu = avg_cpu if avg_cpu is not None else meta.get('avg_cpu', 50.0)

    if cpu < 5.0:
        current_cost = resource.estimated_monthly_cost
        # Rightsizing or stopping yields ~70% to 100% savings
        savings_monthly = round(current_cost * 0.85, 2)
        savings_yearly = round(savings_monthly * 12, 2)
        inst_type = meta.get('instance_type', 'unknown')

        return {
            'category': 'Idle Compute',
            'title': f'Idle EC2 Instance Detected ({inst_type})',
            'description': f'Instance {resource.name or resource.resource_id} is running with only {cpu:.1f}% average CPU utilization over the last 14 days.',
            'evidence': f'Observed 14-day average CPU utilization is {cpu:.2f}% (Threshold < 5.0%). Estimated monthly cost: .',
            'estimated_monthly_savings': savings_monthly,
            'estimated_yearly_savings': savings_yearly,
            'confidence': 0.95,
            'severity': 'High' if current_cost > 100 else 'Medium',
            'action_notes': f'Consider stopping instance or rightsizing from {inst_type} to a smaller burstable instance (e.g., t4g.small or t3.small).'
        }
    return None

def evaluate_stopped_ec2(resource: Resource) -> Optional[Dict[str, Any]]:
    if resource.resource_type != 'EC2' or resource.state != 'stopped':
        return None
    
    meta = json.loads(resource.metadata_json or '{}')
    stopped_days = meta.get('stopped_days', 15)

    if stopped_days >= 14:
        storage_cost = resource.estimated_monthly_cost if resource.estimated_monthly_cost > 0 else 20.00
        savings_monthly = storage_cost
        savings_yearly = round(savings_monthly * 12, 2)

        return {
            'category': 'Stopped Compute Storage Waste',
            'title': f'Long-term Stopped EC2 Instance ({resource.name or resource.resource_id})',
            'description': f'Instance has remained in stopped state for {stopped_days} days while its attached root/data volumes continue incurring storage charges.',
            'evidence': f'Stopped duration: {stopped_days} days (Threshold >= 14 days). Ongoing storage fee: /mo.',
            'estimated_monthly_savings': savings_monthly,
            'estimated_yearly_savings': savings_yearly,
            'confidence': 0.90,
            'severity': 'Medium',
            'action_notes': 'Review whether this stopped instance is still required. Create an AMI backup and terminate the instance to eliminate storage costs.'
        }
    return None

def evaluate_unattached_ebs(resource: Resource) -> Optional[Dict[str, Any]]:
    if resource.resource_type != 'EBS' or resource.state != 'available':
        return None
    
    meta = json.loads(resource.metadata_json or '{}')
    size_gb = meta.get('size_gb', 0)
    vol_type = meta.get('volume_type', 'gp3')
    savings_monthly = resource.estimated_monthly_cost
    savings_yearly = round(savings_monthly * 12, 2)

    return {
        'category': 'Unattached Storage',
        'title': f'Unattached EBS Volume ({size_gb} GB {vol_type})',
        'description': f'EBS volume {resource.resource_id} is in available (unattached) state and actively generating unnecessary monthly storage fees.',
        'evidence': f'Volume status: available. Size: {size_gb} GB ({vol_type}). Monthly waste: .',
        'estimated_monthly_savings': savings_monthly,
        'estimated_yearly_savings': savings_yearly,
        'confidence': 0.99,
        'severity': 'High' if savings_monthly > 50 else 'Medium',
        'action_notes': 'Take a final EBS snapshot if historical data retention is needed, then safely delete this unattached volume.'
    }

def evaluate_old_snapshots(resource: Resource) -> Optional[Dict[str, Any]]:
    if resource.resource_type != 'Snapshot':
        return None
    
    meta = json.loads(resource.metadata_json or '{}')
    age_days = meta.get('age_days', 0)
    size_gb = meta.get('volume_size_gb', 0)

    if age_days >= 60:
        savings_monthly = resource.estimated_monthly_cost
        savings_yearly = round(savings_monthly * 12, 2)

        return {
            'category': 'Old Snapshots',
            'title': f'Aged EBS Snapshot Retention ({age_days} days old)',
            'description': f'Snapshot {resource.resource_id} ({size_gb} GB) has exceeded standard 60-day backup retention policies.',
            'evidence': f'Snapshot Age: {age_days} days (Threshold >= 60 days). Size: {size_gb} GB. Monthly cost: .',
            'estimated_monthly_savings': savings_monthly,
            'estimated_yearly_savings': savings_yearly,
            'confidence': 0.85,
            'severity': 'Low' if savings_monthly < 20 else 'Medium',
            'action_notes': 'Verify compliance retention policy and delete this obsolete snapshot if no longer required.'
        }
    return None

def evaluate_unused_elastic_ip(resource: Resource) -> Optional[Dict[str, Any]]:
    if resource.resource_type != 'ElasticIP' or resource.state != 'unassociated':
        return None
    
    meta = json.loads(resource.metadata_json or '{}')
    public_ip = meta.get('public_ip', resource.resource_id)
    savings_monthly = 3.65
    savings_yearly = 43.80

    return {
        'category': 'Unused Network',
        'title': f'Unassociated Elastic IP ({public_ip})',
        'description': f'Elastic IP {public_ip} is allocated but not bound to any running EC2 instance or NAT gateway, incurring idle IPv4 address fees.',
        'evidence': f'State: unassociated. AWS charges .005/hour for idle public IPs (.65/month).',
        'estimated_monthly_savings': savings_monthly,
        'estimated_yearly_savings': savings_yearly,
        'confidence': 1.0,
        'severity': 'Low',
        'action_notes': 'Release the unallocated Elastic IP back to the AWS IPv4 pool.'
    }

def evaluate_low_traffic_elb(resource: Resource) -> Optional[Dict[str, Any]]:
    if resource.resource_type != 'ELB':
        return None
    
    meta = json.loads(resource.metadata_json or '{}')
    targets = meta.get('target_count', 0)
    req_count = meta.get('req_count_7d', 0)

    if targets == 0 or req_count < 50:
        savings_monthly = 24.50
        savings_yearly = 294.00

        return {
            'category': 'Idle Load Balancer',
            'title': f'Low-Traffic Load Balancer ({resource.name or resource.resource_id})',
            'description': f'Application Load Balancer has {targets} registered targets and virtually zero request traffic over the past 14 days.',
            'evidence': f'Healthy targets: {targets}. Request traffic: {req_count} requests in 7 days. Monthly base fee: .50.',
            'estimated_monthly_savings': savings_monthly,
            'estimated_yearly_savings': savings_yearly,
            'confidence': 0.90,
            'severity': 'Medium',
            'action_notes': 'Inspect ingress routing and decommission unused load balancer or consolidate multiple services under a shared ALB.'
        }
    return None

def evaluate_underutilized_rds(resource: Resource, avg_cpu: Optional[float]) -> Optional[Dict[str, Any]]:
    if resource.resource_type != 'RDS':
        return None
    
    meta = json.loads(resource.metadata_json or '{}')
    cpu = avg_cpu if avg_cpu is not None else meta.get('avg_cpu', 50.0)
    conns = meta.get('avg_connections', 20)
    inst_class = meta.get('instance_class', 'db.t3.micro')
    multi_az = meta.get('multi_az', False)

    # If CPU < 10% and connections < 10 on a larger instance (m5, r5)
    if cpu < 10.0 and ('m5' in inst_class or 'r5' in inst_class or '2xlarge' in inst_class or 'xlarge' in inst_class):
        current_cost = resource.estimated_monthly_cost
        # Downsizing by 1-2 tiers yields ~50-70% savings
        savings_monthly = round(current_cost * 0.60, 2)
        savings_yearly = round(savings_monthly * 12, 2)

        return {
            'category': 'Database Rightsizing',
            'title': f'Underutilized RDS Database ({inst_class})',
            'description': f'Database instance {resource.name} is averaging only {cpu:.1f}% CPU utilization and {conns} concurrent connections.',
            'evidence': f'14-day average CPU: {cpu:.1f}%, Connections: {conns}. Current instance class: {inst_class} (Multi-AZ: {multi_az}). Monthly cost: .',
            'estimated_monthly_savings': savings_monthly,
            'estimated_yearly_savings': savings_yearly,
            'confidence': 0.88,
            'severity': 'High' if savings_monthly > 150 else 'Medium',
            'action_notes': f'Downsize RDS instance class from {inst_class} to a burstable or smaller instance (e.g., db.t3.large or db.m5.large) and evaluate Multi-AZ requirement for non-production environments.'
        }
    return None

def evaluate_s3_lifecycle(resource: Resource) -> Optional[Dict[str, Any]]:
    if resource.resource_type != 'S3':
        return None
    
    meta = json.loads(resource.metadata_json or '{}')
    has_lifecycle = meta.get('has_lifecycle_rules', True)
    size_gb = meta.get('size_gb', 500)

    if not has_lifecycle and size_gb >= 1000:
        current_cost = resource.estimated_monthly_cost
        savings_monthly = round(current_cost * 0.45, 2)
        savings_yearly = round(savings_monthly * 12, 2)

        return {
            'category': 'Storage Lifecycle',
            'title': f'Missing S3 Lifecycle Policy ({resource.name})',
            'description': f'Bucket holds {size_gb:,.0f} GB of data entirely in Standard tier with no automated lifecycle transition rules configured.',
            'evidence': f'Bucket size: {size_gb:,.0f} GB. Lifecycle rules: None. Estimated current monthly spend: .',
            'estimated_monthly_savings': savings_monthly,
            'estimated_yearly_savings': savings_yearly,
            'confidence': 0.90,
            'severity': 'Medium' if savings_monthly < 150 else 'High',
            'action_notes': 'Configure S3 Lifecycle rules to transition objects older than 30 days to S3 Standard-Infrequent Access (S3-IA) and older than 90 days to S3 Glacier Flexible / Deep Archive.'
        }
    return None
