-- NBA Analytics Database Setup
-- ==============================
-- Creates schemas and staging tables only.
-- dbt will create DWH and Analytics layers.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas (empty, dbt will populate dwh and analytics)
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dwh;
CREATE SCHEMA IF NOT EXISTS analytics;

-- =====================
-- STAGING TABLES ONLY
-- =====================

-- Staging: Raw player game stats
CREATE TABLE IF NOT EXISTS staging.player_game_stats_raw (
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
CREATE TABLE IF NOT EXISTS staging.team_game_stats_raw (
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

-- Staging indexes
CREATE INDEX IF NOT EXISTS idx_staging_player_load_ts
    ON staging.player_game_stats_raw(load_timestamp);

CREATE INDEX IF NOT EXISTS idx_staging_player_game_id
    ON staging.player_game_stats_raw(game_id);

CREATE INDEX IF NOT EXISTS idx_staging_player_id
    ON staging.player_game_stats_raw(player_id);

-- Grant permissions
GRANT USAGE ON SCHEMA staging, dwh, analytics TO PUBLIC;
GRANT ALL ON ALL TABLES IN SCHEMA staging TO PUBLIC;
GRANT ALL ON SCHEMA dwh TO PUBLIC;
GRANT ALL ON SCHEMA analytics TO PUBLIC;

-- Comments
COMMENT ON SCHEMA staging IS 'Staging area for raw NBA API data';
COMMENT ON SCHEMA dwh IS 'Data warehouse layer (created by dbt)';
COMMENT ON SCHEMA analytics IS 'Analytics layer (created by dbt)';
