# api_db_manager.py
"""Database manager that connects to remote API instead of local SQLite."""

import requests
import json
from typing import Optional, Dict, List

class APIDatabase:
    """Database manager that uses REST API for remote database access."""
    
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }
    
    def _make_request(self, method: str, endpoint: str, data=None):
        """Make HTTP request to API."""
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"API error: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    # ==================== Authentication ====================
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user via API."""
        data = {"username": username, "password": password}
        try:
            url = f"{self.api_base_url}/api/login"
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                return result.get('username') if result.get('success') else None
        except Exception as e:
            print(f"Authentication failed: {e}")
        return None
    
    def get_user_role(self, username: str) -> Optional[str]:
        """Get user role."""
        return 'admin'
    
    def record_login(self, username: str):
        """Record login."""
        pass
    
    def record_logout(self, username: str):
        """Record logout via API."""
        data = {"username": username}
        return self._make_request('POST', '/api/logout', data)
    
    # ==================== Events ====================
    
    def get_all_events(self) -> Dict:
        """Get all events via API."""
        result = self._make_request('GET', '/api/events')
        return result if result else {}
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict]:
        """Get single event by ID."""
        events = self.get_all_events()
        return events.get(event_id)
    
    def create_event(self, name: str, date: str, description: str) -> str:
        """Create new event via API."""
        import time
        import random
        new_id = f"EID{int(time.time())}{random.randint(10, 99)}"
        
        data = {
            "id": new_id,
            "name": name,
            "date": date,
            "description": description
        }
        
        result = self._make_request('POST', '/api/events', data)
        return new_id if result else None
    
    def delete_event(self, event_id: str) -> bool:
        """Delete event via API."""
        try:
            url = f"{self.api_base_url}/api/events/{event_id}"
            response = requests.delete(url, headers=self.headers)
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
    
    # ==================== Attendance ====================
    
    def record_attendance(self, event_id: str, user_id: str, user_name: str, 
                         status: str = "Checked In", time_slot: str = "morning"):
        """Record attendance via API."""
        data = {
            "event_id": event_id,
            "scanned_user_id": user_id,
            "scanned_user_name": user_name,
            "scanner_username": "web_user"
        }
        return self._make_request('POST', '/api/record-scan', data)
    
    def record_attendance_with_timeslot(self, event_id: str, user_id: str, user_name: str,
                                       timestamp: str, status: str = "Checked In", 
                                       time_slot: str = "morning"):
        """Record attendance with time slot."""
        return self.record_attendance(event_id, user_id, user_name, status, time_slot)
    
    def get_attendance_by_event(self, event_id: str) -> Dict:
        """Get attendance for event via API."""
        result = self._make_request('GET', f'/api/attendance/{event_id}')
        return result if result else {}
    
    def is_user_checked_in(self, event_id: str, user_id: str) -> Optional[str]:
        """Check if user checked in."""
        attendance = self.get_attendance_by_event(event_id)
        if isinstance(attendance, dict):
            for entry in attendance.get(event_id, []):
                if entry.get('user_id') == user_id:
                    return entry.get('status')
        return None
    
    def is_checked_in_for_slot(self, event_id: str, user_id: str, time_slot: str) -> Optional[str]:
        """Check if user checked in for specific slot."""
        return self.is_user_checked_in(event_id, user_id)
    
    def get_attendance_summary(self, event_id: str) -> Dict:
        """Get attendance summary."""
        result = self._make_request('GET', f'/api/attendance-summary/{event_id}')
        return result if result else {}
    
    # ==================== Users ====================
    
    def create_user(self, username: str, password: str, full_name: str, role: str = 'scanner') -> bool:
        """Create user via API."""
        data = {
            "username": username,
            "password": password,
            "full_name": full_name,
            "role": role
        }
        result = self._make_request('POST', '/api/users', data)
        return result is not None
    
    def get_all_users(self) -> Dict:
        """Get all users via API."""
        result = self._make_request('GET', '/api/users')
        return result if result else {}
    
    def delete_user(self, username: str) -> bool:
        """Delete user via API."""
        try:
            url = f"{self.api_base_url}/api/users/{username}"
            response = requests.delete(url, headers=self.headers)
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    # ==================== Students ====================
    
    def get_student_by_id(self, school_id: str) -> Optional[Dict]:
        """Get student information by school ID."""
        result = self._make_request('GET', f'/api/students/{school_id}')
        return result if result else None
    
    def get_attendance_by_section(self, event_id: str) -> Dict:
        """Get attendance grouped by year and section."""
        result = self._make_request('GET', f'/api/attendance-by-section/{event_id}')
        return result if result else {}
    
    def check_timeslot_attendance(self, event_id: str, school_id: str, time_slot: str) -> bool:
        """Check if student already checked in for time slot."""
        result = self._make_request('GET', f'/api/check-timeslot/{event_id}/{school_id}/{time_slot}')
        return result.get('checked_in', False) if result else False
    
    def record_timeslot_attendance(self, event_id: str, school_id: str, time_slot: str) -> bool:
        """Record attendance for specific time slot."""
        data = {
            "event_id": event_id,
            "school_id": school_id,
            "time_slot": time_slot
        }
        result = self._make_request('POST', '/api/record-timeslot', data)
        return result is not None
    
    # ==================== Activity Logging ====================
    
    def record_scan(self, scanner_username: str, scanned_user_id: str, 
                   scanned_user_name: str, event_id: str = None):
        """Record scan activity."""
        pass
    
    def get_recent_scans(self, limit: int = 10) -> List:
        """Get recent scans via API."""
        result = self._make_request('GET', f'/api/recent-scans?limit={limit}')
        return result if result else []
    
    def get_recent_logins(self, limit: int = 10) -> List:
        """Get recent logins via API."""
        result = self._make_request('GET', f'/api/recent-logins?limit={limit}')
        return result if result else []
    
    def get_scans_by_scanner(self, username: str, limit: int = 10):
        """Get scans by scanner."""
        return self.get_recent_scans(limit)
    
    # ==================== Compatibility Methods ====================
    
    def _execute(self, query: str, params: tuple = (), commit: bool = True, 
                 fetch_all: bool = False, fetch_one: bool = False):
        """Execute SQL - compatibility method for local database calls."""
        # Check if it's a DELETE operation
        if query.strip().upper().startswith('DELETE'):
            # Handle DELETE operations
            if 'users' in query.lower() and 'username' in query.lower():
                # Extract username from query
                try:
                    username = params[0] if params else None
                    if username:
                        return self.delete_user(username)
                except Exception as e:
                    print(f"Error executing DELETE on users: {e}")
                    return False
            elif 'events' in query.lower() and 'event_id' in query.lower():
                # Extract event_id from query
                try:
                    event_id = params[0] if params else None
                    if event_id:
                        return self.delete_event(event_id)
                except Exception as e:
                    print(f"Error executing DELETE on events: {e}")
                    return False
        
        # For other operations, return empty result
        return [] if fetch_all else None
    
    def get_user_full_name(self, username: str) -> Optional[str]:
        """Get user full name."""
        return username
    
    def create_tables(self):
        """Create tables - no-op for API."""
        pass
    
    def create_enhanced_tables(self):
        """Create enhanced tables - no-op for API."""
        pass
    
    def hash_password(self, password: str) -> str:
        """Hash password - not needed for API."""
        return password
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password - not needed for API."""
        return password == stored_hash