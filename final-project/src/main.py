import flet as ft
from datetime import datetime
import time
import sqlite3
import random
from typing import Optional, Dict, List
import cv2
from pyzbar import pyzbar
import threading
import base64
import numpy as np

# --- CONSTANTS ---
EMPLOYEES = {
    "E101": "Alice Smith",
    "E102": "Bob Johnson",
    "E103": "Charlie Brown",
    "E104": "Diana Prince",
    "E105": "Ethan Hunt",
    "E106": "Fiona Gallagher",
    "S999": "System Test Key"
}

# --- DATABASE CLASS ---
class Database:
    """Handles all SQLite interactions for events and attendance."""
    
    def __init__(self, db_name: str = "moscan_attendance.db"):
        self.db_name = db_name
        self.create_tables()

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
            created_at TEXT NOT NULL
        )
        """
        
        self._execute(event_table_sql)
        self._execute(attendance_table_sql)
        self._execute(users_table_sql)
        
        # Create default admin user if no users exist
        check_users = "SELECT COUNT(*) FROM users"
        result = self._execute(check_users, fetch_one=True)
        if result and result[0] == 0:
            # Create default admin account (username: admin, password: admin123)
            default_user = """
            INSERT INTO users (username, password, full_name, created_at) 
            VALUES (?, ?, ?, ?)
            """
            self._execute(default_user, ('admin', 'admin123', 'Administrator', datetime.now().isoformat()))

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
        # First delete all attendance records for this event
        attendance_query = "DELETE FROM attendance WHERE event_id = ?"
        self._execute(attendance_query, (event_id,))
        
        # Then delete the event itself
        event_query = "DELETE FROM events WHERE id = ?"
        result = self._execute(event_query, (event_id,))
        return result is not None

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate a user and return their full name if successful."""
        query = "SELECT full_name FROM users WHERE username = ? AND password = ?"
        result = self._execute(query, (username, password), fetch_one=True)
        return result[0] if result else None
    
    def create_user(self, username: str, password: str, full_name: str) -> bool:
        """Create a new user account."""
        query = "INSERT INTO users (username, password, full_name, created_at) VALUES (?, ?, ?, ?)"
        try:
            self._execute(query, (username, password, full_name, datetime.now().isoformat()))
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists

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


# --- QR CAMERA SCANNER CLASS ---
class QRCameraScanner:
    """Handle camera operations and QR code detection using OpenCV."""
    
    def __init__(self, on_qr_detected, on_frame_update):
        self.on_qr_detected = on_qr_detected
        self.on_frame_update = on_frame_update
        self.camera = None
        self.is_running = False
        self.thread = None
        self.last_scanned = None
        self.scan_cooldown = 2  # seconds between same QR scans
        self.current_frame_base64 = None
        
    def start(self):
        """Start the camera and QR detection."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._scan_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop the camera and QR detection."""
        self.is_running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        if self.thread:
            self.thread.join(timeout=1)
    
    def _scan_loop(self):
        """Main scanning loop running in separate thread."""
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            print("Error: Could not open camera")
            self.is_running = False
            return
        
        # Set camera properties for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        while self.is_running:
            ret, frame = self.camera.read()
            
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Decode QR codes in the frame
            decoded_objects = pyzbar.decode(frame)
            
            # Draw rectangles around detected QR codes
            for obj in decoded_objects:
                points = obj.polygon
                if len(points) == 4:
                    pts = [(point.x, point.y) for point in points]
                    pts = [pts[i] for i in range(4)]
                    cv2.polylines(frame, [np.array(pts, dtype=np.int32)], True, (0, 255, 0), 3)
                
                qr_data = obj.data.decode('utf-8')
                current_time = time.time()
                
                # Check cooldown to avoid duplicate scans
                if (self.last_scanned is None or 
                    self.last_scanned[0] != qr_data or 
                    current_time - self.last_scanned[1] > self.scan_cooldown):
                    
                    self.last_scanned = (qr_data, current_time)
                    
                    # Callback to main app
                    if self.on_qr_detected:
                        self.on_qr_detected(qr_data)
            
            # Convert frame to base64 for display
            _, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            self.current_frame_base64 = jpg_as_text
            
            # Update UI with new frame
            if self.on_frame_update:
                self.on_frame_update(jpg_as_text)
            
            # Small delay to reduce CPU usage
            time.sleep(0.05)  # ~20 FPS
        
        if self.camera:
            self.camera.release()


# --- MAIN APP CLASS ---
class MoScanApp:
    """Main application class for MoScan Attendance."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database()
        self.current_user = None
        self.drawer = None
        self.qr_scanner = None
        
        # Configure page
        self.page.title = "MoScan Attendance"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.window.width = 500
        self.page.window.height = 800
        
        # Setup routing
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        
        # Initialize
        self.page.go("/")

    def route_change(self, e):
        """Handle route changes."""
        # Stop camera when leaving scan view
        if self.qr_scanner and self.qr_scanner.is_running:
            self.qr_scanner.stop()
        
        self.page.views.clear()

        route = self.page.route
        
        if route == "/":
            self.page.views.append(self.login_view())
        elif route == "/home":
            if not self.current_user:
                self.page.go("/")
                return
            self.page.views.append(self.home_view())
        elif route == "/create_event":
            if not self.current_user:
                self.page.go("/")
                return
            self.page.views.append(self.create_event_view())
        elif route.startswith("/event/"):
            if not self.current_user:
                self.page.go("/")
                return
            event_id = route.split("/")[-1]
            self.page.views.append(self.event_detail_view(event_id))
        elif route.startswith("/scan/"):
            if not self.current_user:
                self.page.go("/")
                return
            event_id = route.split("/")[-1]
            self.page.views.append(self.scan_view(event_id))
            
        self.page.update()

    def view_pop(self, e):
        """Handle back button."""
        if len(self.page.views) > 1:
            self.page.views.pop()
            top_view = self.page.views[-1]
            self.page.go(top_view.route)

    def create_app_bar(self, title: str, show_back: bool = False):
        """Create standardized app bar."""
        def open_drawer(e):
            self.open_end_drawer()
        
        return ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: self.page.go("/home")
            ) if show_back else None,
            title=ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    on_click=open_drawer
                )
            ] if self.current_user else [],
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
        )

    def create_drawer(self):
        """Create navigation drawer using BottomSheet as alternative."""
        return ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_700),
                            title=ft.Text(
                                f"Welcome, {self.current_user or 'User'}!",
                                weight=ft.FontWeight.BOLD,
                                size=16
                            ),
                        ),
                        ft.Divider(height=1),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.HOME),
                            title=ft.Text("Home"),
                            on_click=lambda e: self.navigate_home()
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.RED),
                            title=ft.Text("Logout", color=ft.Colors.RED),
                            on_click=lambda e: self.logout_handler()
                        ),
                    ],
                    tight=True,
                ),
                padding=20,
            ),
            open=False,
        )
    
    def open_end_drawer(self):
        """Open the navigation drawer."""
        if self.drawer is None:
            self.drawer = self.create_drawer()
            self.page.overlay.append(self.drawer)
            self.page.update()
        self.drawer.open = True
        self.drawer.update()
    
    def navigate_home(self):
        """Navigate to home and close drawer."""
        if self.drawer:
            try:
                self.drawer.open = False
                self.drawer.update()
            except:
                pass
        self.page.go("/home")
    
    def logout_handler(self):
        """Handle logout and close drawer."""
        # First close the drawer
        if self.drawer:
            try:
                self.drawer.open = False
                self.page.update()
            except:
                pass
        
        # Small delay to allow drawer to close
        time.sleep(0.1)
        
        # Then logout
        self.logout()

    def logout(self):
        """Handle logout."""
        # Stop camera if running
        if self.qr_scanner and self.qr_scanner.is_running:
            self.qr_scanner.stop()
        
        # Clear user and drawer
        self.current_user = None
        if self.drawer:
            try:
                if self.drawer in self.page.overlay:
                    self.page.overlay.remove(self.drawer)
            except:
                pass
        self.drawer = None
        
        # Navigate to login
        self.page.go("/")

    def show_snackbar(self, message: str, color: str = ft.Colors.BLUE):
        """Show snackbar message."""
        snackbar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
        )
        self.page.open(snackbar)

    # --- VIEWS ---
    
    def login_view(self):
        """Login screen."""
        username = ft.TextField(
            label="Username",
            width=300,
            prefix_icon=ft.Icons.PERSON
        )
        password = ft.TextField(
            label="Password",
            width=300,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK
        )
        
        error_text = ft.Text(
            "",
            color=ft.Colors.RED,
            size=12,
            visible=False
        )
        
        def authenticate(e):
            # Clear previous error
            error_text.visible = False
            error_text.update()
            
            # Validate inputs
            if not username.value or not password.value:
                error_text.value = "Please enter both username and password"
                error_text.visible = True
                error_text.update()
                return
            
            # Authenticate against database
            user_name = self.db.authenticate_user(username.value.strip(), password.value)
            
            if user_name:
                self.current_user = user_name
                self.show_snackbar(f"Welcome, {user_name}!", ft.Colors.GREEN)
                self.page.go("/home")
            else:
                error_text.value = "Invalid username or password"
                error_text.visible = True
                error_text.update()
                password.value = ""
                password.update()
        
        # Allow Enter key to submit
        username.on_submit = authenticate
        password.on_submit = authenticate
        
        return ft.View(
            "/",
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.QR_CODE_SCANNER,
                                size=80,
                                color=ft.Colors.BLUE_700
                            ),
                            ft.Text(
                                "MoScan",
                                size=40,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700
                            ),
                            ft.Text(
                                "Attendance Management System",
                                size=16,
                                color=ft.Colors.GREY_700
                            ),
                            ft.Container(height=40),
                            username,
                            password,
                            error_text,
                            ft.Container(height=10),
                            ft.ElevatedButton(
                                "LOGIN",
                                width=300,
                                height=50,
                                on_click=authenticate,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.BLUE_700,
                                    color=ft.Colors.WHITE,
                                )
                            ),
                            ft.Container(height=20),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "Default Login:",
                                            size=12,
                                            color=ft.Colors.GREY_600,
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        ft.Text(
                                            "Username: admin",
                                            size=11,
                                            color=ft.Colors.GREY_500
                                        ),
                                        ft.Text(
                                            "Password: admin123",
                                            size=11,
                                            color=ft.Colors.GREY_500
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2
                                ),
                                padding=10,
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                border_radius=5,
                                bgcolor=ft.Colors.GREY_50
                            ),
                            ft.Container(height=10),
                            ft.Text(
                                "where showing up is mandatory. bro.",
                                size=12,
                                color=ft.Colors.GREY_500,
                                italic=True
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ],
            bgcolor=ft.Colors.WHITE
        )

    def home_view(self):
        """Home screen with event list."""
        events = self.db.get_all_events()
        
        def delete_event_handler(event_id: str, event_name: str):
            """Handle event deletion with confirmation."""
            def confirm_delete(e):
                self.db.delete_event(event_id)
                self.show_snackbar(f"Event '{event_name}' deleted", ft.Colors.GREEN)
                self.page.close(dialog)
                self.page.go("/home")  # Refresh the view
            
            def cancel_delete(e):
                self.page.close(dialog)
            
            dialog = ft.AlertDialog(
                title=ft.Text("Delete Event"),
                content=ft.Text(f"Are you sure you want to delete '{event_name}'? This will also delete all attendance records."),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel_delete),
                    ft.TextButton(
                        "Delete",
                        on_click=confirm_delete,
                        style=ft.ButtonStyle(color=ft.Colors.RED)
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.open(dialog)
        
        def create_event_card(event_id: str, event_data: dict):
            return ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.EVENT, color=ft.Colors.BLUE_700),
                                title=ft.Text(
                                    event_data['name'],
                                    weight=ft.FontWeight.BOLD,
                                    size=16
                                ),
                                subtitle=ft.Text(event_data['date']),
                                trailing=ft.PopupMenuButton(
                                    items=[
                                        ft.PopupMenuItem(
                                            text="View Attendance",
                                            icon=ft.Icons.LIST,
                                            on_click=lambda e, eid=event_id: self.page.go(f"/event/{eid}")
                                        ),
                                        ft.PopupMenuItem(
                                            text="Start Scanning",
                                            icon=ft.Icons.QR_CODE_SCANNER,
                                            on_click=lambda e, eid=event_id: self.page.go(f"/scan/{eid}")
                                        ),
                                        ft.PopupMenuItem(),  # Divider
                                        ft.PopupMenuItem(
                                            text="Delete Event",
                                            icon=ft.Icons.DELETE,
                                            on_click=lambda e, eid=event_id, name=event_data['name']: delete_event_handler(eid, name)
                                        ),
                                    ]
                                )
                            ),
                            ft.Container(
                                content=ft.Text(
                                    event_data['desc'],
                                    size=12,
                                    color=ft.Colors.GREY_700
                                ),
                                padding=ft.padding.only(left=16, right=16, bottom=10)
                            )
                        ]
                    ),
                    padding=0
                )
            )
        
        event_list = ft.ListView(
            controls=[create_event_card(eid, data) for eid, data in events.items()],
            spacing=10,
            padding=20,
            expand=True
        ) if events else ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.EVENT_BUSY, size=80, color=ft.Colors.GREY_400),
                    ft.Text("No events yet", size=20, color=ft.Colors.GREY_600),
                    ft.Text("Create your first event", size=14, color=ft.Colors.GREY_500)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            alignment=ft.alignment.center,
            expand=True
        )
        
        return ft.View(
            "/home",
            [
                self.create_app_bar("MoScan"),
                event_list,
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    on_click=lambda e: self.page.go("/create_event"),
                    bgcolor=ft.Colors.BLUE_700,
                )
            ]
        )

    def create_event_view(self):
        """Create new event screen."""
        name_field = ft.TextField(
            label="Event Name",
            hint_text="Enter event name",
            prefix_icon=ft.Icons.EVENT
        )
        date_field = ft.TextField(
            label="Date",
            hint_text="e.g., Dec 15, 2024",
            prefix_icon=ft.Icons.CALENDAR_TODAY
        )
        desc_field = ft.TextField(
            label="Description",
            hint_text="Optional description",
            multiline=True,
            min_lines=3,
            max_lines=5
        )
        
        def save_event(e):
            if name_field.value and date_field.value:
                self.db.create_event(
                    name_field.value,
                    date_field.value,
                    desc_field.value or "No description"
                )
                self.show_snackbar("Event created successfully!", ft.Colors.GREEN)
                self.page.go("/home")
            else:
                self.show_snackbar("Name and date are required", ft.Colors.RED)
        
        return ft.View(
            "/create_event",
            [
                self.create_app_bar("Create Event", show_back=True),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "New Event",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700
                            ),
                            ft.Container(height=20),
                            name_field,
                            date_field,
                            desc_field,
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "CREATE EVENT",
                                width=300,
                                height=50,
                                on_click=save_event,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.BLUE_700,
                                    color=ft.Colors.WHITE
                                )
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=15
                    ),
                    padding=20,
                    expand=True
                )
            ]
        )

    def scan_view(self, event_id: str):
        """QR scanning screen with OpenCV camera support."""
        event = self.db.get_event_by_id(event_id)
        if not event:
            self.page.go("/home")
            return
        
        scan_log = ft.ListView(spacing=5, padding=10)
        
        # Load recent scans
        attendance = self.db.get_attendance_by_event(event_id)
        for user_id, record in list(attendance.items())[:10]:
            scan_log.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                    title=ft.Text(record['name']),
                    subtitle=ft.Text(record['time']),
                    dense=True
                )
            )
        
        # Camera and input controls
        qr_input = ft.TextField(
            label="Enter ID manually",
            hint_text="e.g., E101",
            prefix_icon=ft.Icons.QR_CODE,
            autofocus=True,
            expand=True
        )
        
        camera_status = ft.Text(
            "Camera: Ready",
            size=12,
            color=ft.Colors.GREY_600,
            weight=ft.FontWeight.BOLD
        )
        
        # Camera preview image
        camera_image = ft.Image(
            src_base64="",
            width=640,
            height=480,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            error_content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.CAMERA_ALT, size=50, color=ft.Colors.GREY_400),
                        ft.Text("Loading camera...", size=12, color=ft.Colors.GREY_600)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                bgcolor=ft.Colors.GREY_200,
                width=640,
                height=480,
                alignment=ft.alignment.center
            )
        )
        
        camera_icon = ft.Container(
            content=ft.Icon(
                ft.Icons.QR_CODE_SCANNER,
                size=100,
                color=ft.Colors.BLUE_700,
            ),
            alignment=ft.alignment.center,
        )
        
        # Stack to show either icon or camera feed
        camera_stack = ft.Stack(
            [
                camera_icon,
                camera_image,
            ]
        )
        
        camera_container = ft.Container(
            content=camera_stack,
            height=300,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            border=ft.border.all(2, ft.Colors.BLUE_200),
            alignment=ft.alignment.center
        )
        
        camera_active = [False]
        
        def update_camera_frame(frame_base64: str):
            """Update the camera preview with new frame."""
            if not camera_active[0]:
                return
            
            try:
                if frame_base64 and len(frame_base64) > 0:
                    camera_image.src_base64 = frame_base64
                    camera_image.visible = True
                    camera_icon.visible = False
                    camera_image.update()
                    camera_icon.update()
            except Exception as e:
                print(f"Error updating frame: {e}")
        
        def process_scan(user_id: str):
            """Process a scanned or entered ID."""
            user_id = user_id.strip().upper()
            
            if not user_id:
                return
            
            if user_id not in EMPLOYEES:
                self.show_snackbar(f"Unknown ID: {user_id}", ft.Colors.RED)
                return
            
            user_name = EMPLOYEES[user_id]
            existing = self.db.is_user_checked_in(event_id, user_id)
            
            if existing:
                self.show_snackbar(f"{user_name} already checked in at {existing}", ft.Colors.ORANGE)
                return
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.db.record_attendance(event_id, user_id, user_name, timestamp)
            
            # Update UI
            scan_log.controls.insert(0, ft.ListTile(
                leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                title=ft.Text(user_name),
                subtitle=ft.Text(timestamp),
                dense=True
            ))
            
            try:
                scan_log.update()
            except:
                pass
            
            self.show_snackbar(f"✓ {user_name} checked in!", ft.Colors.GREEN)
        
        def on_qr_detected(qr_data: str):
            """Callback when QR code is detected by camera."""
            process_scan(qr_data)
        
        def handle_manual_scan(e):
            """Handle manual ID entry."""
            user_id = qr_input.value
            qr_input.value = ""
            qr_input.update()
            process_scan(user_id)
        
        def toggle_camera(e):
            """Toggle camera on/off."""
            camera_active[0] = not camera_active[0]
            
            if camera_active[0]:
                # Start camera
                camera_btn.icon = ft.Icons.STOP_CIRCLE
                camera_btn.bgcolor = ft.Colors.RED_700
                camera_btn.tooltip = "Stop Camera"
                camera_status.value = "Camera: Starting..."
                camera_status.color = ft.Colors.ORANGE_700
                camera_container.bgcolor = ft.Colors.BLACK
                camera_container.border = ft.border.all(2, ft.Colors.GREEN_400)
                
                # Keep icon visible until first frame arrives
                camera_image.visible = False
                camera_icon.visible = True
                camera_icon.content.color = ft.Colors.ORANGE_700
                
                camera_btn.update()
                camera_status.update()
                camera_container.update()
                camera_icon.update()
                
                # Initialize and start scanner (this will update frames)
                self.qr_scanner = QRCameraScanner(on_qr_detected, update_camera_frame)
                self.qr_scanner.start()
                
                # Update status after a moment
                def update_status():
                    time.sleep(0.5)
                    if camera_active[0]:
                        try:
                            camera_status.value = "Camera: Scanning..."
                            camera_status.color = ft.Colors.GREEN_700
                            camera_status.update()
                        except:
                            pass
                
                threading.Thread(target=update_status, daemon=True).start()
                
            else:
                # Stop camera
                camera_btn.icon = ft.Icons.VIDEOCAM
                camera_btn.bgcolor = ft.Colors.BLUE_700
                camera_btn.tooltip = "Start Camera"
                camera_status.value = "Camera: Stopped"
                camera_status.color = ft.Colors.GREY_600
                camera_container.bgcolor = ft.Colors.BLUE_50
                camera_container.border = ft.border.all(2, ft.Colors.BLUE_200)
                
                # Show icon, hide camera feed
                camera_image.visible = False
                camera_icon.visible = True
                camera_icon.content.color = ft.Colors.BLUE_700
                
                if self.qr_scanner:
                    self.qr_scanner.stop()
            
                camera_btn.update()
                camera_status.update()
                camera_container.update()
                camera_icon.update()
                camera_image.update()
        
        qr_input.on_submit = handle_manual_scan
        
        camera_btn = ft.IconButton(
            icon=ft.Icons.VIDEOCAM,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
            tooltip="Start Camera",
            on_click=toggle_camera
        )
        
        return ft.View(
            f"/scan/{event_id}",
            [
                self.create_app_bar(event['name'], show_back=True),
                ft.Column(
                    controls=[
                        camera_container,
                        camera_status,
                        ft.Row(
                            [
                                qr_input,
                                camera_btn,
                                ft.IconButton(
                                    icon=ft.Icons.SEND,
                                    icon_color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.BLUE_700,
                                    on_click=handle_manual_scan
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Divider(),
                        ft.Text("Recent Activity", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=scan_log,
                            height=200,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=10
                        )
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                )
            ],
            padding=20
        )

    def event_detail_view(self, event_id: str):
        """Event detail with attendance log."""
        event = self.db.get_event_by_id(event_id)
        if not event:
            self.page.go("/home")
            return
        
        attendance = self.db.get_attendance_by_event(event_id)
        
        attendance_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Time", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(record['name'])),
                        ft.DataCell(ft.Text(user_id)),
                        ft.DataCell(ft.Text(record['time'])),
                        ft.DataCell(ft.Text(record['status'], color=ft.Colors.GREEN)),
                    ]
                ) for user_id, record in attendance.items()
            ] if attendance else [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("No attendance records yet", italic=True)),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            ]
        )
        
        def export_data(e):
            self.show_snackbar(f"Exporting {len(attendance)} records...", ft.Colors.BLUE)
        
        return ft.View(
            f"/event/{event_id}",
            [
                self.create_app_bar(event['name'], show_back=True),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                event['name'],
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700
                            ),
                            ft.Text(event['date'], size=16, color=ft.Colors.GREY_700),
                            ft.Divider(),
                            ft.Text(
                                f"Total Attendees: {len(attendance)}",
                                size=18,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [attendance_table],
                                    scroll=ft.ScrollMode.AUTO
                                ),
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                border_radius=10,
                                padding=10,
                                expand=True
                            ),
                            ft.ElevatedButton(
                                "Export to CSV",
                                icon=ft.Icons.DOWNLOAD,
                                on_click=export_data,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.BLUE_700,
                                    color=ft.Colors.WHITE
                                )
                            )
                        ],
                        spacing=15
                    ),
                    padding=20,
                    expand=True
                )
            ]
        )


# --- MAIN ---
def main(page: ft.Page):
    app = MoScanApp(page)

if __name__ == "__main__":
    ft.app(target=main, port=8000, host="0.0.0.0")