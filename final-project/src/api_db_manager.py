# api_db_manager.py
"""Database manager that connects to remote API instead of local SQLite."""

import requests
import json
from typing import Optional, Dict

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
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user via API."""
        data = {"username": username, "password": password}
        # Login endpoint doesn't require API key
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
        """Get user role - assume admin for API access."""
        # For simplicity, users with API access are considered admin
        return 'admin'
    
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
    
    def record_attendance(self, event_id: str, user_id: str, user_name: str, 
                         timestamp: str, status: str = "Checked In"):
        """Record attendance via API."""
        data = {
            "event_id": event_id,
            "scanned_user_id": user_id,
            "scanned_user_name": user_name,
            "scanner_username": "api_user"  # You'll need to pass actual scanner
        }
        return self._make_request('POST', '/api/record-scan', data)
    
    def get_attendance_by_event(self, event_id: str) -> Dict:
        """Get attendance for event via API."""
        result = self._make_request('GET', f'/api/attendance/{event_id}')
        return result if result else {}
    
    def record_login(self, username: str):
        """Record login - handled by API."""
        pass
    
    def record_logout(self, username: str):
        """Record logout via API."""
        data = {"username": username}
        return self._make_request('POST', '/api/logout', data)
    
    # Add other methods as needed to match the original Database class interface
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
    
    def get_recent_scans(self, limit: int = 10):
        """Get recent scans via API."""
        return self._make_request('GET', f'/api/recent-scans?limit={limit}')
    
    def get_recent_logins(self, limit: int = 10):
        """Get recent logins via API."""
        return self._make_request('GET', f'/api/recent-logins?limit={limit}')