# Troubleshooting Guide

## Common Issues and Solutions

### 1. Docker Build Errors

#### Error: "failed to compute cache key: not found"

**Cause**: Missing directories that Docker is trying to copy.

**Solution**: The fixed package includes all necessary directories. If you still see this:

```bash
# Make sure these directories exist:
mkdir -p airflow/plugins
mkdir -p airflow/config
mkdir -p src/etl/transformers
mkdir -p src/etl/loaders
mkdir -p src/api
mkdir -p src/utils

# Create placeholder files
touch airflow/plugins/.gitkeep
touch airflow/config/.gitkeep
```

### 2. Environment Variable Warnings

#### Warning: "AIRFLOW_FERNET_KEY variable is not set"

**Cause**: .env file not created or Fernet key not generated.

**Solution**:

**Option A - Automated (recommended)**:
```bash
./setup.sh
```

**Option B - Manual**:
```bash
# Generate Fernet key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Copy and edit .env
cp .env.example .env

# Edit .env and paste the key from above
nano .env  # or use any text editor
```

**Option C - Quick fix**:
```bash
# Just use a sample key for testing
cp .env.example .env
sed -i '' 's/your_fernet_key_here/zTxZ8VfKj8D9K0X2qQvN9RzB6fEsW5yJ4pNsG7HsA8Q=/' .env
sed -i '' 's/your_secret_key_here/test_secret_key_12345/' .env
```

### 3. Services Won't Start

#### Check Service Status

```bash
docker-compose ps
```

You should see:
- `nba_postgres` - Up (healthy)
- `nba_redis` - Up (healthy)
- `nba_airflow_webserver` - Up (healthy)
- `nba_airflow_scheduler` - Up
- `nba_streamlit` - Up

#### If Postgres is unhealthy:

```bash
# Check logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres

# If that doesn't work, recreate it
docker-compose down
docker volume rm nba-analytics-engine_postgres_data
docker-compose up -d postgres
```

#### If Airflow won't start:

```bash
# Check logs
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler

# Common issues:
# 1. Database not ready - just wait 30 seconds and check again
# 2. Fernet key not set - see solution above
# 3. Out of memory - increase Docker memory to 8GB

# Restart Airflow services
docker-compose restart airflow-webserver airflow-scheduler
```

### 4. Port Conflicts

#### Error: "port is already allocated"

**Find what's using the port**:

```bash
# On Mac/Linux
lsof -i :8080  # Airflow
lsof -i :8501  # Streamlit  
lsof -i :5432  # PostgreSQL

# On Windows PowerShell
Get-NetTCPConnection -LocalPort 8080
```

**Solutions**:

1. **Stop the conflicting service**
2. **Change the port** in docker-compose.yml:
   ```yaml
   ports:
     - "9090:8080"  # Use 9090 instead of 8080
   ```

### 5. Can't Access Web UI

#### Airflow UI (http://localhost:8080) not loading

1. **Check if service is running**:
   ```bash
   docker-compose ps airflow-webserver
   ```

2. **Check logs**:
   ```bash
   docker-compose logs airflow-webserver | tail -50
   ```

3. **Wait longer** - Airflow takes 2-3 minutes to fully start
4. **Try accessing**: http://127.0.0.1:8080

#### Streamlit not loading

```bash
# Check if running
docker-compose ps streamlit

# Check logs
docker-compose logs streamlit

# Restart it
docker-compose restart streamlit
```

### 6. Import Errors in Python

#### ModuleNotFoundError

**In Airflow DAGs**:
```bash
# The issue is usually with PYTHONPATH
# Check if src/ is properly mounted
docker-compose exec airflow-webserver ls -la /opt/airflow/src/
```

**In Streamlit**:
```bash
# Check if src/ is mounted
docker-compose exec streamlit ls -la /app/src/
```

**Solution**: Already fixed in docker-compose.yml with proper volume mounts.

### 7. Database Connection Errors

#### "could not connect to server"

```bash
# Wait for postgres to be ready
docker-compose exec postgres pg_isready

# If it says "accepting connections", postgres is ready
# If not, wait 30 seconds and try again

# Test connection manually
docker-compose exec postgres psql -U postgres -d nba_analytics -c "SELECT 1;"
```

#### "database does not exist"

```bash
# Create the database
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE nba_analytics;"

# Run setup script
docker-compose exec postgres psql -U postgres -d nba_analytics -f /docker-entrypoint-initdb.d/setup_db.sql
```

### 8. Out of Memory

#### Symptoms:
- Services randomly stopping
- Docker becoming unresponsive
- "Killed" messages in logs

**Solution**:
1. Open Docker Desktop
2. Go to Settings → Resources → Memory
3. Increase to **at least 8GB**
4. Click "Apply & Restart"
5. Restart your containers:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### 9. Data Not Loading

#### NBA API not responding

**Symptoms**: Airflow tasks failing with API errors

**Solutions**:
1. **Check your internet connection**
2. **Check NBA API status** (sometimes it's down)
3. **Rate limiting** - the code includes retry logic, just wait
4. **Test manually**:
   ```bash
   docker-compose exec airflow-webserver python3 -c "
   from nba_api.stats.static import teams
   print(teams.get_teams())
   "
   ```

### 10. Complete Reset

If nothing works, start fresh:

```bash
# Stop and remove everything
docker-compose down -v

# Remove all Docker images for this project
docker images | grep nba | awk '{print $3}' | xargs docker rmi -f

# Remove .env
rm .env

# Start over
./setup.sh
```

## Getting More Help

### View All Logs
```bash
# All services
docker-compose logs

# Last 100 lines
docker-compose logs --tail=100

# Follow logs in real-time
docker-compose logs -f

# Specific service
docker-compose logs -f airflow-scheduler
```

### Execute Commands Inside Containers

```bash
# Airflow
docker-compose exec airflow-webserver bash

# Postgres
docker-compose exec postgres psql -U postgres -d nba_analytics

# Streamlit
docker-compose exec streamlit bash
```

### Verify Installation

```bash
# Check all Python dependencies
docker-compose exec airflow-webserver pip list

# Check database tables
docker-compose exec postgres psql -U postgres -d nba_analytics -c "\dt staging.*"

# Check dbt
docker-compose exec dbt dbt --version
```

## Prevention Tips

1. **Always run setup.sh first** before docker-compose up
2. **Wait for services** - don't rush, give it 2-3 minutes
3. **Check logs** if something doesn't work
4. **Allocate enough resources** - 8GB RAM minimum
5. **Keep Docker Desktop updated**

## Still Stuck?

Create an issue on GitHub with:
1. Your operating system
2. Docker version (`docker --version`)
3. Error message
4. Output of `docker-compose logs`
5. What you were trying to do

Most issues are:
- ✅ Fernet key not set → Run setup.sh
- ✅ Services not ready → Wait 2-3 minutes
- ✅ Port conflicts → Change ports in docker-compose.yml
- ✅ Out of memory → Increase Docker memory to 8GB
