# config/constants.py
"""Application constants and configuration."""

# Employee database
EMPLOYEES = {
    "E101": "Alice Smith",
    "E102": "Bob Johnson",
    "E103": "Charlie Brown",
    "E104": "Diana Prince",
    "E105": "Ethan Hunt",
    "E106": "Fiona Gallagher",
    "S999": "System Test Key"
}

# App configuration
APP_TITLE = "MaScan Attendance"
APP_TAGLINE = "where showing up is mandatory. bro."
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800

# Default credentials
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"

# Database
DATABASE_NAME = "mascan_attendance.db"

# Camera settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 20
QR_SCAN_COOLDOWN = 2  # seconds

# Colors
PRIMARY_COLOR = "#F9A825"  # Yellow 800
# Light variant for backgrounds
YELLOW_50 = "#FFFDE7"  # Yellow 50 (light)
# Alias for explicit usage
YELLOW_800 = PRIMARY_COLOR