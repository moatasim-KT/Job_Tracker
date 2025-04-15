"""
Consolidated database migration script.
"""
import sqlite3
import os
from job_tracker import create_app, db  # Import app and db
from datetime import datetime

def update_database():
    """
    Consolidated migration to update the database schema.
    Adds company_data and company_reviews columns to the job table if they don't exist,
    and creates the company_source table if it doesn't exist.
    """
    print("Starting database migration...")
    
    app = create_app()  # Create Flask app
    with app.app_context():  # Use app context
        try:
            # Get database connection from SQLAlchemy
            conn = db.engine.raw_connection()
            cursor = conn.cursor()
            
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
                print("Adding company_data column to job table...")
                cursor.execute("ALTER TABLE job ADD COLUMN company_data TEXT")
            else:
                print("company_data column already exists")
            
            # Add company_reviews column if it doesn't exist
            if 'company_reviews' not in columns:
                print("Adding company_reviews column to job table...")
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
            if 'conn' in locals() and conn:
                conn.rollback()
            print(f"Error during migration: {str(e)}")
        
        finally:
            if 'conn' in locals() and conn:
                conn.close()

if __name__ == "__main__":
    update_database()
