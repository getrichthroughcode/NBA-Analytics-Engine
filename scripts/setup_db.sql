-- NBA Analytics Database Setup
-- ==============================
-- Creates the complete database schema including:
-- - Staging tables for raw data
-- - Dimension tables (star schema)
-- - Fact tables for analytics
-- - Materialized views for performance
-- - Indexes for query optimization

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text matching

-- Drop existing objects (for clean setup)
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS dwh CASCADE;
DROP SCHEMA IF EXISTS analytics CASCADE;

-- Create schemas
CREATE SCHEMA staging;
CREATE SCHEMA dwh;
CREATE SCHEMA analytics;

-- Set search path
SET search_path TO dwh, staging, analytics, public;

-- =====================
-- STAGING TABLES
-- =====================

-- Staging: Raw player game stats

CREATE TABLE staging.player_game_stats_raw (
    load_id UUID DEFAULT uuid_generate_v4(),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    game_id VARCHAR(20) NOT NULL,
    team_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    player_name VARCHAR(100),
    position VARCHAR(10),
    jersey_num VARCHAR(10),
    minutes_played NUMERIC(5,2),
    field_goals_made INTEGER,
    field_goals_attempted INTEGER,
    field_goal_pct NUMERIC(5,3),
    three_pointers_made INTEGER,
    three_pointers_attempted INTEGER,
    three_point_pct NUMERIC(5,3),
    free_throws_made INTEGER,
    free_throws_attempted INTEGER,
    free_throw_pct NUMERIC(5,3),
    offensive_rebounds INTEGER,
    defensive_rebounds INTEGER,
    total_rebounds INTEGER,
    assists INTEGER,
    steals INTEGER,
    blocks INTEGER,
    turnovers INTEGER,
    personal_fouls INTEGER,
    points INTEGER,
    plus_minus INTEGER,
    offensive_rating NUMERIC(6,1),
    defensive_rating NUMERIC(6,1),
    net_rating NUMERIC(6,1),
    true_shooting_pct NUMERIC(5,3),
    effective_fg_pct NUMERIC(5,3),
    usage_pct NUMERIC(5,3),
    pace NUMERIC(6,2),
    pie NUMERIC(5,3),
    assist_percentage NUMERIC(5,3),
    assist_to_turnover NUMERIC(5,2),
    assist_ratio NUMERIC(5,1),
    offensive_rebound_pct NUMERIC(5,3),
    defensive_rebound_pct NUMERIC(5,3),
    rebound_percentage NUMERIC(5,3),
    turnover_ratio NUMERIC(5,1),
    raw_data JSONB
);

-- Staging: Raw team game stats
CREATE TABLE staging.team_game_stats_raw (
    load_id UUID DEFAULT uuid_generate_v4(),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    game_id VARCHAR(20) NOT NULL,
    team_id INTEGER NOT NULL,
    team_name VARCHAR(100),
    game_date DATE,
    matchup VARCHAR(20),
    is_home BOOLEAN,
    win_loss VARCHAR(1),
    field_goals_made INTEGER,
    field_goals_attempted INTEGER,
    three_pointers_made INTEGER,
    three_pointers_attempted INTEGER,
    free_throws_made INTEGER,
    free_throws_attempted INTEGER,
    offensive_rebounds INTEGER,
    defensive_rebounds INTEGER,
    total_rebounds INTEGER,
    assists INTEGER,
    steals INTEGER,
    blocks INTEGER,
    turnovers INTEGER,
    personal_fouls INTEGER,
    points INTEGER,
    raw_data JSONB
);

-- =====================
-- DIMENSION TABLES
-- =====================

-- Dimension: Players (SCD Type 2)
CREATE TABLE dwh.dim_players (
    player_key SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    position VARCHAR(10),
    height_inches INTEGER,
    weight_lbs INTEGER,
    birth_date DATE,
    college VARCHAR(100),
    draft_year INTEGER,
    draft_round INTEGER,
    draft_number INTEGER,
    -- SCD Type 2 fields
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Teams (SCD Type 2)
CREATE TABLE dwh.dim_teams (
    team_key SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL,
    team_name VARCHAR(100) NOT NULL,
    team_abbreviation VARCHAR(3) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(50),
    conference VARCHAR(10),
    division VARCHAR(20),
    arena_name VARCHAR(100),
    -- SCD Type 2 fields
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Seasons
CREATE TABLE dwh.dim_seasons (
    season_key SERIAL PRIMARY KEY,
    season_id VARCHAR(10) NOT NULL UNIQUE,  -- e.g., '2024-25'
    season_type VARCHAR(20),  -- Regular Season, Playoffs, etc.
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_games INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Games
CREATE TABLE dwh.dim_games (
    game_key SERIAL PRIMARY KEY,
    game_id VARCHAR(20) NOT NULL UNIQUE,
    game_date DATE NOT NULL,
    season_key INTEGER REFERENCES dwh.dim_seasons(season_key),
    home_team_key INTEGER REFERENCES dwh.dim_teams(team_key),
    away_team_key INTEGER REFERENCES dwh.dim_teams(team_key),
    home_team_score INTEGER,
    away_team_score INTEGER,
    overtime_periods INTEGER DEFAULT 0,
    attendance INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Date (for time-based analysis)
CREATE TABLE dwh.dim_date (
    date_key INTEGER PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_of_week_name VARCHAR(20) NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT FALSE
);

-- =====================
-- FACT TABLES
-- =====================

-- Fact: Player Game Statistics
CREATE TABLE dwh.fact_player_game_stats (
    game_stats_key SERIAL PRIMARY KEY,
    player_key INTEGER NOT NULL REFERENCES dwh.dim_players(player_key),
    team_key INTEGER NOT NULL REFERENCES dwh.dim_teams(team_key),
    game_key INTEGER NOT NULL REFERENCES dwh.dim_games(game_key),
    season_key INTEGER NOT NULL REFERENCES dwh.dim_seasons(season_key),
    date_key INTEGER NOT NULL REFERENCES dwh.dim_date(date_key),

    -- Game context
    is_starter BOOLEAN,
    is_home BOOLEAN,
    won_game BOOLEAN,

    -- Basic stats
    minutes_played NUMERIC(5,1),
    points INTEGER,
    field_goals_made INTEGER,
    field_goals_attempted INTEGER,
    three_pointers_made INTEGER,
    three_pointers_attempted INTEGER,
    free_throws_made INTEGER,
    free_throws_attempted INTEGER,
    offensive_rebounds INTEGER,
    defensive_rebounds INTEGER,
    total_rebounds INTEGER,
    assists INTEGER,
    steals INTEGER,
    blocks INTEGER,
    turnovers INTEGER,
    personal_fouls INTEGER,
    plus_minus INTEGER,

    -- Shooting percentages
    field_goal_pct NUMERIC(5,3),
    three_point_pct NUMERIC(5,3),
    free_throw_pct NUMERIC(5,3),

    -- Advanced metrics
    true_shooting_pct NUMERIC(5,3),
    effective_fg_pct NUMERIC(5,3),
    usage_rate NUMERIC(5,1),
    offensive_rating NUMERIC(5,1),
    defensive_rating NUMERIC(5,1),
    per NUMERIC(5,1),
    box_plus_minus NUMERIC(5,1),
    offensive_win_shares NUMERIC(5,2),
    defensive_win_shares NUMERIC(5,2),
    total_win_shares NUMERIC(5,2),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE (player_key, game_key)
);

-- Fact: Team Game Statistics
CREATE TABLE dwh.fact_team_game_stats (
    team_game_key SERIAL PRIMARY KEY,
    team_key INTEGER NOT NULL REFERENCES dwh.dim_teams(team_key),
    game_key INTEGER NOT NULL REFERENCES dwh.dim_games(game_key),
    season_key INTEGER NOT NULL REFERENCES dwh.dim_seasons(season_key),
    date_key INTEGER NOT NULL REFERENCES dwh.dim_date(date_key),

    -- Game context
    is_home BOOLEAN,
    won_game BOOLEAN,
    opponent_team_key INTEGER REFERENCES dwh.dim_teams(team_key),

    -- Team stats
    points INTEGER,
    field_goals_made INTEGER,
    field_goals_attempted INTEGER,
    three_pointers_made INTEGER,
    three_pointers_attempted INTEGER,
    free_throws_made INTEGER,
    free_throws_attempted INTEGER,
    offensive_rebounds INTEGER,
    defensive_rebounds INTEGER,
    total_rebounds INTEGER,
    assists INTEGER,
    steals INTEGER,
    blocks INTEGER,
    turnovers INTEGER,
    personal_fouls INTEGER,

    -- Four Factors
    effective_fg_pct NUMERIC(5,3),
    turnover_pct NUMERIC(5,1),
    offensive_rebound_pct NUMERIC(5,1),
    free_throw_rate NUMERIC(5,3),

    -- Advanced metrics
    offensive_rating NUMERIC(5,1),
    defensive_rating NUMERIC(5,1),
    net_rating NUMERIC(5,1),
    pace NUMERIC(5,1),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE (team_key, game_key)
);

-- =====================
-- INDEXES
-- =====================

-- Staging indexes
--CREATE INDEX idx_staging_player_game_date ON staging.player_game_stats_raw(game_date);
CREATE INDEX idx_staging_player_load_ts ON staging.player_game_stats_raw(load_timestamp);

-- Dimension indexes
CREATE INDEX idx_dim_players_id ON dwh.dim_players(player_id);
CREATE INDEX idx_dim_players_name ON dwh.dim_players(player_name);
CREATE INDEX idx_dim_players_current ON dwh.dim_players(is_current) WHERE is_current = TRUE;

CREATE INDEX idx_dim_teams_id ON dwh.dim_teams(team_id);
CREATE INDEX idx_dim_teams_current ON dwh.dim_teams(is_current) WHERE is_current = TRUE;

CREATE INDEX idx_dim_games_date ON dwh.dim_games(game_date);
CREATE INDEX idx_dim_games_season ON dwh.dim_games(season_key);

-- Fact table indexes (critical for query performance)
CREATE INDEX idx_fact_player_stats_player ON dwh.fact_player_game_stats(player_key);
CREATE INDEX idx_fact_player_stats_team ON dwh.fact_player_game_stats(team_key);
CREATE INDEX idx_fact_player_stats_game ON dwh.fact_player_game_stats(game_key);
CREATE INDEX idx_fact_player_stats_season ON dwh.fact_player_game_stats(season_key);
CREATE INDEX idx_fact_player_stats_date ON dwh.fact_player_game_stats(date_key);

CREATE INDEX idx_fact_team_stats_team ON dwh.fact_team_game_stats(team_key);
CREATE INDEX idx_fact_team_stats_game ON dwh.fact_team_game_stats(game_key);
CREATE INDEX idx_fact_team_stats_season ON dwh.fact_team_game_stats(season_key);

-- =====================
-- MATERIALIZED VIEWS
-- =====================

-- Materialized View: Player Season Statistics
CREATE MATERIALIZED VIEW analytics.mv_player_season_stats AS
SELECT
    p.player_key,
    p.player_name,
    t.team_name,
    s.season_id,
    COUNT(*) as games_played,
    SUM(f.minutes_played) as total_minutes,
    ROUND(AVG(f.points), 1) as ppg,
    ROUND(AVG(f.total_rebounds), 1) as rpg,
    ROUND(AVG(f.assists), 1) as apg,
    ROUND(AVG(f.steals), 1) as spg,
    ROUND(AVG(f.blocks), 1) as bpg,
    ROUND(AVG(f.field_goal_pct), 3) as fg_pct,
    ROUND(AVG(f.three_point_pct), 3) as fg3_pct,
    ROUND(AVG(f.free_throw_pct), 3) as ft_pct,
    ROUND(AVG(f.true_shooting_pct), 3) as ts_pct,
    ROUND(AVG(f.per), 1) as avg_per,
    SUM(f.total_win_shares) as win_shares
FROM dwh.fact_player_game_stats f
JOIN dwh.dim_players p ON f.player_key = p.player_key
JOIN dwh.dim_teams t ON f.team_key = t.team_key
JOIN dwh.dim_seasons s ON f.season_key = s.season_key
WHERE p.is_current = TRUE
GROUP BY p.player_key, p.player_name, t.team_name, s.season_id;

CREATE UNIQUE INDEX idx_mv_player_season ON analytics.mv_player_season_stats(player_key, season_id);

-- Materialized View: League Leaders
CREATE MATERIALIZED VIEW analytics.mv_league_leaders AS
WITH ranked_stats AS (
    SELECT
        player_key,
        season_id,
        ppg,
        rpg,
        apg,
        ROW_NUMBER() OVER (PARTITION BY season_id ORDER BY ppg DESC) as ppg_rank,
        ROW_NUMBER() OVER (PARTITION BY season_id ORDER BY rpg DESC) as rpg_rank,
        ROW_NUMBER() OVER (PARTITION BY season_id ORDER BY apg DESC) as apg_rank
    FROM analytics.mv_player_season_stats
    WHERE games_played >= 20
)
SELECT * FROM ranked_stats
WHERE ppg_rank <= 50 OR rpg_rank <= 50 OR apg_rank <= 50;

-- =====================
-- COMMENTS
-- =====================

COMMENT ON SCHEMA staging IS 'Staging area for raw NBA API data';
COMMENT ON SCHEMA dwh IS 'Data warehouse layer with star schema';
COMMENT ON SCHEMA analytics IS 'Analytics layer with aggregated views';

COMMENT ON TABLE dwh.dim_players IS 'Player dimension with SCD Type 2 for tracking changes';
COMMENT ON TABLE dwh.fact_player_game_stats IS 'Grain: One row per player per game';

-- Grant permissions (adjust as needed)
GRANT USAGE ON SCHEMA staging, dwh, analytics TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA dwh, analytics TO PUBLIC;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA staging TO PUBLIC;
