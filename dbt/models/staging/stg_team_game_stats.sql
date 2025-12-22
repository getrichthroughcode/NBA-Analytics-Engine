{{
  config(
    materialized='view'
  )
}}

/*
Staging: Team Game Stats
=========================
Cleans and standardizes raw team game statistics.
*/

WITH source AS (
    SELECT * FROM {{ source('staging', 'team_game_stats_raw') }}
),

cleaned AS (
    SELECT
        -- IDs
        game_id,
        team_id,
        team_name,

        -- Game info
        game_date,
        matchup,
        is_home,
        win_loss,

        -- Stats
        COALESCE(field_goals_made, 0) as field_goals_made,
        COALESCE(field_goals_attempted, 0) as field_goals_attempted,
        COALESCE(three_pointers_made, 0) as three_pointers_made,
        COALESCE(three_pointers_attempted, 0) as three_pointers_attempted,
        COALESCE(free_throws_made, 0) as free_throws_made,
        COALESCE(free_throws_attempted, 0) as free_throws_attempted,
        COALESCE(offensive_rebounds, 0) as offensive_rebounds,
        COALESCE(defensive_rebounds, 0) as defensive_rebounds,
        COALESCE(total_rebounds, 0) as total_rebounds,
        COALESCE(assists, 0) as assists,
        COALESCE(steals, 0) as steals,
        COALESCE(blocks, 0) as blocks,
        COALESCE(turnovers, 0) as turnovers,
        COALESCE(personal_fouls, 0) as personal_fouls,
        COALESCE(points, 0) as points,

        -- Metadata
        load_timestamp

    FROM source
    WHERE team_id IS NOT NULL
      AND game_id IS NOT NULL
)

SELECT * FROM cleaned
