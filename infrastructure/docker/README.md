# 🐳 Docker Infrastructure

This directory contains containerization and orchestration manifests for deploying Smart Cloud Cost Guardian (SCCG).

## Overview

- **Development Orchestration**: Uses the root [docker-compose.yml](../../docker-compose.yml) which spins up `sccg-backend` (port 8000) and `sccg-frontend` (port 80).
- **Production Orchestration**: Uses [docker-compose.prod.yml](docker-compose.prod.yml) with hardened container configurations, strict restart policies, and isolated bridge networks.
- **Nginx Reverse Proxy**: Production reverse proxy template configured in [nginx.conf](nginx.conf) with gzip compression, security headers (CSP, X-Frame-Options, XSS protection), and SPA history API routing.

## Deployment Commands

### Development Stack
```bash
# From project root
docker-compose up --build -d
```

### Production Stack
```bash
# Using the production compose profile
docker compose -f infrastructure/docker/docker-compose.prod.yml up --build -d
```

## Architecture Inside Docker

```
[ Browser / Client ]
        │
        ▼ (Port 80/443)
[ Nginx (Frontend Container) ]
  ├── Static HTML/CSS/JS (React 18 SPA)
  └── /api/* Proxy Pass
        │
        ▼ (Port 8000, internal network)
[ FastAPI (Backend Container) ]
  ├── Uvicorn ASGI Worker
  ├── SQLite / PostgreSQL Volume
  └── Background Sync Scheduler
```
