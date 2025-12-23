{{
  config(
    materialized='materialized_view',
    schema='analytics'
  )
}}

SELECT * FROM {{ ref('player_season_stats') }}
