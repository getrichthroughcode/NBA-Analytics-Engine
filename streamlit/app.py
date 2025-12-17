"""
NBA Analytics Dashboard
=======================
Interactive dashboard for NBA analytics and insights.

Features:
- Player statistics and comparisons
- Team performance tracking
- League leaders and standings
- Advanced metrics visualization
- Game predictions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.database import DatabaseConnection
from src.analytics.metrics import AdvancedMetricsCalculator

# Page configuration
st.set_page_config(
    page_title="NBA Analytics Engine",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    h1 {
        color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db_connection():
    """Get database connection (cached)"""
    return DatabaseConnection()


@st.cache_data(ttl=3600)
def load_league_leaders(stat: str, season: str = '2024-25', limit: int = 10):
    """Load league leaders for a specific stat"""
    db = get_db_connection()
    
    query = f"""
    SELECT 
        p.player_name,
        t.team_abbreviation,
        pss.{stat},
        pss.games_played,
        pss.mpg
    FROM player_season_stats pss
    JOIN dim_players p ON pss.player_key = p.player_key
    JOIN dim_teams t ON pss.team_key = t.team_key
    WHERE pss.season_id = %s
        AND pss.games_played >= 20  -- Minimum games qualifier
    ORDER BY pss.{stat} DESC
    LIMIT %s
    """
    
    df = db.execute_query(query, (season, limit))
    return df


@st.cache_data(ttl=3600)
def load_player_career_stats(player_name: str):
    """Load career statistics for a player"""
    db = get_db_connection()
    
    query = """
    SELECT 
        s.season_id,
        t.team_abbreviation,
        pss.games_played,
        pss.ppg,
        pss.rpg,
        pss.apg,
        pss.fg_pct,
        pss.fg3_pct,
        pss.ft_pct,
        pss.ts_pct,
        pss.per,
        pss.win_shares,
        pss.usage_rate
    FROM player_season_stats pss
    JOIN dim_players p ON pss.player_key = p.player_key
    JOIN dim_teams t ON pss.team_key = t.team_key
    JOIN dim_seasons s ON pss.season_key = s.season_key
    WHERE p.player_name = %s
    ORDER BY s.season_id DESC
    """
    
    df = db.execute_query(query, (player_name,))
    return df


@st.cache_data(ttl=3600)
def load_team_standings(season: str = '2024-25'):
    """Load current standings"""
    db = get_db_connection()
    
    query = """
    SELECT 
        t.team_name,
        t.conference,
        t.division,
        tss.wins,
        tss.losses,
        ROUND(tss.wins::NUMERIC / (tss.wins + tss.losses), 3) as win_pct,
        tss.offensive_rating,
        tss.defensive_rating,
        tss.net_rating
    FROM team_season_stats tss
    JOIN dim_teams t ON tss.team_key = t.team_key
    WHERE tss.season_id = %s
    ORDER BY t.conference, win_pct DESC
    """
    
    df = db.execute_query(query, (season,))
    return df


def main():
    """Main dashboard application"""
    
    # Sidebar
    st.sidebar.title("🏀 NBA Analytics")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Home", "League Leaders", "Player Comparison", "Team Analytics", "Game Predictions"]
    )
    
    # Season selector
    current_season = "2024-25"
    season = st.sidebar.selectbox(
        "Select Season",
        ["2024-25", "2023-24", "2022-23", "2021-22", "2020-21"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "This dashboard provides comprehensive NBA analytics "
        "including advanced metrics, player comparisons, and predictions."
    )
    
    # Main content
    if page == "Home":
        show_home_page(season)
    elif page == "League Leaders":
        show_league_leaders_page(season)
    elif page == "Player Comparison":
        show_player_comparison_page(season)
    elif page == "Team Analytics":
        show_team_analytics_page(season)
    elif page == "Game Predictions":
        show_predictions_page(season)


def show_home_page(season: str):
    """Display home page with overview"""
    
    st.title("NBA Analytics Engine")
    st.markdown(f"### Season {season} Overview")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Games", "1,230", "+15")
    with col2:
        st.metric("Total Players", "530", "+23")
    with col3:
        st.metric("Avg PPG", "110.5", "+2.3")
    with col4:
        st.metric("Avg Pace", "99.2", "+1.1")
    
    st.markdown("---")
    
    # League standings
    st.subheader("Current Standings")
    
    standings = load_team_standings(season)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Eastern Conference")
        east = standings[standings['conference'] == 'East'].head(8)
        st.dataframe(
            east[['team_name', 'wins', 'losses', 'win_pct', 'net_rating']],
            hide_index=True,
            use_container_width=True
        )
    
    with col2:
        st.markdown("##### Western Conference")
        west = standings[standings['conference'] == 'West'].head(8)
        st.dataframe(
            west[['team_name', 'wins', 'losses', 'win_pct', 'net_rating']],
            hide_index=True,
            use_container_width=True
        )


def show_league_leaders_page(season: str):
    """Display league leaders"""
    
    st.title("League Leaders")
    st.markdown(f"### Season {season}")
    
    # Stat selector
    stat_category = st.selectbox(
        "Select Stat Category",
        ["Points", "Rebounds", "Assists", "Steals", "Blocks", "PER", "Win Shares"]
    )
    
    # Map display names to database columns
    stat_mapping = {
        "Points": "ppg",
        "Rebounds": "rpg",
        "Assists": "apg",
        "Steals": "spg",
        "Blocks": "bpg",
        "PER": "per",
        "Win Shares": "win_shares"
    }
    
    stat_col = stat_mapping[stat_category]
    
    # Load and display leaders
    leaders = load_league_leaders(stat_col, season, limit=15)
    
    if not leaders.empty:
        # Create visualization
        fig = px.bar(
            leaders.head(10),
            x='player_name',
            y=stat_col,
            color=stat_col,
            color_continuous_scale='Blues',
            title=f'Top 10 Players - {stat_category}',
            labels={'player_name': 'Player', stat_col: stat_category}
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.markdown("### Full Leaderboard")
        st.dataframe(
            leaders,
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("No data available for the selected season.")


def show_player_comparison_page(season: str):
    """Display player comparison tool"""
    
    st.title("Player Comparison")
    st.markdown("### Compare up to 3 players")
    
    # Player selection
    col1, col2, col3 = st.columns(3)
    
    # In a real implementation, you would load player names from the database
    players = ["LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo"]
    
    with col1:
        player1 = st.selectbox("Player 1", players, index=0)
    with col2:
        player2 = st.selectbox("Player 2", players, index=1)
    with col3:
        player3 = st.selectbox("Player 3", players, index=2)
    
    # Load player stats
    if st.button("Compare Players"):
        st.markdown("---")
        
        # Display comparison metrics
        st.subheader("Season Averages Comparison")
        
        # Create comparison dataframe (mock data for now)
        comparison_data = {
            'Stat': ['PPG', 'RPG', 'APG', 'FG%', 'PER', 'Win Shares'],
            player1: [27.1, 7.5, 7.3, 0.506, 25.7, 8.5],
            player2: [29.4, 5.1, 6.2, 0.459, 24.1, 7.2],
            player3: [28.6, 6.7, 5.0, 0.537, 28.3, 9.8]
        }
        
        df = pd.DataFrame(comparison_data)
        
        # Display as table
        st.dataframe(df, hide_index=True, use_container_width=True)
        
        # Radar chart
        fig = go.Figure()
        
        for player in [player1, player2, player3]:
            fig.add_trace(go.Scatterpolar(
                r=df[player].tolist(),
                theta=df['Stat'].tolist(),
                fill='toself',
                name=player
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=True,
            title="Player Comparison Radar"
        )
        
        st.plotly_chart(fig, use_container_width=True)


def show_team_analytics_page(season: str):
    """Display team analytics"""
    
    st.title("Team Analytics")
    st.markdown(f"### Season {season}")
    
    # Team selector
    teams = ["Los Angeles Lakers", "Golden State Warriors", "Boston Celtics"]
    selected_team = st.selectbox("Select Team", teams)
    
    st.markdown("---")
    
    # Team metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Record", "42-18", "+3 wins")
    with col2:
        st.metric("Off Rating", "118.5", "+2.3")
    with col3:
        st.metric("Def Rating", "108.2", "-1.1")
    with col4:
        st.metric("Net Rating", "+10.3", "+3.4")
    
    # Performance trend chart
    st.subheader("Performance Trend")
    
    # Mock data for demonstration
    dates = pd.date_range(start='2024-10-01', end='2024-12-13', freq='W')
    net_rating = [5.2, 6.1, 7.8, 9.2, 10.5, 11.2, 10.8, 10.3, 10.1, 10.3]
    
    df_trend = pd.DataFrame({
        'Date': dates[:len(net_rating)],
        'Net Rating': net_rating
    })
    
    fig = px.line(
        df_trend,
        x='Date',
        y='Net Rating',
        title=f'{selected_team} - Net Rating Trend',
        markers=True
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def show_predictions_page(season: str):
    """Display game predictions"""
    
    st.title("Game Predictions")
    st.markdown("### Machine Learning-Powered Predictions")
    
    st.info("🚧 Game prediction feature coming soon!")
    
    st.markdown("""
    This feature will include:
    - Win probability predictions
    - Score predictions
    - Player performance forecasts
    - Playoff probability tracker
    """)


if __name__ == "__main__":
    main()
