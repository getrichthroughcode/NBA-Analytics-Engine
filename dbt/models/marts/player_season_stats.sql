{{
  config(
    materialized='table',
    schema='analytics'
  )
}}

/*
Player Season Statistics
========================
Aggregates from fact table with proper star schema joins.
*/

WITH player_season_agg AS (
    SELECT
        f.player_key,
        f.season_key,
        f.team_key,
        COUNT(*) as games_played,
        SUM(f.minutes_played) as total_minutes,
        SUM(f.points) as total_points,
        SUM(f.total_rebounds) as total_reb,
        SUM(f.assists) as total_ast,
        SUM(f.steals) as total_stl,
        SUM(f.blocks) as total_blk,
        SUM(f.turnovers) as total_tov,
        SUM(f.field_goals_made) as total_fgm,
        SUM(f.field_goals_attempted) as total_fga,
        SUM(f.three_pointers_made) as total_3pm,
        SUM(f.three_pointers_attempted) as total_3pa,
        SUM(f.free_throws_made) as total_ftm,
        SUM(f.free_throws_attempted) as total_fta
    FROM {{ ref('fact_player_game_stats') }} f
    GROUP BY f.player_key, f.season_key, f.team_key
)

SELECT
    agg.*,

    -- Per-game averages
    ROUND(agg.total_points::NUMERIC / NULLIF(agg.games_played, 0), 1) as ppg,
    ROUND(agg.total_reb::NUMERIC / NULLIF(agg.games_played, 0), 1) as rpg,
    ROUND(agg.total_ast::NUMERIC / NULLIF(agg.games_played, 0), 1) as apg,
    ROUND(agg.total_stl::NUMERIC / NULLIF(agg.games_played, 0), 1) as spg,
    ROUND(agg.total_blk::NUMERIC / NULLIF(agg.games_played, 0), 1) as bpg,
    ROUND(agg.total_minutes::NUMERIC / NULLIF(agg.games_played, 0), 1) as mpg,

    -- Shooting percentages
    ROUND(agg.total_fgm::NUMERIC / NULLIF(agg.total_fga, 0), 3) as fg_pct,
    ROUND(agg.total_3pm::NUMERIC / NULLIF(agg.total_3pa, 0), 3) as fg3_pct,
    ROUND(agg.total_ftm::NUMERIC / NULLIF(agg.total_fta, 0), 3) as ft_pct,

    -- Dimension attributes
    p.player_name,
    p.position,
    t.team_name,
    s.season_id,

    -- Metadata
    CURRENT_TIMESTAMP as dbt_updated_at

FROM player_season_agg agg
LEFT JOIN {{ ref('dim_players') }} p ON agg.player_key = p.player_key
LEFT JOIN {{ ref('dim_teams') }} t ON agg.team_key = t.team_key
LEFT JOIN {{ ref('dim_seasons') }} s ON agg.season_key = s.season_key
WHERE agg.games_played >= 1
