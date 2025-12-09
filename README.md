<div align="center">

# 🎯 MaScan — QR Attendance Checker

**A Smart Attendance Management System Powered by QR Codes**

[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg?style=for-the-badge)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.28.3-blueviolet.svg?style=for-the-badge)](https://flet.dev)

*Group 12 Final Project | Software Engineering 1 • Information Assurance • Application Development*

</div>

---

## 📖 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)
- [Security](#-security)
- [Database Schema](#-database-schema)
- [Architecture](#-architecture)
- [Contributing](#-contributing)
- [Contributors](#-contributors)
- [License](#-license)

---

## ✨ Features

✅ **QR Code Scanning** — Real-time detection via OpenCV + pyzbar
✅ **Event Management** — Create, manage, and track events with multiple time slots
✅ **User Management** — Role-based access control (Admin/Scanner) with secure authentication
✅ **PDF Export** — Generate formatted attendance reports
✅ **Activity Logging** — Complete audit trail of all system actions
✅ **Modern UI** — Built with Flet for cross-platform desktop & web support
✅ **Multi-Device API** — Optional REST API server for team-based scanning
✅ **Real-Time Sync** — Automatic data synchronization across devices

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Webcam (optional, for QR scanning)

### Installation & Setup

```bash
# 1. Clone repository
git clone https://github.com/thebaynal/QR-Attendance-Checker.git
cd QR-Attendance-Checker

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python final-project/src/main.py
```

### Default Login
| Username | Password |
|----------|----------|
| `admin` | `Admin@123` |

⚠️ **Change the default password immediately after first login!**

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
# Desktop mode (local SQLite database)
python final-project/src/main.py

# Web mode (browser-based)
python final-project/src/main.py --web

# Multi-device mode (start API server first)
# Terminal 1:
python final-project/src/api_server.py

# Terminal 2:
python final-project/src/main.py
```

---

## 📱 Usage

### Typical Workflow

1. **Admin creates event** (e.g., "Morning Assembly - Dec 9")
2. **Admin uploads student list** (CSV with student data)
3. **System generates QR codes** for all students
4. **Scanners scan QR codes** during the event
5. **Real-time sync** updates all connected devices
6. **Admin exports attendance** to PDF with formatted names

### Running Different Modes

**Desktop Application**
- Full QR scanning with webcam
- Create events & manage users
- Uses local SQLite database
- No network required

**Web Application** (Browser-Based)
- Access via web browser
- Mobile/tablet access on same WiFi
- Manual QR entry (no camera support)
- Still uses local database

**Multi-Device** (API Server)
- Multiple devices share one database
- Real-time data synchronization
- Best for distributed scanning teams
- Mobile access via REST API

---

## 🗂️ Project Structure

```
QR-Attendance-Checker/
├── final-project/
│   └── src/
│       ├── main.py                      # Entry point
│       ├── app.py                       # Application orchestration
│       ├── api_server.py                # Flask REST API (optional)
│       ├── sync_service.py              # Real-time data sync
│       │
│       ├── config/
│       │   ├── constants.py             # Configuration constants
│       │   └── remote_config.py         # API endpoint config
│       │
│       ├── database/
│       │   ├── db_manager.py            # SQLite database operations
│       │   └── init_db.py               # Database initialization
│       │
│       ├── api/
│       │   └── api_db_manager.py        # API client wrapper
│       │
│       ├── utils/
│       │   ├── qr_scanner.py            # OpenCV QR detection
│       │   ├── pdf_export.py            # PDF report generation
│       │   └── csv_utils.py             # CSV import/export
│       │
│       └── views/
│           ├── base_view.py             # Base view class
│           ├── login_view.py            # Authentication
│           ├── home_view.py             # Events dashboard
│           ├── event_view.py            # Event details & export
│           ├── scan_view.py             # QR scanner interface
│           ├── create_event_view.py     # Event creation
│           ├── qr_generator_view.py     # Batch QR generation
│           ├── user_management_view.py  # User CRUD
│           └── activity_log_view.py     # Audit logs
│
├── requirements.txt                     # Python dependencies
├── README.md                            # This file
├── LICENSE                              # MIT License
└── START_HERE.txt                       # Setup guide
```

---

## 💻 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **UI Framework** | Flet 0.28.3 | Cross-platform desktop & web interface |
| **Backend** | Python 3.9+ | Core application logic |
| **Database** | SQLite 3 | Persistent local data storage |
| **QR Detection** | OpenCV + pyzbar | Real-time QR scanning & decoding |
| **Web Server** | Flask | REST API for multi-device support |
| **Security** | Bcrypt | Cryptographic password hashing (12 rounds) |
| **PDF Reports** | ReportLab | Formatted attendance report generation |
| **Real-Time Sync** | Threading/Polling | 2-second automatic data synchronization |

---

## 🔐 Security

### Features Implemented

✅ **Bcrypt Password Hashing** — 12-round cryptographic hashing
✅ **Role-Based Access Control** — Admin and Scanner roles with enforced permissions
✅ **Activity Audit Trail** — Complete logging of all system actions
✅ **API Authentication** — Secure REST endpoints with verification
✅ **Session Management** — User session tracking and timeout
✅ **Password Requirements** — Strong password enforcement

### Best Practices

- ⚠️ Change default admin password immediately
- ⚠️ Use strong passwords (16+ characters recommended)
- ⚠️ Keep `.env` file private and out of version control
- ⚠️ Regularly review activity logs for suspicious activity
- ⚠️ Enable debug mode only during development

---

## 📊 Database Schema

### 7 Core Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **users** | User accounts & authentication | `username` (PK), `password` (hashed), `role` (admin/scanner) |
| **events** | Attendance events | `id` (PK), `name`, `date`, `description` |
| **students_qrcodes** | Student records with QR data | `school_id` (PK), `last_name`, `first_name`, `middle_initial`, `qr_data` |
| **attendance_timeslots** | Multi-period attendance tracking | `event_id`, `user_id`, morning/afternoon status |
| **attendance** | Legacy attendance records | `event_id`, `user_id`, `timestamp`, `status` |
| **login_history** | User login/logout audit trail | `username` (FK), `login_time`, `logout_time` |
| **scan_history** | QR scan audit trail | `scanner_username` (FK), `scanned_user_id` (FK), `event_id` (FK), `scan_time` |

### Name Component Storage

Students are stored with three name fields:
- `last_name` — "Alba"
- `first_name` — "John Raymond"
- `middle_initial` — "S"

Formatted for exports as: **"Alba, John Raymond, S."**

---

## 🏗️ Architecture

### System Layers

```
┌─────────────────────────────────────────┐
│     PRESENTATION LAYER (Flet UI)       │
│  Login • Events • Scanner • Reports    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│    APPLICATION LOGIC LAYER             │
│  Validation • Auth • Sync • PDF Gen    │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
┌───────▼────────┐  ┌─▼────────────────┐
│  SQLite DB     │  │  Flask API       │
│  (Local)       │  │  (Optional)      │
└────────────────┘  └──────────────────┘
```

### Data Flow

```
QR Code
  ↓
OpenCV Detection
  ↓
pyzbar Decode
  ↓
Database Record
  ↓
Sync Service (2-sec polling)
  ↓
All Connected Devices Update
  ↓
PDF Export (formatted names)
```

---

## 🤝 Contributing

We welcome contributions from the community! Here's how to get started:

### For Developers

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

### Code Guidelines

- Follow PEP 8 Python style guide
- Add docstrings to functions and classes
- Include type hints where possible
- Test your changes before submitting

### Reporting Issues

- Check if the issue already exists
- Provide clear description and reproduction steps
- Include Python version and OS information

---

## 👥 Contributors

### Group 12 — Software Engineering Final Project

This project combines requirements from:
- **Software Engineering 1**
- **Information Assurance**
- **Application Development**

| Member | GitHub | Role |
|--------|--------|------|
| **macmac-12** | [Profile](https://github.com/macmac-12) | Backend & Database |
| **thebaynal** | [Profile](https://github.com/thebaynal) | Full Stack & DevOps |
| **JohnRaymondAlba** | [Profile](https://github.com/JohnRaymondAlba) | UI & Frontend |
| **Fred727wysi** | [Profile](https://github.com/Fred727wysi) | Documentation |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

### You Are Free To

✅ Use for commercial purposes
✅ Modify and distribute
✅ Use privately
✅ Include in larger projects

### You Must

📋 Include original license and copyright notice

---

## 🙏 Acknowledgments

Built with ❤️ using these technologies:

- [**Flet**](https://flet.dev) — Modern cross-platform UI framework
- [**Python**](https://www.python.org/) — Powerful, expressive programming language
- [**OpenCV**](https://opencv.org/) — Computer vision and image processing
- [**pyzbar**](https://github.com/NaturalHistoryMuseum/pyzbar) — QR code decoding
- [**SQLite**](https://www.sqlite.org/) — Reliable, serverless database
- [**Bcrypt**](https://github.com/pyca/bcrypt) — Cryptographic security
- [**Flask**](https://flask.palletsprojects.com/) — Lightweight web framework
- [**ReportLab**](https://www.reportlab.com/) — PDF generation library

---

<div align="center">

### 🎓 MaScan — QR Attendance Checker

*Group 12 Final Project*

**[View Repository](https://github.com/thebaynal/QR-Attendance-Checker)** • **[Report Issue](https://github.com/thebaynal/QR-Attendance-Checker/issues)**

**Status**: ✅ Active | **Last Updated**: December 9, 2025

⭐ If this project helps you, consider giving it a star!

</div>
