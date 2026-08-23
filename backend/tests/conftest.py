import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database.base import Base
from app.database.session import get_db
from app.database.seed_demo import seed_demo_data
from app.main import app
from app.api.deps import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.aws_account import AWSAccount

TEST_DATABASE_URL = "sqlite:///./test_sccg.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_demo_data(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_sccg.db"):
        try:
            os.remove("test_sccg.db")
        except Exception:
            pass

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        acc = db_session.query(AWSAccount).first()
        if acc and acc.user:
            return acc.user
        return db_session.query(User).first()

    def override_get_current_admin_user():
        admin = db_session.query(User).filter(User.role == 'ADMIN').first()
        return admin or db_session.query(User).first()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_admin_user] = override_get_current_admin_user

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
