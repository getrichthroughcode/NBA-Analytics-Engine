# NBA Analytics Engine: ETL, Modeling & Insights

> **Full-stack analytics platform** — End-to-end pipeline ingesting 30+ years of NBA data with automated ETL, data warehouse, and interactive dashboards.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-green.svg)](https://www.postgresql.org/)
[![Apache Airflow](https://img.shields.io/badge/Airflow-2.7+-orange.svg)](https://airflow.apache.org/)
[![dbt](https://img.shields.io/badge/dbt-1.6+-red.svg)](https://www.getdbt.com/)

## 🏀 Overview

A scalable, production-grade NBA analytics platform featuring:
- **ETL Pipeline**: Automated data ingestion from NBA API (30+ years of historical data)
- **Data Warehouse**: Star schema optimized for analytics queries
- **Advanced Analytics**: PER, Win Shares, temporal trends, statistical comparisons
- **ML Predictions**: Machine learning models for game outcome predictions
- **Interactive Dashboards**: Real-time visualization with Streamlit

## 🎯 Key Features

### Data Engineering
- ✅ **Complete ETL Pipeline**: REST API ingestion → transformation → loading
- ✅ **Airflow Orchestration**: Scheduled daily refreshes of 500+ team/player statistics
- ✅ **Incremental Loads**: Efficient delta processing with SCD Type 2
- ✅ **Data Quality**: Automated validation checks and monitoring
- ✅ **Star Schema**: Optimized dimensional model for fast queries

### Analytics & ML
- 📊 **Advanced Metrics**: PER, Win Shares, True Shooting %, Usage Rate
- 📈 **Temporal Analysis**: Season trends, career trajectories, team evolution
- 🔍 **Statistical Comparisons**: Player vs player, team vs league averages
- 🤖 **ML Predictions**: Game outcome forecasting with Scikit-learn
- 📉 **Performance Tracking**: Real-time player and team monitoring

### Infrastructure
- 🐳 **Docker Containerization**: Complete environment reproducibility
- 🔄 **CI/CD Pipeline**: GitHub Actions for automated testing and deployment
- 🧪 **Unit Tests**: Comprehensive test coverage for data quality
- 📝 **dbt Transformations**: Version-controlled SQL transformations
- 🎨 **Streamlit UI**: Interactive, responsive dashboards

## 🛠 Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Language** | Python 3.9+ |
| **Data Processing** | Pandas, NumPy, Scikit-learn |
| **Database** | PostgreSQL 14+ |
| **Orchestration** | Apache Airflow 2.7+ |
| **Transformation** | dbt Core 1.6+ |
| **Visualization** | Streamlit, Plotly, Matplotlib |
| **API Integration** | NBA API (nba_api library) |
| **Containerization** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions, pytest |
| **Version Control** | Git, GitHub |

## 📁 Project Structure

```
nba-analytics-engine/
├── airflow/                    # Orchestration layer
│   ├── dags/
│   │   ├── nba_daily_refresh.py
│   │   ├── nba_historical_load.py
│   │   └── nba_ml_pipeline.py
│   ├── plugins/
│   └── config/
├── dbt/                        # Transformation layer
│   ├── models/
│   │   ├── staging/           # Raw → staging
│   │   ├── intermediate/      # Business logic
│   │   └── marts/             # Star schema
│   ├── tests/
│   └── macros/
├── src/                        # Application code
│   ├── etl/
│   │   ├── extractors/        # NBA API clients
│   │   ├── transformers/      # Data processing
│   │   └── loaders/           # DB writers
│   ├── analytics/
│   │   ├── metrics.py         # Advanced stats
│   │   └── models.py          # ML models
│   ├── api/
│   │   └── endpoints.py       # REST API
│   └── utils/
├── streamlit/                  # Visualization layer
│   ├── app.py
│   ├── pages/
│   └── components/
├── tests/                      # Test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docker/                     # Container configs
│   ├── Dockerfile.airflow
│   ├── Dockerfile.streamlit
│   └── docker-compose.yml
├── scripts/                    # Utility scripts
│   ├── setup_db.sql
│   ├── seed_data.py
│   └── run_tests.sh
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── requirements.txt
├── setup.py
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- PostgreSQL 14+ (or use Docker)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/getrichthroughcode/nba-analytics-engine.git
cd nba-analytics-engine
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Launch with Docker Compose**
```bash
docker-compose up -d
```

4. **Initialize the database**
```bash
docker-compose exec airflow python scripts/setup_db.sql
```

5. **Trigger historical data load**
```bash
docker-compose exec airflow airflow dags trigger nba_historical_load
```

### Access Points
- **Airflow UI**: http://localhost:8080 (user: admin, password: admin)
- **Streamlit Dashboard**: http://localhost:8501
- **PostgreSQL**: localhost:5432 (user: postgres)

## 📊 Data Architecture

### Star Schema Design

```
┌─────────────────┐
│  dim_players    │
│─────────────────│
│ player_key (PK) │
│ player_id       │
│ player_name     │
│ position        │
│ ...             │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐      ┌──────────────────┐
│   dim_teams     │      │   dim_seasons    │
│─────────────────│      │──────────────────│
│ team_key (PK)   │      │ season_key (PK)  │
│ team_id         │      │ season_id        │
│ team_name       │      │ start_year       │
│ conference      │      │ end_year         │
│ ...             │      │ ...              │
└─────────────────┘      └──────────────────┘
         │                        │
         │ 1:N                    │ 1:N
         ▼                        ▼
┌───────────────────────────────────────────┐
│           fact_player_game_stats          │
│───────────────────────────────────────────│
│ game_stats_key (PK)                       │
│ player_key (FK) ────────────────────┐     │
│ team_key (FK) ──────────────────┐   │     │
│ season_key (FK) ────────────┐   │   │     │
│ game_id                     │   │   │     │
│ points                      │   │   │     │
│ rebounds                    │   │   │     │
│ assists                     │   │   │     │
│ minutes_played             │   │   │     │
│ ...                        │   │   │     │
└────────────────────────────┴───┴───┴─────┘
```

### Data Flow

```
NBA API → Extract (Python) → Raw Layer (PostgreSQL)
                                    ↓
                            Staging (dbt)
                                    ↓
                            Intermediate (dbt)
                                    ↓
                            Marts (Star Schema)
                                    ↓
              ┌─────────────────────┴──────────────────┐
              ↓                                        ↓
    Analytics Layer (Python/SQL)              Streamlit Dashboard
              ↓
    ML Models (Scikit-learn)
```

## 🎯 Key Metrics & Analytics

### Advanced Player Metrics
- **PER (Player Efficiency Rating)**: Per-minute productivity measure
- **Win Shares**: Estimate of wins contributed by a player
- **True Shooting %**: Shooting efficiency including 3PT and FT
- **Usage Rate**: % of team plays used by a player
- **BPM (Box Plus/Minus)**: Box score estimate of points per 100 possessions

### Team Analytics
- **Offensive/Defensive Rating**: Points scored/allowed per 100 possessions
- **Pace**: Possessions per 48 minutes
- **Four Factors**: eFG%, TOV%, ORB%, FT/FGA
- **Net Rating**: Offensive Rating - Defensive Rating

### ML Models
- **Game Outcome Prediction**: Win probability based on team stats
- **Player Performance Forecasting**: Next-game statistics prediction
- **Playoff Probability**: End-of-season playoff chances

## 🔄 Automation & Scheduling

### Airflow DAGs

1. **nba_daily_refresh** (Daily at 2 AM EST)
   - Extract previous day's games
   - Update player/team statistics
   - Refresh materialized views
   - Run data quality checks
   - Update ML models

2. **nba_historical_load** (On-demand)
   - Backfill historical data (1946-present)
   - Incremental season-by-season loading
   - Data validation and reconciliation

3. **nba_ml_pipeline** (Weekly)
   - Retrain prediction models
   - Feature engineering
   - Model evaluation and deployment

## 🧪 Testing & Quality

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run data quality checks
dbt test

# Validate data freshness
python scripts/data_quality.py
```

### Quality Checks
- ✅ Schema validation
- ✅ Null checks on critical fields
- ✅ Referential integrity
- ✅ Duplicate detection
- ✅ Statistical anomaly detection
- ✅ Data freshness monitoring

## 📈 Sample Queries

### Top 10 Players by PER (Current Season)
```sql
SELECT
    p.player_name,
    t.team_name,
    AVG(f.per) as avg_per,
    AVG(f.points) as avg_points
FROM fact_player_game_stats f
JOIN dim_players p ON f.player_key = p.player_key
JOIN dim_teams t ON f.team_key = t.team_key
JOIN dim_seasons s ON f.season_key = s.season_key
WHERE s.season_id = '2024-25'
GROUP BY p.player_name, t.team_name
ORDER BY avg_per DESC
LIMIT 10;
```

### Team Performance Trends
```sql
WITH team_stats AS (
    SELECT
        t.team_name,
        s.season_id,
        AVG(f.offensive_rating) as off_rtg,
        AVG(f.defensive_rating) as def_rtg,
        AVG(f.net_rating) as net_rtg
    FROM fact_team_game_stats f
    JOIN dim_teams t ON f.team_key = t.team_key
    JOIN dim_seasons s ON f.season_key = s.season_key
    GROUP BY t.team_name, s.season_id
)
SELECT * FROM team_stats
WHERE team_name = 'Los Angeles Lakers'
ORDER BY season_id DESC;
```

## 🎨 Dashboard Features

### Player Dashboard
- Career statistics and trends
- Shot charts and heat maps
- Per-game and advanced metrics
- Head-to-head comparisons
- Injury history and availability

### Team Dashboard
- Season overview and standings
- Offensive/defensive efficiency
- Lineup analysis
- Schedule and results
- Playoff probability tracker

### League Dashboard
- Power rankings
- Statistical leaders
- Trending players/teams
- Playoff picture
- Historical comparisons

## 🚧 Roadmap

- [ ] **Phase 1**: Core ETL and data warehouse (✅ Complete)
- [ ] **Phase 2**: Basic analytics and dashboards (✅ Complete)
- [ ] **Phase 3**: ML predictions and advanced metrics (🔄 In Progress)
- [ ] **Phase 4**: Real-time game tracking
- [ ] **Phase 5**: Mobile app integration
- [ ] **Phase 6**: Public API deployment

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [nba_api](https://github.com/swar/nba_api) - NBA stats API wrapper
- Basketball-Reference for metric formulas
- NBA.com for official statistics

## 📧 Contact

- **GitHub**: [@getrichthroughcode](https://github.com/getrichthroughcode)
- **Project**: [NBA Analytics Engine](https://github.com/getrichthroughcode/nba-analytics-engine)

---

**Built with ❤️ and 🏀 by a data enthusiast**
