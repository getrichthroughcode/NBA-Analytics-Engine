# NBA Analytics Engine - Complete Project Structure

```
nba-analytics-engine/
│
├── README.md                          # Main project documentation
├── LICENSE                            # MIT License
├── setup.py                          # Python package configuration
├── requirements.txt                   # Python dependencies
├── pytest.ini                        # Testing configuration
├── .gitignore                        # Git ignore patterns
├── .env.example                      # Environment template
├── docker-compose.yml                # Docker orchestration
│
├── QUICK_START.md                    # Quick setup guide
├── MANUAL_SETUP.md                   # Manual setup instructions
├── TROUBLESHOOTING.md                # Common issues & solutions
├── IMPLEMENTATION_GUIDE.md           # Detailed technical guide
├── CV_PROJECT_SUMMARY.md             # Resume/interview prep
├── setup.sh                          # Automated setup script
│
├── .github/                          # GitHub configuration
│   └── workflows/
│       └── ci.yml                    # CI/CD pipeline
│
├── airflow/                          # Orchestration layer
│   ├── dags/
│   │   ├── nba_daily_refresh.py      # Daily data refresh
│   │   ├── nba_historical_load.py    # Historical backfill
│   │   └── nba_ml_pipeline.py        # ML training pipeline
│   ├── plugins/                      # Custom Airflow plugins
│   │   └── README.md
│   └── config/                       # Airflow configuration
│       └── README.md
│
├── dbt/                              # Transformation layer
│   ├── dbt_project.yml               # dbt project config
│   ├── profiles.yml                  # Connection profiles
│   ├── models/
│   │   ├── staging/                  # Raw → staging
│   │   │   ├── sources.yml           # Source definitions
│   │   │   └── stg_player_game_stats.sql
│   │   ├── intermediate/             # Business logic
│   │   │   └── int_player_game_metrics.sql
│   │   └── marts/                    # Star schema (analytics)
│   │       └── player_season_stats.sql
│   ├── tests/                        # dbt tests
│   │   └── .gitkeep
│   └── macros/                       # dbt macros
│       └── .gitkeep
│
├── src/                              # Application code
│   ├── __init__.py
│   ├── etl/                          # ETL pipeline
│   │   ├── __init__.py
│   │   ├── extractors/               # NBA API clients
│   │   │   ├── __init__.py
│   │   │   └── nba_extractor.py      # Main extractor
│   │   ├── transformers/             # Data processing
│   │   │   ├── __init__.py
│   │   │   └── nba_transformer.py    # Data transformation
│   │   └── loaders/                  # DB writers
│   │       ├── __init__.py
│   │       └── postgres_loader.py    # PostgreSQL loader
│   ├── analytics/                    # Analytics & ML
│   │   ├── __init__.py
│   │   ├── metrics.py                # Advanced NBA metrics
│   │   └── models.py                 # ML prediction models
│   ├── api/                          # REST API (future)
│   │   └── __init__.py
│   └── utils/                        # Utilities
│       ├── __init__.py
│       ├── logger.py                 # Logging utilities
│       ├── config.py                 # Configuration
│       ├── database.py               # DB connections
│       └── data_quality.py           # Data validation
│
├── streamlit/                        # Visualization layer
│   ├── app.py                        # Main dashboard
│   ├── pages/                        # Multi-page app pages
│   │   └── .gitkeep
│   └── components/                   # Reusable UI components
│       └── .gitkeep
│
├── tests/                            # Test suite
│   ├── unit/                         # Unit tests
│   │   └── test_extractors.py
│   ├── integration/                  # Integration tests
│   │   └── .gitkeep
│   └── fixtures/                     # Test data
│       └── .gitkeep
│
├── docker/                           # Container configs
│   ├── Dockerfile.airflow            # Airflow image
│   ├── Dockerfile.streamlit          # Streamlit image
│   └── Dockerfile.dbt                # dbt image
│
└── scripts/                          # Utility scripts
    └── setup_db.sql                  # Database initialization
```

## Directory Descriptions

### Root Level
- **Documentation files**: README, guides, troubleshooting
- **Configuration files**: setup.py, requirements.txt, .env.example
- **Automation**: setup.sh, docker-compose.yml

### `/airflow` - Orchestration
- **dags/**: DAG definitions for workflows
  - Daily refresh, historical load, ML pipeline
- **plugins/**: Custom operators, hooks, sensors
- **config/**: Additional Airflow configuration

### `/dbt` - Data Transformation
- **models/staging/**: Clean raw data
- **models/intermediate/**: Business logic transformations
- **models/marts/**: Final analytics tables (star schema)
- **tests/**: Data quality tests
- **macros/**: Reusable SQL macros

### `/src` - Application Code
- **etl/**: Extract, Transform, Load pipeline
  - extractors: NBA API integration
  - transformers: Data cleaning & enrichment
  - loaders: Database writing
- **analytics/**: Advanced metrics & ML models
- **api/**: REST API endpoints (future)
- **utils/**: Shared utilities

### `/streamlit` - Dashboard
- **app.py**: Main dashboard application
- **pages/**: Multi-page sections
- **components/**: Reusable UI components

### `/tests` - Testing
- **unit/**: Fast, isolated tests
- **integration/**: End-to-end workflow tests
- **fixtures/**: Test data samples

### `/docker` - Containerization
- Dockerfiles for each service
- Optimized for production deployment

### `/scripts` - Utilities
- Database setup scripts
- Data seeding scripts
- Helper bash scripts

## Key Files

### Configuration
- `setup.py`: Package installation & metadata
- `requirements.txt`: Python dependencies
- `pytest.ini`: Testing configuration
- `.gitignore`: Version control exclusions
- `.env.example`: Environment variable template

### Documentation
- `README.md`: Project overview
- `QUICK_START.md`: Fast setup guide
- `IMPLEMENTATION_GUIDE.md`: Deep dive
- `TROUBLESHOOTING.md`: Common issues
- `CV_PROJECT_SUMMARY.md`: Interview prep

### Automation
- `setup.sh`: One-command setup
- `docker-compose.yml`: Service orchestration
- `.github/workflows/ci.yml`: CI/CD pipeline

## Data Flow Through Structure

```
NBA API
   ↓
src/etl/extractors/  ← Extract data
   ↓
src/etl/transformers/  ← Clean & enrich
   ↓
src/etl/loaders/  ← Load to staging
   ↓
dbt/models/staging/  ← Standardize
   ↓
dbt/models/intermediate/  ← Transform
   ↓
dbt/models/marts/  ← Final tables
   ↓
streamlit/app.py  ← Visualize
src/analytics/models.py  ← Predict
```

## Orchestration Flow

```
airflow/dags/nba_daily_refresh.py
   ↓
1. Extract (src/etl/extractors/)
2. Transform (src/etl/transformers/)
3. Load (src/etl/loaders/)
4. dbt run (dbt/models/)
5. dbt test (dbt/tests/)
6. Data quality checks
```

## Total File Count

- **Python files**: 15+
- **SQL files**: 4+
- **YAML files**: 3+
- **Markdown files**: 10+
- **Dockerfiles**: 3
- **Shell scripts**: 1

## Next Steps to Complete

1. Add more dbt models in `dbt/models/`
2. Create Streamlit pages in `streamlit/pages/`
3. Add integration tests in `tests/integration/`
4. Create sample fixtures in `tests/fixtures/`
5. Add dbt macros in `dbt/macros/`
