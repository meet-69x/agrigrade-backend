# AgriGrade AI — Backend

FastAPI + PostgreSQL backend for AI-powered onion quality grading at
procurement centres (SIH26031). Handles auth, batch/image ingestion, the
CV grading pipeline, and reporting.

## Quick start

Requires Docker + Docker Compose.

```bash
docker compose up --build
```

This starts:
- **PostgreSQL** on `localhost:5432`
- **API** on `localhost:8000`

Interactive API docs (Swagger): **http://localhost:8000/docs**

Once it's running, seed a test centre + admin login:

```bash
docker compose exec api python seed.py
```

This creates:
- Centre: "Nashik Procurement Centre"
- Login: `admin@agrigrade.ai` / `admin123`

## Project structure

```
app/
├── main.py                 # FastAPI app + router registration
├── config.py                # env-based settings
├── database.py               # SQLAlchemy engine/session
├── models/                  # DB tables: User, Centre, Batch, Onion
├── schemas/                  # Pydantic request/response models
├── routers/
│   ├── auth.py               # signup, login, /me
│   ├── centres.py            # create/list procurement centres
│   ├── batches.py            # upload + process a batch, list, detail, PDF report
│   └── onions.py              # human override endpoint
├── services/
│   ├── cv_pipeline.py         # OpenCV segmentation + size/shape/color features
│   ├── defect_model.py        # rule-based defect detection (swap for a CNN later)
│   ├── grading.py             # transparent rule-based grading engine
│   └── batch_processor.py     # orchestrates the full pipeline + saves to DB
└── auth/
    └── security.py            # password hashing, JWT issuing/verification
```

## Core flow

1. `POST /auth/login` → get a JWT
2. `POST /batches` (multipart form: `centre_id`, `label`, `image` file) →
   creates a batch, runs segmentation → defect detection → grading
   synchronously, returns full per-onion results
3. `GET /batches` → list/filter batch history
4. `GET /batches/{id}` → full detail incl. all onion results
5. `GET /batches/{id}/report` → downloadable PDF report
6. `PATCH /onions/{id}/override` → human correction of a grade

## Swapping in a real ML model later

- Replace the body of `segment_onions()` in `cv_pipeline.py` with a
  YOLOv8-seg / Mask R-CNN call — keep the same return shape
  (`bbox`, `size_mm`, `shape_score`, `color_uniformity`, `crop`).
- Replace the body of `detect_defects()` in `defect_model.py` with your
  trained CNN's inference call — keep the same return shape
  (`defect_tags: list[str]`, `confidence: float`).
- Nothing else in the codebase needs to change.

## Calibration note

`PIXELS_PER_MM` in `cv_pipeline.py` is currently a fixed assumption. For
accurate real-world sizing, add a fixed-size calibration marker (e.g. a
coin or ArUco marker) to every captured frame and compute this value
dynamically per image instead.

## Running without Docker (local Python)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start a local Postgres however you like, then set DATABASE_URL
cp .env.example .env

uvicorn app.main:app --reload
```

## Auth notes

- JWT-based, `Authorization: Bearer <token>` header on protected routes.
- Roles: `operator` (default) and `admin`. `require_admin` dependency is
  available in `auth/security.py` for admin-only routes as you add them.
