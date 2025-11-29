import flet as ft
from datetime import datetime
import time
import sqlite3
import random # Used for simple mock event ID generation

# --- GLOBAL MOCK DATA (Only for Employee IDs) ---

# Employee database (user ID is the QR content)
USERS = {
    "E101": "Alice Smith",
    "E102": "Bob Johnson",
    "E103": "Charlie Brown",
    "E104": "Diana Prince",
    "E105": "Ethan Hunt",
    "E106": "Fiona Gallagher",
    "S999": "System Test Key"
    
}

CURRENT_USER_NAME = None # Tracks the currently logged-in user
CURRENT_EVENT_ID = None # Tracks the event ID being scanned or viewed

# --- DATABASE CLASS (SQLite Persistence) ---

class Database:
    """Handles all SQLite interactions for events and attendance."""
    def __init__(self, db_name="moscan_attendance.db"):
        self.db_name = db_name
        self.conn = None
        self.create_tables()

    def _execute(self, query, params=(), commit=True, fetch_all=False, fetch_one=False):
        """Internal helper for executing SQL commands."""
        result = None
        try:
            self.conn = sqlite3.connect(self.db_name)
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            
            if commit:
                self.conn.commit()
                
            return result
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if self.conn:
                self.conn.close()

    def create_tables(self):
        """Creates the necessary tables if they don't exist."""
        print(f"Attempting to connect to database: {self.db_name}")
        
        # Events table
        event_table_sql = """
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT
        )
        """
        
        # Attendance log table
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
        self._execute(event_table_sql, commit=True)
        self._execute(attendance_table_sql, commit=True)
        print("Database tables ensured.")


    # --- EVENT METHODS ---

    def get_all_events(self):
        """Fetches all events."""
        query = "SELECT id, name, date, description FROM events ORDER BY date DESC"
        results = self._execute(query, fetch_all=True)
        
        events = {}
        if results:
            for row in results:
                event_id, name, date, description = row
                events[event_id] = {
                    "name": name, 
                    "date": date, 
                    "desc": description
                }
        return events

    def get_event_by_id(self, event_id):
        """Fetches a single event by ID."""
        query = "SELECT id, name, date, description FROM events WHERE id = ?"
        row = self._execute(query, (event_id,), fetch_one=True)
        if row:
            event_id, name, date, description = row
            return {
                "id": event_id,
                "name": name,
                "date": date,
                "desc": description
            }
        return None

    def create_event(self, name, date, description):
        """Inserts a new event into the database."""
        # Simple ID generation
        new_id = f"EID{int(time.time())}{random.randint(10, 99)}"
        query = "INSERT INTO events (id, name, date, description) VALUES (?, ?, ?, ?)"
        self._execute(query, (new_id, name, date, description))
        return new_id

    # --- ATTENDANCE METHODS ---

    def record_attendance(self, event_id, user_id, user_name, timestamp, status="Checked In"):
        """Records a new attendance entry."""
        query = """
        INSERT INTO attendance (event_id, user_id, user_name, timestamp, status) 
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            self._execute(query, (event_id, user_id, user_name, timestamp, status))
        except sqlite3.IntegrityError:
            # This handles the case where the user tries to check in twice (PRIMARY KEY violation)
            pass

    def is_user_checked_in(self, event_id, user_id):
        """Checks if a user has already checked in for a specific event."""
        query = "SELECT timestamp FROM attendance WHERE event_id = ? AND user_id = ?"
        result = self._execute(query, (event_id, user_id), fetch_one=True)
        return result[0] if result else None

    def get_attendance_by_event(self, event_id):
        """Fetches all attendance records for a given event."""
        query = "SELECT user_id, user_name, timestamp, status FROM attendance WHERE event_id = ? ORDER BY timestamp DESC"
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

# --- UI COMPONENTS (Shared/Helper) ---

def create_app_bar(page: ft.Page, title: str, show_back_button: bool = False):
    """Creates a standardized AppBar."""
    
    # Refactored: Use a proper function to open the drawer safely
    def open_menu(e):
        if page.drawer:
            page.drawer.open = True
            page.update()
        else:
            print("Debug: Cannot open menu. page.drawer is not initialized.")

    actions = [
        ft.IconButton(
            ft.icons.MENU,
            tooltip="Open Menu",
            # Updated to use the safe, dedicated handler
            on_click=open_menu
        )
    ]
    
    if page.route == "/home":
        title_widget = ft.Row([
            ft.Text("MoScan", size=20, weight=ft.FontWeight.BOLD),
        ])
    else:
        title_widget = ft.Text(title, size=20, weight=ft.FontWeight.BOLD)

    return ft.AppBar(
        leading=ft.Container(
            content=ft.IconButton(
                icon=ft.icons.ARROW_BACK,
                on_click=lambda e: page.go("/home")
            ) if show_back_button else None
        ),
        title=title_widget,
        actions=actions,
        bgcolor=ft.colors.WHITE,
        elevation=1,
    )

# --- UTILITY FUNCTIONS ---

def update_status(page: ft.Page, message: str, color: str = ft.colors.BLUE_900):
    """Updates the status text on the page."""
    # Find the status_text control in the current view's content
    status_text = getattr(page.views[-1].controls[-1], 'status_text', None)
    
    if status_text:
        status_text.value = message
        status_text.color = color
        status_text.size = 18
        page.update()
        
        def reset_size():
            time.sleep(1.5)
            status_text.size = 16
            page.update()
        page.run_thread(reset_size)
    else:
        print(f"Status update: {message}") # Fallback print if control isn't found

# --- ATTENDANCE LOGIC (Now using DB) ---

def record_attendance(page: ft.Page, db: Database, user_id: str, event_id: str, qr_input: ft.TextField, log_column: ft.Column):
    """Handles the core logic for recording attendance using the database."""
    
    # 1. Input Validation
    user_id = user_id.strip().upper()
    qr_input.value = "" # Clear input immediately

    if not user_id:
        update_status(page, "Error: Input is empty. Please scan/enter a QR code.", ft.colors.RED_600)
        page.update()
        return

    # 2. Check if the ID is a known user
    if user_id not in USERS:
        update_status(page, f"Error: Unknown ID '{user_id}'. Access denied.", ft.colors.RED_600)
        qr_input.disabled = True
        page.update()
        page.run_thread(lambda: (time.sleep(1), setattr(qr_input, 'disabled', False), page.update()))
        return

    user_name = USERS[user_id]
    
    # 3. Check if the user has already checked in (DB Check)
    last_check_in_time = db.is_user_checked_in(event_id, user_id)
    if last_check_in_time:
        update_status(page, f"Warning: {user_name} already checked in at {last_check_in_time}.", ft.colors.ORANGE_700)
        page.update()
        return

    # 4. Successful Check-in (DB Insert)
    current_time = datetime.now().strftime("%H:%M:%S")
    db.record_attendance(event_id, user_id, user_name, current_time, status="Checked In")
    
    # Update UI Log
    add_to_scan_log(user_id, user_name, current_time, log_column)
    
    # Update Status
    update_status(page, f"SUCCESS! {user_name} checked in at {current_time}.", ft.colors.GREEN_700)

    page.update()

def add_to_scan_log(user_id: str, name: str, timestamp: str, log_column: ft.Column):
    """Adds a new attendance record to the small log visible on the QR Scan screen."""
    # Remove the placeholder if it exists
    if log_column.controls and log_column.controls[0].content and hasattr(log_column.controls[0].content, 'value') and log_column.controls[0].content.value == "Latest scans will appear here...":
         log_column.controls.pop(0)

    log_column.controls.insert(
        0, # Insert at the top
        ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN_700, size=20),
                    ft.Text(f"{name}", weight=ft.FontWeight.BOLD, size=14),
                    ft.Text(f"({timestamp})", size=12, color=ft.colors.BLACK54),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10
            ),
            padding=5,
            border_radius=ft.border_radius.all(4),
            bgcolor=ft.colors.WHITE
        )
    )
    # Ensure the log doesn't grow too large on the screen
    if len(log_column.controls) > 10:
        log_column.controls.pop()

    log_column.update()

# --- VIEWS (SCREENS) ---

def CreateEventView(page: ft.Page, db: Database):
    """View for creating a new event."""
    
    status_text = ft.Text("", height=20) # Define status text control here

    def save_event(e):
        name = event_name_input.value.strip()
        date = event_date_input.value.strip()
        desc = event_desc_input.value.strip()
        
        if name and date:
            db.create_event(name, date, desc if desc else "No description provided.")
            page.go("/home")
        else:
            status_text.value = "Event Name and Date are required."
            status_text.color = ft.colors.RED_600
            page.update()

    event_name_input = ft.TextField(label="Event Name (Required)", width=400)
    event_date_input = ft.TextField(label="Date (e.g., Nov 20, 2025) (Required)", width=400)
    event_desc_input = ft.TextField(label="Description", multiline=True, min_lines=2, max_lines=4, width=400)
    
    view_content = ft.Container(
        content=ft.Column(
            [
                ft.Text("Define New Event Details", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                event_name_input,
                event_date_input,
                event_desc_input,
                status_text,
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text("SAVE EVENT", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.colors.GREEN_700,
                    color=ft.colors.WHITE,
                    on_click=save_event,
                    width=300,
                    height=50,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        ),
        padding=20,
        expand=True
    )
    
    setattr(view_content, 'status_text', status_text)
    
    return ft.View(
        "/create_event",
        [
            create_app_bar(page, "Create New Event", show_back_button=True),
            view_content,
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        bgcolor=ft.colors.BLUE_GREY_50
    )


def LoginView(page: ft.Page, open_logout_dialog):
    """Initial Login Screen."""
    
    def authenticate(e):
        global CURRENT_USER_NAME
        # Simplified: Just check if the field is not empty
        if username_input.value and password_input.value:
            CURRENT_USER_NAME = "Admin User"
            # Ensure the drawer is created immediately upon successful login
            page.drawer = create_drawer(page, open_logout_dialog) 
            page.go("/home")
        else:
            login_status.value = "Please enter mock credentials (e.g., any value in both fields)."
            page.update()
            
    username_input = ft.TextField(label="Username", width=300)
    password_input = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
    login_status = ft.Text("")
    
    view_content = ft.Container(
        content=ft.Column(
            [
                ft.Text("Welcome to MoScan", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
                ft.Text("Sign in to continue", size=18, color=ft.colors.BLACK54),
                ft.Divider(height=40, color=ft.colors.TRANSPARENT),
                username_input,
                password_input,
                login_status,
                ft.Container(
                    content=ft.Text(
                        "where showing up is mandatory. bro.",
                        size=12,
                        color=ft.colors.BLACK54,
                        text_align=ft.TextAlign.CENTER
                    ),
                    padding=ft.padding.only(top=10)
                ),
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text("LOGIN", size=18, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.colors.YELLOW_ACCENT_700,
                    color=ft.colors.BLACK,
                    on_click=authenticate,
                    width=300,
                    height=50,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),
        alignment=ft.alignment.center,
        expand=True
    )

    return ft.View(
        "/",
        [
            view_content
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        bgcolor=ft.colors.WHITE
    )

def HomeView(page: ft.Page, db: Database):
    """Home Screen with Event List (Now dynamically loaded from DB)."""
    
    events_data = db.get_all_events() # Fetch all events from DB

    def create_event_card(event_id: str, event_data: dict):
        """Generates a card for an event."""
        return ft.Card(
            elevation=2,
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(event_data['name'], size=18, weight=ft.FontWeight.W_600),
                                ft.Text(event_data['date'], size=14, color=ft.colors.BLACK54),
                                ft.Text(event_data['desc'], size=12, color=ft.colors.BLACK45, italic=True, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                            ],
                            spacing=5,
                            expand=True
                        ),
                        ft.PopupMenuButton(
                            icon=ft.icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(
                                    content=ft.Text("View Attendance Log"),
                                    on_click=lambda e: page.go(f"/event/{event_id}")
                                ),
                                ft.PopupMenuItem(
                                    content=ft.Text("Start QR Scan Session"),
                                    on_click=lambda e: page.go(f"/scan/{event_id}")
                                ),
                            ]
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=15
            ),
            width=400
        )

    event_list_controls = [
        ft.Container(
            content=ft.Row(
                [
                    ft.Text("Events", size=24, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        ft.icons.ADD_CIRCLE, 
                        icon_color=ft.colors.BLUE_700, 
                        icon_size=30, 
                        tooltip="Create New Event",
                        on_click=lambda e: page.go("/create_event")
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            width=400,
            padding=ft.padding.only(bottom=10)
        )
    ]
    
    if not events_data:
        event_list_controls.append(
             ft.Text("No events found. Click '+' to create one.", color=ft.colors.BLACK54)
        )
    else:
        for event_id, event_data in events_data.items():
            event_list_controls.append(create_event_card(event_id, event_data))
            
    # Placeholder for status messages (even if none are typically needed here)
    status_text = ft.Text("", height=20)

    view_content = ft.Container(
        content=ft.Column(
            event_list_controls + [status_text],
            scroll=ft.ScrollMode.ADAPTIVE,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            expand=True
        ),
        padding=20,
        expand=True
    )
    
    setattr(view_content, 'status_text', status_text)

    return ft.View(
        "/home",
        [
            create_app_bar(page, "Home"),
            view_content,
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

def QRScanView(page: ft.Page, db: Database, event_id: str):
    """QR Scanning Screen (Now fetching event info from DB)."""
    
    event_info = db.get_event_by_id(event_id)
    if not event_info:
        page.go("/home")
        return
    
    # Status Message Area
    status_text_control = ft.Text("Ready to scan...", color=ft.colors.BLACK54, size=16)
    
    # Small log for latest scans
    latest_scans_log = ft.Column(
        [ft.Text("Latest scans will appear here...")],
        scroll=ft.ScrollMode.ADAPTIVE,
        height=150,
        spacing=5,
        horizontal_alignment=ft.CrossAxisAlignment.START
    )

    def load_initial_log(log_column: ft.Column):
        """Loads recent scans from the DB into the log."""
        attendance = db.get_attendance_by_event(event_id)
        
        log_column.controls.clear()
        
        if attendance:
            for user_id, record in list(attendance.items())[:10]: # Show up to 10 recent scans
                # Add the controls directly to the list, do not call .update() here
                log_column.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN_700, size=20),
                                ft.Text(f"{record['name']}", weight=ft.FontWeight.BOLD, size=14),
                                ft.Text(f"({record['time']})", size=12, color=ft.colors.BLACK54),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=10
                        ),
                        padding=5,
                        border_radius=ft.border_radius.all(4),
                        bgcolor=ft.colors.WHITE
                    )
                )
        else:
            log_column.controls.append(ft.Text("Latest scans will appear here..."))
        
        # NOTE: We do NOT call log_column.update() here, as the view hasn't been added to the page yet.
        # The first render will happen when page.views.append() is called.
        
    def on_scan_submit(e):
        record_attendance(page, db, qr_input.value, event_id, qr_input, latest_scans_log)

    qr_input = ft.TextField(
        label="Scan QR Code / Enter ID",
        hint_text="e.g., E101",
        width=300,
        on_submit=on_scan_submit
    )
    
    # --- Load initial log data BEFORE the controls are put into the view ---
    load_initial_log(latest_scans_log)
    # --- The controls list is now populated and ready for the view construction ---


    view_content = ft.Container(
        content=ft.Column(
            [
                ft.Text(f"Scanning for: {event_info['name']}", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
                ft.Text(f"ID: {event_id}", size=14, color=ft.colors.BLACK54),

                # Mock QR Code Scan Area (following the wireframe)
                ft.Container(
                    content=ft.Text("Mock QR Camera Feed Area", color=ft.colors.BLACK54),
                    alignment=ft.alignment.center,
                    width=300,
                    height=200,
                    bgcolor=ft.colors.BLACK12,
                    border_radius=10,
                    margin=ft.margin.only(top=10, bottom=20)
                ),
                
                # Scan/Input Controls
                ft.Row(
                    [
                        qr_input,
                        ft.IconButton(
                            icon=ft.icons.SEND,
                            icon_color=ft.colors.BLUE_900,
                            icon_size=30,
                            tooltip="Record Attendance",
                            on_click=on_scan_submit
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
                
                # Status and Quick Log
                ft.Container(
                    content=status_text_control,
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(top=10, bottom=20)
                ),
                ft.Text("Latest Activity:", size=16, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=latest_scans_log,
                    width=400,
                    bgcolor=ft.colors.BLUE_GREY_50,
                    border_radius=10,
                    padding=10
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        ),
        padding=20,
        expand=True
    )
    
    # Attach status_text to the view_content object for the helper function
    setattr(view_content, 'status_text', status_text_control) 
    
    return ft.View(
        f"/scan/{event_id}",
        [
            create_app_bar(page, event_info['name'], show_back_button=True),
            view_content,
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

def EventDetailView(page: ft.Page, db: Database, event_id: str):
    """Event Detail View with Attendance Log (Now fetching data from DB)."""
    
    event_info = db.get_event_by_id(event_id)
    if not event_info:
        page.go("/home")
        return

    # Fetch attendance from DB
    attendance_data = db.get_attendance_by_event(event_id)
    
    # Attendance Table Setup
    attendance_rows = []
    
    # Populate rows
    if attendance_data:
        for user_id, record in attendance_data.items():
            attendance_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(record['name'])),
                        ft.DataCell(ft.Text(user_id)),
                        ft.DataCell(ft.Text(record['time'])),
                        ft.DataCell(ft.Text(record['status'], color=ft.colors.GREEN_700)),
                    ]
                )
            )
    else:
        # Placeholder row if no attendance recorded
         attendance_rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("No records yet.")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ]
            )
        )

    attendance_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Time")),
            ft.DataColumn(ft.Text("Status")),
        ],
        rows=attendance_rows,
        width=500,
    )
    
    # Status Message Area (for updates like export)
    status_text_control = ft.Text("", height=20, color=ft.colors.BLACK54, size=16)

    # Export Button (Mock)
    export_button = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(ft.icons.FILE_DOWNLOAD),
            ft.Text("Export File", weight=ft.FontWeight.BOLD)
        ]),
        bgcolor=ft.colors.BLUE_700,
        color=ft.colors.WHITE,
        on_click=lambda e: update_status(page, f"Exporting {len(attendance_data)} attendance records...", ft.colors.BLUE_900),
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )
    

    view_content = ft.Container(
        content=ft.Column(
            [
                ft.Text(event_info['name'], size=30, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
                ft.Text(event_info['date'], size=18, color=ft.colors.BLACK87),
                
                # Mock Search/Filter Bar
                ft.Row(
                    [
                        ft.TextField(hint_text="Search Name/Section", expand=True),
                        ft.IconButton(ft.icons.FILTER_ALT)
                    ],
                    width=500,
                    spacing=10
                ),
                
                # Attendance List/Table
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"Sign-in Sheet (Total: {len(attendance_data)} attendees)", weight=ft.FontWeight.W_600, size=16),
                            ft.ResponsiveRow([
                                ft.Container(
                                    content=attendance_table, 
                                    col={"xs": 12, "md": 12}, 
                                    # Ensure table expands responsively
                                )
                            ])

                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        scroll=ft.ScrollMode.ADAPTIVE,
                        expand=True
                    ),
                    padding=ft.padding.all(10),
                    margin=ft.margin.only(top=10),
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                    expand=True
                ),
                
                # Bottom Actions
                ft.Row([export_button], alignment=ft.MainAxisAlignment.CENTER, width=500),
                ft.Container(content=status_text_control, alignment=ft.alignment.center)

            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            expand=True
        ),
        padding=20,
        expand=True
    )
    
    # Attach status_text to the view_content object for the helper function
    setattr(view_content, 'status_text', status_text_control)

    return ft.View(
        f"/event/{event_id}",
        [
            create_app_bar(page, event_info['name'], show_back_button=True),
            view_content,
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

# --- MENU AND LOGOUT FUNCTIONS ---

def perform_logout(page: ft.Page):
    """The actual logic to perform logout and navigation."""
    global CURRENT_USER_NAME
    CURRENT_USER_NAME = None
    # Ensure the dialog is closed if it somehow didn't close
    if page.dialog:
        page.dialog.open = False
    page.drawer = None # Clear the drawer on logout
    page.go("/")
    page.update()

def open_logout_dialog(e, page: ft.Page):
    """Shows a confirmation dialog before logging out."""
    
    def close_dialog(e):
        page.dialog.open = False
        page.update()
        
    def confirm_and_logout(e):
        # Close the dialog UI before performing the actual logout navigation
        close_dialog(e) 
        perform_logout(page)
        
    page.dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Logout"),
        content=ft.Text("Are you sure you want to sign out of MoScan?"),
        actions=[
            ft.TextButton(
                "Cancel", 
                on_click=close_dialog,
                style=ft.ButtonStyle(color=ft.colors.BLACK54)
            ),
            ft.TextButton(
                "Logout", 
                on_click=confirm_and_logout,
                style=ft.ButtonStyle(color=ft.colors.RED_600, weight=ft.FontWeight.BOLD)
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: page.update(),
    )
    
    page.dialog.open = True
    page.update()

def create_drawer(page: ft.Page, logout_handler):
    """Creates the navigation drawer (menu) content, dynamically setting the user name."""
    user_name = CURRENT_USER_NAME if CURRENT_USER_NAME else 'Admin'
    return ft.NavigationDrawer(
        # Always close the drawer when a menu item is clicked
        on_dismiss=lambda e: page.update(), 
        controls=[
            ft.Container(height=10),
            ft.Container(
                content=ft.Text(
                    f"Welcome, {user_name}!", 
                    size=20, 
                    weight=ft.FontWeight.BOLD
                ),
                padding=ft.padding.only(left=20)
            ),
            ft.Divider(),
            ft.ListTile(
                title=ft.Text("Home", weight=ft.FontWeight.BOLD),
                leading=ft.Icon(ft.icons.HOME),
                on_click=lambda e: (setattr(page.drawer, 'open', False), page.go("/home"), page.update()),
            ),
            ft.ListTile(
                title=ft.Text("Logout", weight=ft.FontWeight.BOLD),
                leading=ft.Icon(ft.icons.LOGOUT),
                on_click=lambda e: (setattr(page.drawer, 'open', False), page.update(), logout_handler(e, page)),
            ),
        ]
    )


# --- MAIN APPLICATION LOGIC ---

# Global database instance
db = Database()

def main(page: ft.Page):
    """
    The main entry point for the Flet application, setting up routing and navigation.
    """
    page.title = "MoScan Attendance"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.colors.BLUE_GREY_50
    page.padding = 0
    
    page.window_height = 800
    page.window_width = 500
    
    # Drawer setup (can be recreated on login/logout)
    # The drawer is now created explicitly in LoginView.authenticate or in route_change.

    def route_change(route):
        """Handles navigation when the route changes."""
        page.views.clear()
        
        # Ensure the drawer exists if the user is authenticated
        if CURRENT_USER_NAME and page.drawer is None:
            page.drawer = create_drawer(page, open_logout_dialog)

        # Default/Login View
        if page.route == "/":
            page.views.append(LoginView(page, open_logout_dialog))
        
        # Create Event View
        elif page.route == "/create_event":
            if not CURRENT_USER_NAME: page.go("/"); return
            page.views.append(CreateEventView(page, db))
            
        # Home View
        elif page.route == "/home":
            if not CURRENT_USER_NAME:
                page.go("/")
                return
            page.views.append(HomeView(page, db))
        
        # Event Detail View
        elif page.route.startswith("/event/"):
            if not CURRENT_USER_NAME: page.go("/"); return
            event_id = page.route.split("/")[-1]
            page.views.append(EventDetailView(page, db, event_id))

        # QR Scan View
        elif page.route.startswith("/scan/"):
            if not CURRENT_USER_NAME: page.go("/"); return
            event_id = page.route.split("/")[-1]
            page.views.append(QRScanView(page, db, event_id))
            
        page.update()

    def view_pop(view):
        """Handles back button functionality."""
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Initial route setup
    if not CURRENT_USER_NAME:
        page.go("/")
    else:
        page.go("/home")

    page.update()

# Run the application in web mode, binding to all interfaces for mobile access
if __name__ == "__main__":
    # IMPORTANT: host="0.0.0.0" is required for external devices (like your phone) 
    # to access the app using your computer's local IP address.
    ft.app(target=main, view=ft.WEB_BROWSER, port=8000, host="192.168.254.113")