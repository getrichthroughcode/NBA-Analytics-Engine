{{
  config(
    materialized='table',
    schema='dwh',
    unique_key='player_key'
  )
}}

/*
Dimension: Players
==================
Creates player dimension from staging data.
Simplified version without full SCD Type 2 (for now).
*/

WITH unique_players AS (
    SELECT DISTINCT
        player_id,
        player_name,
        position
    FROM {{ ref('stg_player_game_stats') }}
    WHERE player_id IS NOT NULL
),

with_keys AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY player_id) as player_key,
        player_id,
        player_name,
        position,
        CURRENT_DATE as effective_date,
        NULL::DATE as expiration_date,
        TRUE as is_current,
        CURRENT_TIMESTAMP as created_at,
        CURRENT_TIMESTAMP as updated_at
    FROM unique_players
)

SELECT * FROM with_keys
