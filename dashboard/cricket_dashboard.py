import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import numpy as np

# Page configuration
st.set_page_config(
   page_title="Cricket Analytics Dashboard",
   page_icon="📊",
   layout="wide",
   initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
# Custom CSS for professional styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    /* Fix metric cards */
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
    
    /* Fix selectbox */
    .stSelectbox > div > div {
        background-color: white !important;
        color: black !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background-color: white !important;
        color: black !important;
    }
    
    h1, h2, h3 {
        color: #1f2937;
        font-family: 'Arial', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_data
def load_data():
   import os
   
   # Get the absolute path to the database
   current_dir = os.getcwd()
   db_path = os.path.join(current_dir, "data", "cricket_data.db")
   
   if not os.path.exists(db_path):
       st.error(f"Database not found at {db_path}")
       return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
   
   try:
       conn = sqlite3.connect(db_path)
       
       matches_df = pd.read_sql_query("SELECT * FROM matches", conn)
       deliveries_df = pd.read_sql_query("SELECT * FROM deliveries", conn)
       innings_df = pd.read_sql_query("SELECT * FROM innings", conn)
       
       conn.close()
       
       return matches_df, deliveries_df, innings_df
       
   except Exception as e:
       st.error(f"Database error: {str(e)}")
       return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Load data
matches_df, deliveries_df, innings_df = load_data()

# Header
st.title("Cricket Data Analytics Dashboard")
st.markdown("---")

# Sidebar filters
st.sidebar.header("Filters")

if len(matches_df) > 0:
   format_options = ["All", "tests", "odis", "t20s", "ipl"]
else:
   format_options = ["All"]

format_filter = st.sidebar.selectbox(
   "Select Format",
   options=format_options,
   index=0
)

st.sidebar.write(f"Current filter: {format_filter}")

# Filter data based on selection
if format_filter != "All":
   filtered_matches = matches_df[matches_df['format'] == format_filter]
   match_ids = filtered_matches['match_id'].tolist()
   filtered_deliveries = deliveries_df[deliveries_df['match_id'].isin(match_ids)]
   filtered_innings = innings_df[innings_df['match_id'].isin(match_ids)]
else:
   filtered_matches = matches_df
   filtered_deliveries = deliveries_df
   filtered_innings = innings_df

# Key Performance Indicators
st.header("Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
   total_matches = len(filtered_matches)
   st.metric("Total Matches", f"{total_matches:,}")

with col2:
   total_deliveries = len(filtered_deliveries)
   st.metric("Total Deliveries", f"{total_deliveries:,}")

with col3:
   total_runs = filtered_deliveries['total_runs'].sum()
   st.metric("Total Runs", f"{total_runs:,}")

with col4:
   total_wickets = len(filtered_deliveries[filtered_deliveries['wicket_type'].notna()])
   st.metric("Total Wickets", f"{total_wickets:,}")

with col5:
   if len(filtered_innings) > 0:
       avg_score = filtered_innings['total_runs'].mean()
       st.metric("Average Score", f"{avg_score:.1f}")
   else:
       st.metric("Average Score", "0")

st.markdown("---")

# Two column layout for charts
col1, col2 = st.columns(2)

with col1:
   st.subheader("Top 10 Run Scorers")
   if len(filtered_deliveries) > 0:
       top_batsmen = (filtered_deliveries.groupby('batter')['batter_runs']
                      .sum().reset_index()
                      .sort_values('batter_runs', ascending=False)
                      .head(10))
       
       if len(top_batsmen) > 0:
           fig1 = px.bar(top_batsmen, 
                         x='batter_runs', 
                         y='batter',
                         orientation='h',
                         title="",
                         color='batter_runs',
                         color_continuous_scale='Blues')
           fig1.update_layout(
               showlegend=False,
               height=400,
               yaxis={'categoryorder': 'total ascending'},
               plot_bgcolor='white',
               font=dict(size=12)
           )
           st.plotly_chart(fig1, use_container_width=True)
       else:
           st.write("No batting data available for selected filter")
   else:
       st.write("No data available")

with col2:
   st.subheader("Top 10 Wicket Takers")
   if len(filtered_deliveries) > 0:
       wicket_data = filtered_deliveries[filtered_deliveries['wicket_type'].notna()]
       if len(wicket_data) > 0:
           top_bowlers = (wicket_data['bowler'].value_counts()
                          .head(10).reset_index())
           top_bowlers.columns = ['bowler', 'wickets']
           
           fig2 = px.bar(top_bowlers,
                         x='wickets',
                         y='bowler',
                         orientation='h',
                         title="",
                         color='wickets',
                         color_continuous_scale='Reds')
           fig2.update_layout(
               showlegend=False,
               height=400,
               yaxis={'categoryorder': 'total ascending'},
               plot_bgcolor='white',
               font=dict(size=12)
           )
           st.plotly_chart(fig2, use_container_width=True)
       else:
           st.write("No wicket data available for selected filter")
   else:
       st.write("No data available")

# Format comparison
st.subheader("Performance by Format")

if format_filter == "All" and len(matches_df) > 0:
   format_data = innings_df.merge(matches_df[['match_id', 'format']], on='match_id')
   format_stats = format_data.groupby('format').agg({
       'total_runs': ['mean', 'max', 'count'],
       'total_wickets': 'mean'
   }).round(2)
   
   format_stats.columns = ['Avg Runs', 'Highest Score', 'Innings Played', 'Avg Wickets']
   format_stats = format_stats.reset_index()
   
   fig3 = px.bar(format_stats,
                 x='format',
                 y='Avg Runs',
                 title="Average Runs by Format",
                 color='Avg Runs',
                 color_continuous_scale='Greens')
   fig3.update_layout(
       showlegend=False,
       plot_bgcolor='white',
       font=dict(size=12)
   )
   st.plotly_chart(fig3, use_container_width=True)
else:
   st.write("Select 'All' formats to see comparison chart")

# Dismissal analysis
col1, col2 = st.columns(2)

with col1:
   st.subheader("Dismissal Types Distribution")
   if len(filtered_deliveries) > 0:
       wicket_types = (filtered_deliveries[filtered_deliveries['wicket_type'].notna()]
                       ['wicket_type'].value_counts())
       
       if len(wicket_types) > 0:
           fig4 = px.pie(values=wicket_types.values,
                         names=wicket_types.index,
                         title="")
           fig4.update_layout(
               showlegend=True,
               height=400,
               font=dict(size=12)
           )
           st.plotly_chart(fig4, use_container_width=True)
       else:
           st.write("No dismissal data available")
   else:
       st.write("No data available")

with col2:
   st.subheader("Team Win Analysis")
   if not filtered_matches.empty and 'winner' in filtered_matches.columns:
       winners = filtered_matches['winner'].dropna().value_counts().head(8)
       
       if len(winners) > 0:
           fig5 = px.bar(x=winners.index,
                         y=winners.values,
                         title="",
                         color=winners.values,
                         color_continuous_scale='Purples')
           fig5.update_layout(
               showlegend=False,
               height=400,
               plot_bgcolor='white',
               xaxis_title="Team",
               yaxis_title="Wins",
               font=dict(size=12),
               xaxis_tickangle=45
           )
           st.plotly_chart(fig5, use_container_width=True)
       else:
           st.write("No winner data available")
   else:
       st.write("No match data available")

# Data tables
st.markdown("---")
st.subheader("Detailed Statistics")

tab1, tab2, tab3 = st.tabs(["Batting Stats", "Bowling Stats", "Match Results"])

with tab1:
   if len(filtered_deliveries) > 0:
       batting_stats = (filtered_deliveries.groupby('batter').agg({
           'batter_runs': ['sum', 'count'],
           'delivery_number': 'count'
       }).round(2))
       batting_stats.columns = ['Total Runs', 'Scoring Shots', 'Balls Faced']
       batting_stats['Strike Rate'] = (batting_stats['Total Runs'] / batting_stats['Balls Faced'] * 100).round(2)
       batting_stats = batting_stats[batting_stats['Balls Faced'] >= 20].sort_values('Total Runs', ascending=False)
       
       if len(batting_stats) > 0:
           st.dataframe(batting_stats.head(15), use_container_width=True)
       else:
           st.write("No batting statistics available (minimum 20 balls required)")
   else:
       st.write("No data available")

with tab2:
   if len(filtered_deliveries) > 0:
       bowling_stats = (filtered_deliveries.groupby('bowler').agg({
           'total_runs': 'sum',
           'delivery_number': 'count',
           'wicket_type': lambda x: x.notna().sum()
       }).round(2))
       bowling_stats.columns = ['Runs Conceded', 'Balls Bowled', 'Wickets']
       bowling_stats['Economy Rate'] = (bowling_stats['Runs Conceded'] / bowling_stats['Balls Bowled'] * 6).round(2)
       bowling_stats = bowling_stats[bowling_stats['Balls Bowled'] >= 30].sort_values('Wickets', ascending=False)
       
       if len(bowling_stats) > 0:
           st.dataframe(bowling_stats.head(15), use_container_width=True)
       else:
           st.write("No bowling statistics available (minimum 30 balls required)")
   else:
       st.write("No data available")

with tab3:
   if len(filtered_matches) > 0:
       match_results = filtered_matches[['match_id', 'format', 'team1', 'team2', 'winner', 'venue', 'date']].copy()
       match_results['date'] = pd.to_datetime(match_results['date'], errors='coerce').dt.strftime('%Y-%m-%d')
       st.dataframe(match_results, use_container_width=True)
   else:
       st.write("No match data available")

# Footer
st.markdown("---")
st.markdown(
   """
   **Cricket Analytics Dashboard** | Data Source: Cricsheet | 
   Total Records Analyzed: {:,} deliveries across {:,} matches
   """.format(len(deliveries_df), len(matches_df))
)