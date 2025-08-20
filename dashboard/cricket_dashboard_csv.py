import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Cricket Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    [data-testid="metric-container"] {
        background-color: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
        padding: 1rem !important;
        border-radius: 0.5rem !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    [data-testid="metric-container"] > div {
        color: #1f2937 !important;
    }
    
    [data-testid="metric-container"] label {
        color: #6b7280 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #1f2937 !important;
        font-size: 2rem !important;
        font-weight: bold !important;
    }
    
    .stSelectbox > div > div {
        background-color: white !important;
        color: black !important;
    }
    
    h1, h2, h3 {
        color: #1f2937;
        font-family: 'Arial', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Load data from CSV files
@st.cache_data
def load_data():
    try:
        matches_df = pd.read_csv("data/processed/matches.csv")
        deliveries_df = pd.read_csv("data/processed/deliveries.csv")
        innings_df = pd.read_csv("data/processed/innings.csv")
        return matches_df, deliveries_df, innings_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Load data
matches_df, deliveries_df, innings_df = load_data()

# Header
st.title("Cricket Data Analytics Dashboard")
st.markdown("---")

# Sidebar filters
st.sidebar.header("Filters")
format_options = ["All", "tests", "odis", "t20s", "ipl"]
format_filter = st.sidebar.selectbox("Select Format", options=format_options, index=0)

# Filter data
if format_filter != "All":
    filtered_matches = matches_df[matches_df['format'] == format_filter]
    match_ids = filtered_matches['match_id'].tolist()
    filtered_deliveries = deliveries_df[deliveries_df['match_id'].isin(match_ids)]
    filtered_innings = innings_df[innings_df['match_id'].isin(match_ids)]
else:
    filtered_matches = matches_df
    filtered_deliveries = deliveries_df
    filtered_innings = innings_df

# KPIs
st.header("Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Matches", f"{len(filtered_matches):,}")

with col2:
    st.metric("Total Deliveries", f"{len(filtered_deliveries):,}")

with col3:
    total_runs = filtered_deliveries['total_runs'].sum() if len(filtered_deliveries) > 0 else 0
    st.metric("Total Runs", f"{total_runs:,}")

with col4:
    total_wickets = len(filtered_deliveries[filtered_deliveries['wicket_type'].notna()]) if len(filtered_deliveries) > 0 else 0
    st.metric("Total Wickets", f"{total_wickets:,}")

with col5:
    avg_score = filtered_innings['total_runs'].mean() if len(filtered_innings) > 0 else 0
    st.metric("Average Score", f"{avg_score:.1f}")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Run Scorers")
    if len(filtered_deliveries) > 0:
        top_batsmen = (filtered_deliveries.groupby('batter')['batter_runs']
                       .sum().reset_index()
                       .sort_values('batter_runs', ascending=False)
                       .head(10))
        
        fig1 = px.bar(top_batsmen, x='batter_runs', y='batter', orientation='h',
                      color='batter_runs', color_continuous_scale='Blues')
        fig1.update_layout(showlegend=False, height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Top 10 Wicket Takers")
    if len(filtered_deliveries) > 0:
        wicket_data = filtered_deliveries[filtered_deliveries['wicket_type'].notna()]
        if len(wicket_data) > 0:
            top_bowlers = wicket_data['bowler'].value_counts().head(10).reset_index()
            top_bowlers.columns = ['bowler', 'wickets']
            
            fig2 = px.bar(top_bowlers, x='wickets', y='bowler', orientation='h',
                          color='wickets', color_continuous_scale='Reds')
            fig2.update_layout(showlegend=False, height=400, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig2, use_container_width=True)

# Format comparison
if format_filter == "All" and len(matches_df) > 0:
    st.subheader("Performance by Format")
    format_data = innings_df.merge(matches_df[['match_id', 'format']], on='match_id')
    format_stats = format_data.groupby('format')['total_runs'].mean().reset_index()
    
    fig3 = px.bar(format_stats, x='format', y='total_runs', 
                  title="Average Runs by Format", color='total_runs', color_continuous_scale='Greens')
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**Cricket Analytics Dashboard** | Data Source: Cricsheet")