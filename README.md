# 📱 MaScan - QR Attendance Management System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flet](https://img.shields.io/badge/Flet-0.23.0-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

*A modern, efficient QR code-based attendance tracking system built with Python and Flet*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots) • [Contributing](#-contributing)

</div>

---

## 🌟 Features

### ✨ Core Functionality
- **QR Code Scanning** - Fast and accurate attendance tracking via camera or manual input
- **Time Slot Management** - Separate morning and afternoon attendance sessions
- **Event Management** - Create and manage multiple events with ease
- **User Authentication** - Secure login system with role-based access
- **Activity Logging** - Track all login and scan activities for auditing

### 🎨 Premium UI/UX
- **Modern Design** - Clean, intuitive interface with premium styling
- **Responsive Layout** - Works seamlessly on different screen sizes
- **Real-time Feedback** - Visual confirmations for all actions
- **Dark Mode Support** - Eye-friendly interface options
- **Smooth Animations** - Polished transitions and micro-interactions

### 📊 Management Features
- **Student Database** - Comprehensive student information management
- **Attendance Reports** - Generate detailed attendance summaries
- **PDF Export** - Export attendance data for record-keeping
- **QR Code Generation** - Bulk generate QR codes for students
- **Analytics Dashboard** - View attendance statistics at a glance

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Webcam (for QR scanning feature)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Fred727wysi/QR-Attendance-Checker.git
   cd QR-Attendance-Checker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python final-project/src/main.py
   ```

---

## 📖 Usage

### Default Login Credentials
```
Username: admin
Password: admin123
```

⚠️ **Important:** Change the default credentials after first login!

### Basic Workflow

1. **Login** → Use your credentials to access the system
2. **Create Event** → Set up an attendance event with date and details
3. **Scan Attendance** → 
   - Select time slot (Morning/Afternoon)
   - Use camera to scan QR codes or enter IDs manually
   - View real-time attendance updates
4. **View Reports** → Check attendance summaries and export data
5. **Activity Log** → Monitor all system activities (admin only)

---

## 🏗️ Project Structure

```
QR-Attendance-Checker/
│
├── final-project/
│   └── src/
│       ├── assets/              # Images and logos
│       ├── config/              # Configuration files
│       │   ├── __init__.py
│       │   └── constants.py     # App constants
│       │
│       ├── database/            # Database management
│       │   ├── __init__.py
│       │   └── db_manager.py    # Database operations
│       │
│       ├── utils/               # Utility functions
│       │   ├── __init__.py
│       │   ├── image_utils.py   # Image processing
│       │   ├── logger.py        # Logging utilities
│       │   ├── pdf_export.py    # PDF generation
│       │   └── qr_scanner.py    # QR code scanning
│       │
│       ├── views/               # UI views
│       │   ├── __init__.py
│       │   ├── activity_log_view.py
│       │   ├── base_view.py
│       │   ├── create_event_view.py
│       │   ├── event_view.py
│       │   ├── home_view.py
│       │   ├── login_view.py
│       │   ├── scan_view.py
│       │   ├── qr_generator_view.py
│       │   └── user_management_view.py
│       │
│       ├── __init__.py
│       ├── app.py               # Main application logic
│       └── main.py              # Entry point
│
├── mascan_attendance.db         # SQLite database
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

---

## 💾 Database Schema

### Tables

#### `users`
- User authentication and management
- Fields: `id`, `username`, `password`, `full_name`, `role`

#### `students_qrcodes`
- Student information and QR codes
- Fields: `id`, `school_id`, `name`, `qr_code`

#### `events`
- Event details and scheduling
- Fields: `id`, `name`, `date`, `location`, `description`

#### `attendance_timeslots`
- Time-based attendance records
- Fields: `id`, `event_id`, `user_id`, `user_name`, `timestamp`, `time_slot`

#### `login_history`
- User login tracking
- Fields: `id`, `username`, `login_time`, `logout_time`

#### `scan_history`
- QR scan activity log
- Fields: `id`, `scanner_username`, `scanned_user_id`, `scanned_user_name`, `event_id`, `scan_time`

---

## 🎨 Screenshots

### Login Screen
Clean and modern authentication interface with premium styling.

### Home Dashboard
Quick access to all major features with statistics overview.

### Scan View
Real-time camera preview with visual feedback for successful scans.

### Activity Log
Comprehensive tracking of all system activities with filtering options.

---

## 🛠️ Tech Stack

- **Framework:** [Flet](https://flet.dev/) - Modern Python UI framework
- **Database:** SQLite - Lightweight embedded database
- **QR Processing:** OpenCV & pyzbar - Computer vision and barcode decoding
- **PDF Generation:** ReportLab - Professional PDF creation
- **Image Processing:** Pillow - Python Imaging Library

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Getting Started

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Commit with clear messages**
   ```bash
   git commit -m "Add: Amazing new feature"
   ```
5. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### Commit Message Guidelines

- `Add:` New feature or functionality
- `Fix:` Bug fix
- `Update:` Modify existing feature
- `Refactor:` Code restructuring
- `Docs:` Documentation changes
- `Style:` UI/UX improvements

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Lead Developer:** Fred727wysi  
**Contributors:** [View Contributors](https://github.com/Fred727wysi/QR-Attendance-Checker/graphs/contributors)

---

## 🐛 Bug Reports & Feature Requests

Found a bug or have a feature idea? 

- **Bug Report:** [Open an Issue](https://github.com/Fred727wysi/QR-Attendance-Checker/issues/new?labels=bug)
- **Feature Request:** [Open an Issue](https://github.com/Fred727wysi/QR-Attendance-Checker/issues/new?labels=enhancement)

---

## 📞 Support

Need help? 

- 📧 Email: [Your Email]
- 💬 Discord: [Your Discord Server]
- 📖 Documentation: [Wiki](https://github.com/Fred727wysi/QR-Attendance-Checker/wiki)

---

## 🎯 Roadmap

### Version 2.0 (Planned)
- [ ] Mobile app version
- [ ] Cloud database support
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Email notifications
- [ ] Bulk import/export features
- [ ] API for third-party integrations

### Version 1.1 (In Progress)
- [x] Activity logging system
- [x] Time slot management
- [x] Enhanced UI/UX
- [ ] Report customization
- [ ] Backup/restore functionality

---

## 🌐 System Requirements

### Minimum
- **OS:** Windows 10, macOS 10.14, or Linux
- **RAM:** 4GB
- **Storage:** 100MB free space
- **Python:** 3.8+

### Recommended
- **OS:** Windows 11, macOS 12+, or Ubuntu 20.04+
- **RAM:** 8GB
- **Storage:** 500MB free space
- **Python:** 3.10+
- **Camera:** 720p or higher for QR scanning

---

## ⚡ Performance Tips

- Use a good quality webcam for faster QR code detection
- Keep the database file backed up regularly
- Clear old attendance records periodically to maintain performance
- Use SSD storage for faster database operations

---

## 🔒 Security

- Always change default credentials
- Keep the application updated
- Regularly backup your database
- Use strong passwords for user accounts
- Limit admin access to trusted users only

---

## 📚 Additional Resources

- [Flet Documentation](https://flet.dev/docs/)
- [Python SQLite Tutorial](https://docs.python.org/3/library/sqlite3.html)
- [QR Code Standards](https://www.qrcode.com/en/about/)
- [Project Wiki](https://github.com/Fred727wysi/QR-Attendance-Checker/wiki)

---

<div align="center">

**⭐ Star this repository if you find it helpful! ⭐**

Made with ❤️ by the MaScan Team

[Report Bug](https://github.com/Fred727wysi/QR-Attendance-Checker/issues) • [Request Feature](https://github.com/Fred727wysi/QR-Attendance-Checker/issues) • [View Documentation](https://github.com/Fred727wysi/QR-Attendance-Checker/wiki)

</div>