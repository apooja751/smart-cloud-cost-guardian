import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = 'Smart Cloud Cost Guardian'
    APP_VERSION: str = '1.0.0'
    APP_ENV: str = 'development'
    DEBUG: bool = True
    API_V1_STR: str = '/api/v1'

    # Database
    DATABASE_URL: str = Field(
        default_factory=lambda: f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'sccg.db')).replace(chr(92), '/')}"
    )

    # Security
    JWT_SECRET: str = 'super-secret-sccg-guardian-jwt-key-2026-production-finops'
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ENCRYPTION_KEY: str = 'k_Z516c09bTz8r-QnQo_fKq4W1R_tLp8-xZfX_4hE7w='

    # AWS
    AWS_DEFAULT_REGION: str = 'us-east-1'
    DEMO_MODE: bool = True

    # AI / LLM
    LLM_PROVIDER: str = 'offline'  # 'gemini', 'openai', 'claude', 'offline'
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = 'gemini-1.5-flash'

    # Email / Notifications
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = 'alerts@cloudcostguardian.io'
    SNS_TOPIC_ARN: Optional[str] = None

    # CORS
    CORS_ORIGINS: List[str] = ['http://localhost:5173', 'http://localhost:3000', 'http://localhost:8000', 'http://127.0.0.1:5173']

    # Storage
    REPORTS_STORAGE_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'reports_storage')

    class Config:
        env_file = '.env'
        extra = 'allow'

settings = Settings()
