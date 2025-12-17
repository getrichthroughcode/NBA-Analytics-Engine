"""
NBA Data Transformer
====================
Transforms raw NBA API data into clean, validated format.
"""
import json
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


class NBATransformer:
    """
    Transforms raw NBA data into clean, standardized format.

    Features:
    - Data type validation
    - Null handling
    - Column standardization
    - Data cleaning
    """

    def __init__(self):
        logger.info("NBA Transformer initialized")

    def transform_games(self, games: List[Dict]) -> List[Dict]:
        """
        Transform raw game data.

        Args:
            games: List of raw game dictionaries

        Returns:
            List of transformed game dictionaries
        """
        logger.info(f"Transforming {len(games)} games")

        transformed = []
        for game in games:
            try:
                cleaned_game = {
                    "game_id": str(game.get("GAME_ID")),
                    "team_id": int(game.get("TEAM_ID", 0)),
                    "team_name": game.get("TEAM_NAME", ""),
                    "game_date": self._parse_date(game.get("GAME_DATE")),
                    "matchup": game.get("MATCHUP", ""),
                    "is_home": "@" not in game.get("MATCHUP", ""),
                    "win_loss": game.get("WL", "L"),
                    "field_goals_made": int(game.get("FGM", 0)),
                    "field_goals_attempted": int(game.get("FGA", 0)),
                    "three_pointers_made": int(game.get("FG3M", 0)),
                    "three_pointers_attempted": int(game.get("FG3A", 0)),
                    "free_throws_made": int(game.get("FTM", 0)),
                    "free_throws_attempted": int(game.get("FTA", 0)),
                    "offensive_rebounds": int(game.get("OREB", 0)),
                    "defensive_rebounds": int(game.get("DREB", 0)),
                    "total_rebounds": int(game.get("REB", 0)),
                    "assists": int(game.get("AST", 0)),
                    "steals": int(game.get("STL", 0)),
                    "blocks": int(game.get("BLK", 0)),
                    "turnovers": int(game.get("TOV", 0)),
                    "personal_fouls": int(game.get("PF", 0)),
                    "points": int(game.get("PTS", 0)),
                    "raw_data": json.dumps(game),  # Store original API response as JSONB
                }
                transformed.append(cleaned_game)
            except Exception as e:
                logger.warning(
                    f"Failed to transform game {game.get('GAME_ID')}: {str(e)}"
                )
                continue

        logger.info(f"Successfully transformed {len(transformed)} games")

        return transformed

    def transform_player_stats(self, stats: List[Dict]) -> List[Dict]:
        """
        Transform raw player statistics.

        Args:
            stats: List of raw player stat dictionaries

        Returns:
            List of transformed stat dictionaries
        """
        logger.info(f"Transforming {len(stats)} player stat records")

        transformed = []
        for stat in stats:
            try:
                # Parse minutes from "MM:SS" format to decimal
                minutes_str = stat.get("minutes", "0:00")
                minutes_played = self._parse_minutes(minutes_str)

                cleaned_stat = {
                    # Identifiers
                    "game_id": str(stat.get("gameId")),
                    "team_id": int(stat.get("teamId", 0)),
                    "player_id": int(stat.get("personId", 0)),
                    "player_name": f"{stat.get('firstName', '')} {stat.get('familyName', '')}".strip(),
                    # Player details
                    "position": stat.get("position", ""),
                    "jersey_num": stat.get("jerseyNum", ""),
                    # Playing time
                    "minutes_played": minutes_played,
                    # Shooting stats
                    "field_goals_made": int(stat.get("fieldGoalsMade", 0)),
                    "field_goals_attempted": int(stat.get("fieldGoalsAttempted", 0)),
                    "field_goal_pct": float(stat.get("fieldGoalsPercentage", 0.0)),
                    "three_pointers_made": int(stat.get("threePointersMade", 0)),
                    "three_pointers_attempted": int(
                        stat.get("threePointersAttempted", 0)
                    ),
                    "three_point_pct": float(stat.get("threePointersPercentage", 0.0)),
                    "free_throws_made": int(stat.get("freeThrowsMade", 0)),
                    "free_throws_attempted": int(stat.get("freeThrowsAttempted", 0)),
                    "free_throw_pct": float(stat.get("freeThrowsPercentage", 0.0)),
                    # Rebounds
                    "offensive_rebounds": int(stat.get("reboundsOffensive", 0)),
                    "defensive_rebounds": int(stat.get("reboundsDefensive", 0)),
                    "total_rebounds": int(stat.get("reboundsTotal", 0)),
                    # Other stats
                    "assists": int(stat.get("assists", 0)),
                    "steals": int(stat.get("steals", 0)),
                    "blocks": int(stat.get("blocks", 0)),
                    "turnovers": int(stat.get("turnovers", 0)),
                    "personal_fouls": int(stat.get("foulsPersonal", 0)),
                    "points": int(stat.get("points", 0)),
                    "plus_minus": int(stat.get("plusMinusPoints", 0))
                    if stat.get("plusMinusPoints")
                    else None,
                    # Advanced metrics
                    "offensive_rating": float(stat.get("offensiveRating", 0.0))
                    if stat.get("offensiveRating")
                    else None,
                    "defensive_rating": float(stat.get("defensiveRating", 0.0))
                    if stat.get("defensiveRating")
                    else None,
                    "net_rating": float(stat.get("netRating", 0.0))
                    if stat.get("netRating")
                    else None,
                    "true_shooting_pct": float(stat.get("trueShootingPercentage", 0.0))
                    if stat.get("trueShootingPercentage")
                    else None,
                    "effective_fg_pct": float(
                        stat.get("effectiveFieldGoalPercentage", 0.0)
                    )
                    if stat.get("effectiveFieldGoalPercentage")
                    else None,
                    "usage_pct": float(stat.get("usagePercentage", 0.0))
                    if stat.get("usagePercentage")
                    else None,
                    "pace": float(stat.get("pace", 0.0)) if stat.get("pace") else None,
                    "pie": float(stat.get("PIE", 0.0)) if stat.get("PIE") else None,
                    # Assist metrics
                    "assist_percentage": float(stat.get("assistPercentage", 0.0))
                    if stat.get("assistPercentage")
                    else None,
                    "assist_to_turnover": float(stat.get("assistToTurnover", 0.0))
                    if stat.get("assistToTurnover")
                    else None,
                    "assist_ratio": float(stat.get("assistRatio", 0.0))
                    if stat.get("assistRatio")
                    else None,
                    # Rebound metrics
                    "offensive_rebound_pct": float(
                        stat.get("offensiveReboundPercentage", 0.0)
                    )
                    if stat.get("offensiveReboundPercentage")
                    else None,
                    "defensive_rebound_pct": float(
                        stat.get("defensiveReboundPercentage", 0.0)
                    )
                    if stat.get("defensiveReboundPercentage")
                    else None,
                    "rebound_percentage": float(stat.get("reboundPercentage", 0.0))
                    if stat.get("reboundPercentage")
                    else None,
                    # Other advanced
                    "turnover_ratio": float(stat.get("turnoverRatio", 0.0))
                    if stat.get("turnoverRatio")
                    else None,
                    # Raw data
                    "raw_data": json.dumps(stat),
                }
                transformed.append(cleaned_stat)
            except Exception as e:
                logger.warning(
                    f"Failed to transform player stat for player {stat.get('personId')}: {str(e)}"
                )
                continue

        logger.info(f"Successfully transformed {len(transformed)} player stat records")
        return transformed

    def _parse_minutes(self, minutes_str: str) -> float:
        """
        Parse minutes from MM:SS format to decimal minutes.

        Args:
            minutes_str: Minutes in "MM:SS" format

        Returns:
            Decimal minutes
        """
        try:
            if not minutes_str or minutes_str == "":
                return 0.0

            parts = minutes_str.split(":")
            if len(parts) != 2:
                return 0.0

            minutes = int(parts[0])
            seconds = int(parts[1])

            return round(minutes + (seconds / 60.0), 2)
        except:
            return 0.0

    def _parse_date(self, date_str: str) -> str:
        """
        Parse date string to standardized format.

        Args:
            date_str: Date string in various formats

        Returns:
            Date in YYYY-MM-DD format
        """
        if not date_str:
            return None

        try:
            # Try common NBA API formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y%m%d"]:
                try:
                    dt = datetime.strptime(str(date_str), fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            logger.warning(f"Could not parse date: {date_str}")
            return None
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {str(e)}")
            return None

    def _parse_minutes(self, minutes_str: str) -> float:
        """
        Parse minutes string (MM:SS) to decimal minutes.

        Args:
            minutes_str: Minutes in MM:SS format

        Returns:
            Minutes as float
        """
        if not minutes_str or minutes_str == "0":
            return 0.0

        try:
            if ":" in str(minutes_str):
                parts = str(minutes_str).split(":")
                minutes = int(parts[0])
                seconds = int(parts[1])
                return round(minutes + seconds / 60.0, 1)
            else:
                return float(minutes_str)
        except Exception as e:
            logger.warning(f"Could not parse minutes: {minutes_str}")
            return 0.0

    def validate_data(self, data: List[Dict], required_fields: List[str]) -> bool:
        """
        Validate that data contains required fields.

        Args:
            data: List of data dictionaries
            required_fields: List of required field names

        Returns:
            True if valid, False otherwise
        """
        if not data:
            logger.warning("Empty data provided for validation")
            return False

        for idx, record in enumerate(data):
            missing_fields = [f for f in required_fields if f not in record]
            if missing_fields:
                logger.error(f"Record {idx} missing required fields: {missing_fields}")
                return False

        logger.info("Data validation passed")
        return True
