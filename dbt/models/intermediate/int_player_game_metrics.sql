{{
  config(
    materialized='view'
  )
}}

/*
Intermediate: Player Game Metrics
==================================
Calculates shooting percentages and other derived metrics.

Source: stg_player_game_stats
*/

WITH player_stats AS (
    SELECT * FROM {{ ref('stg_player_game_stats') }}
),

with_metrics AS (
    SELECT
        *,
        
        -- Shooting percentages
        CASE 
            WHEN field_goals_attempted > 0 
            THEN ROUND(field_goals_made::NUMERIC / field_goals_attempted, 3)
            ELSE NULL
        END as field_goal_pct,
        
        CASE 
            WHEN three_pointers_attempted > 0 
            THEN ROUND(three_pointers_made::NUMERIC / three_pointers_attempted, 3)
            ELSE NULL
        END as three_point_pct,
        
        CASE 
            WHEN free_throws_attempted > 0 
            THEN ROUND(free_throws_made::NUMERIC / free_throws_attempted, 3)
            ELSE NULL
        END as free_throw_pct,
        
        -- Starter flag (if played > 20 minutes, likely a starter)
        CASE WHEN minutes_played >= 20 THEN TRUE ELSE FALSE END as is_starter

    FROM player_stats
)

SELECT * FROM with_metrics
