from contextlib import asynccontextmanager
from math import asin, cos, radians, sin, sqrt
from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Address
from schemas import AddressCreate, AddressUpdate, AddressResponse, NearbyAddress

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Address Book API", version="1.0.0", lifespan=lifespan)

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0088
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * radius * asin(min(1.0, sqrt(a)))

@app.post("/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(payload: AddressCreate, db: Session = Depends(get_db)):
    address = Address(**payload.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address

@app.get("/addresses", response_model=list[AddressResponse])
def list_addresses(db: Session = Depends(get_db)):
    return db.scalars(select(Address).order_by(Address.id)).all()

# Static route must precede /addresses/{address_id}.
@app.get("/addresses/nearby", response_model=list[NearbyAddress])
def nearby_addresses(
    latitude: float = Query(ge=-90, le=90, allow_inf_nan=False),
    longitude: float = Query(ge=-180, le=180, allow_inf_nan=False),
    distance_km: float = Query(ge=0, allow_inf_nan=False),
    db: Session = Depends(get_db),
):
    matches = []
    for address in db.scalars(select(Address)):
        distance = haversine_km(latitude, longitude, address.latitude, address.longitude)
        if distance <= distance_km:
            matches.append(NearbyAddress(**AddressResponse.model_validate(address).model_dump(), distance_km=round(distance, 3)))
    return sorted(matches, key=lambda item: item.distance_km)

@app.get("/addresses/{address_id}", response_model=AddressResponse)
def get_address(address_id: int, db: Session = Depends(get_db)):
    address = db.get(Address, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@app.put("/addresses/{address_id}", response_model=AddressResponse)
def update_address(address_id: int, payload: AddressUpdate, db: Session = Depends(get_db)):
    address = db.get(Address, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    for field, value in payload.model_dump().items():
        setattr(address, field, value)
    db.commit()
    db.refresh(address)
    return address

@app.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: int, db: Session = Depends(get_db)):
    address = db.get(Address, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(address)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
