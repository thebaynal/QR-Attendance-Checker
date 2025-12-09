<div align="center">

# 🎯 MaScan — QR Attendance Checker

**A Smart Attendance Management System Powered by QR Codes**

[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg?style=for-the-badge)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.28.3-blueviolet.svg?style=for-the-badge)](https://flet.dev)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg?style=for-the-badge)](https://github.com/thebaynal/QR-Attendance-Checker)
[![PRs](https://img.shields.io/badge/PRs-Welcome-blue.svg?style=for-the-badge)](https://github.com/thebaynal/QR-Attendance-Checker/pulls)

*Group 12 Final Project | Software Engineering 1 • Information Assurance • Application Development*

</div>

---

## 📖 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Documentation](#-documentation)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Security](#-security)
- [Database](#-database-schema)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [Contributors](#-contributors)
- [Support](#-support)
- [License](#-license)

---

## ✨ Features

<table>
<tr>
<td>

🎫 **QR Code Scanning**
- Real-time attendance tracking
- Desktop camera integration
- Multi-threaded processing

</td>
<td>

📊 **Event Management**
- Create & manage events
- Track attendance per event
- Time-slot support (Morning/Lunch/Afternoon)

</td>
</tr>
<tr>
<td>

👥 **User Management**
- Role-based access control
- Admin & Scanner roles
- Secure authentication

</td>
<td>

📈 **Analytics & Reports**
- Attendance statistics
- PDF & CSV export
- Activity logging & audit trail

</td>
</tr>
<tr>
<td>

🎨 **Modern UI**
- Beautiful animations
- Intuitive interface
- Responsive design

</td>
<td>

🔐 **Enterprise Security**
- Bcrypt password hashing (12 rounds)
- API authentication
- Complete audit trail

</td>
</tr>
<tr>
<td>

📱 **Multi-Device Support**
- Desktop application
- Web browser access
- Network API server

</td>
<td>

⚡ **Real-Time Sync**
- 2-second polling interval
- Automatic refresh across devices
- Structured data storage

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites
- **Python** 3.9 or higher
- **pip** package manager
- **Camera** (optional - for QR scanning)

### 30-Second Installation

```bash
# Clone the repository
git clone https://github.com/thebaynal/QR-Attendance-Checker.git
cd QR-Attendance-Checker

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
python final-project/src/main.py
```

### Login with Default Credentials

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `Admin@123` |

> ⚠️ **IMPORTANT**: Change admin password immediately after first login!

---

## 📚 Documentation

> **New to the project?** Start with the guides below 👇

| 📖 Guide | 🎯 Purpose |
|----------|-----------|
| **[START_HERE.txt](./START_HERE.txt)** | Quick orientation guide |
| **[QUICK_START.txt](./QUICK_START.txt)** | Rapid deployment steps |
| **[SECURITY_SETUP_GUIDE.txt](./SECURITY_SETUP_GUIDE.txt)** | Authentication & security |
| **[ERD_MERMAID.md](./ERD_MERMAID.md)** | Database schema visualization |
| **[BUILD_GUIDE.txt](./BUILD_GUIDE.txt)** | Desktop/Web/APK building |

### Quick Links for Common Tasks

- 🆘 **Something broken?** → Check TROUBLESHOOTING.txt
- 📱 **Multi-device setup?** → SECURITY_SETUP_GUIDE.txt
- 🔒 **Security questions?** → SECURITY_SETUP_GUIDE.txt
- 💻 **Building & deploying?** → BUILD_GUIDE.txt

---

## 🏗️ Architecture

### System Design

```
┌──────────────────────────────────────────────────────────┐
│                   USER INTERFACE LAYER                  │
│    (Flet - Desktop & Web Multi-Device Support)          │
│  • Login Screen • Event Management • QR Scanner          │
│  • Activity Logs • Reports & Analytics                   │
└──────────────────────┬─────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────┐
│              APPLICATION LOGIC LAYER                   │
│  • View Management • Data Validation • Real-Time Sync  │
│  • Password Hashing (Bcrypt) • Role-Based Access       │
└──────────────────────┬─────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼─────────┐         ┌────────▼──────────┐
│ LOCAL DATABASE  │         │   API SERVER      │
│   (SQLite)      │         │  (Flask REST)     │
│ Single Device   │         │ Multi-Device      │
└────────────────┘         └────────────────────┘
```

### Three Deployment Modes

```
MODE 1: DESKTOP           MODE 2: WEB              MODE 3: API
(Local)                   (Network)                (Shared DB)
┌─────────────┐          ┌─────────────┐         ┌──────────┐
│   Laptop    │          │   Laptop    │         │  Server  │
│  + Camera   │          │  + Camera   │         │(Port 5000)
│  SQLite DB  │          │  SQLite DB  │         │ SQLite   │
└─────────────┘          └─────────────┘         └──────────┘
                              ▲
                              │ Browser
                          ┌───┴──────┐
                          │  Phone   │
                          │  Tablet  │
```

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| **Main App** | `app.py` | Orchestration, routing, state management |
| **Database Layer** | `database/db_manager.py` | SQLite CRUD operations & transactions |
| **API Client** | `api_db_manager.py` | REST API wrapper for remote database |
| **QR Scanner** | `views/scan_view.py` | Real-time QR detection via OpenCV |
| **PDF Export** | `utils/pdf_export.py` | Report generation with formatted names |
| **Sync Service** | `sync_service.py` | 2-second polling for real-time updates |
| **API Server** | `api_server.py` | Flask REST endpoints for all devices |

### Views (8 Screens)

| View | Route | Purpose | Access |
|------|-------|---------|--------|
| **Login** | `/` | User authentication | Public |
| **Home** | `/home` | Events dashboard | Admin/Scanner |
| **Create Event** | `/create_event` | New event form | Admin |
| **Event Details** | `/event/<id>` | Attendance & export | Admin/Scanner |
| **QR Scanner** | `/scan/<id>` | Real-time scanning | Admin/Scanner |
| **QR Generator** | `/qr_generator` | Batch QR generation from CSV | Admin |
| **User Manager** | `/user_management` | User CRUD | Admin |
| **Activity Log** | `/activity_log` | Login/scan audit trail | Admin |

---

## 💻 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **UI Framework** | Flet 0.28.3 | Desktop & web UI, cross-platform |
| **Backend** | Python 3.9+ | Core application logic |
| **Database** | SQLite 3 | Local persistent storage |
| **QR Detection** | OpenCV + pyzbar | Real-time QR scanning |
| **Web Server** | Flask | REST API for multi-device access |
| **Security** | Bcrypt | Password hashing (12 rounds) |
| **PDF Export** | ReportLab | Report generation with formatting |
| **Real-Time** | Threading/Polling | 2-second sync interval |

### How They Work Together

```
Student CSV
    ↓
QR Generator (OpenCV generates codes)
    ↓
SQLite Database (stores with components: last_name, first_name, middle_initial)
    ↓
Desktop Scanner (detects QR via OpenCV)
    ↓
Flask API / Local DB (records scan)
    ↓
Sync Service (polls every 2 seconds for changes)
    ↓
All Devices Refresh (real-time update)
    ↓
PDF Export (formats names as "Last, First, M.")
```

---

## 🔧 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/thebaynal/QR-Attendance-Checker.git
cd QR-Attendance-Checker
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # macOS/Linux
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Application

```bash
# Option 1: Desktop mode (single device, local database)
python final-project/src/main.py

# Option 2: Web mode (browser-based, single device)
python final-project/src/main.py --web

# Option 3: Multi-device (start API server first)
# Terminal 1:
python final-project/src/api_server.py

# Terminal 2:
python final-project/src/main.py
```

**Need detailed help?** → See START_HERE.txt or QUICK_START.txt

---

## 📱 Usage

### Typical Workflow

1. **Admin creates event** (e.g., "Morning Assembly - Dec 9")
2. **Admin uploads CSV** with student list
3. **System generates QR codes** for all students
4. **Scanners scan QR codes** during event
5. **Real-time sync** updates all connected devices
6. **Admin exports attendance** to PDF with formatted names

### Desktop App

```bash
python final-project/src/main.py
```
- ✅ Full QR scanning with camera
- ✅ Create events & manage users
- ✅ Local database (no network needed)
- ✅ Export to PDF/CSV

### Web App (Same Network)

```bash
python final-project/src/main.py --web
```
- ✅ Access from any browser
- ✅ Access from phone on same WiFi
- ✅ Manual QR entry (no camera)
- ✅ Still uses local database

### Multi-Device (API Server)

```bash
# Terminal 1: Start API server
python final-project/src/api_server.py

# Terminal 2: Run app (connects to API)
python final-project/src/main.py
```
- ✅ Multiple devices share ONE database
- ✅ Real-time sync (2-second polling)
- ✅ Best for distributed scanning teams
- ✅ Phone can access via API endpoint

---

## 🗂️ Project Structure

```
QR-Attendance-Checker/
│
├── final-project/
│   └── src/
│       ├── main.py                    # Entry point
│       ├── app.py                     # App orchestrator & sync service
│       ├── api_server.py              # Flask REST API server
│       ├── sync_service.py            # Real-time sync (2-sec polling)
│       │
│       ├── config/
│       │   ├── remote_config.py       # API configuration
│       │   └── constants.py           # App constants
│       │
│       ├── database/
│       │   ├── db_manager.py          # SQLite manager (7 tables)
│       │   └── init_db.py             # Database initialization
│       │
│       ├── api/
│       │   └── api_db_manager.py      # API client wrapper
│       │
│       ├── utils/
│       │   ├── qr_scanner.py          # OpenCV QR detection
│       │   ├── pdf_export.py          # PDF generation
│       │   └── csv_utils.py           # CSV handling
│       │
│       └── views/
│           ├── base_view.py           # Base view class
│           ├── login_view.py
│           ├── home_view.py
│           ├── scan_view.py
│           ├── event_view.py
│           ├── create_event_view.py
│           ├── qr_generator_view.py
│           ├── user_management_view.py
│           ├── activity_log_view.py
│           └── ui_utils.py            # Animations & styling
│
├── data/
│   ├── attendance.json
│   ├── events.json
│   └── users.json
│
├── docs/                              # Documentation
├── requirements.txt
├── README.md                          # This file
├── START_HERE.txt
├── QUICK_START.txt
├── ERD_MERMAID.md                     # Database schema (with visual)
├── SECURITY_SETUP_GUIDE.txt
├── BUILD_GUIDE.txt
└── LICENSE
```

---

## 🔐 Security

### Features Implemented

✅ **Bcrypt Password Hashing** - 12 rounds, cryptographically secure
✅ **Role-Based Access Control** - Admin & Scanner roles with enforced permissions
✅ **Activity Audit Trail** - Complete login & scan history logged
✅ **API Authentication** - Secure endpoints with verification
✅ **Environment Configuration** - Sensitive data via .env file
✅ **Session Management** - Automatic session tracking

### Best Practices

- ⚠️ Always change default credentials immediately
- ⚠️ Keep `.env` file private and out of version control
- ⚠️ Use strong passwords (16+ characters recommended)
- ⚠️ Regularly review activity logs for suspicious behavior
- ⚠️ Enable debug mode only during development

**See SECURITY_SETUP_GUIDE.txt for detailed security configuration**

---

## 📊 Database Schema

### 7 Core Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **users** | Accounts & auth | username (PK), password (hashed), role (admin/scanner) |
| **events** | Attendance events | id (PK), name, date, description |
| **students_qrcodes** | Student records | school_id (PK), name, last_name, first_name, middle_initial, qr_data |
| **attendance_timeslots** | Multi-period tracking | event_id, user_id, morning/lunch/afternoon status |
| **attendance** | Legacy records | event_id, user_id, timestamp, status |
| **login_history** | Session audit | username (FK), login_time, logout_time |
| **scan_history** | Scan audit trail | scanner_username (FK), scanned_user_id (FK), event_id (FK), scan_time |

### Name Component Storage

Students stored with **three name fields**:
- `last_name` — "Alba"
- `first_name` — "John Raymond"
- `middle_initial` — "S"

Formatted for exports as: **"Alba, John Raymond, S."**

**See ERD_MERMAID.md for complete schema visualization**

---

## 🤝 Contributing

We welcome contributions! Here's how:

### For Developers

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m "feat: add amazing feature"`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### For Everyone

- 🐛 **Report Bugs**: [Create an issue](https://github.com/thebaynal/QR-Attendance-Checker/issues)
- 💡 **Suggest Features**: [Start a discussion](https://github.com/thebaynal/QR-Attendance-Checker/discussions)
- 📝 **Improve Docs**: Submit a pull request
- ⭐ **Show Support**: Star the repository!

---

## 📋 Roadmap

### Completed ✅

- ✅ Bcrypt password security
- ✅ REST API server (multi-device support)
- ✅ Activity logging & audit trail
- ✅ PDF export with formatted names
- ✅ Role-based access control (Admin/Scanner)
- ✅ Real-time sync (2-second polling)
- ✅ Structured name component storage
- ✅ CSV batch import with QR generation

### In Progress 🔄

- 🔄 Performance optimization
- 🔄 UI/UX enhancements
- 🔄 Mobile app improvements

### Planned 📋

- [ ] Advanced filtering & search
- [ ] Attendance analytics dashboard
- [ ] Email notifications
- [ ] Cloud synchronization
- [ ] Native mobile app (Android/iOS)

---

## 👥 Contributors

### Group 12 - Software Engineering Final Project

This project is the combined final requirement for:
- **Software Engineering 1**
- **Information Assurance**
- **Application Development**

| Member | GitHub | Contributions |
|--------|--------|---|
| **macmac-12** | [Profile](https://github.com/macmac-12) | 48 commits |
| **thebaynal** | [Profile](https://github.com/thebaynal) | 50+ commits |
| **JohnRaymondAlba** | [Profile](https://github.com/JohnRaymondAlba) | 18 commits |
| **Fred727wysi** | [Profile](https://github.com/Fred727wysi) | 1 commit |

**Total**: 120+ commits across 4 months of collaborative development

---

## 📞 Support

### Need Help?

| Resource | Where to Find |
|----------|---|
| 📚 **Documentation** | See docs/ folder & text files |
| 🚀 **Getting Started** | START_HERE.txt |
| ⚡ **Quick Setup** | QUICK_START.txt |
| 🔒 **Security Config** | SECURITY_SETUP_GUIDE.txt |
| 🏗️ **Build & Deploy** | BUILD_GUIDE.txt |
| 🐛 **Issues** | [GitHub Issues](https://github.com/thebaynal/QR-Attendance-Checker/issues) |

### Contact

- 📧 **Report Bugs**: Create a GitHub issue
- 💬 **Ask Questions**: Open a GitHub discussion
- 🌐 **View Code**: [GitHub Repository](https://github.com/thebaynal/QR-Attendance-Checker)

---

## 📄 License

This project is licensed under the **MIT License**.

### You Can

✅ Use for commercial purposes
✅ Modify and distribute
✅ Use privately
✅ Include in larger projects

### You Must

📋 Include original license & copyright notice

**See LICENSE file for full details**

---

## 🙏 Acknowledgments

Built with ❤️ by Group 12 using these amazing tools:

- [**Flet**](https://flet.dev) — Beautiful cross-platform UI
- [**Python**](https://www.python.org/) — Powerful, expressive language
- [**OpenCV**](https://opencv.org/) — Computer vision & QR detection
- [**SQLite**](https://www.sqlite.org/) — Reliable, serverless database
- [**Bcrypt**](https://github.com/pyca/bcrypt) — Cryptographic security
- [**Flask**](https://flask.palletsprojects.com/) — Lightweight web framework
- [**pyzbar**](https://github.com/NaturalHistoryMuseum/pyzbar) — QR code decoding

---

<div align="center">

### 🎓 Group 12 Final Project

**MaScan — QR Attendance Checker**

*Combined Requirement: Software Engineering 1 • Information Assurance • Application Development*

---

⭐ **If you find this project helpful, please consider giving us a star!**

[View on GitHub](https://github.com/thebaynal/QR-Attendance-Checker) • [Documentation](./START_HERE.txt) • [Report Issue](https://github.com/thebaynal/QR-Attendance-Checker/issues)

**Status**: ✅ Active Development | **Last Updated**: December 9, 2025

</div>
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
