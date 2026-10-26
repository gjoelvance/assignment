# Address Book API

FastAPI + SQLite address book with validated CRUD and geographic radius search.

## Install

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs for Swagger UI.

## Endpoints

- `POST /addresses` — create an address
- `GET /addresses` — list addresses
- `GET /addresses/{address_id}` — get an address
- `PUT /addresses/{address_id}` — replace an address
- `DELETE /addresses/{address_id}` — delete an address
- `GET /addresses/nearby?latitude=40.7484&longitude=-73.9857&distance_km=5` — find nearby addresses, sorted by distance

`PUT` requires all address fields. Search distance is in kilometers and includes addresses exactly on the radius. Distances are calculated using the Haversine great-circle formula. This example scans all saved addresses; for very large databases, add spatial indexing.

## Tests

```bash
pytest -q
```
