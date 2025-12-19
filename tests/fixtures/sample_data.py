"""
Test fixtures - sample data for unit tests
Provides realistic NBA stat data for testing.
"""


def get_sample_raw_player_stat():
    """
    Sample raw player stat from NBA API (before transformation).
    
    This represents what comes directly from the NBA API.
    Uses the actual field names from the API.
    
    Returns:
        Dictionary with raw API field names
    """
    return {
        "gameId": "0022400123",
        "teamId": 1610612752,
        "personId": 203507,
        "firstName": "Giannis",
        "familyName": "Antetokounmpo",
        "position": "F",
        "jerseyNum": "34",
        "minutes": "35:24",
        "points": 30,
        "fieldGoalsMade": 12,
        "fieldGoalsAttempted": 20,
        "fieldGoalsPercentage": 0.600,
        "threePointersMade": 2,
        "threePointersAttempted": 5,
        "threePointersPercentage": 0.400,
        "freeThrowsMade": 4,
        "freeThrowsAttempted": 6,
        "freeThrowsPercentage": 0.667,
        "reboundsOffensive": 3,
        "reboundsDefensive": 9,
        "reboundsTotal": 12,
        "assists": 8,
        "steals": 2,
        "blocks": 1,
        "turnovers": 3,
        "foulsPersonal": 2,
        "plusMinusPoints": 15,
        "offensiveRating": 118.5,
        "defensiveRating": 105.2,
        "netRating": 13.3,
        "trueShootingPercentage": 0.625,
        "effectiveFieldGoalPercentage": 0.650,
        "usagePercentage": 0.285,
        "pace": 98.5,
        "PIE": 0.215
    }


def get_sample_transformed_player_stat():
    """
    Sample transformed player stat (after transformation).
    
    This represents data after going through NBATransformer.
    Uses your database schema field names.
    Includes all metrics already calculated by the API.
    
    Returns:
        Dictionary with transformed field names matching your schema
    """
    return {
        "game_id": "0022400123",
        "team_id": 1610612752,
        "player_id": 203507,
        "player_name": "Giannis Antetokounmpo",
        "position": "F",
        "jersey_num": "34",
        "minutes_played": 35.4,
        "field_goals_made": 12,
        "field_goals_attempted": 20,
        "field_goal_pct": 0.600,
        "three_pointers_made": 2,
        "three_pointers_attempted": 5,
        "three_point_pct": 0.400,
        "free_throws_made": 4,
        "free_throws_attempted": 6,
        "free_throw_pct": 0.667,
        "offensive_rebounds": 3,
        "defensive_rebounds": 9,
        "total_rebounds": 12,
        "assists": 8,
        "steals": 2,
        "blocks": 1,
        "turnovers": 3,
        "personal_fouls": 2,
        "points": 30,
        "plus_minus": 15,
        "offensive_rating": 118.5,
        "defensive_rating": 105.2,
        "net_rating": 13.3,
        "true_shooting_pct": 0.625,
        "effective_fg_pct": 0.650,
        "usage_pct": 0.285,
        "pace": 98.5,
        "pie": 0.215,
        "assist_percentage": None,
        "assist_to_turnover": 2.67,
        "assist_ratio": None,
        "offensive_rebound_pct": None,
        "defensive_rebound_pct": None,
        "rebound_percentage": None,
        "turnover_ratio": None,
        "raw_data": "{}"
    }


def get_sample_transformed_stat_without_ts():
    """
    Sample transformed stat with missing true_shooting_pct and effective_fg_pct.
    
    This simulates cases where the NBA API doesn't provide these metrics,
    forcing your code to calculate them.
    
    Used to test that calculate_advanced_metrics() properly calculates
    missing metrics.
    
    Returns:
        Dictionary with None values for calculated metrics
    """
    stat = get_sample_transformed_player_stat()
    stat["true_shooting_pct"] = None
    stat["effective_fg_pct"] = None
    return stat


def get_sample_minimal_stat():
    """
    Minimal player stat with only required fields.
    
    Used to test that your code handles missing optional fields.
    
    Returns:
        Dictionary with minimal required fields
    """
    return {
        "game_id": "0022400123",
        "team_id": 1610612752,
        "player_id": 203507,
        "player_name": "Test Player",
        "points": 10,
        "field_goals_made": 4,
        "field_goals_attempted": 10,
        "three_pointers_made": 1,
        "free_throws_made": 1,
        "free_throws_attempted": 1,
        "true_shooting_pct": None,
        "effective_fg_pct": None,
    }


def get_sample_zero_stats():
    """
    Player stat with all zeros (DNP - Did Not Play scenario).
    
    Used to test edge cases where player didn't play.
    
    Returns:
        Dictionary with zero values
    """
    return {
        "game_id": "0022400123",
        "team_id": 1610612752,
        "player_id": 203507,
        "player_name": "Bench Player",
        "minutes_played": 0.0,
        "points": 0,
        "field_goals_made": 0,
        "field_goals_attempted": 0,
        "three_pointers_made": 0,
        "three_pointers_attempted": 0,
        "free_throws_made": 0,
        "free_throws_attempted": 0,
        "offensive_rebounds": 0,
        "defensive_rebounds": 0,
        "total_rebounds": 0,
        "assists": 0,
        "steals": 0,
        "blocks": 0,
        "turnovers": 0,
        "personal_fouls": 0,
        "plus_minus": 0,
        "true_shooting_pct": None,
        "effective_fg_pct": None,
    }


def get_sample_game_data():
    """
    Sample game data from NBA API.
    
    Used to test game-level extractors and transformers.
    
    Returns:
        Dictionary with game information
    """
    return {
        "GAME_ID": "0022400123",
        "GAME_DATE": "2024-12-15",
        "HOME_TEAM_ID": 1610612752,
        "VISITOR_TEAM_ID": 1610612738,
        "SEASON": "2024-25",
        "HOME_TEAM_SCORE": 115,
        "VISITOR_TEAM_SCORE": 108
    }


def get_sample_team_stats():
    """
    Sample team-level stats.
    
    Used to test calculations that require team context
    (like usage rate, team ratings, etc.).
    
    Returns:
        Dictionary with team statistics
    """
    return {
        "team_id": 1610612752,
        "game_id": "0022400123",
        "team_fga": 85,
        "team_fta": 24,
        "team_tov": 12,
        "team_min": 240.0,
        "team_oreb": 10,
        "team_dreb": 35,
        "team_points": 115,
        "team_ast": 25
    }
