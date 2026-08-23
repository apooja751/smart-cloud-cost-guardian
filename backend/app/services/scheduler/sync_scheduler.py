from apscheduler.schedulers.background import BackgroundScheduler
from app.database.session import SessionLocal
from app.models.aws_account import AWSAccount
from app.services.aws.collector import synchronize_aws_account
from app.core.logging import logger

scheduler = BackgroundScheduler()

def scheduled_sync_job():
    logger.info("Executing scheduled AWS accounts synchronization...")
    db = SessionLocal()
    try:
        accounts = db.query(AWSAccount).filter(AWSAccount.status.in_(['Connected', 'Synchronizing'])).all()
        for acc in accounts:
            try:
                synchronize_aws_account(db, acc.id)
            except Exception as e:
                logger.error(f"Scheduled sync failed for account #{acc.id}: {e}")
    finally:
        db.close()

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(scheduled_sync_job, 'interval', hours=6, id='aws_sync_interval')
        scheduler.start()
        logger.info("FinOps background sync scheduler started (interval=6h).")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("FinOps background sync scheduler stopped.")
