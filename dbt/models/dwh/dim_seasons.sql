{{
  config(
    materialized='table',
    schema='dwh',
    unique_key='season_key'
  )
}}

/*
Dimension: Seasons
==================
Creates season dimension based on game dates.
Infers season from date (Oct-April = one season).
*/

WITH game_dates AS (
    SELECT DISTINCT
        game_date,
        EXTRACT(YEAR FROM game_date) as year,
        EXTRACT(MONTH FROM game_date) as month
    FROM {{ ref('stg_team_game_stats') }}
),

seasons AS (
    SELECT DISTINCT
        CASE
            WHEN month >= 10 THEN year || '-' || (year + 1)::TEXT
            ELSE (year - 1)::TEXT || '-' || year::TEXT
        END as season_id,
        CASE
            WHEN month >= 10 THEN (year || '-10-01')::DATE
            ELSE ((year - 1)::TEXT || '-10-01')::DATE
        END as start_date,
        CASE
            WHEN month >= 10 THEN ((year + 1)::TEXT || '-06-30')::DATE
            ELSE (year || '-06-30')::DATE
        END as end_date
    FROM game_dates
),

with_keys AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY season_id) as season_key,
        season_id,
        'Regular Season' as season_type,
        start_date,
        end_date,
        NULL::INTEGER as total_games,
        CURRENT_TIMESTAMP as created_at
    FROM seasons
)

SELECT * FROM with_keys
