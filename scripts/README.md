# 🛠️ Operational & Administrative Scripts

This directory contains management utilities for operating the Smart Cloud Cost Guardian platform.

## Available CLI Tools

### `scripts/manage.py`
A centralized operational CLI for database inspection, seeding, and health reporting.

#### Usage:
```bash
# Seed realistic FinOps demo dataset (users, AWS accounts, resources, recommendations)
python scripts/manage.py seed

# Inspect connected AWS accounts and connection status
python scripts/manage.py accounts

# Calculate and display the explainable Cloud Health Score breakdown
python scripts/manage.py health

# Print open cost optimization recommendations and monthly potential savings
python scripts/manage.py recs
```
