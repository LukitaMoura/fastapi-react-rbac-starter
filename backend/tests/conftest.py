import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.seed import SENHA_DEMO, seed


@pytest.fixture
def client():
    # Banco em memória isolado por teste; StaticPool mantém a mesma conexão
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSession = sessionmaker(bind=engine, autoflush=False)
    Base.metadata.create_all(engine)
    with TestingSession() as db:
        seed(db)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def login(client):
    def _login(email: str) -> dict:
        r = client.post("/api/auth/login", json={"email": email, "senha": SENHA_DEMO})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['access_token']}"}
    return _login
