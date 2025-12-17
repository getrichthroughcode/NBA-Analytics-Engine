"""
NBA Daily Refresh DAG
=====================
Daily orchestration of NBA data pipeline:
1. Extract previous day's games and player stats
2. Load into staging tables
3. Run dbt transformations
4. Update materialized views
5. Run data quality checks
6. Refresh ML model predictions

Schedule: Daily at 2 AM EST (after games conclude)
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago

import sys
import os

sys.path.insert(0, os.path.abspath("/opt/airflow"))

from src.etl.extractors.nba_extractor import NBAExtractor
from src.etl.transformers.nba_transformer import NBATransformer
from src.etl.loaders.postgres_loader import PostgresLoader
from src.analytics.metrics import calculate_advanced_metrics
from src.utils.data_quality import run_data_quality_checks
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Default arguments
default_args = {
    "owner": "nba-analytics",
    "depends_on_past": False,
    "start_date": datetime(2024, 10, 1),
    "email": ["abdoulaye.diallo.eng@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=2),
}

# Initialize DAG
dag = DAG(
    "nba_daily_refresh",
    default_args=default_args,
    description="Daily NBA data pipeline - extract, transform, load, and analyze",
    schedule_interval="0 2 * * *",  # 2 AM EST daily
    catchup=False,
    max_active_runs=1,
    tags=["nba", "daily", "production"],
)


def extract_yesterday_games(**context):
    """Extract all games and player stats from yesterday"""
    logger.info("Starting daily extraction for yesterday's games")

    execution_date = context["execution_date"]
    target_date = (execution_date - timedelta(days=1)).strftime("%Y-%m-%d")

    extractor = NBAExtractor()

    # Extract game data
    games = extractor.get_games_by_date(target_date)
    logger.info(f"Extracted {len(games)} games for {target_date}")

    # Extract player stats for each game
    all_player_stats = []
    for game in games:
        game_id = game["GAME_ID"]
        player_stats = extractor.get_player_game_stats(game_id)
        all_player_stats.extend(player_stats)

    logger.info(f"Extracted stats for {len(all_player_stats)} player-game records")

    # Push data to XCom for next task
    context["task_instance"].xcom_push(key="games", value=games)
    context["task_instance"].xcom_push(key="player_stats", value=all_player_stats)

    return {
        "date": target_date,
        "games_count": len(games),
        "player_stats_count": len(all_player_stats),
    }


def transform_data(**context):
    """Transform raw data into clean, validated format"""
    logger.info("Starting data transformation")

    # Pull data from XCom
    ti = context["task_instance"]
    games = ti.xcom_pull(key="games", task_ids="extract_yesterday_games")
    player_stats = ti.xcom_pull(key="player_stats", task_ids="extract_yesterday_games")

    transformer = NBATransformer()

    # Transform games
    transformed_games = transformer.transform_games(games)

    # Transform player stats
    transformed_player_stats = transformer.transform_player_stats(player_stats)

    # Calculate advanced metrics
    enhanced_player_stats = calculate_advanced_metrics(transformed_player_stats)

    logger.info(
        f"Transformed {len(transformed_games)} games and {len(enhanced_player_stats)} player records"
    )

    # Push transformed data to XCom
    ti.xcom_push(key="transformed_games", value=transformed_games)
    ti.xcom_push(key="transformed_player_stats", value=enhanced_player_stats)

    return {
        "transformed_games": len(transformed_games),
        "transformed_player_stats": len(enhanced_player_stats),
    }


def load_to_staging(**context):
    """Load transformed data into PostgreSQL staging tables"""
    logger.info("Starting data load to staging tables")

    # Pull transformed data from XCom
    ti = context["task_instance"]
    games = ti.xcom_pull(key="transformed_games", task_ids="transform_data")
    player_stats = ti.xcom_pull(
        key="transformed_player_stats", task_ids="transform_data"
    )

    loader = PostgresLoader()

    # Load games
    games_loaded = loader.load_games_staging(games)
    logger.info(f"Loaded {games_loaded} games to staging")

    # Load player stats
    stats_loaded = loader.load_player_stats_staging(player_stats)
    logger.info(f"Loaded {stats_loaded} player stats to staging")

    return {"games_loaded": games_loaded, "stats_loaded": stats_loaded}


def validate_data_quality(**context):
    """Run comprehensive data quality checks"""
    logger.info("Running data quality validation")

    results = run_data_quality_checks()

    # Check for critical failures
    if results.get("critical_failures", 0) > 0:
        raise ValueError(
            f"Data quality check failed: {results['critical_failures']} critical issues found"
        )

    logger.info(
        f"Data quality check passed: {results['checks_passed']}/{results['total_checks']} checks passed"
    )

    return results


# Define tasks
extract_task = PythonOperator(
    task_id="extract_yesterday_games",
    python_callable=extract_yesterday_games,
    provide_context=True,
    dag=dag,
)

transform_task = PythonOperator(
    task_id="transform_data",
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

load_task = PythonOperator(
    task_id="load_to_staging",
    python_callable=load_to_staging,
    provide_context=True,
    dag=dag,
)

# dbt run - transform staging to marts
dbt_run_task = BashOperator(
    task_id="dbt_run",
    bash_command="cd /dbt && dbt run --profiles-dir /root/.dbt",
    dag=dag,
)

# dbt test - validate data
dbt_test_task = BashOperator(
    task_id="dbt_test",
    bash_command="cd /dbt && dbt test --profiles-dir /root/.dbt",
    dag=dag,
)

# Data quality validation
quality_check_task = PythonOperator(
    task_id="validate_data_quality",
    python_callable=validate_data_quality,
    provide_context=True,
    dag=dag,
)

# Refresh materialized views
refresh_views_task = PostgresOperator(
    task_id="refresh_materialized_views",
    postgres_conn_id="nba_postgres",
    sql="""
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_player_season_stats;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_team_season_stats;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_player_career_stats;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_league_leaders;
    """,
    dag=dag,
)

# Update statistics for query optimization
update_stats_task = PostgresOperator(
    task_id="update_table_statistics",
    postgres_conn_id="nba_postgres",
    sql="""
        ANALYZE fact_player_game_stats;
        ANALYZE fact_team_game_stats;
        ANALYZE dim_players;
        ANALYZE dim_teams;
    """,
    dag=dag,
)

# Define task dependencies
extract_task >> transform_task >> load_task >> dbt_run_task >> dbt_test_task
dbt_test_task >> quality_check_task >> refresh_views_task >> update_stats_task
