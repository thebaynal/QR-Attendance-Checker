# 👨‍💻 Development Guide

## Project Overview

QR-Attendance-Checker is a comprehensive attendance management system built with Flet (Python UI framework) and SQLite.

**Tech Stack:**
- Frontend: Flet 0.28.3
- Backend: Python 3.9+
- Database: SQLite
- API: Flask REST
- Password Security: Bcrypt

---

## Project Structure

```
final-project/src/
├── main.py                 # Entry point
├── app.py                  # Main app orchestrator
├── init_db.py              # Database initialization
├── api_server.py           # REST API server
├── config/
│   ├── __init__.py
│   └── constants.py        # App configuration
├── database/
│   ├── __init__.py
│   └── db_manager.py       # Database operations
├── utils/
│   ├── __init__.py
│   ├── qr_scanner.py       # QR code detection
│   └── pdf_export.py       # PDF generation
└── views/
    ├── __init__.py
    ├── base_view.py        # Base view class
    ├── login_view.py       # Login UI
    ├── home_view.py        # Events list
    ├── create_event_view.py
    ├── event_view.py       # Event details
    ├── scan_view.py        # QR scanning
    ├── qr_generator_view.py
    ├── user_management_view.py
    ├── activity_log_view.py
    └── ui_utils.py         # UI animations & styles
```

---

## Key Components

### Database (db_manager.py)

**Main Methods:**
- `authenticate_user(username, password)` - Login verification
- `create_user(username, password, full_name, role)` - Add user
- `create_event(name, date, description)` - Create event
- `record_attendance(event_id, user_id, user_name, timestamp, status)` - Record scan
- `get_events()` - Fetch all events
- `get_attendance_summary(event_id)` - Get attendance for event
- `hash_password(password)` - Bcrypt hashing
- `verify_password(password, hashed)` - Verify password

**Tables:**
- `users` - Admin/Scanner accounts
- `events` - Event records
- `attendance` - Attendance tracking
- `login_history` - Login/logout audit trail
- `scan_history` - QR scan audit trail

---

### Views (MVC Pattern)

All views inherit from `BaseView`:

```python
from views.base_view import BaseView

class MyView(BaseView):
    def build(self):
        return ft.View("/my_route", [...])
```

**Available Views:**
1. **LoginView** - Authentication
2. **HomeView** - Events dashboard
3. **CreateEventView** - Create new event
4. **EventView** - Event details & attendance
5. **ScanView** - QR code scanning
6. **QRGeneratorView** - Generate QR codes
7. **UserManagementView** - Manage users
8. **ActivityLogView** - View audit logs

---

### UI Utilities (ui_utils.py)

**AnimationUtils:**
```python
AnimationUtils.fade_in_container(content, duration=600)
AnimationUtils.slide_in_container(content, direction="bottom", duration=600)
AnimationUtils.scale_in_button(content, duration=400)
```

**StyleUtils:**
```python
StyleUtils.primary_button(text, on_click)
StyleUtils.secondary_button(text, on_click)
StyleUtils.stat_card(icon, value, label)
StyleUtils.COLORS  # Color palette
```

**LoadingIndicator:**
```python
LoadingIndicator.pulse_dots()  # Animated loading dots
```

---

## Adding a New View

### Step 1: Create View File

`views/my_view.py`:
```python
from views.base_view import BaseView
import flet as ft

class MyView(BaseView):
    def build(self):
        return ft.View(
            "/my_route",
            [
                ft.AppBar(title=ft.Text("My View")),
                ft.Text("Hello World!")
            ]
        )
```

### Step 2: Register in app.py

```python
from views.my_view import MyView

class MaScanApp(ft.Container):
    def __init__(self):
        # ... existing code ...
        self.my_view = MyView(self)
```

### Step 3: Add Route Handler

In `app.py` `route_change()` method:
```python
elif route == "/my_route":
    new_view = self.my_view.build()
```

### Step 4: Add Navigation

In drawer or menu:
```python
ft.ListTile(
    title=ft.Text("My View"),
    on_click=lambda _: self.go("/my_route")
)
```

---

## Database Queries

### Get All Events

```python
events = self.db.get_events()
for event in events:
    print(event['name'], event['date'])
```

### Record Attendance

```python
self.db.record_attendance(
    event_id="evt_123",
    user_id="stu_456",
    user_name="John Doe",
    timestamp="2025-12-08T10:30:00",
    status="present"
)
```

### Get Attendance Summary

```python
attendance = self.db.get_attendance_summary("evt_123")
for record in attendance:
    print(f"{record['user_name']}: {record['status']}")
```

---

## Authentication Flow

1. User enters credentials
2. `db.authenticate_user(username, password)` called
3. Bcrypt verifies password against hash
4. On success: User data returned
5. On failure: None returned, error shown

### Password Hashing

```python
# Creating user
password = "MyPassword123!@#"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

# Verifying password
is_valid = bcrypt.checkpw(password.encode(), hashed)
```

---

## API Endpoints

### Login
```bash
POST /api/login
Body: {"username": "admin", "password": "Admin@123"}
```

### Get Events
```bash
GET /api/events
Headers: {"X-API-Key": "your-api-key"}
```

### Record Scan
```bash
POST /api/record-scan
Headers: {"X-API-Key": "your-api-key"}
Body: {
    "scanner_username": "scanner1",
    "scanned_user_id": "stu_123",
    "scanned_user_name": "John",
    "event_id": "evt_456"
}
```

---

## Configuration

Edit `config/constants.py`:

```python
APP_TITLE = "MaScan QR Attendance"
WINDOW_WIDTH = 414
WINDOW_HEIGHT = 850
DATABASE_NAME = "mascan_attendance.db"
```

Edit `.env` for secrets:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin@123
API_KEY=QRAttendanceAPI_SecureKey_789!@#$%
DEBUG_MODE=true
```

---

## Testing

### Test Login
```bash
python -m pytest tests/test_auth.py
```

### Test Database
```bash
python -m pytest tests/test_db.py
```

### Test API
```bash
python -m pytest tests/test_api.py
```

---

## Performance Tips

**Database:**
- Use indexes for frequently queried columns
- Limit query results with LIMIT clause
- Use pagination for large datasets

**UI:**
- Use ListView with virtualization
- Lazy load images
- Cache frequently accessed data

**API:**
- Implement caching headers
- Use connection pooling
- Rate limit endpoints

---

## Deployment

### Desktop (Windows/Mac/Linux)
```bash
flet run
```

### Android
```bash
buildozer android debug
```

### Web
```bash
flet run -w
```

---

## Debugging

Enable debug mode in `.env`:
```env
DEBUG_MODE=true
```

Check console output for:
- Database errors
- Authentication failures
- API request/response
- UI rendering issues

---

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes
3. Test thoroughly
4. Commit with clear message: `git commit -m "feat: add my feature"`
5. Push: `git push origin feature/my-feature`
6. Create Pull Request

---

## Future Enhancements

- [ ] Export to CSV per event
- [ ] Bulk QR code download
- [ ] Advanced filtering and search
- [ ] Multiple time slots (Morning/Afternoon/Lunch)
- [ ] Attendance categories (Food/Attendance)
- [ ] Mobile app version (Android/iOS)
- [ ] Cloud synchronization
- [ ] Email notifications

---

## Resources

- [Flet Documentation](https://flet.dev)
- [Bcrypt Documentation](https://github.com/pyca/bcrypt)
- [Flask Documentation](https://flask.palletsprojects.com)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

## Support

For issues or questions:
- Check Troubleshooting Guide
- Review Security Guide
- Check console output for errors
```
