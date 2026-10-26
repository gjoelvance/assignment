from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, get_db
from main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

def override_db():
    with TestingSession() as db:
        yield db

app.dependency_overrides[get_db] = override_db

payload = {"street": "350 Fifth Avenue", "city": "New York", "state": "NY", "postal_code": "10118", "country": "USA", "latitude": 40.7484, "longitude": -73.9857}

def test_crud_and_nearby():
    with TestClient(app) as client:
        created = client.post("/addresses", json=payload)
        assert created.status_code == 201
        address_id = created.json()["id"]
        assert client.get(f"/addresses/{address_id}").status_code == 200
        nearby = client.get("/addresses/nearby", params={"latitude": 40.7484, "longitude": -73.9857, "distance_km": 1})
        assert nearby.status_code == 200
        assert any(a["id"] == address_id for a in nearby.json())
        updated = client.put(f"/addresses/{address_id}", json={**payload, "city": "Manhattan"})
        assert updated.json()["city"] == "Manhattan"
        assert client.delete(f"/addresses/{address_id}").status_code == 204
        assert client.get(f"/addresses/{address_id}").status_code == 404

def test_validation():
    with TestClient(app) as client:
        assert client.post("/addresses", json={**payload, "latitude": 91}).status_code == 422
        assert client.post("/addresses", json={**payload, "street": "   "}).status_code == 422
        assert client.get("/addresses/nearby", params={"latitude": 0, "longitude": 0, "distance_km": -1}).status_code == 422
