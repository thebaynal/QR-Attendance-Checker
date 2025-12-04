# database/db_manager.py
"""Database manager for handling all SQLite operations."""

import sqlite3
import time
import random
from datetime import datetime
from typing import Optional, Dict


class Database:
    """Handles all SQLite interactions for events and attendance."""
    
    def __init__(self, db_name: str = "mascan_attendance.db"):
        self.db_name = db_name
        self.create_tables()
        self._ensure_admin_role()
    
    def _ensure_admin_role(self):
        """Ensure the admin user has the correct role."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # Force update admin user's role to 'admin'
                cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
                conn.commit()
                print("Ensured admin user has 'admin' role")
        except sqlite3.Error as e:
            print(f"Error ensuring admin role: {e}")

    def _execute(self, query: str, params: tuple = (), commit: bool = True, 
                 fetch_all: bool = False, fetch_one: bool = False):
        """Execute SQL command with proper error handling."""
        result = None
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                
                if commit:
                    conn.commit()
                    
            return result
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def _add_column_if_not_exists(self, table: str, column: str, column_type: str):
        """Add a column to a table if it doesn't already exist."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                # Check if column exists
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                if column not in columns:
                    print(f"Adding column '{column}' to table '{table}'")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
                    conn.commit()
        except sqlite3.Error as e:
            print(f"Database error adding column: {e}")

    def create_tables(self):
        """Create necessary tables if they don't exist."""
        event_table_sql = """
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT
        )
        """
        
        attendance_table_sql = """
        CREATE TABLE IF NOT EXISTS attendance (
            event_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            user_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL,
            PRIMARY KEY (event_id, user_id),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
        """
        
        users_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'scanner',
            created_at TEXT NOT NULL
        )
        """
        
        self._execute(event_table_sql)
        self._execute(attendance_table_sql)
        self._execute(users_table_sql)
        
        # Add role column to users table if it doesn't exist (migration)
        self._add_column_if_not_exists('users', 'role', "TEXT DEFAULT 'scanner'")
        self._add_column_if_not_exists('users', 'created_at', "TEXT DEFAULT ''")
        
        # Ensure admin user exists and has correct role
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Check if admin exists
                cursor.execute("SELECT username, role FROM users WHERE username = 'admin'")
                admin_row = cursor.fetchone()
                
                if admin_row:
                    username, current_role = admin_row
                    print(f"Admin user found with role: {current_role}")
                    
                    # Update role to 'admin' if it's not already
                    if current_role != 'admin':
                        cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
                        conn.commit()
                        print("Admin user role updated to 'admin'")
                    else:
                        print("Admin user already has 'admin' role")
                else:
                    # Create admin user
                    print("Creating default admin user")
                    cursor.execute(
                        "INSERT INTO users (username, password, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
                        ('admin', 'admin123', 'Administrator', 'admin', datetime.now().isoformat())
                    )
                    conn.commit()
                    print("Default admin user created")
        except sqlite3.Error as e:
            print(f"Error ensuring admin user: {e}")

    # Event operations
    def get_all_events(self) -> Dict:
        """Fetch all events."""
        query = "SELECT id, name, date, description FROM events ORDER BY date DESC"
        results = self._execute(query, fetch_all=True)
        
        events = {}
        if results:
            for row in results:
                event_id, name, date, description = row
                events[event_id] = {
                    "name": name, 
                    "date": date, 
                    "desc": description or "No description"
                }
        return events

    def get_event_by_id(self, event_id: str) -> Optional[Dict]:
        """Fetch a single event by ID."""
        query = "SELECT id, name, date, description FROM events WHERE id = ?"
        row = self._execute(query, (event_id,), fetch_one=True)
        if row:
            event_id, name, date, description = row
            return {
                "id": event_id,
                "name": name,
                "date": date,
                "desc": description or "No description"
            }
        return None

    def create_event(self, name: str, date: str, description: str) -> str:
        """Insert a new event into the database."""
        new_id = f"EID{int(time.time())}{random.randint(10, 99)}"
        query = "INSERT INTO events (id, name, date, description) VALUES (?, ?, ?, ?)"
        self._execute(query, (new_id, name, date, description))
        return new_id

    def delete_event(self, event_id: str) -> bool:
        """Delete an event and all its attendance records."""
        attendance_query = "DELETE FROM attendance WHERE event_id = ?"
        self._execute(attendance_query, (event_id,))
        
        event_query = "DELETE FROM events WHERE id = ?"
        result = self._execute(event_query, (event_id,))
        return result is not None

    # Attendance operations
    def record_attendance(self, event_id: str, user_id: str, user_name: str, 
                         timestamp: str, status: str = "Checked In"):
        """Record a new attendance entry."""
        query = """
        INSERT INTO attendance (event_id, user_id, user_name, timestamp, status) 
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            self._execute(query, (event_id, user_id, user_name, timestamp, status))
            return True
        except sqlite3.IntegrityError:
            return False

    def is_user_checked_in(self, event_id: str, user_id: str) -> Optional[str]:
        """Check if a user has already checked in for a specific event."""
        query = "SELECT timestamp FROM attendance WHERE event_id = ? AND user_id = ?"
        result = self._execute(query, (event_id, user_id), fetch_one=True)
        return result[0] if result else None

    def get_attendance_by_event(self, event_id: str) -> Dict:
        """Fetch all attendance records for a given event."""
        query = """
        SELECT user_id, user_name, timestamp, status 
        FROM attendance 
        WHERE event_id = ? 
        ORDER BY timestamp DESC
        """
        results = self._execute(query, (event_id,), fetch_all=True)
        
        attendance_log = {}
        if results:
            for row in results:
                user_id, user_name, timestamp, status = row
                attendance_log[user_id] = {
                    "name": user_name,
                    "time": timestamp,
                    "status": status
                }
        return attendance_log

    # User authentication
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate a user and return their username if successful."""
        query = "SELECT username FROM users WHERE username = ? AND password = ?"
        result = self._execute(query, (username, password), fetch_one=True)
        return result[0] if result else None
    
    def get_user_role(self, username: str) -> Optional[str]:
        """Get user role (admin or scanner)."""
        query = "SELECT role FROM users WHERE username = ?"
        result = self._execute(query, (username,), fetch_one=True)
        return result[0] if result else None
    
    def create_user(self, username: str, password: str, full_name: str, role: str = 'scanner') -> bool:
        """Create a new user account with specified role."""
        # Check if user already exists
        check_query = "SELECT username FROM users WHERE username = ?"
        existing = self._execute(check_query, (username,), fetch_one=True)
        if existing:
            return False
        
        query = "INSERT INTO users (username, password, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)"
        result = self._execute(query, (username, password, full_name, role, datetime.now().isoformat()))
        return result is not None