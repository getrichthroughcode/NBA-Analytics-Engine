"""
PostgreSQL Data Loader
======================
Loads transformed data into PostgreSQL database.
"""

from datetime import datetime
from typing import Dict, List

import pandas as pd

from src.utils.database import DatabaseConnection
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PostgresLoader:
    """
    Loads data into PostgreSQL database.

    Features:
    - Batch inserts
    - Error handling
    - Transaction management
    """

    def __init__(self):
        self.db = DatabaseConnection()
        logger.info("PostgreSQL Loader initialized")

    def load_games_staging(self, games: List[Dict]) -> int:
        """
        Load games into staging table.

        Args:
            games: List of game dictionaries

        Returns:
            Number of rows loaded
        """
        if not games:
            logger.warning("No games to load")
            return 0

        logger.info(f"Loading {len(games)} games to staging")

        try:
            df = pd.DataFrame(games)
            df["load_timestamp"] = datetime.now()

            rows_loaded = self.db.insert_dataframe(
                df=df,
                table_name="team_game_stats_raw",
                schema="staging",
                if_exists="append",
            )

            logger.info(f"Successfully loaded {rows_loaded} games")
            return rows_loaded

        except Exception as e:
            logger.error(f"Failed to load games: {str(e)}")
            raise

    def load_player_stats_staging(self, stats: List[Dict]) -> int:
        """
        Load player statistics into staging table.

        Args:
            stats: List of player stat dictionaries

        Returns:
            Number of rows loaded
        """
        if not stats:
            logger.warning("No player stats to load")
            return 0

        logger.info(f"Loading {len(stats)} player stats to staging")

        try:
            df = pd.DataFrame(stats)
            df["load_timestamp"] = datetime.now()

            rows_loaded = self.db.insert_dataframe(
                df=df,
                table_name="player_game_stats_raw",
                schema="staging",
                if_exists="append",
            )

            logger.info(f"Successfully loaded {rows_loaded} player stats")
            return rows_loaded

        except Exception as e:
            logger.error(f"Failed to load player stats: {str(e)}")
            raise

    def load_to_dimension(self, data: List[Dict], table_name: str, schema: str = "dwh") -> int:
        """
        Load data into dimension table with SCD Type 2 logic.

        Args:
            data: List of dimension records
            table_name: Target dimension table
            schema: Database schema

        Returns:
            Number of rows loaded
        """
        if not data:
            logger.warning(f"No data to load to {table_name}")
            return 0

        logger.info(f"Loading {len(data)} records to {schema}.{table_name}")

        try:
            df = pd.DataFrame(data)

            # Add SCD Type 2 fields if not present
            if "effective_date" not in df.columns:
                df["effective_date"] = datetime.now().date()
            if "is_current" not in df.columns:
                df["is_current"] = True

            rows_loaded = self.db.insert_dataframe(
                df=df, table_name=table_name, schema=schema, if_exists="append"
            )

            logger.info(f"Successfully loaded {rows_loaded} dimension records")
            return rows_loaded

        except Exception as e:
            logger.error(f"Failed to load dimension data: {str(e)}")
            raise

    def load_to_fact(self, data: List[Dict], table_name: str, schema: str = "dwh") -> int:
        """
        Load data into fact table.

        Args:
            data: List of fact records
            table_name: Target fact table
            schema: Database schema

        Returns:
            Number of rows loaded
        """
        if not data:
            logger.warning(f"No data to load to {table_name}")
            return 0

        logger.info(f"Loading {len(data)} records to {schema}.{table_name}")

        try:
            df = pd.DataFrame(data)

            # Add metadata
            df["created_at"] = datetime.now()
            df["updated_at"] = datetime.now()

            rows_loaded = self.db.insert_dataframe(
                df=df, table_name=table_name, schema=schema, if_exists="append"
            )

            logger.info(f"Successfully loaded {rows_loaded} fact records")
            return rows_loaded

        except Exception as e:
            logger.error(f"Failed to load fact data: {str(e)}")
            raise

    def truncate_staging(self, table_name: str) -> None:
        """
        Truncate staging table.

        Args:
            table_name: Staging table to truncate
        """
        logger.info(f"Truncating staging.{table_name}")

        try:
            self.db.execute_sql(f"TRUNCATE TABLE staging.{table_name}")
            logger.info(f"Successfully truncated staging.{table_name}")
        except Exception as e:
            logger.error(f"Failed to truncate table: {str(e)}")
            raise
