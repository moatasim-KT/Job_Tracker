"""
Database migration script to add company information fields
"""

import sqlite3
import os
from datetime import datetime

# Database file path
DB_PATH = 'instance/site.db'

def migrate_database():
    """
    Migrate the database to add the company_data and company_reviews columns to the Job table
    and create the CompanySource table
    """
    print("Starting database migration...")
    
    # Check if the database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if the job table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job'")
        if not cursor.fetchone():
            print("Job table doesn't exist. Database may not be initialized.")
            print("Run the application first to create the database schema.")
            return
        
        # Check if company_data and company_reviews columns already exist in Job table
        cursor.execute("PRAGMA table_info(job)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add company_data column if it doesn't exist
        if 'company_data' not in columns:
            print("Adding company_data column to Job table...")
            cursor.execute("ALTER TABLE job ADD COLUMN company_data TEXT")
        else:
            print("company_data column already exists")
        
        # Add company_reviews column if it doesn't exist
        if 'company_reviews' not in columns:
            print("Adding company_reviews column to Job table...")
            cursor.execute("ALTER TABLE job ADD COLUMN company_reviews TEXT")
        else:
            print("company_reviews column already exists")
        
        # Check if CompanySource table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_source'")
        if not cursor.fetchone():
            print("Creating CompanySource table...")
            cursor.execute("""
            CREATE TABLE company_source (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                linkedin_url TEXT,
                website_url TEXT,
                glassdoor_url TEXT,
                last_updated TIMESTAMP
            )
            """)
        else:
            print("CompanySource table already exists")
        
        # Commit changes
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {str(e)}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
