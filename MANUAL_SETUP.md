# Manual Setup Instructions

If the automated setup script doesn't work, follow these steps:

## Step 1: Generate Fernet Key

Run this command in your terminal:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output (it will look like: `xYz123abc...`)

## Step 2: Create .env File

```bash
cp .env.example .env
```

Then edit `.env` and replace:
- `your_fernet_key_here` with the key from Step 1
- `your_secret_key_here` with any random string (or use another Fernet key)

## Step 3: Start Docker Compose

```bash
docker-compose up -d
```

## Step 4: Wait for Services

Give it 2-3 minutes for all services to start. Check status with:

```bash
docker-compose ps
```

All services should show "Up" or "Up (healthy)"

## Step 5: Initialize Database

```bash
docker-compose exec postgres psql -U postgres -d nba_analytics -f /docker-entrypoint-initdb.d/setup_db.sql
```

## Step 6: Verify

- Airflow: http://localhost:8080 (login: admin/admin)
- Streamlit: http://localhost:8501
- PostgreSQL: http://localhost:5433 (login: postgres/postgres)

## Troubleshooting

### Error: "Cannot connect to Docker daemon"
- Start Docker Desktop
- Wait for it to fully start
- Try again

### Error: "Port already in use"
One of the required ports (8080, 8501, 5432) is in use.

Find what's using the port:
```bash
# On Mac/Linux
lsof -i :8080
lsof -i :8501
lsof -i :5432

# On Windows (PowerShell)
Get-NetTCPConnection -LocalPort 8080
```

Then either:
1. Stop the conflicting service
2. Or edit `docker-compose.yml` to use different ports

### Error: "Out of memory"
- Open Docker Desktop
- Go to Settings → Resources → Memory
- Increase to at least 8GB
- Click "Apply & Restart"

### Services won't start
Check logs:
```bash
docker-compose logs
```

Or for specific service:
```bash
docker-compose logs airflow-scheduler
docker-compose logs postgres
```

### Database initialization fails
The database might already be initialized. This is OK - you can proceed.

## Clean Slate (if needed)

To completely reset and start over:

```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Remove the .env file
rm .env

# Start from Step 1 again
```
