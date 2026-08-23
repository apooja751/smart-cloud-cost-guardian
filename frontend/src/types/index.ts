export interface User {
  id: number;
  name: string;
  email: string;
  role: 'USER' | 'ADMIN';
  is_active: boolean;
  created_at: string;
}

export interface AWSAccount {
  id: number;
  user_id: number;
  account_id: string;
  account_name: string;
  region: string;
  connection_type: 'IAM_ROLE' | 'ACCESS_KEY' | 'DEMO';
  status: 'Connected' | 'Disconnected' | 'Error' | 'Synchronizing';
  last_sync_at?: string;
  error_message?: string;
  discovered_resources_count: number;
  created_at: string;
}

export interface Resource {
  id: number;
  aws_account_id: number;
  resource_id: string;
  resource_type: string;
  service: string;
  region: string;
  name?: string;
  state?: string;
  estimated_monthly_cost: number;
  metadata?: Record<string, any>;
  last_seen_at: string;
  recommendations_count: number;
}

export interface ResourceMetric {
  id: number;
  metric_name: string;
  metric_value: number;
  unit?: string;
  timestamp: string;
}

export interface ResourceDetail extends Resource {
  metrics: ResourceMetric[];
  recommendations: Array<{
    id: number;
    title: string;
    category: string;
    monthly_savings: number;
    severity: string;
    evidence: string;
    status: string;
  }>;
}

export interface CostSummary {
  current_month_cost: number;
  previous_month_cost: number;
  cost_change_percentage: number;
  forecasted_monthly_cost: number;
  potential_monthly_savings: number;
  cloud_health_score: number;
  currency: string;
}

export interface DailyCost {
  date: string;
  amount: number;
  service?: string;
}

export interface ServiceCost {
  service: string;
  amount: number;
  percentage: number;
}

export interface Recommendation {
  id: number;
  aws_account_id: number;
  resource_id?: number;
  category: string;
  title: string;
  description: string;
  action_notes?: string;
  estimated_monthly_savings: number;
  estimated_annual_savings: number;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  confidence: number;
  evidence: string;
  status: 'Active' | 'Reviewed' | 'Dismissed' | 'Snoozed';
  created_at: string;
}

export interface HealthScore {
  overall_score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  breakdown: {
    cost_efficiency: number;
    resource_utilization: number;
    optimization_opportunities: number;
    budget_adherence: number;
    anomaly_health: number;
  };
  explanations: string[];
}

export interface ForecastPoint {
  date: string;
  predicted_amount: number;
  lower_bound: number;
  upper_bound: number;
}

export interface ForecastData {
  aws_account_id: number;
  forecast_month: string;
  predicted_total: number;
  trend_percentage: number;
  model_used: string;
  is_sufficient_data: boolean;
  message?: string;
  daily_forecasts: ForecastPoint[];
}

export interface Anomaly {
  id: number;
  aws_account_id: number;
  service: string;
  date: string;
  expected_cost: number;
  actual_cost: number;
  deviation_percentage: number;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  status: string;
  created_at: string;
}

export interface Budget {
  id: number;
  aws_account_id: number;
  name: string;
  amount: number;
  currency: string;
  period: string;
  service?: string;
  current_spend: number;
  spent_percentage: number;
  status: 'OK' | 'WARNING' | 'EXCEEDED';
  threshold_50: boolean;
  threshold_75: boolean;
  threshold_90: boolean;
  threshold_100: boolean;
  created_at: string;
}

export interface AlertItem {
  id: number;
  user_id: number;
  aws_account_id?: number;
  type: string;
  title: string;
  message: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  read: boolean;
  created_at: string;
}

export interface ReportItem {
  id: number;
  aws_account_id: number;
  title: string;
  reporting_period: string;
  format: string;
  download_url: string;
  created_at: string;
}

export interface AssistantResponse {
  question: string;
  answer: string;
  intent: string;
  suggested_followups: string[];
}
