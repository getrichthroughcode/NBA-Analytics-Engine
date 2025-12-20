"""
Advanced NBA Metrics Calculator
================================
Calculates advanced basketball statistics including:
- PER (Player Efficiency Rating)
- Win Shares (Offensive, Defensive, Total)
- True Shooting Percentage
- Usage Rate
- Box Plus/Minus (BPM)
- And more...

Formulas based on Basketball-Reference.com methodology.
"""

from typing import Dict, List

from ..utils.logger import get_logger

logger = get_logger(__name__)


class AdvancedMetricsCalculator:
    """
    Calculates advanced NBA metrics for players and teams.

    All calculations follow Basketball-Reference.com formulas where applicable.
    """

    # League average constants (updated annually)
    LEAGUE_PACE = 99.0  # Possessions per 48 minutes
    LEAGUE_PPG = 110.0  # Points per game

    def __init__(self):
        logger.info("Advanced Metrics Calculator initialized")

    @staticmethod
    def calculate_true_shooting_pct(points: int, fga: int, fta: int) -> float:
        """
        Calculate True Shooting Percentage.

        TS% = PTS / (2 * (FGA + 0.44 * FTA))

        Args:
            points: Total points scored
            fga: Field goals attempted
            fta: Free throws attempted

        Returns:
            True shooting percentage (0-1)
        """
        if fga + fta == 0:
            return 0.0

        ts_pct = points / (2 * (fga + 0.44 * fta))
        return round(ts_pct, 3)

    @staticmethod
    def calculate_effective_fg_pct(fgm: int, fg3m: int, fga: int) -> float:
        """
        Calculate Effective Field Goal Percentage.

        eFG% = (FGM + 0.5 * 3PM) / FGA

        Args:
            fgm: Field goals made
            fg3m: Three-pointers made
            fga: Field goals attempted

        Returns:
            Effective FG percentage (0-1)
        """
        if fga == 0:
            return 0.0

        efg_pct = (fgm + 0.5 * fg3m) / fga
        return round(efg_pct, 3)

    @staticmethod
    def calculate_usage_rate(
        fga: int,
        fta: int,
        tov: int,
        min_played: float,
        team_min: float,
        team_fga: int,
        team_fta: int,
        team_tov: int,
    ) -> float:
        """
        Calculate Usage Rate (percentage of team plays used by player).

        USG% = 100 * ((FGA + 0.44 * FTA + TOV) * (Tm MP / 5)) /
               (MP * (Tm FGA + 0.44 * Tm FTA + Tm TOV))

        Args:
            fga: Player field goals attempted
            fta: Player free throws attempted
            tov: Player turnovers
            min_played: Player minutes played
            team_min: Team total minutes
            team_fga: Team field goals attempted
            team_fta: Team free throws attempted
            team_tov: Team turnovers

        Returns:
            Usage rate as percentage
        """
        if min_played == 0 or team_min == 0:
            return 0.0

        player_poss = fga + 0.44 * fta + tov
        team_poss = team_fga + 0.44 * team_fta + team_tov

        if team_poss == 0:
            return 0.0

        usg_rate = 100 * ((player_poss * (team_min / 5)) / (min_played * team_poss))
        return round(usg_rate, 1)

    @staticmethod
    def calculate_per(
        min_played: float,
        fg3m: int,
        ast: int,
        fgm: int,
        ftm: int,
        oreb: int,
        dreb: int,
        stl: int,
        blk: int,
        fga: int,
        fta: int,
        tov: int,
        pf: int,
        team_pace: float = LEAGUE_PACE,
        league_pace: float = LEAGUE_PACE,
    ) -> float:
        """
        Calculate Player Efficiency Rating (PER).

        Simplified formula (full formula is very complex).

        Args:
            min_played: Minutes played
            fg3m: Three-pointers made
            ast: Assists
            fgm: Field goals made
            ftm: Free throws made
            oreb: Offensive rebounds
            dreb: Defensive rebounds
            stl: Steals
            blk: Blocks
            fga: Field goals attempted
            fta: Free throws attempted
            tov: Turnovers
            pf: Personal fouls
            team_pace: Team pace factor
            league_pace: League average pace

        Returns:
            Player Efficiency Rating
        """
        if min_played == 0:
            return 0.0

        # Simplified PER calculation (actual formula has many more factors)
        factor = (2 / 3) - (0.5 * (league_pace / team_pace)) / (2 * (league_pace / team_pace))
        VOP = 1.0  # Value of possession (simplified)
        DRB_perc = 0.75  # Defensive rebound percentage (simplified)

        uPER = (1 / min_played) * (
            fg3m
            + (2 / 3) * ast
            + (2 - factor * (team_pace / league_pace)) * fgm
            + (ftm * 0.5 * (1 + (1 - (ast / (2 * fgm))) + (2 / 3) * (ast / (2 * fgm))))
            + VOP * oreb
            + VOP * dreb * (1 - DRB_perc)
            + VOP * stl
            + VOP * blk
            + VOP * ast
            - VOP * (fga - fgm)
            - VOP * 0.44 * (fta - ftm)
            - VOP * tov
            - pf
        )

        # Scale to league average of 15
        per = uPER * (15 / league_pace)

        return round(per, 1)

    @staticmethod
    def calculate_offensive_rating(points: int, possessions: int) -> float:
        """
        Calculate Offensive Rating (points produced per 100 possessions).

        Simplified version - full calculation requires team-level context.

        Args:
            points: Points scored
            possessions: Number of possessions

        Returns:
            Offensive rating (points per 100 possessions)
        """
        if possessions == 0:
            return 0.0

        ortg = 100 * (points / possessions)
        return round(ortg, 1)

    @staticmethod
    def calculate_defensive_rating(
        dreb: int,
        stl: int,
        blk: int,
        pf: int,
        min_played: float,
        team_min: float,
        team_dreb: int,
        team_stl: int,
        team_blk: int,
        opp_points: int,
        opp_possessions: int,
    ) -> float:
        """
        Calculate Defensive Rating (points allowed per 100 possessions).

        Args:
            dreb: Defensive rebounds
            stl: Steals
            blk: Blocks
            pf: Personal fouls
            min_played: Minutes played
            team_min: Team minutes
            team_dreb: Team defensive rebounds
            team_stl: Team steals
            team_blk: Team blocks
            opp_points: Opponent points
            opp_possessions: Opponent possessions

        Returns:
            Defensive rating
        """
        if min_played == 0 or team_min == 0:
            return 0.0

        # Simplified defensive rating
        team_drtg = 100 * (opp_points / opp_possessions) if opp_possessions > 0 else 100

        # Defensive impact (simplified)
        ((team_dreb + team_stl + team_blk) / team_min) * min_played
        player_def = (dreb + stl + blk) / min_played if min_played > 0 else 0
        team_def = (team_dreb + team_stl + team_blk) / team_min if team_min > 0 else 0

        # Adjust team DRTG based on player contribution
        if team_def > 0:
            drtg = team_drtg * (1 - (player_def - team_def) / team_def * 0.1)
        else:
            drtg = team_drtg

        return round(drtg, 1)

    @staticmethod
    def calculate_win_shares(
        points: int,
        fgm: int,
        fga: int,
        ftm: int,
        fta: int,
        oreb: int,
        dreb: int,
        ast: int,
        stl: int,
        blk: int,
        tov: int,
        min_played: float,
        team_wins: int,
        team_games: int,
    ) -> Dict[str, float]:
        """
        Calculate Win Shares (offensive, defensive, and total).

        Args:
            points: Points scored
            fgm: Field goals made
            fga: Field goals attempted
            ftm: Free throws made
            fta: Free throws attempted
            oreb: Offensive rebounds
            dreb: Defensive rebounds
            ast: Assists
            stl: Steals
            blk: Blocks
            tov: Turnovers
            min_played: Minutes played
            team_wins: Team wins
            team_games: Team games played

        Returns:
            Dictionary with offensive_ws, defensive_ws, and total_ws
        """
        # Simplified Win Shares calculation
        # Real formula is extremely complex

        # Offensive Win Shares (simplified)
        marginal_offense = points - 0.92 * (fga - fgm) - 0.44 * (fta - ftm)
        marginal_points_per_win = 30.0  # League average (simplified)
        ows = marginal_offense / marginal_points_per_win

        # Defensive Win Shares (simplified)
        defensive_contribution = dreb + stl + blk - (tov * 0.5)
        dws = defensive_contribution / marginal_points_per_win * 0.7

        # Total Win Shares
        ws = ows + dws

        return {
            "offensive_ws": round(ows, 1),
            "defensive_ws": round(dws, 1),
            "total_ws": round(ws, 1),
        }

    @staticmethod
    def calculate_box_plus_minus(
        points: int,
        reb: int,
        ast: int,
        stl: int,
        blk: int,
        tov: int,
        fga: int,
        fgm: int,
        fta: int,
        min_played: float,
    ) -> float:
        """
        Calculate Box Plus/Minus (BPM).

        Simplified version of the stat.

        Args:
            points: Points
            reb: Total rebounds
            ast: Assists
            stl: Steals
            blk: Blocks
            tov: Turnovers
            fga: Field goals attempted
            fgm: Field goals made
            fta: Free throws attempted
            min_played: Minutes played

        Returns:
            Box Plus/Minus value
        """
        if min_played == 0:
            return 0.0

        # Simplified BPM (actual formula is very complex with many coefficients)
        raw_bpm = (
            0.123 * points
            + 0.101 * reb
            + 0.215 * ast
            + 0.422 * stl
            + 0.631 * blk
            - 0.176 * (fga - fgm)
            - 0.146 * (fta - (points - 2 * fgm))
            - 0.162 * tov  # FTM approximation
        ) / (min_played / 48)

        # Adjust to league average of 0
        bpm = raw_bpm - 2.0

        return round(bpm, 1)


def calculate_advanced_metrics(player_stats: List[Dict]) -> List[Dict]:
    """
    Calculate all advanced metrics for a list of player game stats.

    Args:
        player_stats: List of TRANSFORMED player statistics dictionaries

    Returns:
        Enhanced list with advanced metrics added
    """
    logger.info(f"Calculating advanced metrics for {len(player_stats)} player records")

    calculator = AdvancedMetricsCalculator()
    enhanced_stats = []

    for stats in player_stats:
        # Extract base stats - USE TRANSFORMED FIELD NAMES
        points = stats.get("points", 0)
        fgm = stats.get("field_goals_made", 0)
        fga = stats.get("field_goals_attempted", 0)
        fg3m = stats.get("three_pointers_made", 0)
        stats.get("free_throws_made", 0)
        fta = stats.get("free_throws_attempted", 0)
        stats.get("offensive_rebounds", 0)
        stats.get("defensive_rebounds", 0)
        stats.get("total_rebounds", 0)
        stats.get("assists", 0)
        stats.get("steals", 0)
        stats.get("blocks", 0)
        stats.get("turnovers", 0)
        stats.get("personal_fouls", 0)
        stats.get("minutes_played", 0)

        # Calculate advanced metrics - USE SCHEMA FIELD NAMES
        # Only override if not already calculated by API
        if stats.get("true_shooting_pct") is None:
            stats["true_shooting_pct"] = calculator.calculate_true_shooting_pct(points, fga, fta)

        if stats.get("effective_fg_pct") is None:
            stats["effective_fg_pct"] = calculator.calculate_effective_fg_pct(fgm, fg3m, fga)

        # Note: PER, Usage, WS require team-level data
        # These would be calculated in a separate aggregation step

        enhanced_stats.append(stats)

    logger.info("Advanced metrics calculation complete")
    return enhanced_stats
