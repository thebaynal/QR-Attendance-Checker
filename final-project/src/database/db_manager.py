"""Database manager now using MySQL instead of SQLite."""

import mysql.connector
from mysql.connector import errorcode
import time
import random
from datetime import datetime
from typing import Optional, Dict

class Database:
    """Handles all MySQL interactions for events and attendance."""

    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",       # CHANGE THIS if needed
                user="root",            # CHANGE THIS
                password="divinogwapo12",    # CHANGE THIS
                database="moscan_attendance"    # CHANGE THIS (create manually in phpMyAdmin)
            )
            # buffered=True is important to prevent 'Unread result found' errors
            self.cursor = self.conn.cursor(buffered=True)
            self.create_tables()
            print("Connected to MySQL Database successfully.")
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL: {err}")
            raise

    def _execute(self, query: str, params: tuple = (), commit: bool = True,
                 fetch_all: bool = False, fetch_one: bool = False):

        result = None
        try:
            self.cursor.execute(query, params)

            if fetch_one:
                result = self.cursor.fetchone()
            elif fetch_all:
                result = self.cursor.fetchall()

            if commit:
                self.conn.commit()

            return result

        except mysql.connector.Error as e:
            print(f"MySQL Query Error: {e}")
            return None

    def create_tables(self):
        event_table_sql = """
        CREATE TABLE IF NOT EXISTS events (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            date VARCHAR(255) NOT NULL,
            description TEXT
        )
        """

        attendance_table_sql = """
        CREATE TABLE IF NOT EXISTS attendance (
            event_id VARCHAR(255) NOT NULL,
            user_id VARCHAR(255) NOT NULL,
            user_name VARCHAR(255) NOT NULL,
            timestamp VARCHAR(255) NOT NULL,
            status VARCHAR(255) NOT NULL,
            PRIMARY KEY (event_id, user_id),
            FOREIGN KEY (event_id) REFERENCES events(id)
                ON DELETE CASCADE
        )
        """

        users_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(255) PRIMARY KEY,
            password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            created_at VARCHAR(255) NOT NULL
        )
        """

        self._execute(event_table_sql)
        self._execute(attendance_table_sql)
        self._execute(users_table_sql)

        # Create initial admin user
        count = self._execute("SELECT COUNT(*) FROM users", fetch_one=True)
        if count and count[0] == 0:
            create_admin = """
            INSERT INTO users (username, password, full_name, created_at)
            VALUES (%s, %s, %s, %s)
            """
            self._execute(create_admin, ('admin', 'admin123', 'Administrator', datetime.now().isoformat()))

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
        # FIXED: Replaced ? with %s
        query = "SELECT id, name, date, description FROM events WHERE id = %s"
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
        # FIXED: Replaced ? with %s
        query = "INSERT INTO events (id, name, date, description) VALUES (%s, %s, %s, %s)"
        self._execute(query, (new_id, name, date, description))
        return new_id

    def delete_event(self, event_id: str) -> bool:
        """Delete an event and all its attendance records."""
        # FIXED: Replaced ? with %s
        attendance_query = "DELETE FROM attendance WHERE event_id = %s"
        self._execute(attendance_query, (event_id,))
        
        event_query = "DELETE FROM events WHERE id = %s"
        result = self._execute(event_query, (event_id,))
        # Check if cursor has rowcount to ensure deletion happened
        return True 

    # Attendance operations
    def record_attendance(self, event_id: str, user_id: str, user_name: str, 
                          timestamp: str, status: str = "Checked In"):
        """Record a new attendance entry."""
        # FIXED: Replaced ? with %s
        query = """
        INSERT INTO attendance (event_id, user_id, user_name, timestamp, status) 
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self._execute(query, (event_id, user_id, user_name, timestamp, status))
            return True
        except mysql.connector.Error as err:
            # FIXED: Catch MySQL duplicate entry error (Code 1062) instead of sqlite3.IntegrityError
            if err.errno == errorcode.ER_DUP_ENTRY:
                return False
            print(f"Error recording attendance: {err}")
            return False

    def is_user_checked_in(self, event_id: str, user_id: str) -> Optional[str]:
        """Check if a user has already checked in for a specific event."""
        # FIXED: Replaced ? with %s
        query = "SELECT timestamp FROM attendance WHERE event_id = %s AND user_id = %s"
        result = self._execute(query, (event_id, user_id), fetch_one=True)
        return result[0] if result else None

    def get_attendance_by_event(self, event_id: str) -> Dict:
        """Fetch all attendance records for a given event."""
        # FIXED: Replaced ? with %s
        query = """
        SELECT user_id, user_name, timestamp, status 
        FROM attendance 
        WHERE event_id = %s 
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
        """Authenticate a user and return their full name if successful."""
        # FIXED: Replaced ? with %s
        query = "SELECT full_name FROM users WHERE username = %s AND password = %s"
        result = self._execute(query, (username, password), fetch_one=True)
        return result[0] if result else None
    
    def create_user(self, username: str, password: str, full_name: str) -> bool:
        """Create a new user account."""
        # FIXED: Replaced ? with %s
        query = "INSERT INTO users (username, password, full_name, created_at) VALUES (%s, %s, %s, %s)"
        try:
            self._execute(query, (username, password, full_name, datetime.now().isoformat()))
            return True
        except mysql.connector.Error as err:
            # FIXED: Catch MySQL duplicate entry error instead of sqlite3.IntegrityError
            if err.errno == errorcode.ER_DUP_ENTRY:
                return False
            print(f"Error creating user: {err}")
            return False