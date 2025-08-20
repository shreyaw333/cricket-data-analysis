import pandas as pd
import sqlite3
import os

def prepare_powerbi_data():
    """Prepare CSV files optimized for Power BI"""
    
    print("🔄 Preparing data for Power BI...")
    
    # Connect to database
    conn = sqlite3.connect("data/cricket_data.db")
    
    # Create PowerBI data directory
    powerbi_dir = "data/powerbi"
    os.makedirs(powerbi_dir, exist_ok=True)
    
    # Load and prepare datasets
    
    # 1. Enhanced Matches table
    matches_query = """
    SELECT 
        match_id,
        format,
        city,
        venue,
        date,
        team1,
        team2,
        toss_winner,
        toss_decision,
        winner,
        result_type,
        result_margin,
        player_of_match,
        CASE WHEN toss_winner = winner THEN 1 ELSE 0 END as toss_advantage
    FROM matches
    WHERE team1 IS NOT NULL AND team2 IS NOT NULL
    """
    
    matches_df = pd.read_sql_query(matches_query, conn)
    matches_df['date'] = pd.to_datetime(matches_df['date'])
    matches_df.to_csv(f"{powerbi_dir}/matches.csv", index=False)
    
    # 2. Player Performance Summary
    player_stats_query = """
    SELECT 
        d.batter as player_name,
        m.format,
        COUNT(*) as balls_faced,
        SUM(d.batter_runs) as total_runs,
        ROUND(AVG(d.batter_runs), 2) as avg_runs_per_ball,
        ROUND(SUM(d.batter_runs) * 100.0 / COUNT(*), 2) as strike_rate,
        COUNT(CASE WHEN d.batter_runs = 4 THEN 1 END) as fours,
        COUNT(CASE WHEN d.batter_runs = 6 THEN 1 END) as sixes,
        COUNT(CASE WHEN d.batter_runs >= 4 THEN 1 END) as boundaries
    FROM deliveries d
    JOIN matches m ON d.match_id = m.match_id
    WHERE d.batter IS NOT NULL
    GROUP BY d.batter, m.format
    HAVING balls_faced >= 20
    """
    
    player_stats_df = pd.read_sql_query(player_stats_query, conn)
    player_stats_df.to_csv(f"{powerbi_dir}/player_batting_stats.csv", index=False)
    
    # 3. Bowling Statistics
    bowling_stats_query = """
    SELECT 
        d.bowler as player_name,
        m.format,
        COUNT(*) as balls_bowled,
        SUM(d.total_runs) as runs_conceded,
        COUNT(CASE WHEN d.wicket_type IS NOT NULL THEN 1 END) as wickets,
        ROUND(SUM(d.total_runs) * 6.0 / COUNT(*), 2) as economy_rate,
        ROUND(COUNT(*) * 1.0 / COUNT(CASE WHEN d.wicket_type IS NOT NULL THEN 1 END), 2) as bowling_average
    FROM deliveries d
    JOIN matches m ON d.match_id = m.match_id
    WHERE d.bowler IS NOT NULL
    GROUP BY d.bowler, m.format
    HAVING balls_bowled >= 30
    """
    
    bowling_stats_df = pd.read_sql_query(bowling_stats_query, conn)
    bowling_stats_df.to_csv(f"{powerbi_dir}/player_bowling_stats.csv", index=False)
    
    # 4. Team Performance by Format
    team_performance_query = """
    WITH team_stats AS (
        SELECT 
            m.format,
            m.team1 as team,
            COUNT(*) as matches_played,
            SUM(CASE WHEN m.winner = m.team1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN m.toss_winner = m.team1 THEN 1 ELSE 0 END) as tosses_won
        FROM matches m
        WHERE m.team1 IS NOT NULL
        GROUP BY m.format, m.team1
        UNION ALL
        SELECT 
            m.format,
            m.team2 as team,
            COUNT(*) as matches_played,
            SUM(CASE WHEN m.winner = m.team2 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN m.toss_winner = m.team2 THEN 1 ELSE 0 END) as tosses_won
        FROM matches m
        WHERE m.team2 IS NOT NULL
        GROUP BY m.format, m.team2
    )
    SELECT 
        format,
        team,
        SUM(matches_played) as total_matches,
        SUM(wins) as total_wins,
        SUM(tosses_won) as total_tosses_won,
        ROUND(SUM(wins) * 100.0 / SUM(matches_played), 2) as win_percentage,
        ROUND(SUM(tosses_won) * 100.0 / SUM(matches_played), 2) as toss_win_percentage
    FROM team_stats
    GROUP BY format, team
    HAVING total_matches >= 2
    """
    
    team_performance_df = pd.read_sql_query(team_performance_query, conn)
    team_performance_df.to_csv(f"{powerbi_dir}/team_performance.csv", index=False)
    
    # 5. Venue Analysis
    venue_analysis_query = """
    SELECT 
        m.venue,
        m.city,
        m.format,
        COUNT(DISTINCT m.match_id) as matches_played,
        ROUND(AVG(i.total_runs), 2) as avg_runs_per_innings,
        MAX(i.total_runs) as highest_score,
        MIN(i.total_runs) as lowest_score,
        COUNT(CASE WHEN m.toss_decision = 'bat' THEN 1 END) as chose_to_bat,
        COUNT(CASE WHEN m.toss_decision = 'field' THEN 1 END) as chose_to_field
    FROM matches m
    JOIN innings i ON m.match_id = i.match_id
    WHERE m.venue IS NOT NULL
    GROUP BY m.venue, m.city, m.format
    """
    
    venue_analysis_df = pd.read_sql_query(venue_analysis_query, conn)
    venue_analysis_df.to_csv(f"{powerbi_dir}/venue_analysis.csv", index=False)
    
    # 6. Match Outcomes Analysis
    outcomes_query = """
    SELECT 
        match_id,
        format,
        winner,
        result_type,
        result_margin,
        CASE 
            WHEN result_type = 'runs' AND result_margin >= 100 THEN 'Comprehensive (100+ runs)'
            WHEN result_type = 'runs' AND result_margin >= 50 THEN 'Comfortable (50-99 runs)'
            WHEN result_type = 'runs' AND result_margin < 50 THEN 'Close (< 50 runs)'
            WHEN result_type = 'wickets' AND result_margin >= 7 THEN 'Comprehensive (7+ wickets)'
            WHEN result_type = 'wickets' AND result_margin >= 4 THEN 'Comfortable (4-6 wickets)'
            WHEN result_type = 'wickets' AND result_margin < 4 THEN 'Close (< 4 wickets)'
            ELSE 'Other'
        END as victory_margin_category
    FROM matches
    WHERE winner IS NOT NULL
    """
    
    outcomes_df = pd.read_sql_query(outcomes_query, conn)
    outcomes_df.to_csv(f"{powerbi_dir}/match_outcomes.csv", index=False)
    
    conn.close()
    
    # Create a summary file
    summary = {
        'matches': len(matches_df),
        'player_batting_records': len(player_stats_df),
        'player_bowling_records': len(bowling_stats_df),
        'team_performance_records': len(team_performance_df),
        'venue_records': len(venue_analysis_df),
        'outcome_records': len(outcomes_df)
    }
    
    print(f"\n✅ Power BI Data Preparation Complete!")
    print(f"📁 Files saved in: {powerbi_dir}/")
    print(f"📊 Data Summary:")
    for key, value in summary.items():
        print(f"  • {key}: {value:,} records")
    
    return powerbi_dir

if __name__ == "__main__":
    powerbi_dir = prepare_powerbi_data()
    
    print(f"\n🎯 POWER BI SETUP INSTRUCTIONS:")
    print(f"="*50)
    print(f"1. Open Power BI Desktop")
    print(f"2. Get Data > Text/CSV")
    print(f"3. Import files from: {powerbi_dir}/")
    print(f"4. Create relationships between tables")
    print(f"5. Build your dashboard with the visualizations")
    print(f"\n📋 Recommended Dashboard Elements:")
    print(f"  • KPI cards for total matches, runs, wickets")
    print(f"  • Team performance comparison charts")
    print(f"  • Player leaderboards (batting & bowling)")
    print(f"  • Format-wise analysis")
    print(f"  • Venue performance maps")
    print(f"  • Toss impact analysis")