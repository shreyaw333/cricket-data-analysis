import pandas as pd
import json
import os
import glob
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CricketDataProcessor:
    def __init__(self, raw_data_dir="data/raw_json", processed_data_dir="data/processed"):
        self.raw_data_dir = raw_data_dir
        self.processed_data_dir = processed_data_dir
        
        # Create processed data directory
        os.makedirs(processed_data_dir, exist_ok=True)
        
        # Initialize dataframes
        self.matches_df = pd.DataFrame()
        self.players_df = pd.DataFrame()
        self.innings_df = pd.DataFrame()
        self.deliveries_df = pd.DataFrame()
    
    def load_json_file(self, filepath):
        """Load and parse a single JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filepath}: {str(e)}")
            return None
    
    def extract_match_info(self, match_data, filename, match_format):
        """Extract match-level information"""
        try:
            info = match_data.get('info', {})
            meta = match_data.get('meta', {})
            
            match_info = {
                'match_id': filename.replace('.json', ''),
                'format': match_format,
                'city': info.get('city'),
                'venue': info.get('venue'),
                'date': info.get('dates', [None])[0] if info.get('dates') else None,
                'match_type': info.get('match_type'),
                'season': info.get('season'),
                'team1': info.get('teams', [None, None])[0] if len(info.get('teams', [])) > 0 else None,
                'team2': info.get('teams', [None, None])[1] if len(info.get('teams', [])) > 1 else None,
                'toss_winner': info.get('toss', {}).get('winner'),
                'toss_decision': info.get('toss', {}).get('decision'),
                'winner': info.get('outcome', {}).get('winner'),
                'result_type': 'runs' if info.get('outcome', {}).get('by', {}).get('runs') else 'wickets' if info.get('outcome', {}).get('by', {}).get('wickets') else 'other',
                'result_margin': info.get('outcome', {}).get('by', {}).get('runs') or info.get('outcome', {}).get('by', {}).get('wickets'),
                'player_of_match': info.get('player_of_match', [None])[0] if info.get('player_of_match') else None,
                'umpire1': info.get('officials', {}).get('umpires', [None, None])[0] if info.get('officials', {}).get('umpires') else None,
                'umpire2': info.get('officials', {}).get('umpires', [None, None])[1] if len(info.get('officials', {}).get('umpires', [])) > 1 else None,
                'data_version': meta.get('data_version'),
                'created': meta.get('created'),
                'revision': meta.get('revision')
            }
            
            return match_info
            
        except Exception as e:
            logger.error(f"Error extracting match info from {filename}: {str(e)}")
            return None
    
    def extract_players_info(self, match_data, match_id):
        """Extract player information"""
        try:
            players_data = []
            info = match_data.get('info', {})
            players = info.get('players', {})
            
            for team, team_players in players.items():
                for player in team_players:
                    players_data.append({
                        'match_id': match_id,
                        'team': team,
                        'player_name': player
                    })
            
            return players_data
            
        except Exception as e:
            logger.error(f"Error extracting players info from {match_id}: {str(e)}")
            return []
    
    def extract_innings_deliveries(self, match_data, match_id):
        """Extract innings and delivery-level data"""
        try:
            innings_data = []
            deliveries_data = []
            
            innings_list = match_data.get('innings', [])
            
            for innings_num, innings in enumerate(innings_list, 1):
                team = innings.get('team')
                
                # Innings summary
                innings_info = {
                    'match_id': match_id,
                    'innings_number': innings_num,
                    'batting_team': team,
                    'total_overs': 0,
                    'total_runs': 0,
                    'total_wickets': 0,
                    'extras': 0
                }
                
                # Process overs and deliveries
                overs = innings.get('overs', [])
                delivery_count = 0
                
                for over_data in overs:
                    over_num = over_data.get('over', 0)
                    deliveries = over_data.get('deliveries', [])
                    
                    for delivery in deliveries:
                        delivery_count += 1
                        
                        # Extract delivery details
                        runs = delivery.get('runs', {})
                        batter_runs = runs.get('batter', 0)
                        extras_runs = runs.get('extras', 0)
                        total_runs = runs.get('total', 0)
                        
                        delivery_info = {
                            'match_id': match_id,
                            'innings_number': innings_num,
                            'over_number': over_num,
                            'delivery_number': delivery_count,
                            'batting_team': team,
                            'batter': delivery.get('batter'),
                            'non_striker': delivery.get('non_striker'),
                            'bowler': delivery.get('bowler'),
                            'batter_runs': batter_runs,
                            'extras_runs': extras_runs,
                            'total_runs': total_runs,
                            'extras_type': delivery.get('extras', {}).get('wides') and 'wide' or 
                                         delivery.get('extras', {}).get('byes') and 'bye' or
                                         delivery.get('extras', {}).get('legbyes') and 'legbye' or
                                         delivery.get('extras', {}).get('noballs') and 'noball' or None,
                            'wicket_type': delivery.get('wickets', [{}])[0].get('kind') if delivery.get('wickets') else None,
                            'player_dismissed': delivery.get('wickets', [{}])[0].get('player_out') if delivery.get('wickets') else None
                        }
                        
                        deliveries_data.append(delivery_info)
                        
                        # Update innings totals
                        innings_info['total_runs'] += total_runs
                        innings_info['extras'] += extras_runs
                        if delivery.get('wickets'):
                            innings_info['total_wickets'] += len(delivery['wickets'])
                
                innings_info['total_overs'] = len(overs)
                innings_data.append(innings_info)
            
            return innings_data, deliveries_data
            
        except Exception as e:
            logger.error(f"Error extracting innings/deliveries from {match_id}: {str(e)}")
            return [], []
    
    def process_format(self, match_format):
        """Process all files for a specific format"""
        logger.info(f"Processing {match_format} matches...")
        
        format_dir = os.path.join(self.raw_data_dir, match_format)
        json_files = glob.glob(os.path.join(format_dir, "*.json"))
        
        matches_data = []
        all_players_data = []
        all_innings_data = []
        all_deliveries_data = []
        
        for filepath in json_files:
            filename = os.path.basename(filepath)
            match_id = filename.replace('.json', '')
            
            logger.info(f"Processing {filename}...")
            
            # Load JSON data
            match_data = self.load_json_file(filepath)
            if not match_data:
                continue
            
            # Extract match info
            match_info = self.extract_match_info(match_data, filename, match_format)
            if match_info:
                matches_data.append(match_info)
            
            # Extract players
            players_data = self.extract_players_info(match_data, match_id)
            all_players_data.extend(players_data)
            
            # Extract innings and deliveries
            innings_data, deliveries_data = self.extract_innings_deliveries(match_data, match_id)
            all_innings_data.extend(innings_data)
            all_deliveries_data.extend(deliveries_data)
        
        # Convert to DataFrames
        format_matches_df = pd.DataFrame(matches_data)
        format_players_df = pd.DataFrame(all_players_data)
        format_innings_df = pd.DataFrame(all_innings_data)
        format_deliveries_df = pd.DataFrame(all_deliveries_data)
        
        logger.info(f"{match_format} processing complete:")
        logger.info(f"  Matches: {len(format_matches_df)}")
        logger.info(f"  Player records: {len(format_players_df)}")
        logger.info(f"  Innings: {len(format_innings_df)}")
        logger.info(f"  Deliveries: {len(format_deliveries_df)}")
        
        return format_matches_df, format_players_df, format_innings_df, format_deliveries_df
    
    def process_all_formats(self):
        """Process all cricket formats"""
        logger.info("Starting cricket data processing...")
        
        all_matches = []
        all_players = []
        all_innings = []
        all_deliveries = []
        
        formats = ['tests', 'odis', 't20s', 'ipl']
        
        for match_format in formats:
            format_dir = os.path.join(self.raw_data_dir, match_format)
            
            if os.path.exists(format_dir):
                matches_df, players_df, innings_df, deliveries_df = self.process_format(match_format)
                
                all_matches.append(matches_df)
                all_players.append(players_df)
                all_innings.append(innings_df)
                all_deliveries.append(deliveries_df)
        
        # Combine all formats
        self.matches_df = pd.concat(all_matches, ignore_index=True)
        self.players_df = pd.concat(all_players, ignore_index=True)
        self.innings_df = pd.concat(all_innings, ignore_index=True)
        self.deliveries_df = pd.concat(all_deliveries, ignore_index=True)
        
        # Clean and process data
        self.clean_data()
        
        # Save processed data
        self.save_processed_data()
        
        # Show summary
        self.show_summary()
    
    def clean_data(self):
        """Clean and standardize the data"""
        logger.info("Cleaning data...")
        
        # Clean matches data
        if not self.matches_df.empty:
            self.matches_df['date'] = pd.to_datetime(self.matches_df['date'], errors='coerce')
            self.matches_df['result_margin'] = pd.to_numeric(self.matches_df['result_margin'], errors='coerce')
        
        # Clean deliveries data
        if not self.deliveries_df.empty:
            numeric_cols = ['batter_runs', 'extras_runs', 'total_runs', 'over_number', 'delivery_number']
            for col in numeric_cols:
                self.deliveries_df[col] = pd.to_numeric(self.deliveries_df[col], errors='coerce')
    
    def save_processed_data(self):
        """Save processed DataFrames to CSV files"""
        logger.info("Saving processed data...")
        
        self.matches_df.to_csv(os.path.join(self.processed_data_dir, 'matches.csv'), index=False)
        self.players_df.to_csv(os.path.join(self.processed_data_dir, 'players.csv'), index=False)
        self.innings_df.to_csv(os.path.join(self.processed_data_dir, 'innings.csv'), index=False)
        self.deliveries_df.to_csv(os.path.join(self.processed_data_dir, 'deliveries.csv'), index=False)
        
        logger.info(f"Data saved to {self.processed_data_dir}")
    
    def show_summary(self):
        """Show processing summary"""
        print("\n" + "="*60)
        print("🏏 CRICKET DATA PROCESSING SUMMARY")
        print("="*60)
        
        print(f"📊 DATASETS CREATED:")
        print(f"  • Matches: {len(self.matches_df):,} records")
        print(f"  • Players: {len(self.players_df):,} records") 
        print(f"  • Innings: {len(self.innings_df):,} records")
        print(f"  • Deliveries: {len(self.deliveries_df):,} records")
        
        if not self.matches_df.empty:
            print(f"\n🏆 MATCH BREAKDOWN BY FORMAT:")
            format_counts = self.matches_df['format'].value_counts()
            for format_name, count in format_counts.items():
                print(f"  • {format_name.upper()}: {count} matches")
        
        print(f"\n📁 FILES SAVED:")
        print(f"  • data/processed/matches.csv")
        print(f"  • data/processed/players.csv") 
        print(f"  • data/processed/innings.csv")
        print(f"  • data/processed/deliveries.csv")
        
        print(f"\n🎯 Next Steps:")
        print(f"  1. Set up SQL database")
        print(f"  2. Load data into database tables")
        print(f"  3. Write analytical SQL queries")

if __name__ == "__main__":
    processor = CricketDataProcessor()
    processor.process_all_formats()