#!/usr/bin/env python3
"""
Smart Cloud Cost Guardian (SCCG) - Operational Management CLI.
Allows running administrative tasks, inspections, and demo data operations from the terminal.
"""

import sys
import os
import argparse

# Ensure UTF-8 stdout encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.aws_account import AWSAccount
from app.models.resource import Resource
from app.models.recommendation import Recommendation
from app.models.user import User
from app.services.health_score.calculator import calculate_cloud_health_score
from app.database.seed_demo import seed_demo_data


def cmd_seed(args):
    """Seed or re-seed realistic FinOps demo data."""
    print("[+] Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("[+] Seeding realistic demo data (users, AWS accounts, resources, waste recs)...")
        seed_demo_data(db)
        print("[OK] Demo data seeded successfully.")
    except Exception as e:
        print(f"[ERR] Error during seeding: {e}")
    finally:
        db.close()


def cmd_accounts(args):
    """List connected AWS accounts and their status."""
    db = SessionLocal()
    try:
        accounts = db.query(AWSAccount).all()
        if not accounts:
            print("No AWS accounts found in database.")
            return

        print(f"\n{'ID':<5} {'Account Name':<32} {'Account ID':<16} {'Status':<12} {'Region':<12}")
        print("-" * 80)
        for acc in accounts:
            print(f"{acc.id:<5} {acc.account_name:<32} {acc.account_id:<16} {acc.status:<12} {acc.region:<12}")
        print()
    finally:
        db.close()


def cmd_health(args):
    """Compute and display Cloud Health Score breakdown."""
    db = SessionLocal()
    try:
        account = db.query(AWSAccount).first()
        if not account:
            print("No AWS account found to evaluate health score.")
            return

        print(f"\n[SCCG] Evaluating Cloud Health Score for: {account.account_name} ({account.account_id})")
        score_data = calculate_cloud_health_score(db, account.id)

        print("=" * 60)
        print(f"Overall Health Score:  {score_data.get('overall_score', 0)} / 100 (Grade: {score_data.get('grade', 'N/A')})")
        print("=" * 60)
        breakdown = score_data.get('breakdown', {})
        for k, val in breakdown.items():
            max_pts = 25 if 'efficiency' in k or 'utilization' in k else 20 if 'opportunities' in k or 'budget' in k else 10
            print(f"  * {k.replace('_', ' ').title():<30}: {val:>4.1f} / {max_pts}")
        
        explanations = score_data.get('explanations', [])
        if explanations:
            print("\nKey Explanations:")
            for exp in explanations:
                print(f"  - {exp}")
        print()
    finally:
        db.close()


def cmd_recs(args):
    """List active cost recommendations and savings."""
    db = SessionLocal()
    try:
        recs = db.query(Recommendation).filter(Recommendation.status == 'Active').all()
        if not recs:
            print("No active cost recommendations found.")
            return

        total_savings = sum(r.estimated_monthly_savings for r in recs)
        print(f"\n[SCCG] Active Cost Optimization Opportunities: {len(recs)} (Total Savings: ${total_savings:,.2f}/mo)")
        print(f"{'Severity':<10} {'Category':<24} {'Savings/mo':<15} {'Title'}")
        print("-" * 85)
        for r in recs:
            print(f"{r.severity:<10} {r.category[:22]:<24} ${r.estimated_monthly_savings:<14,.2f} {r.title[:35]}")
        print()
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Smart Cloud Cost Guardian (SCCG) - Operational CLI Utility"
    )
    subparsers = parser.add_subparsers(dest="command", help="Operational commands")

    # seed
    subparsers.add_parser("seed", help="Seed demo users, AWS resources, and waste data")

    # accounts
    subparsers.add_parser("accounts", help="List registered AWS accounts and sync status")

    # health
    subparsers.add_parser("health", help="Calculate and print Cloud Health Score")

    # recs
    subparsers.add_parser("recs", help="List active FinOps cost recommendations")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "seed": cmd_seed,
        "accounts": cmd_accounts,
        "health": cmd_health,
        "recs": cmd_recs,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
