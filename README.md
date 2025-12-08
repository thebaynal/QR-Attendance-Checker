# 🎯 MaScan — QR Attendance Checker

> **Smart attendance management system powered by QR codes** • Built with Flet & Python

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-green.svg)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/flet-0.28.3-blueviolet.svg)](https://flet.dev)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](https://github.com/Fred727wysi/QR-Attendance-Checker)

---

## ✨ Features

- 🎫 **QR Code Scanning** — Real-time attendance tracking with camera integration
- 📊 **Event Management** — Create, manage, and track events with ease
- 👥 **User Management** — Role-based access (Admin/Scanner) with secure authentication
- 📈 **Analytics Dashboard** — View attendance statistics and reports
- 📄 **PDF Export** — Generate professional attendance reports
- 🎨 **Modern UI** — Beautiful animations and intuitive interface
- ⏰ **Time Slots** — Support for morning/afternoon attendance tracking
- 🔐 **Secure** — Bcrypt password hashing and role-based authorization

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip or poetry package manager
- Camera (for QR scanning)

### Installation

```bash
# Clone the repository
git clone https://github.com/Fred727wysi/QR-Attendance-Checker.git
cd QR-Attendance-Checker

# Install dependencies
pip install -r requirements.txt

# Or using poetry
poetry install
```

### Initialize Database

```bash
cd final-project/src
python init_db.py
```

### Run the Application

```bash
# Using Flet
cd final-project
flet run

# Or with poetry
poetry run flet run
```

### Default Admin Credentials

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `Admin@123` |

⚠️ **IMPORTANT**: Change the admin password immediately after first login!

---

## 📁 Project Structure

```
QR-Attendance-Checker/
├── final-project/
│   ├── src/
│   │   ├── main.py                 # Application entry point
│   │   ├── app.py                  # Main app orchestrator
│   │   ├── init_db.py              # Database initialization
│   │   ├── config/
│   │   │   └── constants.py        # Configuration constants
│   │   ├── database/
│   │   │   └── db_manager.py       # SQLite database manager
│   │   ├── utils/
│   │   │   ├── qr_scanner.py       # QR detection with OpenCV
│   │   │   └── pdf_export.py       # PDF report generation
│   │   └── views/
│   │       ├── base_view.py        # Base view class
│   │       ├── login_view.py       # Authentication UI
│   │       ├── home_view.py        # Events list
│   │       ├── create_event_view.py# Event creation
│   │       ├── event_view.py       # Event details & export
│   │       ├── scan_view.py        # QR scanning interface
│   │       ├── qr_generator_view.py# QR code generation
│   │       ├── user_management_view.py # User CRUD
│   │       ├── activity_log_view.py    # Audit trail
│   │       └── ui_utils.py         # UI animations & styles
│   └── pyproject.toml              # Project metadata
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🏗️ Architecture Overview

### Core Components

#### 🔧 Application Shell (app.py)
- Manages routing and view lifecycle
- Handles user authentication state
- Coordinates QR camera scanner
- Error handling and fallback UI

#### 💾 Database Layer (db_manager.py)
- SQLite database operations
- User authentication (bcrypt hashing)
- Event CRUD operations
- Attendance recording and querying

#### 🎨 UI Views (8 Total)
| View | Purpose |
|------|---------|
| **LoginView** | User authentication |
| **HomeView** | Events listing dashboard |
| **CreateEventView** | New event creation form |
| **EventView** | Event details & attendance records |
| **ScanView** | Real-time QR code scanning |
| **QRGeneratorView** | Generate & download QR codes (Admin) |
| **UserManagementView** | User administration (Admin) |
| **ActivityLogView** | Login audit trail (Admin) |

#### 🔍 QR Processing (qr_scanner.py)
- Multi-threaded camera capture
- OpenCV-based frame processing
- pyzbar QR code decoding
- Duplicate scan prevention

#### 🎭 Styling System (ui_utils.py)
- **AnimationUtils**: Fade, slide, and scale animations
- **StyleUtils**: Centralized color palette and component styling
- **LoadingIndicator**: Animated loading states

---

## 📊 Database Schema

### Events Table
```sql
CREATE TABLE events (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT
)
```

### Attendance Table
```sql
CREATE TABLE attendance (
    event_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    user_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    status TEXT NOT NULL,
    time_slot TEXT DEFAULT 'morning',
    PRIMARY KEY (event_id, user_id, time_slot)
)
```

### Users Table
```sql
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL (hashed),
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'scanner',
    created_at TEXT NOT NULL
)
```

---

## 🔐 Authentication & Authorization

**Default Roles:**
- **Admin**: Full access (user management, QR generation, reports)
- **Scanner**: Limited access (event scanning, viewing)

**Security Features:**
- Bcrypt password hashing (12 rounds)
- Role-based access control (RBAC)
- Session management
- Activity logging

---

## 📦 Dependencies

### Core
- **flet** (0.28.3) — Cross-platform UI framework
- **sqlite3** — Database engine

### QR Processing
- **opencv-python** — Camera and frame processing
- **pyzbar** — QR code detection
- **qrcode** — QR code generation

### Utilities
- **bcrypt** — Password hashing
- **reportlab** — PDF generation
- **pillow** — Image processing

See requirements.txt for complete list.

---

## 🛠️ Development

### Adding a New View

1. **Create view class** in views
   ```python
   from views.base_view import BaseView
   import flet as ft
   
   class MyView(BaseView):
       def build(self):
           return ft.View("/my_route", [...])
   ```

2. **Register in app.py**
   ```python
   self.my_view = MyView(self)
   ```

3. **Add route handler** in `route_change()`
   ```python
   elif route == "/my_route":
       new_view = self.my_view.build()
   ```

---

## 🚨 Troubleshooting

### Camera Not Working
- Ensure camera permissions are granted
- Check `opencv-python` and `pyzbar` are installed
- Try: `pip install --upgrade opencv-python pyzbar`

### Database Issues
- Delete mascan_attendance.db and reinitialize
- Run: `python init_db.py`

### Import Errors
- Verify you're in the correct directory
- Install dependencies: `pip install -r requirements.txt`

---

## 📋 Roadmap

- [ ] Export to CSV per event
- [ ] Bulk QR code download
- [ ] Advanced filtering and search
- [ ] Multiple time slots (Morning/Afternoon/Lunch)
- [ ] Attendance categories (Food/Attendance)
- [ ] Mobile app version (Android/iOS)
- [ ] Cloud synchronization
- [ ] Email notifications

---

## 👥 Contributors

- ----
- ----
- ----
- ----

---

## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

---

## 📞 Support

For issues, questions, or suggestions:
- **GitHub Issues**: [Create an issue](https://github.com/Fred727wysi/QR-Attendance-Checker/issues)
- **Email**: fred727wysi@gmail.com

---

## 🙏 Acknowledgments

Built with ❤️ using [Flet](https://flet.dev) and Python

**Last Updated**: December 8, 2025

---

<div align="center">

⭐ If you find this project helpful, please consider starring it!

[View on GitHub](https://github.com/Fred727wysi/QR-Attendance-Checker)

</div>
```

This README includes:
✅ Professional header with badges  
✅ Clear feature list with emojis  
✅ Quick start guide  
✅ Complete project structure  
✅ Architecture overview with component descriptions  
✅ Database schema documentation  
✅ Security & authentication info  
✅ Developer guide  
✅ Troubleshooting section  
✅ Roadmap  
✅ 4 placeholder dashes in contributors  
✅ Beautiful formatting and organization  
✅ Links to GitHub and support  

