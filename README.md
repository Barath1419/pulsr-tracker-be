# pulsr-tracker-be

Backend API for **Pulsr** — a daily timeline tracker where users log activities using time ranges.

Built with **FastAPI · PostgreSQL · SQLAlchemy · Alembic · Docker**

---

## Project Structure

```
app/
  main.py
  core/
    config.py          # env vars & settings
    security.py        # JWT & password hashing
  db/
    base.py            # SQLAlchemy base
    session.py         # DB session
  models/
    user.py
    entry.py
  schemas/
    user.py
    entry.py
  api/
    deps.py            # dependency injection
    routes/
      auth.py
      entries.py
  services/
    user_service.py
    entry_service.py
  repositories/
    user_repo.py
    entry_repo.py

alembic/               # migrations
Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

---

## Prerequisites

- Python 3.11+
- PostgreSQL 16 (or Docker)
- pip

---

## Local Setup (without Docker)

### 1. Clone the repo

```bash
git clone <repo-url>
cd pulsr-tracker-be
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:root@localhost:5432/tracker-pulsr-be
SECRET_KEY=change-me-to-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> Use `localhost` when running locally. Use `db` (Docker service name) when running inside Docker.

### 5. Create the database

Make sure PostgreSQL is running, then create the database:

```bash
psql -U postgres -c "CREATE DATABASE \"tracker-pulsr-be\";"
```

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Start the server

```bash
uvicorn app.main:app --reload
```

API is now live at: `http://localhost:8000`
Swagger docs: `http://localhost:8000/docs`

---

## Docker Setup

### 1. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` — set `DB_HOST=db` (Docker service name):

```env
DATABASE_URL=postgresql://postgres:root@db:5432/tracker-pulsr-be
SECRET_KEY=change-me-to-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 2. Start all services

```bash
docker compose up --build
```

This starts:
- `db` — PostgreSQL on port `5432`
- `app` — FastAPI on port `8000`

### 3. Run migrations (first time)

```bash
docker compose exec app alembic upgrade head
```

### 4. Access the API

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### Stop services

```bash
docker compose down
```

### Stop and remove volumes (reset DB)

```bash
docker compose down -v
```

---

## API Endpoints

### Auth

| Method | Endpoint     | Description       |
|--------|--------------|-------------------|
| POST   | /auth/signup | Register new user |
| POST   | /auth/login  | Login, get JWT    |

### Entries

| Method | Endpoint                    | Description                      |
|--------|-----------------------------|----------------------------------|
| POST   | /entries                    | Create a new entry               |
| GET    | /entries                    | List all entries for current user |
| GET    | /entries?date=YYYY-MM-DD    | Filter entries by date           |
| DELETE | /entries/{id}               | Delete an entry                  |

All `/entries` routes require `Authorization: Bearer <token>` header.

---

## Postman

Import `pulsr.postman_collection.json` into Postman.

- Run **Login** first — the token is auto-saved to the `{{token}}` variable.
- All entry routes use `{{token}}` automatically.

---

## Database Migrations (Alembic)

```bash
# Create a new migration
alembic revision --autogenerate -m "your message"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

---

## Environment Variables

| Variable                      | Description                       | Example                                               |
|-------------------------------|-----------------------------------|-------------------------------------------------------|
| `DATABASE_URL`                | PostgreSQL connection string      | `postgresql://postgres:root@localhost:5432/pulsr-be`  |
| `SECRET_KEY`                  | JWT signing secret (keep private) | `supersecretkey`                                      |
| `ALGORITHM`                   | JWT algorithm                     | `HS256`                                               |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry in minutes           | `60`                                                  |
