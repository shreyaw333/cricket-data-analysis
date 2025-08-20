import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Use non-interactive backend
plt.switch_backend('Agg')
plt.style.use('default')
sns.set_palette("husl")

class CricketEDAFixed:
    def __init__(self, db_path="data/cricket_data.db"):
        self.conn = sqlite3.connect(db_path)
        self.load_data()
        
        import os
        os.makedirs("visualizations", exist_ok=True)
    
    def load_data(self):
        """Load data from database"""
        self.matches_df = pd.read_sql_query("SELECT * FROM matches", self.conn)
        self.deliveries_df = pd.read_sql_query("SELECT * FROM deliveries", self.conn)
        self.innings_df = pd.read_sql_query("SELECT * FROM innings", self.conn)
        
        print("📊 Data loaded for EDA:")
        print(f"  • Matches: {len(self.matches_df)}")
        print(f"  • Deliveries: {len(self.deliveries_df)}")
    
    def create_quick_visualizations(self):
        """Create 10 visualizations quickly without display"""
        
        print("\n🎨 Creating all visualizations...")
        
        # 1. Format Distribution
        plt.figure(figsize=(10, 6))
        format_counts = self.matches_df['format'].value_counts()
        plt.pie(format_counts.values, labels=format_counts.index, autopct='%1.1f%%')
        plt.title('Distribution of Matches by Format')
        plt.savefig('visualizations/1_format_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ 1. Format Distribution")
        
        # 2. Top Batsmen
        top_batsmen = self.deliveries_df.groupby('batter')['batter_runs'].sum().nlargest(10)
        plt.figure(figsize=(12, 6))
        top_batsmen.plot(kind='bar', color='skyblue')
        plt.title('Top 10 Batsmen by Total Runs')
        plt.xlabel('Batsman')
        plt.ylabel('Total Runs')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('visualizations/2_top_batsmen.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ 2. Top Batsmen")
        
        # 3. Wicket Types
        wickets_data = self.deliveries_df[self.deliveries_df['wicket_type'].notna()]
        wicket_counts = wickets_data['wicket_type'].value_counts()
        plt.figure(figsize=(10, 8))
        plt.pie(wicket_counts.values, labels=wicket_counts.index, autopct='%1.1f%%')
        plt.title('Distribution of Dismissal Types')
        plt.savefig('visualizations/3_dismissal_types.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ 3. Dismissal Types")
        
        # 4. Runs by Format Box Plot
        viz_data = self.innings_df.merge(self.matches_df[['match_id', 'format']], on='match_id')
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=viz_data, x='format', y='total_runs')
        plt.title('Distribution of Team Scores by Format')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('visualizations/4_runs_by_format.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ 4. Runs by Format")
        
        # 5. Top Bowlers
        bowler_wickets = self.deliveries_df[self.deliveries_df['wicket_type'].notna()]
        top_bowlers = bowler_wickets['bowler'].value_counts().head(10)
        plt.figure(figsize=(12, 6))
        top_bowlers.plot(kind='barh', color='lightcoral')
        plt.title('Top 10 Bowlers by Wickets Taken')
        plt.xlabel('Wickets')
        plt.tight_layout()
        plt.savefig('visualizations/5_top_bowlers.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ 5. Top Bowlers")
        
        # 6. Sixes Analysis
        sixes_data = self.deliveries_df[self.deliveries_df['batter_runs'] == 6]
        top_six_hitters = sixes_data['batter'].value_counts().head(8)
        plt.figure(figsize=(10, 6))
        top_six_hitters.plot(kind='bar', color='orange')
        plt.title('Most Sixes Hit by Batsmen')
        plt.xlabel('Batsman')
        plt.ylabel('Number of Sixes')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('visualizations/6_most_sixes.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ 6. Most Sixes")
        
        # 7. Format Scoring Comparison
        format_stats = viz_data.groupby('format')['total_runs'].agg(['mean', 'max', 'min'])
        plt.figure(figsize=(10, 6))
        format_stats['mean'].plot(kind='bar', color='green', alpha=0.7)
        plt.title('Average Score by Cricket Format')
        plt.xlabel('Format')
        plt.ylabel('Average Runs')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('visualizations/7_format_scoring.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ 7. Format Scoring")
        
        # 8. Toss Impact
        toss_data = self.matches_df[self.matches_df['toss_winner'].notna() & 
                                   self.matches_df['winner'].notna()]
        toss_data['toss_winner_won'] = (toss_data['toss_winner'] == toss_data['winner'])
        toss_impact = toss_data.groupby('format')['toss_winner_won'].mean() * 100
        
        plt.figure(figsize=(10, 6))
        bars = toss_impact.plot(kind='bar', color='purple', alpha=0.7)
        plt.axhline(y=50, color='red', linestyle='--', label='50% (No advantage)')
        plt.title('Toss Winner Success Rate by Format')
        plt.xlabel('Format')
        plt.ylabel('Win Percentage (%)')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('visualizations/8_toss_impact.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ 8. Toss Impact")
        
        # 9. Venue Analysis
        venue_data = viz_data.groupby('venue')['total_runs'].mean().sort_values(ascending=False).head(8)
        plt.figure(figsize=(12, 6))
        venue_data.plot(kind='barh', color='teal')
        plt.title('Highest Scoring Venues (Average Runs)')
        plt.xlabel('Average Runs per Innings')
        plt.tight_layout()
        plt.savefig('visualizations/9_venue_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ 9. Venue Analysis")
        
        # 10. Summary Dashboard
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
        
        # Format distribution
        format_counts.plot(kind='pie', ax=ax1, autopct='%1.1f%%')
        ax1.set_title('Matches by Format')
        ax1.set_ylabel('')
        
        # Top scorers
        top_batsmen.head(6).plot(kind='bar', ax=ax2, color='skyblue')
        ax2.set_title('Top 6 Run Scorers')
        ax2.tick_params(axis='x', rotation=45)
        
        # Format averages
        format_stats['mean'].plot(kind='bar', ax=ax3, color='green')
        ax3.set_title('Average Score by Format')
        ax3.tick_params(axis='x', rotation=45)
        
        # Wicket types
        wicket_counts.head(5).plot(kind='bar', ax=ax4, color='coral')
        ax4.set_title('Top 5 Dismissal Types')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.suptitle('Cricket Analysis Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('visualizations/10_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ 10. Summary Dashboard")
        
        print(f"\n🎉 ALL 10 VISUALIZATIONS CREATED!")
        print(f"📁 Saved in: visualizations/ folder")
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    eda = CricketEDAFixed()
    
    try:
        eda.create_quick_visualizations()
        print(f"\n🎯 Next step: Create Power BI dashboard!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        eda.close()