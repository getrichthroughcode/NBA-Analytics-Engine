{{
  config(
    materialized='table',
    schema='dwh',
    unique_key=['team_key', 'game_key']
  )
}}

/*
Fact: Team Game Statistics
===========================
Team performance by game.
*/

SELECT
    ROW_NUMBER() OVER (ORDER BY s.game_id, s.team_id) as team_game_key,

    -- Foreign keys
    t.team_key,
    g.game_key,
    se.season_key,
    d.date_key,

    -- Context
    s.is_home,
    CASE WHEN s.win_loss = 'W' THEN TRUE ELSE FALSE END as won_game,
    NULL::INTEGER as opponent_team_key,  -- TODO: Join to get opponent

    -- Stats (already calculated in staging!)
    s.points,
    s.field_goals_made,
    s.field_goals_attempted,
    s.three_pointers_made,
    s.three_pointers_attempted,
    s.free_throws_made,
    s.free_throws_attempted,
    s.offensive_rebounds,
    s.defensive_rebounds,
    s.total_rebounds,
    s.assists,
    s.steals,
    s.blocks,
    s.turnovers,
    s.personal_fouls,

    -- Percentages
    CASE
        WHEN s.field_goals_attempted > 0
        THEN ROUND(s.field_goals_made::NUMERIC / s.field_goals_attempted, 3)
        ELSE NULL
    END as effective_fg_pct,

    -- Metadata
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at

FROM {{ ref('stg_team_game_stats') }} s
LEFT JOIN {{ ref('dim_teams') }} t
    ON s.team_id = t.team_id AND t.is_current = TRUE
LEFT JOIN {{ ref('dim_games') }} g
    ON s.game_id = g.game_id
LEFT JOIN {{ ref('dim_seasons') }} se
    ON s.game_date >= se.start_date AND s.game_date <= se.end_date
LEFT JOIN {{ ref('dim_date') }} d
    ON TO_CHAR(s.game_date, 'YYYYMMDD')::INTEGER = d.date_key
