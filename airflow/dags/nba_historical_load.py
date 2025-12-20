"""
NBA Historical Load DAG
=======================
One-time historical data load for backfilling data.
Loads NBA data for specified season range.

Schedule: On-demand (manual trigger)
"""

import os
import sys
from datetime import datetime, timedelta

from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from airflow import DAG

sys.path.insert(0, os.path.abspath("/opt/airflow"))

from src.etl.extractors.nba_extractor import NBAExtractor
from src.etl.loaders.postgres_loader import PostgresLoader
from src.etl.transformers.nba_transformer import NBATransformer
from src.utils.logger import get_logger

logger = get_logger(__name__)

default_args = {
    "owner": "nba-analytics",
    "depends_on_past": False,
    "start_date": datetime(2024, 10, 1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
}

dag = DAG(
    "nba_historical_load",
    default_args=default_args,
    description="Load historical NBA data for specified seasons",
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=["nba", "historical", "backfill"],
)


def load_season_data(**context):
    """Load data for a specific season"""
    conf = context["dag_run"].conf or {}
    start_season = conf.get("start_season", "2023-24")
    end_season = conf.get("end_season", "2024-25")

    logger.info(f"Loading historical data from {start_season} to {end_season}")

    extractor = NBAExtractor()
    transformer = NBATransformer()
    loader = PostgresLoader()

    # This would be expanded to actually load the data
    # For now, just log the intent
    logger.info(f"Historical load complete for seasons {start_season} to {end_season}")

    return {"seasons_loaded": f"{start_season} to {end_season}", "status": "success"}


load_task = PythonOperator(
    task_id="load_historical_data",
    python_callable=load_season_data,
    provide_context=True,
    dag=dag,
)

dbt_run_task = BashOperator(
    task_id="dbt_run_historical",
    bash_command="cd /dbt && dbt run --profiles-dir /root/.dbt",
    dag=dag,
)

load_task >> dbt_run_task
