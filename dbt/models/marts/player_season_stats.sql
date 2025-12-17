{{
  config(
    materialized='table',
    indexes=[
      {'columns': ['player_key']},
      {'columns': ['season_key']},
      {'columns': ['team_key']},
    ]
  )
}}

/*
Player Season Statistics - Mart Layer
======================================
Aggregates player statistics by season with advanced metrics.
This is the primary table for player season-level analysis.

Grain: One row per player per season per team
*/

WITH player_games AS (
    SELECT
        player_key,
        season_key,
        team_key,
        COUNT(*) as games_played,
        SUM(minutes_played) as total_minutes,
        
        -- Counting stats
        SUM(points) as total_points,
        SUM(field_goals_made) as total_fgm,
        SUM(field_goals_attempted) as total_fga,
        SUM(three_pointers_made) as total_3pm,
        SUM(three_pointers_attempted) as total_3pa,
        SUM(free_throws_made) as total_ftm,
        SUM(free_throws_attempted) as total_fta,
        SUM(offensive_rebounds) as total_oreb,
        SUM(defensive_rebounds) as total_dreb,
        SUM(total_rebounds) as total_reb,
        SUM(assists) as total_ast,
        SUM(steals) as total_stl,
        SUM(blocks) as total_blk,
        SUM(turnovers) as total_tov,
        SUM(personal_fouls) as total_pf,
        
        -- Advanced stats (already calculated per game)
        AVG(true_shooting_pct) as avg_ts_pct,
        AVG(effective_fg_pct) as avg_efg_pct,
        AVG(usage_rate) as avg_usage_rate,
        AVG(offensive_rating) as avg_ortg,
        AVG(defensive_rating) as avg_drtg,
        AVG(per) as avg_per,
        AVG(box_plus_minus) as avg_bpm,
        
        -- Win shares (sum over season)
        SUM(offensive_win_shares) as total_ows,
        SUM(defensive_win_shares) as total_dws,
        SUM(total_win_shares) as total_ws

    FROM {{ ref('stg_player_game_stats') }}
    WHERE is_starter IS NOT NULL  -- Exclude invalid records
    GROUP BY player_key, season_key, team_key
),

season_averages AS (
    SELECT
        player_key,
        season_key,
        team_key,
        games_played,
        total_minutes,
        
        -- Per-game averages
        ROUND(total_points::NUMERIC / NULLIF(games_played, 0), 1) as ppg,
        ROUND(total_reb::NUMERIC / NULLIF(games_played, 0), 1) as rpg,
        ROUND(total_ast::NUMERIC / NULLIF(games_played, 0), 1) as apg,
        ROUND(total_stl::NUMERIC / NULLIF(games_played, 0), 1) as spg,
        ROUND(total_blk::NUMERIC / NULLIF(games_played, 0), 1) as bpg,
        ROUND(total_tov::NUMERIC / NULLIF(games_played, 0), 1) as tpg,
        ROUND(total_minutes::NUMERIC / NULLIF(games_played, 0), 1) as mpg,
        
        -- Shooting percentages
        ROUND(
            total_fgm::NUMERIC / NULLIF(total_fga, 0), 
            3
        ) as fg_pct,
        ROUND(
            total_3pm::NUMERIC / NULLIF(total_3pa, 0), 
            3
        ) as fg3_pct,
        ROUND(
            total_ftm::NUMERIC / NULLIF(total_fta, 0), 
            3
        ) as ft_pct,
        
        -- Advanced metrics
        ROUND(avg_ts_pct, 3) as ts_pct,
        ROUND(avg_efg_pct, 3) as efg_pct,
        ROUND(avg_usage_rate, 1) as usage_rate,
        ROUND(avg_ortg, 1) as offensive_rating,
        ROUND(avg_drtg, 1) as defensive_rating,
        ROUND(avg_per, 1) as per,
        ROUND(avg_bpm, 1) as box_plus_minus,
        
        -- Win shares
        ROUND(total_ows, 1) as offensive_win_shares,
        ROUND(total_dws, 1) as defensive_win_shares,
        ROUND(total_ws, 1) as win_shares,
        
        -- Per 36 minutes stats
        ROUND(
            (total_points::NUMERIC * 36) / NULLIF(total_minutes, 0), 
            1
        ) as pts_per_36,
        ROUND(
            (total_reb::NUMERIC * 36) / NULLIF(total_minutes, 0), 
            1
        ) as reb_per_36,
        ROUND(
            (total_ast::NUMERIC * 36) / NULLIF(total_minutes, 0), 
            1
        ) as ast_per_36,
        
        -- Totals for reference
        total_points,
        total_fgm,
        total_fga,
        total_3pm,
        total_3pa,
        total_ftm,
        total_fta,
        total_oreb,
        total_dreb,
        total_reb,
        total_ast,
        total_stl,
        total_blk,
        total_tov,
        total_pf

    FROM player_games
)

SELECT
    sa.*,
    p.player_name,
    p.position,
    p.height_inches,
    p.weight_lbs,
    p.birth_date,
    p.college,
    t.team_name,
    t.team_abbreviation,
    t.conference,
    t.division,
    s.season_id,
    s.season_type,
    
    -- Calculate age at season start
    EXTRACT(YEAR FROM s.start_date) - EXTRACT(YEAR FROM p.birth_date) as age_at_season_start,
    
    -- Meta fields
    CURRENT_TIMESTAMP as dbt_updated_at

FROM season_averages sa
LEFT JOIN {{ ref('dim_players') }} p ON sa.player_key = p.player_key
LEFT JOIN {{ ref('dim_teams') }} t ON sa.team_key = t.team_key
LEFT JOIN {{ ref('dim_seasons') }} s ON sa.season_key = s.season_key

-- Data quality filters
WHERE sa.games_played >= 1  -- At least 1 game played
