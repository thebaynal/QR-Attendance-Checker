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
        self.create_enhanced_tables()
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
            # Return empty list for fetch_all, None for fetch_one, to prevent iteration errors
            return [] if fetch_all else None

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
                    print(f"Column '{column}' added successfully")
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
        
        # Updated attendance table with time_slot column
        attendance_table_sql = """
        CREATE TABLE IF NOT EXISTS attendance (
            event_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            user_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL,
            time_slot TEXT DEFAULT 'morning',
            PRIMARY KEY (event_id, user_id, time_slot),
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
        
        # Add columns to existing tables if they don't exist (migration)
        self._add_column_if_not_exists('users', 'role', "TEXT DEFAULT 'scanner'")
        self._add_column_if_not_exists('users', 'created_at', "TEXT DEFAULT ''")
        self._add_column_if_not_exists('attendance', 'time_slot', "TEXT DEFAULT 'morning'")
        
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

    # Attendance operations with time slot support
    def record_attendance(self, event_id: str, user_id: str, user_name: str, 
                         timestamp: str, status: str = "Checked In"):
        """Record a new attendance entry (backward compatible - defaults to morning)."""
        return self.record_attendance_with_timeslot(event_id, user_id, user_name, 
                                                    timestamp, "morning", status)
    
    def record_attendance_with_timeslot(self, event_id: str, user_id: str, 
                                       user_name: str, timestamp: str, 
                                       time_slot: str = "morning", 
                                       status: str = "Checked In") -> bool:
        """Record attendance for a specific time slot."""
        query = """
        INSERT INTO attendance (event_id, user_id, user_name, timestamp, time_slot, status) 
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            self._execute(query, (event_id, user_id, user_name, timestamp, time_slot, status))
            return True
        except sqlite3.IntegrityError as e:
            print(f"Integrity error: {e}")
            return False

    def is_user_checked_in(self, event_id: str, user_id: str) -> Optional[str]:
        """Check if a user has already checked in for a specific event (any time slot)."""
        query = "SELECT timestamp FROM attendance WHERE event_id = ? AND user_id = ? LIMIT 1"
        result = self._execute(query, (event_id, user_id), fetch_one=True)
        return result[0] if result else None
    
    def is_checked_in_for_slot(self, event_id: str, user_id: str, time_slot: str) -> Optional[str]:
        """Check if user is already checked in for a specific time slot."""
        query = """
        SELECT timestamp FROM attendance 
        WHERE event_id = ? AND user_id = ? AND time_slot = ?
        """
        result = self._execute(query, (event_id, user_id, time_slot), fetch_one=True)
        return result[0] if result else None

    def get_attendance_by_event(self, event_id: str) -> Dict:
        """Fetch all attendance records for a given event."""
        query = """
        SELECT user_id, user_name, timestamp, status, time_slot
        FROM attendance 
        WHERE event_id = ? 
        ORDER BY timestamp DESC
        """
        results = self._execute(query, (event_id,), fetch_all=True)
        
        attendance_log = {}
        if results:
            for row in results:
                user_id, user_name, timestamp, status, time_slot = row
                # Use composite key for users who attended multiple slots
                key = f"{user_id}_{time_slot}"
                attendance_log[key] = {
                    "name": user_name,
                    "time": timestamp,
                    "status": status,
                    "time_slot": time_slot
                }
        return attendance_log
    
    def get_attendance_summary(self, event_id: str) -> Dict:
        """Get attendance summary by time slot using new database structure."""
        try:
            # Get attendance by section which has the new timeslot structure
            attendance_by_section = self.get_attendance_by_section(event_id)
            
            morning_count = 0
            afternoon_count = 0
            
            # Count Present status for each time slot
            for section_name, students in attendance_by_section.items():
                for student in students:
                    if student.get('morning_status') == 'Present':
                        morning_count += 1
                    if student.get('afternoon_status') == 'Present':
                        afternoon_count += 1
            
            return {
                'morning': morning_count,
                'afternoon': afternoon_count
            }
        except Exception as e:
            print(f"Error getting attendance summary: {e}")
            
            # Fallback to old attendance table if new structure fails
            try:
                query = """
                SELECT time_slot, COUNT(DISTINCT user_id) as count
                FROM attendance
                WHERE event_id = ?
                GROUP BY time_slot
                """
                results = self._execute(query, (event_id,), fetch_all=True)
                
                summary = {'morning': 0, 'afternoon': 0}
                if results:
                    for row in results:
                        time_slot, count = row
                        if time_slot in summary:
                            summary[time_slot] = count
                
                return summary
            except Exception as fallback_error:
                print(f"Fallback error: {fallback_error}")
                return {'morning': 0, 'afternoon': 0}

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
        
        try:
            query = "INSERT INTO users (username, password, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)"
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (username, password, full_name, role, datetime.now().isoformat()))
                conn.commit()
                # If we get here without exception, insert was successful
                return True
        except sqlite3.Error as e:
            print(f"Error creating user: {e}")
            return False
    
    # database/db_manager.py (Add these methods)

    def create_enhanced_tables(self):
        """Create enhanced tables for time-slot attendance tracking."""
        
        # Enhanced students table with section/year info
        students_table = """
        CREATE TABLE IF NOT EXISTS students_qrcodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            year_level TEXT,
            section TEXT,
            qr_data TEXT NOT NULL UNIQUE,
            qr_data_encoded TEXT NOT NULL,
            csv_data TEXT,
            created_at TEXT NOT NULL
        )
        """
        
        # Enhanced attendance with separate columns for each time slot
        attendance_table = """
        CREATE TABLE IF NOT EXISTS attendance_timeslots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            morning_time TEXT,
            morning_status TEXT DEFAULT 'Absent',
            lunch_time TEXT,
            lunch_status TEXT DEFAULT 'Absent',
            afternoon_time TEXT,
            afternoon_status TEXT DEFAULT 'Absent',
            date_recorded TEXT NOT NULL,
            UNIQUE(event_id, user_id),
            FOREIGN KEY (event_id) REFERENCES events(id),
            FOREIGN KEY (user_id) REFERENCES students_qrcodes(school_id)
        )
        """
        
        self._execute(students_table)
        self._execute(attendance_table)
        
        # Ensure required columns exist (migration)
        self._add_column_if_not_exists('students_qrcodes', 'year_level', 'TEXT')
        self._add_column_if_not_exists('students_qrcodes', 'section', 'TEXT')
        self._add_column_if_not_exists('attendance_timeslots', 'morning_time', 'TEXT')
        self._add_column_if_not_exists('attendance_timeslots', 'morning_status', "TEXT DEFAULT 'Absent'")
        self._add_column_if_not_exists('attendance_timeslots', 'lunch_time', 'TEXT')
        self._add_column_if_not_exists('attendance_timeslots', 'lunch_status', "TEXT DEFAULT 'Absent'")
        self._add_column_if_not_exists('attendance_timeslots', 'afternoon_time', 'TEXT')
        self._add_column_if_not_exists('attendance_timeslots', 'afternoon_status', "TEXT DEFAULT 'Absent'")
        
        # Create indexes for better performance
        self._execute("CREATE INDEX IF NOT EXISTS idx_students_section ON students_qrcodes(year_level, section)")
        self._execute("CREATE INDEX IF NOT EXISTS idx_attendance_event ON attendance_timeslots(event_id)")

    def record_timeslot_attendance(self, event_id: str, school_id: str, time_slot: str) -> bool:
        """Record attendance for a specific time slot."""
        from datetime import datetime
        
        time_now = datetime.now().strftime("%H:%M:%S")
        date_now = datetime.now().strftime("%Y-%m-%d")
        
        # Check if record exists
        check_query = "SELECT id FROM attendance_timeslots WHERE event_id = ? AND user_id = ?"
        existing = self._execute(check_query, (event_id, school_id), fetch_one=True)
        
        if existing:
            # Update existing record
            if time_slot == 'morning':
                update_query = """
                UPDATE attendance_timeslots 
                SET morning_time = ?, morning_status = 'Present'
                WHERE event_id = ? AND user_id = ?
                """
            elif time_slot == 'lunch':
                update_query = """
                UPDATE attendance_timeslots 
                SET lunch_time = ?, lunch_status = 'Present'
                WHERE event_id = ? AND user_id = ?
                """
            else:  # afternoon
                update_query = """
                UPDATE attendance_timeslots 
                SET afternoon_time = ?, afternoon_status = 'Present'
                WHERE event_id = ? AND user_id = ?
                """
            
            self._execute(update_query, (time_now, event_id, school_id))
        else:
            # Create new record
            insert_query = """
            INSERT INTO attendance_timeslots 
            (event_id, user_id, {}_time, {}_status, date_recorded)
            VALUES (?, ?, ?, 'Present', ?)
            """.format(time_slot, time_slot)
            
            self._execute(insert_query, (event_id, school_id, time_now, date_now))
        
        return True

    def get_attendance_by_section(self, event_id: str) -> dict:
        """Get attendance grouped by year and section."""
        query = """
        SELECT 
            s.school_id,
            s.name,
            COALESCE(s.year_level, 'N/A') as year_level,
            COALESCE(s.section, 'N/A') as section,
            COALESCE(a.morning_time, '') as morning_time,
            COALESCE(a.morning_status, 'Absent') as morning_status,
            COALESCE(a.lunch_time, '') as lunch_time,
            COALESCE(a.lunch_status, 'Absent') as lunch_status,
            COALESCE(a.afternoon_time, '') as afternoon_time,
            COALESCE(a.afternoon_status, 'Absent') as afternoon_status
        FROM students_qrcodes s
        LEFT JOIN attendance_timeslots a 
            ON s.school_id = a.user_id AND a.event_id = ?
        ORDER BY s.year_level, s.section, s.name
        """
        
        results = self._execute(query, (event_id,), fetch_all=True)
        
        # Handle case where results is None or empty
        if not results:
            return {}
        
        # Group by section
        grouped_data = {}
        for row in results:
            school_id, name, year, section, m_time, m_status, l_time, l_status, a_time, a_status = row
            
            section_key = f"{year or 'N/A'} - {section or 'N/A'}"
            
            if section_key not in grouped_data:
                grouped_data[section_key] = []
            
            grouped_data[section_key].append({
                'school_id': school_id,
                'name': name,
                'morning_time': m_time,
                'morning_status': m_status,
                'lunch_time': l_time,
                'lunch_status': l_status,
                'afternoon_time': a_time,
                'afternoon_status': a_status
            })
        
        return grouped_data

    def check_timeslot_attendance(self, event_id: str, school_id: str, time_slot: str) -> bool:
        """Check if student already checked in for specific time slot."""
        query = f"""
        SELECT {time_slot}_status 
        FROM attendance_timeslots 
        WHERE event_id = ? AND user_id = ?
        """
        result = self._execute(query, (event_id, school_id), fetch_one=True)
        
        return result and result[0] == 'Present'

    def get_student_by_id(self, school_id: str) -> dict:
        """Get student information by school ID."""
        query = "SELECT school_id, name, year_level, section FROM students_qrcodes WHERE school_id = ?"
        result = self._execute(query, (school_id,), fetch_one=True)
        
        if result:
            return {
                'school_id': result[0],
                'name': result[1],
                'year_level': result[2],
                'section': result[3]
            }
        return None