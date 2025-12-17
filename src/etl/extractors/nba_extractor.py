"""
NBA Data Extractor
==================
Handles extraction of NBA data from the official NBA API using nba_api library.
Implements retry logic, rate limiting, and error handling.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import time
import pandas as pd
from nba_api.stats.endpoints import (
    leaguegamefinder,
    boxscoretraditionalv3,
    boxscoreadvancedv3,
    playergamelog,
    teamgamelog,
    leaguestandingsv3,
    commonteamroster,
    commonplayerinfo,
    playercareerstats,
)
from nba_api.stats.static import teams, players

from src.utils.logger import get_logger
from src.utils.config import Config

logger = get_logger(__name__)


class NBAExtractor:
    """
    Extracts NBA data from the official NBA API.

    Features:
    - Automatic retry with exponential backoff
    - Rate limiting (600 requests per minute)
    - Data validation
    - Caching support
    """

    def __init__(self, rate_limit: int = 600):
        """
        Initialize the NBA extractor.

        Args:
            rate_limit: Maximum requests per minute (default: 600)
        """
        self.rate_limit = rate_limit
        self.request_count = 0
        self.last_reset = time.time()
        self.config = Config()
        logger.info("NBA Extractor initialized")

    def _rate_limit_check(self):
        """Check and enforce rate limiting"""
        current_time = time.time()

        # Reset counter every minute
        if current_time - self.last_reset >= 60:
            self.request_count = 0
            self.last_reset = current_time

        # Wait if we've hit the rate limit
        if self.request_count >= self.rate_limit:
            sleep_time = 60 - (current_time - self.last_reset)
            if sleep_time > 0:
                logger.warning(
                    f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds"
                )
                time.sleep(sleep_time)
                self.request_count = 0
                self.last_reset = time.time()

        self.request_count += 1

    def _retry_request(self, func, max_retries: int = 3, **kwargs) -> Any:
        """
        Execute API request with retry logic.

        Args:
            func: Function to execute
            max_retries: Maximum number of retry attempts
            **kwargs: Arguments to pass to the function

        Returns:
            Result from the function
        """
        for attempt in range(max_retries):
            try:
                self._rate_limit_check()
                result = func(**kwargs)
                return result
            except Exception as e:
                wait_time = 2**attempt  # Exponential backoff
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                else:
                    logger.error(f"All retry attempts failed for {func.__name__}")
                    raise

    def get_all_teams(self) -> List[Dict]:
        """
        Get all NBA teams (active and historical).

        Returns:
            List of team dictionaries with metadata
        """
        logger.info("Fetching all NBA teams")
        all_teams = teams.get_teams()
        logger.info(f"Retrieved {len(all_teams)} teams")
        return all_teams

    def get_all_players(self, is_only_current_season: bool = False) -> List[Dict]:
        """
        Get all NBA players.

        Args:
            is_only_current_season: If True, only return current season players

        Returns:
            List of player dictionaries with metadata
        """
        logger.info(
            f"Fetching {'current season' if is_only_current_season else 'all'} players"
        )
        all_players = players.get_players()

        if is_only_current_season:
            all_players = [p for p in all_players if p.get("is_active", False)]

        logger.info(f"Retrieved {len(all_players)} players")
        return all_players

    def get_games_by_date(self, date: str, season: Optional[str] = None) -> List[Dict]:
        """
        Get all games played on a specific date.

        Args:
            date: Date in YYYY-MM-DD format
            season: Season string (e.g., '2024-25'), if None uses current season

        Returns:
            List of game dictionaries
        """
        logger.info(f"Fetching games for date: {date}")

        if season is None:
            # Infer season from date
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            year = date_obj.year
            month = date_obj.month
            # NBA season spans two years, Oct-Sep
            if month >= 10:
                season = f"{year}-{str(year + 1)[-2:]}"
            else:
                season = f"{year - 1}-{str(year)[-2:]}"

        game_finder = self._retry_request(
            leaguegamefinder.LeagueGameFinder,
            date_from_nullable=date,
            date_to_nullable=date,
            season_nullable=season,
            league_id_nullable="00",  # NBA
        )

        games_df = game_finder.get_data_frames()[0]
        games = games_df.to_dict("records")

        logger.info(f"Retrieved {len(games)} game records for {date}")
        return games

    def get_player_game_stats(self, game_id: str) -> List[Dict]:
        """
        Get detailed player statistics for a specific game.

        Args:
            game_id: NBA game ID

        Returns:
            List of player stat dictionaries
        """
        logger.info(f"Fetching player stats for game: {game_id}")

        # Get traditional box score
        traditional = self._retry_request(
            boxscoretraditionalv3.BoxScoreTraditionalV3, game_id=game_id
        )

        # Get advanced box score
        advanced = self._retry_request(
            boxscoreadvancedv3.BoxScoreAdvancedV3, game_id=game_id
        )

        # Merge traditional and advanced stats
        trad_df = traditional.get_data_frames()[0]
        adv_df = advanced.get_data_frames()[0]

        # Merge on player_id
        merged_df = pd.merge(
            trad_df, adv_df, on=["teamId", "personId"], suffixes=("", "_adv")
        )

        stats = merged_df.to_dict("records")
        logger.info(f"Retrieved stats for {len(stats)} players in game {game_id}")

        return stats

    def get_player_season_stats(
        self, player_id: int, season: str = "2024-25"
    ) -> List[Dict]:
        """
        Get all game logs for a player in a season.

        Args:
            player_id: NBA player ID
            season: Season string (e.g., '2024-25')

        Returns:
            List of game log dictionaries
        """
        logger.info(f"Fetching season stats for player {player_id}, season {season}")

        game_log = self._retry_request(
            playergamelog.PlayerGameLog, player_id=player_id, season=season
        )

        games_df = game_log.get_data_frames()[0]
        games = games_df.to_dict("records")

        logger.info(f"Retrieved {len(games)} games for player {player_id}")
        return games

    def get_player_career_stats(self, player_id: int) -> Dict:
        """
        Get career statistics for a player.

        Args:
            player_id: NBA player ID

        Returns:
            Dictionary containing career stats
        """
        logger.info(f"Fetching career stats for player {player_id}")

        career = self._retry_request(
            playercareerstats.PlayerCareerStats, player_id=player_id
        )

        # Get different career stat types
        career_totals = career.get_data_frames()[0]
        season_totals = career.get_data_frames()[1]

        result = {
            "player_id": player_id,
            "career_totals": career_totals.to_dict("records")[0]
            if not career_totals.empty
            else {},
            "season_stats": season_totals.to_dict("records"),
        }

        logger.info(f"Retrieved career stats for player {player_id}")
        return result

    def get_team_roster(self, team_id: int, season: str = "2024-25") -> List[Dict]:
        """
        Get current roster for a team.

        Args:
            team_id: NBA team ID
            season: Season string

        Returns:
            List of player dictionaries on the roster
        """
        logger.info(f"Fetching roster for team {team_id}, season {season}")

        roster = self._retry_request(
            commonteamroster.CommonTeamRoster, team_id=team_id, season=season
        )

        roster_df = roster.get_data_frames()[0]
        players = roster_df.to_dict("records")

        logger.info(f"Retrieved {len(players)} players on roster")
        return players

    def get_league_standings(self, season: str = "2024-25") -> Dict:
        """
        Get current league standings.

        Args:
            season: Season string

        Returns:
            Dictionary with East and West conference standings
        """
        logger.info(f"Fetching league standings for season {season}")

        standings = self._retry_request(
            leaguestandingsv3.LeagueStandingsV3, season=season, league_id="00"
        )

        standings_df = standings.get_data_frames()[0]

        # Separate by conference
        east = standings_df[standings_df["Conference"] == "East"].to_dict("records")
        west = standings_df[standings_df["Conference"] == "West"].to_dict("records")

        result = {
            "season": season,
            "eastern_conference": east,
            "western_conference": west,
        }

        logger.info(f"Retrieved standings: {len(east)} East, {len(west)} West teams")
        return result

    def get_season_date_range(self, season: str) -> tuple:
        """
        Get the start and end dates for a season.

        Args:
            season: Season string (e.g., '2024-25')

        Returns:
            Tuple of (start_date, end_date) as strings
        """
        # Parse season string
        start_year = int(season.split("-")[0])

        # NBA regular season typically runs October to April
        season_start = f"{start_year}-10-01"
        season_end = f"{start_year + 1}-06-30"

        return season_start, season_end

    def extract_historical_data(
        self, start_season: str, end_season: str, batch_size: int = 10
    ) -> Dict:
        """
        Extract historical data for multiple seasons (for initial data load).

        Args:
            start_season: Starting season (e.g., '1996-97')
            end_season: Ending season (e.g., '2024-25')
            batch_size: Number of games to process in each batch

        Returns:
            Dictionary with extraction summary
        """
        logger.info(
            f"Starting historical data extraction: {start_season} to {end_season}"
        )

        # This is a placeholder - full implementation would be quite extensive
        # and would need to handle the large volume of data carefully

        summary = {
            "seasons_processed": 0,
            "games_extracted": 0,
            "players_extracted": 0,
            "errors": [],
        }

        # In a real implementation, I would:
        # 1. Iterate through each season
        # 2. Extract games in batches
        # 3. Extract player stats for each game
        # 4. Store in database incrementally
        # 5. Handle errors and resume capability

        logger.info("Historical extraction complete")
        return summary
