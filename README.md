<div align="center">

# 🎯 MaScan — QR Attendance Checker

**A Smart Attendance Management System Powered by QR Codes**

[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg?style=for-the-badge)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.28.3-blueviolet.svg?style=for-the-badge)](https://flet.dev)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg?style=for-the-badge)](https://github.com/Fred727wysi/QR-Attendance-Checker)
[![PRs](https://img.shields.io/badge/PRs-Welcome-blue.svg?style=for-the-badge)](https://github.com/Fred727wysi/QR-Attendance-Checker/pulls)

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
- Camera integration
- Multi-threaded processing

</td>
<td>

📊 **Event Management**
- Create & manage events
- Track attendance per event
- Time-slot support

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
- PDF export
- Activity logging

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
- Bcrypt password hashing
- API authentication
- Audit trail

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites
- **Python** 3.9 or higher
- **pip** or poetry
- **Camera** (for QR scanning)

### 30-Second Installation

```bash
# Clone the repository
git clone https://github.com/Fred727wysi/QR-Attendance-Checker.git
cd QR-Attendance-Checker

# Install dependencies
pip install -r requirements.txt

# Initialize database
cd final-project/src
python init_db.py

# Run the app
cd ..
flet run
```

### Login with Default Credentials

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `Admin@123` |

> ⚠️ **Security**: Change admin password immediately after first login!

---

## 📚 Documentation

> **New to the project?** Start here! 👇

| 📖 Guide | 🎯 Purpose | ⏱️ Time |
|----------|-----------|--------|
| **[🚀 Getting Started](./docs/GETTING_STARTED.md)** | Installation & first run | 5 min |
| **[🔐 Security Guide](./docs/SECURITY.md)** | Authentication & best practices | 10 min |
| **[📱 Phone Setup](./docs/PHONE_SETUP.md)** | API server & WiFi config | 15 min |
| **[📦 APK Build](./docs/APK_BUILD.md)** | Deploy to Android | 20 min |
| **[🔧 Troubleshooting](./docs/TROUBLESHOOTING.md)** | Common issues & solutions | — |
| **[👨‍💻 Development](./docs/DEVELOPMENT.md)** | Contributing & architecture | — |

### Quick Links for Common Tasks

- 🆘 **Something broken?** → [Troubleshooting Guide](./docs/TROUBLESHOOTING.md)
- 📱 **Want to use on phone?** → [Phone Setup](./docs/PHONE_SETUP.md)
- 🔒 **Need security info?** → [Security Guide](./docs/SECURITY.md)
- 💻 **Want to contribute?** → [Development Guide](./docs/DEVELOPMENT.md)

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                    MaScan Application                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐         ┌──────────────────┐    │
│  │   Views Layer    │         │   API Server     │    │
│  │  (8 UI Screens)  │         │  (Flask REST)    │    │
│  └────────┬─────────┘         └────────┬─────────┘    │
│           │                            │               │
│           └────────────────┬───────────┘               │
│                            │                           │
│                   ┌────────▼────────┐                 │
│                   │ Database Layer  │                 │
│                   │ (db_manager.py) │                 │
│                   └────────┬────────┘                 │
│                            │                           │
│                   ┌────────▼────────┐                 │
│                   │  SQLite DB      │                 │
│                   └─────────────────┘                 │
│                                                         │
└─────────────────────────────────────────────────────────┘

Desktop ─────────────┐
                     ├──→ Database (Laptop)
Phone (via WiFi) ───┘
```

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| **Main App** | `app.py` | Routing, authentication, state management |
| **Database** | `database/db_manager.py` | SQLite operations, queries, transactions |
| **QR Scanner** | `utils/qr_scanner.py` | OpenCV camera capture, QR detection |
| **PDF Export** | `utils/pdf_export.py` | Report generation with ReportLab |
| **UI System** | `views/ui_utils.py` | Animations, styling, components |
| **API Server** | `api_server.py` | REST API for phone access |

### Views (8 Screens)

| View | Route | Purpose | Access |
|------|-------|---------|--------|
| **Login** | `/` | User authentication | Public |
| **Home** | `/home` | Events dashboard | Admin/Scanner |
| **Create Event** | `/create_event` | New event form | Admin |
| **Event Details** | `/event/<id>` | Attendance & export | Admin/Scanner |
| **QR Scanner** | `/scan/<id>` | Real-time scanning | Admin/Scanner |
| **QR Generator** | `/qr_generator` | Batch QR generation | Admin |
| **User Manager** | `/user_management` | User CRUD | Admin |
| **Activity Log** | `/activity_log` | Audit trail | Admin |

---

## 💻 Technology Stack

```
Frontend          │ Backend        │ Database   │ Security
─────────────────┼────────────────┼────────────┼──────────
Flet 0.28.3      │ Python 3.9+    │ SQLite 3   │ Bcrypt
Flutter UI       │ Flask REST     │ JSON       │ API Keys
Animations       │ OpenCV         │ Queries    │ .env Config
Real-time Camera │ pyzbar QR      │ Transactions│ Audit Log
```

---

## 🔧 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/Fred727wysi/QR-Attendance-Checker.git
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

### Step 4: Initialize Database

```bash
cd final-project/src
python init_db.py
cd ..
```

### Step 5: Run Application

```bash
# Desktop mode (laptop only)
flet run

# Or with API server (laptop + phone)
# Terminal 1:
python src/api_server.py

# Terminal 2:
flet run
```

**Need help?** See Getting Started Guide

---

## 📱 Usage

### Desktop App

1. **Login** with credentials (default: `admin` / `Admin@123`)
2. **Create Events** (Admin only)
3. **Scan QR Codes** to record attendance
4. **View Reports** and export to PDF

### Phone App

1. **Build APK**: See APK Build Guide
2. **Configure API**: Enter laptop IP and API key
3. **Scan from Phone** - Database stays on laptop

### API Server

```bash
# Start server
python final-project/src/api_server.py

# API runs on http://0.0.0.0:5000
# Access from phone: http://<laptop-ip>:5000
```

**Full usage guide:** See Documentation

---

## 🗂️ Project Structure

```
QR-Attendance-Checker/
├── docs/                          # 📚 Documentation
│   ├── GETTING_STARTED.md
│   ├── SECURITY.md
│   ├── PHONE_SETUP.md
│   ├── APK_BUILD.md
│   ├── TROUBLESHOOTING.md
│   └── DEVELOPMENT.md
│
├── final-project/
│   ├── src/
│   │   ├── main.py               # Entry point
│   │   ├── app.py                # App orchestrator
│   │   ├── init_db.py            # Database setup
│   │   ├── api_server.py         # REST API server
│   │   │
│   │   ├── config/
│   │   │   └── constants.py      # App configuration
│   │   │
│   │   ├── database/
│   │   │   └── db_manager.py     # SQLite manager
│   │   │
│   │   ├── utils/
│   │   │   ├── qr_scanner.py     # QR detection
│   │   │   └── pdf_export.py     # PDF generation
│   │   │
│   │   └── views/
│   │       ├── base_view.py      # Base class
│   │       ├── login_view.py
│   │       ├── home_view.py
│   │       ├── scan_view.py
│   │       ├── event_view.py
│   │       ├── create_event_view.py
│   │       ├── qr_generator_view.py
│   │       ├── user_management_view.py
│   │       ├── activity_log_view.py
│   │       └── ui_utils.py       # Animations & styles
│   │
│   └── pyproject.toml
│
├── config/                        # Configuration files
├── data/                          # Data files
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── LICENSE                        # MIT License
```

---

## 🔐 Security

### Features

✅ **Bcrypt Password Hashing** (12 rounds)
✅ **API Key Authentication**
✅ **Role-Based Access Control** (Admin/Scanner)
✅ **Activity Logging & Audit Trail**
✅ **Environment Variable Configuration** (.env)
✅ **Session Management**

### Best Practices

- Always change default passwords
- Keep `.env` file private
- Use strong passwords (16+ characters)
- Regularly review activity logs
- Enable debug mode only in development

**See Security Guide for details**

---

## 📊 Database Schema

### Tables Overview

**users** — Admin & Scanner accounts
```sql
username (PK) | password (hashed) | role | created_at
```

**events** — Event records
```sql
id (PK) | name | date | description
```

**attendance** — QR scan records
```sql
event_id | user_id | user_name | timestamp | status | time_slot
```

**login_history** — Audit trail
```sql
id | username | login_time | logout_time
```

**scan_history** — Scanner audit trail
```sql
id | scanner_username | scanned_user_id | event_id | scan_time
```

---

## 🤝 Contributing

We welcome contributions! Here's how:

### For Developers

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m "feat: add amazing feature"`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### For Everyone Else

- 🐛 **Report Bugs**: [Create an issue](https://github.com/Fred727wysi/QR-Attendance-Checker/issues)
- 💡 **Suggest Features**: [Start a discussion](https://github.com/Fred727wysi/QR-Attendance-Checker/discussions)
- 📝 **Improve Docs**: [Submit a PR](https://github.com/Fred727wysi/QR-Attendance-Checker/pulls)
- ⭐ **Show Support**: Star the repo!

**See Development Guide for technical details**

---

## 📋 Roadmap

### Planned Features

- [ ] CSV export per event
- [ ] Bulk QR code download
- [ ] Advanced filtering & search
- [ ] Multiple time slots (Morning/Afternoon/Lunch)
- [ ] Attendance categories (Food/Attendance)
- [ ] Native mobile app (Android/iOS)
- [ ] Cloud synchronization
- [ ] Email notifications

### In Progress

- 🔄 Performance optimization
- 🔄 UI/UX improvements

### Recently Completed

- ✅ Bcrypt password security
- ✅ REST API server
- ✅ Activity logging
- ✅ PDF export
- ✅ Role-based access control

---

## 👥 Contributors

### Group 12 - Final Project

This project is developed by Group 12 as a combined final requirement for:
- **Software Engineering 1**
- **Information Assurance**
- **Application Development**

| Member | GitHub Profile | Contributions |
|--------|---|---|
| **macmac-12** | [View Profile](https://github.com/macmac-12) | 48 commits |
| **thebaynal** | [View Profile](https://github.com/thebaynal) | 43 commits |
| **JohnRaymondAlba** | [View Profile](https://github.com/JohnRaymondAlba) | 18 commits |
| **Fred727wysi** | [View Profile](https://github.com/Fred727wysi) | 1 commit |

**Total**: 110+ commits | Collaborative development

---

## 📞 Support

### Need Help?

| Resource | Link |
|----------|------|
| **Documentation** | View Docs |
| **Getting Started** | Quick Start |
| **Troubleshooting** | Common Issues |
| **GitHub Issues** | [Report Bug](https://github.com/Fred727wysi/QR-Attendance-Checker/issues) |
| **Discussions** | [Ask Question](https://github.com/Fred727wysi/QR-Attendance-Checker/discussions) |

### Contact

- 🐛 **Report Bug**: [GitHub Issues](https://github.com/Fred727wysi/QR-Attendance-Checker/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Fred727wysi/QR-Attendance-Checker/discussions)

---

## 📄 License

This project is licensed under the **MIT License** — see the LICENSE file for details.

### What You Can Do

✅ Use for commercial purposes
✅ Modify and distribute
✅ Use privately
✅ Include in larger projects

❌ Hold liable for issues
❌ Remove license/copyright

---

## 🙏 Acknowledgments

Built with ❤️ by Group 12 using:

- [**Flet**](https://flet.dev) — Beautiful cross-platform UI
- [**Python**](https://www.python.org/) — Powerful language
- [**OpenCV**](https://opencv.org/) — Computer vision
- [**SQLite**](https://www.sqlite.org/) — Reliable database
- [**Bcrypt**](https://github.com/pyca/bcrypt) — Security
- [**Flask**](https://flask.palletsprojects.com/) — Web framework

---

<div align="center">

### 🎓 Group 12 Final Project

**MaScan — QR Attendance Checker**

*Combined Course Project: Software Engineering 1 • Information Assurance • Application Development*

---

⭐ **Please star this repository if you find it helpful!**

[View on GitHub](https://github.com/Fred727wysi/QR-Attendance-Checker) • Documentation • [Report Issue](https://github.com/Fred727wysi/QR-Attendance-Checker/issues)

**Last Updated**: December 8, 2025

</div>
