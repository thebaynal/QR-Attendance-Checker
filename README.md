Replace the entire README with this simplified version with profile links:

```markdown
<div align="center">

# 🎯 MaScan — QR Attendance Checker

**A Smart Attendance Management System Powered by QR Codes**

[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg?style=for-the-badge)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.28.3-blueviolet.svg?style=for-the-badge)](https://flet.dev)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg?style=for-the-badge)](https://github.com/Fred727wysi/QR-Attendance-Checker)
[![PRs](https://img.shields.io/badge/PRs-Welcome-blue.svg?style=for-the-badge)](https://github.com/Fred727wysi/QR-Attendance-Checker/pulls)

*Group 12 Final Project | Software Engineering 1 • Information Assurance • Application Development*

[📚 Documentation](./docs/) • [🐛 Report Issue](https://github.com/Fred727wysi/QR-Attendance-Checker/issues) • [⭐ Star us](https://github.com/Fred727wysi/QR-Attendance-Checker)

</div>

---

## 📖 Quick Navigation

| Link | Description |
|------|-------------|
| [🚀 Getting Started](./docs/GETTING_STARTED.md) | Installation & first run |
| [🔐 Security Guide](./docs/SECURITY.md) | Authentication & best practices |
| [📱 Phone Setup](./docs/PHONE_SETUP.md) | API server & WiFi configuration |
| [📦 APK Build](./docs/APK_BUILD.md) | Deploy to Android |
| [🔧 Troubleshooting](./docs/TROUBLESHOOTING.md) | Common issues & solutions |
| [👨‍💻 Development](./docs/DEVELOPMENT.md) | Contributing & architecture |

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

```bash
# Clone
git clone https://github.com/Fred727wysi/QR-Attendance-Checker.git
cd QR-Attendance-Checker

# Install
pip install -r requirements.txt

# Setup
cd final-project/src
python init_db.py

# Run
cd ..
flet run
```

**Login:** `admin` / `Admin@123`

> ⚠️ Change password after first login!

---

## 🏗️ Architecture

**Views** → **Database** → **SQLite**

**Components**: Authentication • QR Scanner • Event Management • PDF Export • Activity Logging • API Server

**Technology**: Flet • Python 3.9+ • SQLite • Bcrypt • OpenCV • Flask

---

## 📊 Database

- **users** — Admin/Scanner accounts
- **events** — Event records
- **attendance** — QR scan records
- **login_history** — Audit trail
- **scan_history** — Scanner audit trail

---

## 🔐 Security

✅ Bcrypt password hashing (12 rounds)
✅ API key authentication
✅ Role-based access control
✅ Activity logging & audit trail
✅ Environment variable configuration

---

## 👥 Contributors

### Group 12

| Member | GitHub Profile |
|--------|---|
| **macmac-12** | [View Profile](https://github.com/macmac-12) |
| **thebaynal** | [View Profile](https://github.com/thebaynal) |
| **JohnRaymondAlba** | [View Profile](https://github.com/JohnRaymondAlba) |
| **Fred727wysi** | [View Profile](https://github.com/Fred727wysi) |

---

## 📚 Full Documentation

Complete guides available in [`docs/`](./docs/) folder:

- [Getting Started](./docs/GETTING_STARTED.md)
- [Security Guide](./docs/SECURITY.md)
- [Phone Setup](./docs/PHONE_SETUP.md)
- [APK Build](./docs/APK_BUILD.md)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)
- [Development](./docs/DEVELOPMENT.md)

---

## 📋 Project Structure

```
final-project/src/
├── main.py                 # Entry point
├── app.py                  # App orchestrator
├── init_db.py              # Database setup
├── api_server.py           # REST API
├── config/constants.py     # Configuration
├── database/db_manager.py  # Database operations
├── utils/
│   ├── qr_scanner.py       # QR detection
│   └── pdf_export.py       # PDF generation
└── views/                  # 8 UI screens
    ├── login_view.py
    ├── home_view.py
    ├── scan_view.py
    ├── event_view.py
    ├── create_event_view.py
    ├── qr_generator_view.py
    ├── user_management_view.py
    ├── activity_log_view.py
    └── ui_utils.py         # Animations & styles
```

---

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- pip or poetry
- Camera (for QR scanning)

### Steps

1. **Clone** the repository
2. **Install** dependencies: `pip install -r requirements.txt`
3. **Initialize** database: `python final-project/src/init_db.py`
4. **Run** application: `cd final-project && flet run`

See [Getting Started Guide](./docs/GETTING_STARTED.md) for detailed setup.

---

## 📱 Usage

### Desktop
1. Login (admin / Admin@123)
2. Create events
3. Scan QR codes
4. Export reports

### Phone
1. Build APK (see [APK Build Guide](./docs/APK_BUILD.md))
2. Configure API server
3. Scan from phone

See [Documentation](./docs/) for more.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m "feat: add amazing feature"`
4. Push: `git push origin feature/amazing-feature`
5. Open Pull Request

See [Development Guide](./docs/DEVELOPMENT.md) for details.

---

## 📋 Roadmap

- [ ] CSV export per event
- [ ] Bulk QR code download
- [ ] Advanced filtering & search
- [ ] Multiple time slots
- [ ] Attendance categories
- [ ] Native mobile app
- [ ] Cloud synchronization
- [ ] Email notifications

---

## 📄 License

MIT License — See [LICENSE](LICENSE) file for details.

---

## 📞 Support

- 📚 [Documentation](./docs/)
- 🐛 [Report Issue](https://github.com/Fred727wysi/QR-Attendance-Checker/issues)
- 💬 [Discussions](https://github.com/Fred727wysi/QR-Attendance-Checker/discussions)

---

<div align="center">

## 🎓 Group 12 Final Project

**MaScan — QR Attendance Checker**

*Combined Course Project: Software Engineering 1 • Information Assurance • Application Development*

---

Built with ❤️ | [View on GitHub](https://github.com/Fred727wysi/QR-Attendance-Checker) | ⭐ Star us!

**Last Updated**: December 8, 2025

</div>
