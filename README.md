# Peppermint Fleet Backend

A FastAPI backend scaffold for a robot fleet, with a small robot event simulator and JSON input data.

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

The API is available at `http://localhost:8000`. Open `/docs` for the interactive API documentation.

## Run tests

```powershell
python -m pytest
```

## Run with Docker Compose

```powershell
docker compose up --build
```

## Structure

- `backend/`: FastAPI application, typed models, and in-memory fleet state
- `simulator/`: robot event publisher scaffold
- `tests/`: state and API tests
- `data/`: robot and event input files
