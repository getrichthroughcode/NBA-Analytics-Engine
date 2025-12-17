# NBA Analytics Engine - Quick Start Guide

Get up and running in 10 minutes! ⚡

## Prerequisites

- Docker Desktop installed and running
- 8GB RAM available
- 10GB disk space
- Internet connection

## 🚀 One-Command Setup

```bash
# Clone and start everything
git clone https://github.com/getrichthroughcode/nba-analytics-engine.git && \
cd nba-analytics-engine && \
cp .env.example .env && \
docker-compose up -d
```

Wait 3-4 minutes for all services to start.

## 🎯 Access Your Applications

Once services are running:

| Application | URL | Credentials |
|-------------|-----|-------------|
| **Airflow Web UI** | http://localhost:8080 | admin / admin |
| **Streamlit Dashboard** | http://localhost:8501 | No login required |
| **PostgreSQL** | localhost:5432 | postgres / postgres |

## ✅ Verify Installation

Run this command to check all services are healthy:

```bash
docker-compose ps
```

You should see:
```
NAME                     STATUS
nba_airflow_scheduler    Up (healthy)
nba_airflow_webserver    Up (healthy)
nba_postgres             Up (healthy)
nba_streamlit            Up
nba_redis                Up (healthy)
```

## 📊 Load Sample Data

### Option 1: Load Last Week's Data (Fast - 2 minutes)

```bash
# Trigger daily refresh for recent data
docker-compose exec airflow-webserver airflow dags trigger nba_daily_refresh
```

Watch progress in Airflow UI: http://localhost:8080

### Option 2: Load Full Season (Slower - 30 minutes)

```bash
# Load entire 2024-25 season
docker-compose exec airflow-webserver airflow dags trigger nba_historical_load \
  --conf '{"start_season": "2024-25", "end_season": "2024-25"}'
```

### Option 3: Use Sample Data (Instant)

```bash
# Load pre-built sample dataset
docker-compose exec postgres psql -U postgres -d nba_analytics < scripts/sample_data.sql
```

## 🎨 Explore the Dashboard

1. Open http://localhost:8501
2. Navigate through:
   - **Home**: League overview and standings
   - **League Leaders**: Top performers by stat
   - **Player Comparison**: Compare up to 3 players
   - **Team Analytics**: Team performance tracking

## 🔍 Sample Queries

Connect to PostgreSQL and try these queries:

```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d nba_analytics
```

**Top 10 scorers this season:**
```sql
SELECT 
    player_name,
    team_name,
    ppg,
    games_played
FROM analytics.mv_player_season_stats
WHERE season_id = '2024-25'
ORDER BY ppg DESC
LIMIT 10;
```

**Team standings:**
```sql
SELECT 
    team_name,
    wins,
    losses,
    ROUND(wins::NUMERIC / (wins + losses), 3) as win_pct
FROM dwh.fact_team_game_stats
GROUP BY team_name
ORDER BY win_pct DESC;
```

## 🛠️ Common Tasks

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f airflow-scheduler
docker-compose logs -f streamlit
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart airflow-scheduler
```

### Stop Everything

```bash
docker-compose down
```

### Complete Reset (including data)

```bash
docker-compose down -v  # Warning: Deletes all data!
```

## 📚 Next Steps

1. **Read the Documentation**
   - [README.md](README.md) - Project overview
   - [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Detailed guide
   - [CV_PROJECT_SUMMARY.md](CV_PROJECT_SUMMARY.md) - Resume talking points

2. **Customize Your Setup**
   - Edit `.env` file for custom configuration
   - Modify `airflow/dags/` for custom workflows
   - Update `streamlit/app.py` for custom dashboards

3. **Add More Data**
   - Historical seasons: Modify date ranges in Airflow
   - Additional stats: Extend extractors and transformers
   - Custom metrics: Add calculations in `src/analytics/metrics.py`

## 🐛 Troubleshooting

### Services won't start

```bash
# Check Docker is running
docker info

# Check port conflicts
lsof -i :8080  # Airflow
lsof -i :8501  # Streamlit
lsof -i :5432  # PostgreSQL

# View detailed errors
docker-compose logs
```

### Database connection errors

```bash
# Verify PostgreSQL is ready
docker-compose exec postgres pg_isready

# Recreate database
docker-compose down
docker volume rm nba-analytics-engine_postgres_data
docker-compose up -d
```

### Airflow tasks failing

```bash
# Check Airflow logs
docker-compose logs airflow-scheduler

# Clear failed task
docker-compose exec airflow-webserver airflow tasks clear nba_daily_refresh

# Restart Airflow
docker-compose restart airflow-scheduler airflow-webserver
```

### Out of memory

```bash
# Increase Docker memory allocation:
# Docker Desktop → Settings → Resources → Memory (set to 8GB)
```

## 💡 Pro Tips

1. **Airflow UI**: Bookmark http://localhost:8080/home
2. **Auto-refresh**: Enable in Streamlit for live updates
3. **Database Tool**: Use DBeaver or pgAdmin for easier querying
4. **Performance**: Close unused applications to free up memory
5. **Data**: Start with recent data, add historical data gradually

## 🎯 Success Checklist

- [ ] All services running (`docker-compose ps` shows healthy)
- [ ] Can access Airflow UI
- [ ] Can access Streamlit dashboard
- [ ] Sample data loaded successfully
- [ ] Can run SQL queries
- [ ] Can trigger DAGs in Airflow

## 📞 Getting Help

- **Documentation**: Check [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **Issues**: GitHub Issues for bug reports
- **Questions**: GitHub Discussions for Q&A

## 🎉 You're Ready!

Your NBA Analytics Engine is now running. Start exploring the data and building insights!

**Recommended First Steps:**
1. Load some recent data (Option 1 above)
2. Explore the Streamlit dashboard
3. Run some SQL queries
4. Check out the Airflow DAGs
5. Read the implementation guide for deeper understanding

Happy analyzing! 🏀📊
