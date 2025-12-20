{{
  config(
    materialized='view'
  )
}}

/*
Staging: Player Game Stats
===========================
Cleans and standardizes raw player game statistics from the staging table.

Source: staging.player_game_stats_raw
Grain: One row per player per game
*/

WITH source AS (
    SELECT * FROM {{ source('staging', 'player_game_stats_raw') }}
),

cleaned AS (
    SELECT
        -- IDs
        game_id,
        team_id,
        player_id,
        player_name,

        -- Game info
        game_date,
        matchup,
        is_home,
        CASE
            WHEN win_loss = 'W' THEN TRUE
            WHEN win_loss = 'L' THEN FALSE
            ELSE NULL
        END as won_game,

        -- Playing time
        COALESCE(minutes_played, 0) as minutes_played,

        -- Scoring
        COALESCE(points, 0) as points,
        COALESCE(field_goals_made, 0) as field_goals_made,
        COALESCE(field_goals_attempted, 0) as field_goals_attempted,
        COALESCE(three_pointers_made, 0) as three_pointers_made,
        COALESCE(three_pointers_attempted, 0) as three_pointers_attempted,
        COALESCE(free_throws_made, 0) as free_throws_made,
        COALESCE(free_throws_attempted, 0) as free_throws_attempted,

        -- Rebounds
        COALESCE(offensive_rebounds, 0) as offensive_rebounds,
        COALESCE(defensive_rebounds, 0) as defensive_rebounds,
        COALESCE(total_rebounds, 0) as total_rebounds,

        -- Other stats
        COALESCE(assists, 0) as assists,
        COALESCE(steals, 0) as steals,
        COALESCE(blocks, 0) as blocks,
        COALESCE(turnovers, 0) as turnovers,
        COALESCE(personal_fouls, 0) as personal_fouls,
        COALESCE(plus_minus, 0) as plus_minus,

        -- Metadata
        load_timestamp

    FROM source
    WHERE player_id IS NOT NULL
      AND game_id IS NOT NULL
)

SELECT * FROM cleaned
