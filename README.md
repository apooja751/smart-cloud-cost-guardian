# 🛡️ Smart Cloud Cost Guardian (SCCG)
### *AI-Powered Cloud Cost Optimization, FinOps, and Resource Intelligence Platform*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg?style=flat&logo=React&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0.0-646CFF.svg?style=flat&logo=Vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4.0-38B2AC.svg?style=flat&logo=Tailwind-CSS&logoColor=white)](https://tailwindcss.com/)
[![AWS Boto3](https://img.shields.io/badge/AWS_SDK-Boto3-FF9900.svg?style=flat&logo=Amazon-AWS&logoColor=white)](https://boto3.amazonaws.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Executive Overview

**Smart Cloud Cost Guardian (SCCG)** is an enterprise-grade FinOps web platform designed to securely connect to AWS environments, discover provisioned resources across multiple services, evaluate resource utilization metrics, detect architectural waste, predict future cloud bills with machine learning, and provide grounded AI advisory for cloud cost reduction.

### Key Value Pillars:
1. **Real AWS SDK Integration & High-Fidelity Demo Mode**: Connect live AWS accounts via secure STS cross-account IAM AssumeRole or explore zero-setup simulated environments with 20+ realistic resources.
2. **Deterministic FinOps Waste Engine**: Evaluates 8+ automated waste rules across EC2, EBS, RDS, S3, Elastic IPs, ELB, Snapshots, and Lambda.
3. **Machine Learning Spend Forecaster**: Scikit-learn linear trend regression modeling with 95% confidence intervals.
4. **Explainable 0–100 Cloud Health Score**: Multi-factor grading across Cost Efficiency, Resource Utilization, Opportunity Adoption, Budget Adherence, and Anomaly Cleanliness.
5. **Zero-Hallucination Grounded AI Copilot**: FinOps conversational assistant strictly grounded in your database facts.
6. **Boardroom-Ready PDF Reports**: Automated ReportLab PDF audit generator with KPI summaries, service breakdowns, and recommendation tables.

---

## 🏗️ Architecture & Component Design

```
+-----------------------------------------------------------------------------------+
|                                React 18 + Vite SPA                                |
|  - Tailwind CSS Glassmorphism UI   - Recharts Visualizations   - Lucide Icons     |
|  - Auth & AWS Account Contexts     - 16 Pages & Views          - Advisory-Only    |
+-----------------------------------------------------------------------------------+
                                         │  (REST API / JWT Bearer)
                                         ▼
+-----------------------------------------------------------------------------------+
|                              FastAPI Backend Engine                               |
|  - Pydantic v2 Schemas             - SQLAlchemy 2.0 ORM        - APScheduler      |
|  - OAuth2 Password Flow            - bcrypt Security           - ReportLab PDF    |
+-----------------------------------------------------------------------------------+
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
+───────────────────+          +───────────────────+          +───────────────────+
| AWS Boto3 Service |          | FinOps ML & Rules |          | Factual AI Engine |
| - EC2, EBS, RDS   |          | - 8+ Waste Rules  |          | - Intent Router   |
| - CloudWatch 14d  |          | - Z-Score Outlier |          | - DB Grounding    |
| - Cost Explorer   |          | - Linear Forecast |          | - Gemini API Opt. |
+───────────────────+          +───────────────────+          +───────────────────+
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- Docker & Docker Compose *(optional)*

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations and seed demo data automatically on launch
uvicorn app.main:app --reload --port 8000
```
Backend API interactive Swagger documentation will be live at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

### 3. Demo Credentials
The platform is pre-seeded with rich demo datasets and instant login credentials:
- **Standard User**: `demo@sccg.io` / `Demo123!Secure`
- **System Admin**: `admin@sccg.io` / `Admin123!Secure`

---

## 🐳 Docker Deployment

To launch the full production stack using Docker Compose:
```bash
docker-compose up --build -d
```
Access the application at `http://localhost`.

---

## 🧪 Automated Testing Suite

The backend contains automated tests with 100% pass rate:
```bash
pytest backend/tests -v
```

---

## 🔒 Security & IAM Least-Privilege Policy

Smart Cloud Cost Guardian follows an **advisory-only, read-only** security posture. No destructive write permissions (e.g. `ec2:TerminateInstances`, `ec2:DeleteVolume`) are ever required.

See [`infrastructure/aws/iam_policy.json`](infrastructure/aws/iam_policy.json) for the full least-privilege policy document.

---

## 📄 License
This project is licensed under the MIT License.
