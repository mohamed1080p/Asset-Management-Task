# Asset Management API

A REST API built for the **DarkAtlas Attack Surface Monitoring (ASM)** platform — continuously discovering and tracking an organization's internet-facing assets on behalf of Buguard.

---

## 📋 What It Does

Built as part of the Backend Engineering Track, this API covers the full Asset Management module:

- **Discovers and stores** assets across six types: domains, subdomains, IPs, services, certificates, and technologies
- **Follows asset lifecycle** — records `first_seen` and `last_seen`, and transitions status between `active`, `stale`, and `archived`
- **Maps relationships** — connects assets into a graph (e.g. subdomain → domain, service → IP)
- **Handles re-imports cleanly** — reimporting an existing asset merges its metadata instead of creating a duplicate
- **Supports flexible querying** — filter by type, status, tag, or value, with pagination and sorting built in
- **Secures mutations** — `POST`, `PATCH`, and `DELETE` operations require a valid API key
- **Enforces correctness** — Pydantic handles input shape, services enforce business rules, the DB enforces constraints

---

## 🚀 Getting Started

### Requirements

- Docker & Docker Compose *(easiest path)*
- OR Python 3.11+ with PostgreSQL 14+

### Run with Docker

```bash
cd Asset-Management
docker-compose up -d

# Confirm it's up
curl http://localhost:8000/health

# Browse the docs
open http://localhost:8000/docs
```

```bash
# Tear down
docker-compose down
```

### Run Locally

```bash
# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in DATABASE_URL and API_KEY in .env

# Start the server
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`.

---

## 🔐 Authentication

Write operations require an `X-API-Key` header. Read operations are open.

### Generate a key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Pass it in requests

```bash
curl -X POST http://localhost:8000/assets \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "type": "domain",
    "value": "example.com",
    "source": "manual",
    "tags": ["prod"]
  }'
```

### Environment variables

```env
DATABASE_URL=postgresql://user:password@localhost:5432/asset_management
API_KEY=your-secure-api-key-here
DEBUG=false
```

> ⚠️ Keep `.env` out of version control — it's already in `.gitignore`.

---

## 📚 API Reference

| Format | URL |
|---|---|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/openapi.json |

### Endpoints

#### Assets

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/assets` | List assets — filterable, sortable, paginated | ❌ |
| `POST` | `/assets` | Create an asset | ✅ |
| `GET` | `/assets/{id}` | Fetch a single asset | ❌ |
| `PATCH` | `/assets/{id}` | Update an asset | ✅ |
| `DELETE` | `/assets/{id}` | Remove an asset | ✅ |
| `POST` | `/assets/bulk` | Import a batch of assets | ✅ |
| `POST` | `/assets/{id}/activate` | Reactivate a stale or archived asset | ✅ |
| `POST` | `/assets/mark-stale` | Flag unseen assets as stale | ✅ |

#### Relationships

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/relationships` | Link two assets | ✅ |
| `GET` | `/assets/{id}/relationships` | List all connections for an asset | ❌ |
| `GET` | `/assets/{id}/graph` | Fetch asset plus its full neighbor graph | ❌ |

---

## 📋 Usage Examples

### Create an asset

```bash
curl -X POST http://localhost:8000/assets \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "type": "domain",
    "value": "example.com",
    "source": "scan",
    "tags": ["prod", "root"],
    "metadata": {"discovered_date": "2024-01-15"}
  }'
```

```json
{
  "id": "a1e3f2c1-1234-5678-9abc-def012345678",
  "type": "domain",
  "value": "example.com",
  "status": "active",
  "first_seen": "2024-01-15T10:30:00Z",
  "last_seen": "2024-01-15T10:30:00Z",
  "source": "scan",
  "tags": ["prod", "root"],
  "metadata": {"discovered_date": "2024-01-15"},
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Filter assets

```bash
# Active subdomains tagged "prod", first page
curl "http://localhost:8000/assets?type=subdomain&status=active&tag=prod&page=1&limit=20"
```

### Bulk import

```bash
curl -X POST http://localhost:8000/assets/bulk \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "assets": [
      {"type": "domain", "value": "example.com", "source": "scan"},
      {"type": "subdomain", "value": "api.example.com", "source": "scan"},
      {"type": "ip_address", "value": "203.0.113.10", "source": "scan"}
    ]
  }'
```

```json
{"created": 3, "updated": 0, "duplicates": 0, "total": 3}
```

### Link two assets

```bash
curl -X POST http://localhost:8000/relationships \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "from_asset_id": "a1e3f2c1-1234-5678-9abc-def012345678",
    "to_asset_id": "b2e4f3d2-2345-6789-0def-012345678901",
    "relation_type": "parent"
  }'
```

### Fetch the asset graph

```bash
curl "http://localhost:8000/assets/a1e3f2c1-1234-5678-9abc-def012345678/graph"
```

```json
{
  "asset": {"...": "..."},
  "relationships": [
    {"id": "...", "from_asset_id": "...", "to_asset_id": "...", "relation_type": "parent"}
  ],
  "related_assets": ["..."],
  "relation_count": 1
}
```

---

## 🧪 Testing

```bash
# Full suite
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=app --cov-report=html

# Single class
pytest tests/test_main.py::TestAssetCRUD -v

# Single test
pytest tests/test_main.py::TestAssetCRUD::test_create_asset -v
```

**What's covered:**

- ✅ Asset CRUD
- ✅ Bulk import and upsert deduplication
- ✅ Lifecycle transitions (stale, activate)
- ✅ Relationship creation, retrieval, and graph traversal
- ✅ Pagination and filtering

---

## 🏗️ Project Structure

```
Asset-Management/
├── app/
│   ├── models/
│   │   ├── asset.py                # Asset & AssetTag models, enums
│   │   ├── relationship.py         # Relationship model
│   │   ├── api_key.py              # ApiKey model
│   │   ├── guid.py                 # Custom GUID type decorator
│   │   └── __init__.py
│   ├── services/
│   │   ├── asset_service.py        # CRUD, lifecycle, bulk import
│   │   ├── relationship_service.py # Graph ops
│   │   ├── auth_service.py         # Key hashing and verification
│   │   └── __init__.py
│   ├── main.py                     # Routes and error handlers
│   ├── schemas.py                  # Pydantic schemas
│   ├── database.py                 # Engine and session
│   ├── config.py                   # Settings from environment
│   └── auth.py                     # Auth dependency
├── tests/
│   ├── conftest.py
│   └── test_main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔄 Deduplication & Lifecycle

### How imports stay idempotent

```bash
# First run
POST /assets/bulk → created: 2, updated: 0, duplicates: 0

# Same payload, second run
POST /assets/bulk → created: 0, updated: 2, duplicates: 0
```

The pipeline is:

1. **Deduplicate the batch** — drop repeated `(type, value)` pairs before hitting the DB
2. **Check for existing records** — query by `(type, value)`
3. **Upsert** — update `last_seen` and merge metadata if found; insert if not

### Status transitions

```
active
  ├── re-sighted            → last_seen updated, stays active
  ├── not seen for N days   → mark-stale → stale
  └── stale
        └── /activate       → back to active
```

---

## ✅ Validation & Error Handling

### Request validation (Pydantic)

- `value` — non-empty string, max 500 characters
- `source` — must be `scan`, `import`, or `manual`
- `status` — must be `active`, `stale`, or `archived`
- `tags` — list of non-empty strings
- Relationships — source and target must be different assets

### Business rule validation (services layer)

- Both assets must exist before a relationship can be created
- Self-relationships are rejected
- Duplicate relationships are rejected
- Metadata is merged on upsert, not overwritten

### Error shape

```json
{
  "detail": "Request validation failed",
  "error_code": "VALIDATION_ERROR",
  "errors": [],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Status codes

| Code | When |
|---|---|
| `200` | Successful read |
| `201` | Resource created |
| `204` | Resource deleted |
| `400` | Invalid input or business rule violation |
| `401` | Missing or invalid API key |
| `404` | Resource not found |
| `409` | Duplicate asset |
| `500` | Unexpected server error |
