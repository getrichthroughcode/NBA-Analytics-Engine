{{
  config(
    materialized='table',
    schema='dwh',
    unique_key='date_key'
  )
}}

/*
Dimension: Date
===============
Date dimension for time-based analysis.
*/

WITH game_dates AS (
    SELECT DISTINCT game_date as date
    FROM {{ ref('stg_team_game_stats') }}
    WHERE game_date IS NOT NULL
),

date_details AS (
    SELECT
        TO_CHAR(date, 'YYYYMMDD')::INTEGER as date_key,
        date,
        EXTRACT(YEAR FROM date)::INTEGER as year,
        EXTRACT(QUARTER FROM date)::INTEGER as quarter,
        EXTRACT(MONTH FROM date)::INTEGER as month,
        TO_CHAR(date, 'Month') as month_name,
        EXTRACT(WEEK FROM date)::INTEGER as week,
        EXTRACT(DOW FROM date)::INTEGER as day_of_week,
        TO_CHAR(date, 'Day') as day_of_week_name,
        EXTRACT(DAY FROM date)::INTEGER as day_of_month,
        EXTRACT(DOY FROM date)::INTEGER as day_of_year,
        CASE WHEN EXTRACT(DOW FROM date) IN (0, 6) THEN TRUE ELSE FALSE END as is_weekend,
        FALSE as is_holiday
    FROM game_dates
)

SELECT * FROM date_details
