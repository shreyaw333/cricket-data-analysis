import sqlite3
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CricketDatabase:
    def __init__(self, db_path="data/cricket_data.db", processed_data_dir="data/processed"):
        self.db_path = db_path
        self.processed_data_dir = processed_data_dir
        self.conn = None
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def connect(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False
    
    def create_tables(self):
        """Create database tables with proper schema"""
        logger.info("Creating database tables...")
        
        try:
            cursor = self.conn.cursor()
            
            # Matches table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                match_id TEXT PRIMARY KEY,
                format TEXT,
                city TEXT,
                venue TEXT,
                date DATE,
                match_type TEXT,
                season TEXT,
                team1 TEXT,
                team2 TEXT,
                toss_winner TEXT,
                toss_decision TEXT,
                winner TEXT,
                result_type TEXT,
                result_margin INTEGER,
                player_of_match TEXT,
                umpire1 TEXT,
                umpire2 TEXT,
                data_version TEXT,
                created TEXT,
                revision INTEGER
            )
            ''')
            
            # Players table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                team TEXT,
                player_name TEXT,
                FOREIGN KEY (match_id) REFERENCES matches (match_id)
            )
            ''')
            
            # Innings table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS innings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                innings_number INTEGER,
                batting_team TEXT,
                total_overs INTEGER,
                total_runs INTEGER,
                total_wickets INTEGER,
                extras INTEGER,
                FOREIGN KEY (match_id) REFERENCES matches (match_id)
            )
            ''')
            
            # Deliveries table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT,
                innings_number INTEGER,
                over_number INTEGER,
                delivery_number INTEGER,
                batting_team TEXT,
                batter TEXT,
                non_striker TEXT,
                bowler TEXT,
                batter_runs INTEGER,
                extras_runs INTEGER,
                total_runs INTEGER,
                extras_type TEXT,
                wicket_type TEXT,
                player_dismissed TEXT,
                FOREIGN KEY (match_id) REFERENCES matches (match_id)
            )
            ''')
            
            self.conn.commit()
            logger.info("Database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            return False
    
    def load_csv_to_table(self, csv_filename, table_name):
        """Load CSV data into database table"""
        try:
            csv_path = os.path.join(self.processed_data_dir, csv_filename)
            
            if not os.path.exists(csv_path):
                logger.error(f"CSV file not found: {csv_path}")
                return False
            
            # Read CSV
            df = pd.read_csv(csv_path)
            logger.info(f"Loading {len(df)} records into {table_name}...")
            
            # Load to database
            df.to_sql(table_name, self.conn, if_exists='replace', index=False)
            
            logger.info(f"✅ {table_name} table loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading {table_name}: {str(e)}")
            return False
    
    def load_all_data(self):
        """Load all CSV files into database"""
        logger.info("Loading all data into database...")
        
        tables_to_load = [
            ('matches.csv', 'matches'),
            ('players.csv', 'players'),
            ('innings.csv', 'innings'),
            ('deliveries.csv', 'deliveries')
        ]
        
        success_count = 0
        
        for csv_file, table_name in tables_to_load:
            if self.load_csv_to_table(csv_file, table_name):
                success_count += 1
        
        logger.info(f"Data loading complete: {success_count}/{len(tables_to_load)} tables loaded")
        return success_count == len(tables_to_load)
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        logger.info("Creating database indexes...")
        
        try:
            cursor = self.conn.cursor()
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_matches_format ON matches(format)",
                "CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(date)",
                "CREATE INDEX IF NOT EXISTS idx_matches_venue ON matches(venue)",
                "CREATE INDEX IF NOT EXISTS idx_players_name ON players(player_name)",
                "CREATE INDEX IF NOT EXISTS idx_deliveries_match ON deliveries(match_id)",
                "CREATE INDEX IF NOT EXISTS idx_deliveries_batter ON deliveries(batter)",
                "CREATE INDEX IF NOT EXISTS idx_deliveries_bowler ON deliveries(bowler)",
                "CREATE INDEX IF NOT EXISTS idx_innings_match ON innings(match_id)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            self.conn.commit()
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
    
    def get_database_summary(self):
        """Get summary of database contents"""
        try:
            cursor = self.conn.cursor()
            
            print("\n" + "="*60)
            print("🗄️  DATABASE SUMMARY")
            print("="*60)
            
            tables = ['matches', 'players', 'innings', 'deliveries']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"📊 {table.upper()}: {count:,} records")
            
            # Show some sample data
            print(f"\n🏏 SAMPLE MATCHES:")
            cursor.execute("""
            SELECT match_id, format, team1, team2, winner, venue
            FROM matches 
            LIMIT 5
            """)
            
            for row in cursor.fetchall():
                match_id, format_type, team1, team2, winner, venue = row
                print(f"  • {match_id} | {format_type.upper()} | {team1} vs {team2} | Winner: {winner}")
            
            print(f"\n🎯 DATABASE READY FOR ANALYSIS!")
            print(f"📁 Database location: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error getting database summary: {str(e)}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

def setup_database():
    """Main function to set up the database"""
    db = CricketDatabase()
    
    try:
        # Connect to database
        if not db.connect():
            return False
        
        # Create tables
        if not db.create_tables():
            return False
        
        # Load data
        if not db.load_all_data():
            return False
        
        # Create indexes
        db.create_indexes()
        
        # Show summary
        db.get_database_summary()
        
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = setup_database()
    
    if success:
        print(f"\n✅ Database setup completed successfully!")
        print(f"🔄 Next step: Run SQL analysis queries")
    else:
        print(f"\n❌ Database setup failed. Check logs for details.")