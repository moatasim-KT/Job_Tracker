"""
Script to update the database schema with new columns.
"""
import sqlite3
import os

def update_database():
    """Update the database schema with new columns."""
    print("Updating database schema...")
    
    # Check possible database locations
    possible_db_paths = [
        os.path.join(os.path.dirname(__file__), 'instance', 'jobs.db'),
        os.path.join(os.path.dirname(__file__), 'jobs.db'),
        os.path.join(os.path.dirname(__file__), 'job_tracker', 'job_tracker.db')
    ]
    
    # Find the first database that exists
    db_path = None
    for path in possible_db_paths:
        if os.path.exists(path):
            db_path = path
            print(f"Database found at {db_path}")
            break
    
    if not db_path:
        print("No database found in any of the expected locations")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(job)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add new columns if they don't exist
    if 'company_data' not in columns:
        try:
            cursor.execute("ALTER TABLE job ADD COLUMN company_data TEXT")
            print("Added company_data column to job table")
        except sqlite3.OperationalError as e:
            print(f"Error adding company_data column: {e}")
    
    if 'company_reviews' not in columns:
        try:
            cursor.execute("ALTER TABLE job ADD COLUMN company_reviews TEXT")
            print("Added company_reviews column to job table")
        except sqlite3.OperationalError as e:
            print(f"Error adding company_reviews column: {e}")
    
    # Create CompanySource table if it doesn't exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_source'")
    if not cursor.fetchone():
        try:
            cursor.execute('''
            CREATE TABLE company_source (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name VARCHAR(100) NOT NULL,
                linkedin_url VARCHAR(500),
                website_url VARCHAR(500),
                glassdoor_url VARCHAR(500),
                last_updated DATETIME
            )
            ''')
            print("Created company_source table")
        except sqlite3.OperationalError as e:
            print(f"Error creating company_source table: {e}")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database schema update completed")

if __name__ == "__main__":
    update_database()
