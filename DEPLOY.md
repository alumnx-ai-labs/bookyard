# Deployment & Usage Guide

## Quick Start (Local Development)

Run the full stack with a single command. Code changes will hot-reload.

```bash
docker-compose up --build
```

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Prerequisites
1. **Docker Desktop** installed.
2. **Environment Variables**:
   - `backend/.env`: Must contain `DATABASE_URL` (Supabase) and `ADMIN_SECRET`.
   - `frontend/.env`: Optional frontend vars.

---

## Production Deployment (EC2)

To deploy the optimized production build (Nginx + Uvicorn):

1. **Copy Files**: Clone repo to EC2.
2. **Configure Env**: Set production `.env` files.
3. **Run**:
   ```bash
   # Use the production Dockerfile logic (default build)
   # We need a separate compose or override for prod to simpler run nginx
   # For this MVP, you can just build/run specific images or modify command.
   
   docker-compose up -d
   ```
   *Note: The default `docker-compose.yml` is set for DEV (hot-reload). For strict production, remove the `command` overrides to let the Dockerfile `CMD` (Nginx/Uvicorn) take over.*
