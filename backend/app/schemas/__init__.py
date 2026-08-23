import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# User Schemas
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[str] = 'USER'

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserResponse

# AWS Account Schemas
class AWSAccountConnect(BaseModel):
    account_name: str
    account_id: str
    region: str = 'us-east-1'
    connection_type: str = 'ROLE_ARN'  # 'ROLE_ARN', 'ACCESS_KEY', 'DEMO'
    role_arn: Optional[str] = None
    external_id: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    demo_mode: Optional[bool] = False

class AWSTestConnectionRequest(BaseModel):
    connection_type: str = 'ROLE_ARN'
    region: str = 'us-east-1'
    role_arn: Optional[str] = None
    external_id: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    demo_mode: Optional[bool] = False

class AWSTestConnectionResponse(BaseModel):
    connected: bool
    account_id: Optional[str] = None
    validated_permissions: List[str] = []
    missing_permissions: List[str] = []
    message: str

class AWSAccountResponse(BaseModel):
    id: int
    account_id: str
    account_name: str
    region: str
    connection_type: str
    status: str
    last_sync_at: Optional[datetime.datetime]
    discovered_resources_count: Optional[int] = 0
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Resource Schemas
class ResourceMetricResponse(BaseModel):
    id: int
    metric_name: str
    metric_value: float
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

class ResourceResponse(BaseModel):
    id: int
    aws_account_id: int
    resource_id: str
    resource_type: str
    service: str
    region: str
    name: Optional[str]
    state: Optional[str]
    estimated_monthly_cost: float
    metadata: Optional[Dict[str, Any]] = None
    last_seen_at: datetime.datetime
    recommendations_count: Optional[int] = 0

    class Config:
        from_attributes = True

class ResourceDetailResponse(ResourceResponse):
    metrics: List[ResourceMetricResponse] = []
    recommendations: List[Any] = []

# Cost Schemas
class CostSummaryResponse(BaseModel):
    current_month_cost: float
    previous_month_cost: float
    cost_change_percentage: float
    forecasted_monthly_cost: float
    potential_monthly_savings: float
    cloud_health_score: int
    currency: str = 'USD'

class DailyCostItem(BaseModel):
    date: str
    amount: float
    service: Optional[str] = None

class MonthlyCostItem(BaseModel):
    month: str
    amount: float

class ServiceCostItem(BaseModel):
    service: str
    amount: float
    percentage: float

# Recommendation Schemas
class RecommendationResponse(BaseModel):
    id: int
    aws_account_id: int
    resource_id: Optional[int]
    resource_identifier: Optional[str] = None
    resource_type: Optional[str] = None
    category: str
    title: str
    description: str
    evidence: str
    estimated_monthly_savings: float
    estimated_yearly_savings: float
    confidence: float
    severity: str
    status: str
    action_notes: Optional[str]
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class RecommendationActionRequest(BaseModel):
    action: str = 'REVIEW'  # 'REVIEW', 'DISMISS', 'SNOOZE', 'ACTIVE'
    notes: Optional[str] = None

# Budget Schemas
class BudgetCreate(BaseModel):
    aws_account_id: int
    name: str
    amount: float
    currency: str = 'USD'
    period: str = 'MONTHLY'
    service: Optional[str] = None
    threshold_50: bool = True
    threshold_75: bool = True
    threshold_90: bool = True
    threshold_100: bool = True

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    service: Optional[str] = None
    threshold_50: Optional[bool] = None
    threshold_75: Optional[bool] = None
    threshold_90: Optional[bool] = None
    threshold_100: Optional[bool] = None

class BudgetResponse(BaseModel):
    id: int
    aws_account_id: int
    name: str
    amount: float
    currency: str
    period: str
    service: Optional[str]
    current_spend: float = 0.0
    spent_percentage: float = 0.0
    status: str = 'OK'  # 'OK', 'WARNING', 'EXCEEDED'
    threshold_50: bool
    threshold_75: bool
    threshold_90: bool
    threshold_100: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Alert Schemas
class AlertResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    severity: str
    read: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Forecast Schemas
class ForecastDataPoint(BaseModel):
    date: str
    predicted_amount: float
    lower_bound: float
    upper_bound: float

class ForecastResponse(BaseModel):
    aws_account_id: int
    forecast_month: str
    predicted_total: float
    trend_percentage: float
    model_used: str
    is_sufficient_data: bool
    message: Optional[str] = None
    daily_forecasts: List[ForecastDataPoint] = []

# Anomaly Schemas
class AnomalyResponse(BaseModel):
    id: int
    aws_account_id: int
    service: str
    date: str
    expected_cost: float
    actual_cost: float
    deviation_percentage: float
    severity: str
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Health Score Schemas
class HealthScoreBreakdown(BaseModel):
    cost_efficiency: float
    resource_utilization: float
    optimization_opportunities: float
    budget_adherence: float
    anomaly_health: float

class HealthScoreResponse(BaseModel):
    overall_score: int
    grade: str
    breakdown: HealthScoreBreakdown
    explanations: List[str]

# Assistant Schemas
class AssistantQuestionRequest(BaseModel):
    aws_account_id: Optional[int] = None
    question: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class AssistantAnswerResponse(BaseModel):
    question: str
    answer: str
    intent: str
    factual_context: Optional[Dict[str, Any]] = None
    suggested_followups: List[str] = []

# Report Schemas
class ReportGenerateRequest(BaseModel):
    aws_account_id: int
    reporting_period: str = 'Last 30 Days'
    title: Optional[str] = 'Smart Cloud Cost Guardian FinOps Report'

class ReportResponse(BaseModel):
    id: int
    aws_account_id: int
    title: str
    reporting_period: str
    format: str
    download_url: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Admin Schemas
class SystemHealthResponse(BaseModel):
    status: str
    database_connected: bool
    scheduler_running: bool
    active_users: int
    connected_accounts: int
    total_resources: int
    timestamp: datetime.datetime

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    user_email: Optional[str] = None
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str]
    created_at: datetime.datetime

    class Config:
        from_attributes = True
