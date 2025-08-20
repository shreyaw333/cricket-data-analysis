import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# Use non-interactive backend
plt.switch_backend('Agg')

def fix_venue_visualization():
    conn = sqlite3.connect("data/cricket_data.db")
    
    # Load data
    matches_df = pd.read_sql_query("SELECT * FROM matches", conn)
    innings_df = pd.read_sql_query("SELECT * FROM innings", conn)
    
    # Merge data and handle missing venues
    viz_data = innings_df.merge(matches_df[['match_id', 'format', 'venue']], on='match_id')
    
    # Filter out null venues and get venue stats
    venue_data = viz_data[viz_data['venue'].notna()]
    
    if len(venue_data) > 0:
        venue_stats = venue_data.groupby('venue')['total_runs'].mean().sort_values(ascending=False)
        
        # Take top 8 venues
        top_venues = venue_stats.head(8)
        
        plt.figure(figsize=(12, 6))
        top_venues.plot(kind='barh', color='teal')
        plt.title('Highest Scoring Venues (Average Runs)')
        plt.xlabel('Average Runs per Innings')
        plt.tight_layout()
        plt.savefig('visualizations/9_venue_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ 9. Venue Analysis - Fixed!")
        print(f"📊 Analyzed {len(top_venues)} venues")
    else:
        print("⚠️ No venue data available, creating placeholder...")
        
        # Create a simple placeholder
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'Venue Data Not Available\nin Current Dataset', 
                ha='center', va='center', fontsize=16, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.axis('off')
        plt.title('Venue Analysis Placeholder')
        plt.savefig('visualizations/9_venue_placeholder.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ 9. Venue Placeholder Created")
    
    conn.close()

if __name__ == "__main__":
    fix_venue_visualization()
    print("\n🎉 ALL 10 VISUALIZATIONS NOW COMPLETE!")
    print("📁 Check visualizations/ folder")
    print("🎯 Ready for Power BI dashboard creation!")