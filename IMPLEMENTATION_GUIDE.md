# NBA Analytics Engine - Implementation Guide

## 🎯 Project Overview

This guide walks you through building a production-grade NBA analytics platform from scratch. The project demonstrates expertise in:
- **Data Engineering**: ETL pipelines, data warehousing, orchestration
- **Analytics**: Advanced NBA metrics, statistical modeling
- **Machine Learning**: Predictive models for game outcomes
- **Software Engineering**: Testing, CI/CD, containerization

## 📚 Table of Contents

1. [Architecture](#architecture)
2. [Setup & Installation](#setup--installation)
3. [Development Workflow](#development-workflow)
4. [Data Pipeline](#data-pipeline)
5. [Analytics & Metrics](#analytics--metrics)
6. [Dashboard Development](#dashboard-development)
7. [Testing Strategy](#testing-strategy)
8. [Deployment](#deployment)
9. [Maintenance & Monitoring](#maintenance--monitoring)

## 🏗 Architecture

### System Architecture

```
┌─────────────────┐
│   NBA API       │
│  (nba_api lib)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Airflow DAGs   │  ← Orchestration layer
│  - Daily refresh│
│  - Historical   │
│  - ML pipeline  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │  ← Data warehouse
│  - Staging      │
│  - Dimensions   │
│  - Facts        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   dbt Models    │  ← Transformation layer
│  - Staging      │
│  - Marts        │
│  - Tests        │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐  ┌──────────┐
│Streamlit│ │ ML Models│
│Dashboard│ │ (sklearn)│
└─────────┘ └──────────┘
```

### Tech Stack Rationale

**Why Apache Airflow?**
- Industry-standard orchestration
- Python-native (easy integration)
- Rich monitoring UI
- Extensive plugin ecosystem

**Why PostgreSQL?**
- ACID compliance
- Excellent for analytical queries
- Mature, well-documented
- Free & open-source

**Why dbt?**
- Version control for transformations
- Testing built-in
- Documentation generation
- SQL-based (accessible to analysts)

**Why Streamlit?**
- Rapid development
- Python-native
- Interactive components
- Easy deployment

## 🚀 Setup & Installation

### Prerequisites

```bash
# Required software
- Docker Desktop (latest)
- Python 3.9+
- Git
- PostgreSQL client (psql)

# Optional but recommended
- VSCode with Python extension
- DBeaver or pgAdmin for DB management
- Postman for API testing
```

### Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/getrichthroughcode/nba-analytics-engine.git
cd nba-analytics-engine

# 2. Create environment file
cp .env.example .env

# 3. Generate Airflow Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy output to AIRFLOW_FERNET_KEY in .env

# 4. Start services with Docker Compose
docker-compose up -d

# 5. Wait for services to be healthy (2-3 minutes)
docker-compose ps

# 6. Initialize the database
docker-compose exec postgres psql -U postgres -d nba_analytics -f /docker-entrypoint-initdb.d/setup_db.sql

# 7. Access the applications
# Airflow: http://localhost:8080 (admin/admin)
# Streamlit: http://localhost:8501
# PostgreSQL: localhost:5432
```

### Verify Installation

```bash
# Check Airflow
docker-compose exec airflow-webserver airflow dags list

# Check dbt
docker-compose exec dbt dbt debug

# Check database
docker-compose exec postgres psql -U postgres -d nba_analytics -c "SELECT schema_name FROM information_schema.schemata;"
```

## 💻 Development Workflow

### Local Development Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up pre-commit hooks
pip install pre-commit
pre-commit install

# 4. Run tests
pytest tests/ -v
```

### Code Style & Quality

```bash
# Format code
black src/ tests/ streamlit/
isort src/ tests/ streamlit/

# Lint code
flake8 src/ tests/ streamlit/
pylint src/

# Type checking
mypy src/
```

### Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/player-comparison-v2

# 2. Make changes and commit
git add .
git commit -m "feat: add advanced player comparison metrics"

# 3. Push and create PR
git push origin feature/player-comparison-v2

# 4. CI/CD will run automatically
# - Linting
# - Unit tests
# - Integration tests
# - dbt tests
# - Docker builds
```

## 🔄 Data Pipeline

### Understanding the ETL Flow

**Extract** → **Transform** → **Load**

```python
# Example: Daily refresh workflow

# 1. EXTRACT - Pull data from NBA API
from src.etl.extractors.nba_extractor import NBAExtractor

extractor = NBAExtractor()
games = extractor.get_games_by_date('2024-12-13')
player_stats = extractor.get_player_game_stats(game_id)

# 2. TRANSFORM - Clean and calculate metrics
from src.etl.transformers.nba_transformer import NBATransformer
from src.analytics.metrics import calculate_advanced_metrics

transformer = NBATransformer()
clean_stats = transformer.transform_player_stats(player_stats)
enhanced_stats = calculate_advanced_metrics(clean_stats)

# 3. LOAD - Insert into PostgreSQL
from src.etl.loaders.postgres_loader import PostgresLoader

loader = PostgresLoader()
loader.load_player_stats_staging(enhanced_stats)

# 4. DBT - Transform to star schema
# Triggered via Airflow BashOperator
# dbt run --select marts.player_season_stats
```

### Running the Pipeline

**Manual Execution:**
```bash
# Trigger the daily refresh DAG
docker-compose exec airflow-scheduler airflow dags trigger nba_daily_refresh

# Monitor progress
docker-compose exec airflow-scheduler airflow dags state nba_daily_refresh

# View logs
docker-compose logs -f airflow-scheduler
```

**Historical Data Load:**
```bash
# Load all historical data (30+ years)
docker-compose exec airflow-scheduler airflow dags trigger nba_historical_load \
  --conf '{"start_season": "1996-97", "end_season": "2024-25"}'
```

### Data Quality Checks

```python
# Example: Validate data quality
from src.utils.data_quality import DataQualityChecker

checker = DataQualityChecker()

# Check for nulls in critical fields
checker.check_null_values('fact_player_game_stats', ['player_key', 'points'])

# Check referential integrity
checker.check_referential_integrity(
    'fact_player_game_stats',
    'dim_players',
    'player_key'
)

# Check for duplicates
checker.check_duplicates('fact_player_game_stats', ['player_key', 'game_key'])
```

## 📊 Analytics & Metrics

### Advanced Metrics Implementation

**Player Efficiency Rating (PER)**
```python
from src.analytics.metrics import AdvancedMetricsCalculator

calc = AdvancedMetricsCalculator()

per = calc.calculate_per(
    min_played=36.5,
    fg3m=3,
    ast=7,
    fgm=10,
    ftm=5,
    # ... additional stats
)
# Returns: 25.3 (All-Star level)
```

**Win Shares**
```python
win_shares = calc.calculate_win_shares(
    points=27,
    fgm=10,
    fga=20,
    # ... additional stats
)
# Returns: {'offensive_ws': 0.15, 'defensive_ws': 0.08, 'total_ws': 0.23}
```

### Custom Analysis Examples

**Shot Chart Analysis**
```sql
-- Shooting zones analysis
SELECT
    player_name,
    shot_zone,
    COUNT(*) as attempts,
    SUM(CASE WHEN shot_made THEN 1 ELSE 0 END) as makes,
    ROUND(
        SUM(CASE WHEN shot_made THEN 1 ELSE 0 END)::NUMERIC / COUNT(*),
        3
    ) as fg_pct
FROM shot_chart_data
WHERE player_key = 123 AND season_id = '2024-25'
GROUP BY player_name, shot_zone
ORDER BY attempts DESC;
```

**Clutch Performance**
```sql
-- Performance in clutch time (last 5 minutes, score within 5)
SELECT
    p.player_name,
    COUNT(*) as clutch_games,
    AVG(f.points) as clutch_ppg,
    AVG(f.field_goal_pct) as clutch_fg_pct
FROM fact_player_game_stats f
JOIN dim_players p ON f.player_key = p.player_key
WHERE f.is_clutch_time = TRUE
GROUP BY p.player_name
HAVING COUNT(*) >= 10
ORDER BY clutch_ppg DESC
LIMIT 20;
```

## 🎨 Dashboard Development

### Streamlit Best Practices

**Performance Optimization**
```python
import streamlit as st

# Cache expensive queries
@st.cache_data(ttl=3600)
def load_player_data(player_id):
    # ... database query
    return data

# Cache database connections
@st.cache_resource
def get_db_connection():
    return DatabaseConnection()

# Use session state for user interactions
if 'selected_player' not in st.session_state:
    st.session_state.selected_player = None
```

**Interactive Components**
```python
# Multi-select for player comparison
players = st.multiselect(
    "Select players to compare",
    options=player_list,
    default=["LeBron James", "Stephen Curry"],
    max_selections=3
)

# Slider for date range
date_range = st.slider(
    "Select date range",
    min_value=datetime(2024, 10, 1),
    max_value=datetime.now(),
    value=(datetime(2024, 10, 1), datetime.now())
)

# Dynamic charts with Plotly
fig = go.Figure()
for player in players:
    data = load_player_data(player)
    fig.add_trace(go.Scatter(
        x=data['game_date'],
        y=data['points'],
        name=player,
        mode='lines+markers'
    ))

st.plotly_chart(fig, use_container_width=True)
```

## 🧪 Testing Strategy

### Test Structure

```
tests/
├── unit/                  # Unit tests for individual functions
│   ├── test_extractors.py
│   ├── test_transformers.py
│   ├── test_metrics.py
│   └── test_loaders.py
├── integration/           # Integration tests for workflows
│   ├── test_etl_pipeline.py
│   ├── test_dbt_models.py
│   └── test_api_endpoints.py
└── fixtures/              # Test data and mocks
    ├── sample_games.json
    └── sample_player_stats.json
```

### Writing Tests

```python
# tests/unit/test_metrics.py
import pytest
from src.analytics.metrics import AdvancedMetricsCalculator

@pytest.fixture
def calculator():
    return AdvancedMetricsCalculator()

def test_true_shooting_percentage(calculator):
    ts_pct = calculator.calculate_true_shooting_pct(
        points=30,
        fga=20,
        fta=5
    )
    assert 0 <= ts_pct <= 1
    assert ts_pct == pytest.approx(0.682, rel=0.01)

def test_per_calculation(calculator):
    per = calculator.calculate_per(
        min_played=36,
        fg3m=3,
        ast=7,
        fgm=10,
        ftm=5,
        # ... other stats
    )
    assert per > 0
    assert per < 50  # Reasonable bounds
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_metrics.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run only fast tests (skip slow integration tests)
pytest tests/ -m "not slow"
```

## 🚀 Deployment

### Production Checklist

- [ ] Environment variables configured
- [ ] Database backups enabled
- [ ] Monitoring & alerting set up
- [ ] SSL/TLS certificates configured
- [ ] Rate limiting implemented
- [ ] Error tracking (Sentry) integrated
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Runbooks created

### Deployment Steps

```bash
# 1. Build production images
docker-compose -f docker-compose.prod.yml build

# 2. Run migrations
docker-compose -f docker-compose.prod.yml run dbt dbt run

# 3. Start services
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify health
curl http://localhost:8080/health
curl http://localhost:8501/health

# 5. Trigger initial data load
curl -X POST http://localhost:8080/api/v1/dags/nba_historical_load/dagRuns
```

## 📈 Maintenance & Monitoring

### Daily Operations

**Monitor Airflow DAGs:**
```bash
# Check DAG runs
docker-compose exec airflow-scheduler airflow dags list-runs -d nba_daily_refresh

# View task logs
docker-compose logs airflow-scheduler | grep ERROR
```

**Database Maintenance:**
```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname IN ('staging', 'dwh', 'analytics')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Vacuum and analyze
VACUUM ANALYZE fact_player_game_stats;
VACUUM ANALYZE fact_team_game_stats;
```

### Performance Optimization

**Query Optimization:**
```sql
-- Create covering indexes for common queries
CREATE INDEX idx_player_stats_covering
ON fact_player_game_stats(season_key, player_key)
INCLUDE (points, assists, rebounds);

-- Partition large tables by season
CREATE TABLE fact_player_game_stats_2024
PARTITION OF fact_player_game_stats
FOR VALUES IN ('2024-25');
```

**Airflow Tuning:**
```python
# airflow.cfg adjustments
[core]
parallelism = 32
dag_concurrency = 16
max_active_runs_per_dag = 1

[scheduler]
max_threads = 4
```

## 📝 Common Issues & Solutions

### Issue: Airflow tasks timing out

**Solution:**
```python
# Increase timeout in DAG definition
default_args = {
    'execution_timeout': timedelta(hours=2),  # Increase from 1h
}
```

### Issue: PostgreSQL connection pool exhausted

**Solution:**
```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### Issue: dbt models failing

**Solution:**
```bash
# Run dbt in debug mode
dbt --debug run --select model_name

# Check compiled SQL
cat target/compiled/nba_analytics/models/marts/player_season_stats.sql
```

## 🎓 Learning Resources

- **NBA API Documentation**: https://github.com/swar/nba_api
- **Basketball-Reference**: https://www.basketball-reference.com
- **Airflow Documentation**: https://airflow.apache.org/docs/
- **dbt Documentation**: https://docs.getdbt.com/
- **Advanced NBA Metrics**: Basketball Analytics books

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.
