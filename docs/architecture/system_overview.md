# 🏗️ Architecture & FinOps Engine Specification

Smart Cloud Cost Guardian (SCCG) is architected around an advisory-only FinOps pipeline designed for high precision, zero destructive risk, and mathematical transparency.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        React 18 + Vite SPA Client                      │
│      - Glassmorphism Tailwind UI          - Recharts Visualizations    │
│      - Multi-Tenant AWS Account Context   - 17 Dynamic Views & Modals  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (REST API / Bearer JWT)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend Engine                         │
│      - Pydantic v2 Type Safety            - SQLAlchemy 2.0 ORM         │
│      - APScheduler Background Sync        - ReportLab PDF Generation   │
└────────┬──────────────────────────┼────────────────────────────┬───────┘
         │                          │                            │
         ▼                          ▼                            ▼
┌──────────────────┐      ┌────────────────────┐      ┌──────────────────┐
│   AWS Service    │      │ FinOps Rule Engine │      │ Factual AI Agent │
│   Integrations   │      │  & ML Forecaster   │      │  (Context-Bound) │
│ - STS AssumeRole │      │ - 8+ Waste Rules   │      │ - Dynamic Facts  │
│ - CloudWatch 14d │      │ - Z-Score Outlier  │      │ - Grounded DB    │
│ - Cost Explorer  │      │ - Scikit-Learn OLS │      │ - Zero Hallucin. │
└──────────────────┘      └────────────────────┘      └──────────────────┘
```

---

## 1. Multi-Tier Component Topology

1. **Frontend Presentation Tier**:
   - Single Page Application built on React 18 and Vite.
   - Tailwind CSS with responsive layout and glassmorphism cards.
   - Client-side routing with React Router DOM v7 and protected route guards.
   - Context providers for central authentication (`AuthContext`) and selected AWS account (`AWSAccountContext`).

2. **Application Processing Tier**:
   - Asynchronous Python FastAPI backend serving under Uvicorn ASGI.
   - Modular API structure with decoupled service engines under `app/services/`.
   - Asynchronous periodic task scheduler using APScheduler to trigger daily resource and cost synchronizations.

3. **Data Persistence Tier**:
   - SQLAlchemy 2.0 ORM with declarative models.
   - Zero-dependency local SQLite file engine for development and testing.
   - Drop-in compatibility with enterprise PostgreSQL via standard `DATABASE_URL` connection strings.

---

## 2. Core FinOps Engines

### 🔍 A. Deterministic Waste Engine (`app/services/recommendations/`)
Evaluates 8 deterministic heuristics across AWS resources every sync cycle:
1. **Idle EC2 Instances**: Average CPU utilization < 5% and minimal network I/O over the preceding 14-day observation window.
2. **Unattached EBS Volumes**: Available EBS volumes detached from any instance generating unnecessary storage billing.
3. **Low-Throughput RDS Instances**: Databases with zero active connections or CPU < 3% over 7 days.
4. **Stale EBS Snapshots**: Snapshots older than 90 days with no parent volume.
5. **Unassociated Elastic IP Addresses**: Allocated Elastic IPs not linked to any running instance, incurring hourly idle charges.
6. **Orphaned Elastic Load Balancers**: Active Application or Classic Load Balancers with 0 healthy registered targets.
7. **S3 Storage Optimization**: Buckets without Lifecycle transition policies from Standard to Glacier/Infrequent Access.
8. **Oversized Lambda Memory**: Functions configured with large memory allocations but experiencing low execution durations and low invocation counts.

### 📈 B. Machine Learning Forecaster (`app/services/forecasting/`)
- Ingests daily cost time series over the past 30 to 90 days.
- Utilizes Scikit-learn ordinary least squares (OLS) linear trend regression.
- Calculates standard deviation of residuals to generate a **95% Confidence Interval** band (upper and lower spend bounds).
- Projects total estimated end-of-month spend versus designated budget caps.

### 🚨 C. Statistical Anomaly Detector (`app/services/anomaly/`)
- Computes rolling 14-day cost mean ($\mu$) and standard deviation ($\sigma$) per AWS service.
- Flags any daily cost record exceeding a **Z-Score > 2.0** as an anomaly event.
- Automatically records the anomaly and dispatches notifications through `app/services/notifications/`.

### 🛡️ D. Cloud Health Score Algorithm (`app/services/health_score/`)
Computes an objective, explainable score from 0 to 100 based on five weighted pillars:
- **Cost Efficiency (30%)**: Percentage of cloud budget not consumed by detected architectural waste.
- **Resource Utilization (25%)**: Ratio of active resources meeting healthy CPU/memory utilization baselines.
- **Opportunity Adoption (20%)**: Implementation rate of recommended rightsizing and modernization actions.
- **Budget Adherence (15%)**: Current monthly burn rate versus configured budget threshold.
- **Anomaly Cleanliness (10%)**: Absence of unresolved cost anomalies in the last 30 days.

### 🤖 E. Fact-Grounded FinOps AI Copilot (`app/services/assistant/`)
- Prevents LLM hallucinations by injecting a structured context payload directly from the database before LLM query execution.
- Gathers monthly spend, top 5 cost drivers, active waste recommendations, and health scores.
- Restricts responses strictly to the facts present in the user's infrastructure data.

---

## 3. Security & Least-Privilege Architecture

- **Advisory-Only Policy**: SCCG strictly enforces read-only access. Write and destructive permissions (e.g. `ec2:TerminateInstances`, `ec2:DeleteVolume`) are never requested or used.
- **STS AssumeRole Integration**: Cross-account role assumption with cryptographic `ExternalId` ensures multi-tenant isolation.
- **Credential Encryption**: Any stored credentials or role configurations are symmetrically encrypted using Fernet keys (`cryptography` library) before persistence.
