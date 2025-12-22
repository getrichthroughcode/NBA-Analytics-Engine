{{
  config(
    materialized='table',
    schema='dwh',
    unique_key='game_key'
  )
}}

/*
Dimension: Games
================
Creates game dimension from team game stats.
*/

WITH game_info AS (
    SELECT DISTINCT
        game_id,
        game_date,
        MAX(CASE WHEN is_home = TRUE THEN team_id END) as home_team_id,
        MAX(CASE WHEN is_home = FALSE THEN team_id END) as away_team_id,
        MAX(CASE WHEN is_home = TRUE THEN points END) as home_team_score,
        MAX(CASE WHEN is_home = FALSE THEN points END) as away_team_score
    FROM {{ ref('stg_team_game_stats') }}
    GROUP BY game_id, game_date
),

with_keys AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY g.game_id) as game_key,
        g.game_id,
        g.game_date,
        ht.team_key as home_team_key,
        at.team_key as away_team_key,
        g.home_team_score,
        g.away_team_score,
        0 as overtime_periods,  -- TODO: Calculate from game data
        NULL::INTEGER as attendance,
        CURRENT_TIMESTAMP as created_at
    FROM game_info g
    LEFT JOIN {{ ref('dim_teams') }} ht
        ON g.home_team_id = ht.team_id AND ht.is_current = TRUE
    LEFT JOIN {{ ref('dim_teams') }} at
        ON g.away_team_id = at.team_id AND at.is_current = TRUE
)

SELECT * FROM with_keys
