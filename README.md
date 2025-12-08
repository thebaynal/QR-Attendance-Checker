# MaScan — QR Attendance Checker

A comprehensive QR code-based attendance management system built with Flet for desktop and web deployment.

## Features

✓ **QR Code Scanning** - Desktop app with real-time OpenCV-based QR detection  
✓ **Multi-Device Support** - Access via web browser or REST API from any device  
✓ **Secure Authentication** - Bcrypt password hashing for all user accounts  
✓ **Event Management** - Create, manage, and delete attendance events  
✓ **Time-Slot Tracking** - Support for morning/afternoon attendance sessions  
✓ **User Management** - Admin panel for user creation and role assignment  
✓ **Activity Logging** - Complete audit trail of logins and scans  
✓ **Attendance Reports** - CSV and PDF export of attendance data  
✓ **Web Deployment** - Run as a web server accessible from browsers  

## Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone and setup:**
   ```bash
   cd QR-Attendance-Checker
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows
   source .venv/bin/activate      # Linux/macOS
   pip install -r requirements.txt
   ```

2. **Run the application:**
   
   **Desktop (Local Mode):**
   ```bash
   python final-project/src/main.py
   ```
   
   **Web Server (Access from other devices):**
   ```bash
   python final-project/src/main.py --web
   ```
   
   **API Server (for multi-device shared database):**
   ```bash
   python final-project/src/api_server.py
   ```

3. **Default Login:**
   - Username: `admin`
   - Password: `Admin@123`
   - ⚠️ **Change password immediately after first login!**

## Deployment Options

### Option 1: Desktop Application (Single Device)
```bash
python final-project/src/main.py
```
- Full QR scanning with real-time detection
- Local SQLite database
- Complete access to all features

### Option 2: Web Application (Multi-Device)
```bash
python final-project/src/main.py --web
```
- Access from any browser on your network
- Find your IP: `ipconfig` (Windows) or `ifconfig` (Linux/macOS)
- Access from phone: `http://your-ip:8080`
- Manual QR entry available

### Option 3: API Server (Shared Database)
```bash
# Terminal 1: Start API server
python final-project/src/api_server.py

# Terminal 2: Run app (connects to API)
python final-project/src/main.py
```
- All devices share the same database
- Requires REST API configuration

## Project Structure

```
QR-Attendance-Checker/
├── final-project/
│   └── src/
│       ├── main.py                 # Application entry point
│       ├── app.py                  # Main application controller
│       ├── api_server.py           # REST API server
│       ├── database/
│       │   ├── db_manager.py       # SQLite database manager
│       │   └── init_db.py          # Database initialization
│       ├── views/                  # UI screens
│       │   ├── login_view.py
│       │   ├── home_view.py
│       │   ├── scan_view.py
│       │   ├── event_view.py
│       │   ├── user_management_view.py
│       │   ├── activity_log_view.py
│       │   └── ...
│       ├── utils/
│       │   └── qr_scanner.py       # QR detection engine
│       ├── config/
│       │   └── constants.py        # App configuration
│       └── assets/                 # Images and resources
├── mascan_attendance.db            # SQLite database (auto-created)
├── requirements.txt                # Python dependencies
├── START_HERE.txt                  # Setup guide
└── QUICK_START.txt                 # Quick reference
```

## Database Schema

### Users Table
- `username` (PK): Unique username
- `password`: Bcrypt-hashed password
- `full_name`: User's full name
- `role`: User role (admin/scanner)
- `created_at`: Account creation timestamp

### Events Table
- `id` (PK): Event identifier
- `name`: Event name
- `date`: Event date
- `description`: Event description

### Attendance Table
- `event_id`: Reference to event
- `school_id`: Student identifier
- `scan_time`: When attendance was recorded
- `time_slot`: Session (morning/afternoon)
- `scanner_username`: Who recorded the attendance

### Login History Table
- `username`: User who logged in
- `login_time`: Login timestamp
- `logout_time`: Logout timestamp

## Key Features

### QR Code Scanning
- **Desktop**: Real-time OpenCV-based detection with pyzbar
- **Web/Phone**: Manual entry of QR codes
- **Duplicate Prevention**: Prevents marking same student twice per session

### Event Management
- Create events with name, date, and description
- Support for multiple time slots per event (morning/afternoon)
- Track attendance by event and time slot
- Delete events and associated records

### User Management
- Create scanner accounts for staff
- Role-based access control (admin/scanner)
- Secure password hashing with bcrypt
- Activity logging for all user actions

### Activity Monitoring
- Complete login/logout history
- Scan history with timestamps
- Admin view of all user activities
- Export capabilities

## Security

✓ **Password Security**: Bcrypt hashing with 12 rounds  
✓ **Database Protection**: SQLite with proper connection management  
✓ **Authentication**: Secure login with password verification  
✓ **API Security**: API key authentication for remote access  
✓ **Audit Trail**: Complete logging of all operations  

## Performance

- Optimized database queries with proper indexing
- Lazy loading for activity logs (15 records per view)
- Efficient QR detection with frame skipping
- Web deployment support for scalability

## Troubleshooting

**Camera Not Working?**
- Ensure `opencv-python` and `pyzbar` are installed
- Check system camera permissions
- Try running in desktop mode instead of web

**Database Issues?**
- Delete `mascan_attendance.db` to reset
- Check database file permissions
- Verify SQLite installation

**Web Access Not Working?**
- Confirm firewall allows port 8080
- Use correct IP address (not localhost)
- Check devices are on same network

## Development

### Adding New Features
1. Create new view in `final-project/src/views/`
2. Inherit from `BaseView`
3. Register in `app.py` route handler
4. Add to drawer menu if needed

### Database Changes
- Edit schema in `db_manager.create_tables()`
- Run `init_db.py` to reinitialize
- Add migration logic if needed

### Testing
- Use desktop mode for full feature testing
- Use web mode for browser compatibility
- Check activity logs for audit trail

## License

This project is for educational and organizational use.

## Support

For issues or questions:
1. Check console output for error messages
2. Review `START_HERE.txt` for setup help
3. Check `QUICK_START.txt` for quick reference
4. Examine database with SQLite tools if needed

---

**Last Updated**: December 9, 2025
