# Standard AWS On-Demand monthly estimates for common instance/volume types
EC2_HOURLY_RATES = {
    't2.nano': 0.0058, 't2.micro': 0.0116, 't2.small': 0.023, 't2.medium': 0.0464, 't2.large': 0.0928,
    't3.nano': 0.0052, 't3.micro': 0.0104, 't3.small': 0.0208, 't3.medium': 0.0416, 't3.large': 0.0832, 't3.xlarge': 0.1664, 't3.2xlarge': 0.3328,
    't4g.nano': 0.0042, 't4g.micro': 0.0084, 't4g.small': 0.0168, 't4g.medium': 0.0336, 't4g.large': 0.0672,
    'm5.large': 0.096, 'm5.xlarge': 0.192, 'm5.2xlarge': 0.384, 'm5.4xlarge': 0.768,
    'c5.large': 0.085, 'c5.xlarge': 0.17, 'c5.2xlarge': 0.34, 'c5.4xlarge': 0.68,
    'r5.large': 0.126, 'r5.xlarge': 0.252, 'r5.2xlarge': 0.504, 'r5.4xlarge': 1.008,
}

EBS_GB_MONTHLY = {
    'gp2': 0.10,
    'gp3': 0.08,
    'io1': 0.125,
    'io2': 0.125,
    'st1': 0.045,
    'sc1': 0.015,
    'standard': 0.05
}

RDS_HOURLY_RATES = {
    'db.t3.micro': 0.017, 'db.t3.small': 0.034, 'db.t3.medium': 0.068, 'db.t3.large': 0.136,
    'db.m5.large': 0.178, 'db.m5.xlarge': 0.356, 'db.m5.2xlarge': 0.712,
    'db.r5.large': 0.24, 'db.r5.xlarge': 0.48, 'db.r5.2xlarge': 0.96
}

def estimate_ec2_monthly_cost(instance_type: str) -> float:
    hourly = EC2_HOURLY_RATES.get(instance_type.lower(), 0.05)
    return round(hourly * 730, 2)

def estimate_ebs_monthly_cost(volume_type: str, size_gb: int) -> float:
    rate = EBS_GB_MONTHLY.get(volume_type.lower(), 0.08)
    return round(rate * size_gb, 2)

def estimate_snapshot_monthly_cost(size_gb: int) -> float:
    return round(0.05 * size_gb, 2)

def estimate_rds_monthly_cost(instance_class: str, multi_az: bool = False) -> float:
    hourly = RDS_HOURLY_RATES.get(instance_class.lower(), 0.10)
    multiplier = 2.0 if multi_az else 1.0
    return round(hourly * 730 * multiplier, 2)

def estimate_alb_monthly_cost() -> float:
    return 22.50 # Base ALB ~.0225/hr + LCU baseline
