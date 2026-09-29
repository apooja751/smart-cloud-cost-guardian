# 🔌 Smart Cloud Cost Guardian (SCCG) - REST API Documentation

The SCCG backend is built on **FastAPI** and provides high-performance asynchronous REST endpoints adhering to OpenAPI 3.1 standards.

- **Base URL**: `http://localhost:8000/api/v1`
- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc Technical Reference**: `http://localhost:8000/redoc`

---

## 🔐 Authentication & Security

All private endpoints require a JSON Web Token (JWT) supplied via standard HTTP Authorization Bearer headers:
```http
Authorization: Bearer <your_jwt_access_token>
```

### Authentication Flow
1. `POST /api/v1/auth/token` (or `/login`): Exchange user email and password for an access token.
2. Store the returned JWT token securely in client storage (`localStorage` / secure cookies).
3. Append `Authorization: Bearer <token>` to all subsequent API requests.

---

## 📋 Endpoint Modules Overview

### 1. Authentication & Users (`/api/v1/auth`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register a new user account |
| `POST` | `/api/v1/auth/token` | Authenticate with credentials and receive JWT |
| `GET` | `/api/v1/auth/me` | Fetch profile information for the authenticated user |

### 2. AWS Account Integration (`/api/v1/aws`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/aws/accounts` | List connected AWS accounts for the tenant |
| `POST` | `/api/v1/aws/connect` | Register a new AWS account with Role ARN & ExternalId |
| `POST` | `/api/v1/aws/{id}/sync` | Trigger on-demand resource and cost synchronization |
| `DELETE` | `/api/v1/aws/{id}` | Disconnect and remove an AWS account |

### 3. Resource Inventory & Metrics (`/api/v1/resources`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/resources` | Query discovered resources with service & region filters |
| `GET` | `/api/v1/resources/{id}` | Detailed resource attributes, configuration, and tags |
| `GET` | `/api/v1/resources/{id}/metrics`| Time-series CloudWatch utilization metrics (CPU, IOPS, Network) |

### 4. Cost Analytics (`/api/v1/costs`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/costs/summary` | High-level monthly spend, MoM delta, and run-rate |
| `GET` | `/api/v1/costs/daily` | 30-day historical daily spend breakdown |
| `GET` | `/api/v1/costs/services` | Aggregate spend categorized by AWS service |

### 5. FinOps Recommendations & Waste (`/api/v1/recommendations`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/recommendations` | List actionable cost optimization recommendations |
| `POST` | `/api/v1/recommendations/{id}/dismiss` | Dismiss a recommendation with user rationale |
| `POST` | `/api/v1/recommendations/{id}/apply` | Mark recommendation as applied / remediated |

### 6. Machine Learning Forecasting (`/api/v1/forecast`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/forecast` | Scikit-learn linear regression forecast with 95% confidence intervals |

### 7. Cost Anomaly Detection (`/api/v1/anomalies`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/anomalies` | Detected cost spikes and statistical outliers |
| `POST` | `/api/v1/anomalies/{id}/resolve` | Acknowledge and resolve an anomaly event |

### 8. Budget Tracking (`/api/v1/budgets`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/budgets` | List monthly budget thresholds and consumption % |
| `POST` | `/api/v1/budgets` | Create or update a budget ceiling and alert levels |

### 9. Alerting & Notifications (`/api/v1/alerts`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/alerts` | List unread and historical FinOps alerts |
| `POST` | `/api/v1/alerts/{id}/read` | Mark an alert as read / acknowledged |

### 10. Cloud Health Score (`/api/v1/health-score`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health-score` | Multi-pillar 0–100 overall score with sub-factor breakdown |

### 11. Grounded AI Copilot (`/api/v1/assistant`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/assistant/chat` | Send FinOps question; returns grounded AI advisory based on DB state |

### 12. Audit Reports (`/api/v1/reports`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/reports` | List generated PDF audit reports |
| `POST` | `/api/v1/reports/generate` | Trigger generation of a boardroom-ready PDF audit report |
| `GET` | `/api/v1/reports/{id}/download` | Stream and download the generated PDF report |

### 13. System Administration (`/api/v1/admin`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/admin/users` | List platform users and roles (Admin only) |
| `GET` | `/api/v1/admin/audit-logs` | Comprehensive security and administrative audit trail |

---

## 🛡️ Standard Response & Error Format

Successful responses wrap payload data inside a standardized envelope:
```json
{
  "success": true,
  "data": { ... }
}
```

Errors follow a uniform error structure:
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "AWS Account with id 42 does not exist."
  }
}
```
