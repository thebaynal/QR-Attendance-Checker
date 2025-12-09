#!/usr/bin/env python3
"""
Database initialization script for MaScan Attendance System.
Run this script to create a fresh database with default admin account.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import Database
import bcrypt

def init_database():
    """Initialize a fresh database with secure default admin."""
    print("Initializing MaScan database...")
    
    # Create database instance
    db = Database("mascan_attendance.db")
    
    # Create secure admin password
    default_password = "Admin@123"
    hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
    
    # Update admin user with hashed password
    try:
        import sqlite3
        with sqlite3.connect(db.db_name) as conn:
            cursor = conn.cursor()
            
            # Delete existing admin if exists
            cursor.execute("DELETE FROM users WHERE username = 'admin'")
            
            # Create new admin with hashed password
            cursor.execute(
                "INSERT INTO users (username, password, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
                ('admin', hashed_password, 'Administrator', 'admin', '2025-12-08T00:00:00')
            )
            conn.commit()
            
        print("✅ Database initialized successfully!")
        print("🔐 Admin credentials:")
        print("   Username: admin")
        print("   Password: Admin@123")
        print("\n⚠️  IMPORTANT: Change the admin password after first login!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

if __name__ == "__main__":
    init_database()