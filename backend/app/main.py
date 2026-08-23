import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database.base import Base
from app.database.session import engine, SessionLocal
from app.database.seed_demo import seed_demo_data
from app.services.scheduler.sync_scheduler import start_scheduler, stop_scheduler

from app.api.v1.auth import router as auth_router
from app.api.v1.aws import router as aws_router
from app.api.v1.resources import router as resources_router
from app.api.v1.costs import router as costs_router
from app.api.v1.recommendations import router as recs_router
from app.api.v1.forecast import router as forecast_router
from app.api.v1.anomalies import router as anomalies_router
from app.api.v1.budgets import router as budgets_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.health_score import router as health_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.reports import router as reports_router
from app.api.v1.admin import router as admin_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting Smart Cloud Cost Guardian API Engine...')
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_demo_data(db)
    except Exception as e:
        logger.error(f'Initial seeding notice: {e}')
    finally:
        db.close()

    start_scheduler()
    yield
    stop_scheduler()
    logger.info('Smart Cloud Cost Guardian stopped.')

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description='AI-Powered Cloud Cost Optimization, FinOps, and Resource Intelligence Platform',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f'Unhandled exception at {request.url.path}: {exc}', exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            'success': False,
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal server error occurred. Please try again later.'
            }
        }
    )

api_v1 = settings.API_V1_STR
app.include_router(auth_router, prefix=api_v1)
app.include_router(aws_router, prefix=api_v1)
app.include_router(resources_router, prefix=api_v1)
app.include_router(costs_router, prefix=api_v1)
app.include_router(recs_router, prefix=api_v1)
app.include_router(forecast_router, prefix=api_v1)
app.include_router(anomalies_router, prefix=api_v1)
app.include_router(budgets_router, prefix=api_v1)
app.include_router(alerts_router, prefix=api_v1)
app.include_router(health_router, prefix=api_v1)
app.include_router(assistant_router, prefix=api_v1)
app.include_router(reports_router, prefix=api_v1)
app.include_router(admin_router, prefix=api_v1)

@app.get('/')
def root():
    return {
        'name': settings.APP_NAME,
        'version': settings.APP_VERSION,
        'tagline': 'AI-Powered Cloud Cost Optimization, FinOps, and Resource Intelligence Platform',
        'status': 'OPERATIONAL',
        'docs_url': '/docs'
    }

@app.get('/health')
def health():
    return {'status': 'OK', 'timestamp': str(datetime.datetime.now())}
