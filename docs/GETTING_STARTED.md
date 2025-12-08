# 🚀 Getting Started## Quick Setup (2 minutes)### Prerequisites- Python 3.9+- Camera (for QR scanning)- Virtual environment (recommended)### Installation```bash# Clone and navigategit clone https://github.com/Fred727wysi/QR-Attendance-Checker.gitcd QR-Attendance-Checker# Install dependenciespip install -r [requirements.txt](http://_vscodecontentref_/0)# Initialize databasecd final-project/srcpython init_db.py
Run Application
Desktop Only (Laptop):


cd final-projectflet run
Or directly:


python src/main.py
With API Server (Phone + Laptop):

Terminal 1 - Start API Server:


cd final-project/srcpython api_server.py
Terminal 2 - Start Desktop App:


cd final-projectflet run
Login Credentials
Field	Value
Username	admin
Password	Admin@123
⚠️ Important: Change admin password after first login!

Next Steps
Laptop Only? You're done! App is ready to use.
Want Phone Access? → See Phone Setup Guide
Need Security Details? → See Security Guide
Building for Android? → See APK Build Guide
Troubleshooting
"ModuleNotFoundError: No module named..."

pip install -r requirements.txt
"Camera not working"
Check camera permissions
Try: pip install --upgrade opencv-python pyzbar
"Port 5000 already in use"
Kill the process: taskkill /PID <pid> /F
Or change port in api_server.py
"Login fails with correct password"
Delete mascan_attendance.db
Restart app (recreates database)
For more help, see Troubleshooting


**2. `docs/SECURITY.md`**```markdown# 🔐 Security & Authentication## OverviewYour application includes enterprise-grade security features:- ✅ Bcrypt password hashing (12 rounds)- ✅ Environment variable configuration (.env)- ✅ REST API authentication (API key)- ✅ Activity logging & audit trail- ✅ Role-based access control---## Password Security### How It WorksPasswords are **never** stored in plain text. Instead:1. When set: `password` → `bcrypt_hash` (stored)2. When verified: `password + hash` → `True/False`**Example:**
Password: "Admin@123"
Hash: "$2b$12$lrwnCzM5qOF.gRGAGELTZ.IKdlW.RJOiIIio3x/mUcDEqc97V1wv."


### Changing Admin PasswordEdit `.env`:```envADMIN_PASSWORD=YourNewPassword123!@#
Then restart the app.

Environment Configuration
.env File
Location: Project root directory