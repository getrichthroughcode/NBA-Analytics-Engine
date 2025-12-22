{{
  config(
    materialized='table',
    schema='dwh',
    unique_key='team_key'
  )
}}

/*
Dimension: Teams
================
Creates team dimension from staging data.
*/

WITH unique_teams AS (
    SELECT DISTINCT
        team_id,
        team_name
    FROM {{ ref('stg_team_game_stats') }}
    WHERE team_id IS NOT NULL
),

with_keys AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY team_id) as team_key,
        team_id,
        team_name,
        LEFT(team_name, 3) as team_abbreviation,  -- Simplified
        CURRENT_DATE as effective_date,
        NULL::DATE as expiration_date,
        TRUE as is_current,
        CURRENT_TIMESTAMP as created_at,
        CURRENT_TIMESTAMP as updated_at
    FROM unique_teams
)

SELECT * FROM with_keys
