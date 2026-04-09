#!/usr/bin/env python3
"""
Database setup script - Run this once to create the weather_history table
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env file")
    exit(1)

# --- FIX FOR NEON / SQLALCHEMY COMPATIBILITY ---
# Neon provides links starting with postgres://, but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
# -----------------------------------------------

print(f"Connecting to database: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Create table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_history (
                id SERIAL PRIMARY KEY,
                city VARCHAR(100) NOT NULL,
                temperature FLOAT NOT NULL,
                humidity INTEGER,
                description VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create indexes
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_city ON weather_history(city);
        """))
        
        connection.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON weather_history(created_at);
        """))
        
        connection.commit()
        
        # Verify table was created
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'weather_history'
            )
        """))
        
        exists = result.scalar()
        if exists:
            print("✅ Database setup successful! weather_history table created.")
        else:
            print("❌ Failed to create table")
            exit(1)
            
except Exception as e:
    print(f"❌ Database connection failed: {str(e)}")
    print("\nMake sure:")
    print("1. Your Neon project is active (not paused)")
    print("2. The connection string in .env is correct")
    print("3. You have internet access to reach the Neon cloud")
    exit(1)