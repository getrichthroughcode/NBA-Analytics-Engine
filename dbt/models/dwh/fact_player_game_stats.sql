{{
  config(
    materialized='table',
    schema='dwh',
    unique_key=['game_stats_key']
  )
}}

/*
Fact: Player Game Statistics
=============================
Main fact table with player game-level statistics.
*/

SELECT
    ROW_NUMBER() OVER (ORDER BY s.game_id, s.player_id) as game_stats_key,

    -- Foreign keys to dimensions
    p.player_key,
    t.team_key,
    g.game_key,
    se.season_key,
    d.date_key,

    -- Context
    CASE WHEN s.minutes_played >= 20 THEN TRUE ELSE FALSE END as is_starter,
    NULL::BOOLEAN as is_home,
    NULL::BOOLEAN as won_game,

    -- Basic stats
    s.minutes_played,
    s.points,
    s.field_goals_made,
    s.field_goals_attempted,
    s.three_pointers_made,
    s.three_pointers_attempted,
    s.free_throws_made,
    s.free_throws_attempted,
    s.offensive_rebounds,
    s.defensive_rebounds,
    s.total_rebounds,
    s.assists,
    s.steals,
    s.blocks,
    s.turnovers,
    s.personal_fouls,
    s.plus_minus,

    -- Shooting percentages
    CASE
        WHEN s.field_goals_attempted > 0
        THEN ROUND(s.field_goals_made::NUMERIC / s.field_goals_attempted, 3)
        ELSE NULL
    END as field_goal_pct,

    CASE
        WHEN s.three_pointers_attempted > 0
        THEN ROUND(s.three_pointers_made::NUMERIC / s.three_pointers_attempted, 3)
        ELSE NULL
    END as three_point_pct,

    CASE
        WHEN s.free_throws_attempted > 0
        THEN ROUND(s.free_throws_made::NUMERIC / s.free_throws_attempted, 3)
        ELSE NULL
    END as free_throw_pct,

    -- Advanced metrics from API
    s.true_shooting_pct,
    s.effective_fg_pct,
    s.usage_pct,
    s.offensive_rating,
    s.defensive_rating,
    NULL::NUMERIC(5,1) as per,
    NULL::NUMERIC(5,1) as box_plus_minus,
    NULL::NUMERIC(5,2) as offensive_win_shares,
    NULL::NUMERIC(5,2) as defensive_win_shares,
    NULL::NUMERIC(5,2) as total_win_shares,

    -- Metadata
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at

FROM {{ ref('stg_player_game_stats') }} s
LEFT JOIN {{ ref('dim_players') }} p
    ON s.player_id = p.player_id AND p.is_current = TRUE
LEFT JOIN {{ ref('dim_teams') }} t
    ON s.team_id = t.team_id AND t.is_current = TRUE
LEFT JOIN {{ ref('dim_games') }} g
    ON s.game_id = g.game_id
LEFT JOIN {{ ref('stg_team_game_stats') }} tgs
    ON s.game_id = tgs.game_id AND s.team_id = tgs.team_id
LEFT JOIN {{ ref('dim_seasons') }} se
    ON tgs.game_date >= se.start_date AND tgs.game_date <= se.end_date
LEFT JOIN {{ ref('dim_date') }} d
    ON TO_CHAR(tgs.game_date, 'YYYYMMDD')::INTEGER = d.date_key
