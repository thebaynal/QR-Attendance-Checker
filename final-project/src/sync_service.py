# sync_service.py
"""Background sync service for real-time updates across devices."""

import threading
import time
from typing import Callable, List

class SyncService:
    """Manages background polling for real-time data synchronization."""
    
    def __init__(self, db, poll_interval: float = 2.0):
        """Initialize sync service.
        
        Args:
            db: Database instance (local or API)
            poll_interval: Time in seconds between polls (default 2 seconds)
        """
        self.db = db
        self.poll_interval = poll_interval
        self.running = False
        self.sync_thread = None
        self.callbacks: List[Callable] = []
        
        # Track last known state to detect changes
        self._last_events_hash = None
        self._last_attendance_hash = None
        self._last_scans_hash = None
        self._last_students_hash = None
    
    def register_callback(self, callback: Callable):
        """Register a callback function to be called when data changes.
        
        Args:
            callback: Function to call when data changes
        """
        self.callbacks.append(callback)
    
    def start(self):
        """Start the background sync service."""
        if self.running:
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        print("Sync service started")
    
    def stop(self):
        """Stop the background sync service."""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        print("Sync service stopped")
    
    def _sync_loop(self):
        """Main sync loop running in background thread."""
        while self.running:
            try:
                self._check_for_changes()
                time.sleep(self.poll_interval)
            except Exception as e:
                print(f"Sync error: {e}")
                time.sleep(self.poll_interval)
    
    def _check_for_changes(self):
        """Check if any data has changed and trigger callbacks if needed."""
        try:
            # Check recent scans (most important for real-time attendance)
            recent_scans = self.db.get_recent_scans(limit=50)
            scans_hash = hash(str(recent_scans))
            
            if self._last_scans_hash != scans_hash:
                self._last_scans_hash = scans_hash
                self._trigger_callbacks({'type': 'scans_updated', 'data': recent_scans})
            
            # Check events
            events = self.db.get_all_events()
            events_hash = hash(str(events))
            
            if self._last_events_hash != events_hash:
                self._last_events_hash = events_hash
                self._trigger_callbacks({'type': 'events_updated', 'data': events})
            
            # Check recent logins
            recent_logins = self.db.get_recent_logins(limit=20)
            logins_hash = hash(str(recent_logins))
            
            if self._last_attendance_hash != logins_hash:
                self._last_attendance_hash = logins_hash
                self._trigger_callbacks({'type': 'logins_updated', 'data': recent_logins})
        
        except Exception as e:
            print(f"Error checking for changes: {e}")
    
    def _trigger_callbacks(self, change_data: dict):
        """Trigger all registered callbacks with change data."""
        for callback in self.callbacks:
            try:
                callback(change_data)
            except Exception as e:
                print(f"Callback error: {e}")
