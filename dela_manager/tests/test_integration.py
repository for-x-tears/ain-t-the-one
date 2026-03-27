from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_create_task():
    register_response = client.post("/auth/register", json={
        "username": "integration_user",
        "password": "123456"
    })
    assert register_response.status_code == 200

    login_response = client.post("/auth/login", json={
        "username": "integration_user",
        "password": "123456"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.post("/tasks/", json={
        "title": "Интеграционная задача",
        "description": "тест",
        "completed": False
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Интеграционная задача"
    assert "id" in data