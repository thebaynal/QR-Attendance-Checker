# 🔐 Security & Authentication

## Overview

Your application includes enterprise-grade security features:

- ✅ Bcrypt password hashing (12 rounds)
- ✅ Environment variable configuration (.env)
- ✅ REST API authentication (API key)
- ✅ Activity logging & audit trail
- ✅ Role-based access control

---

## Password Security

### How It Works

Passwords are **never** stored in plain text. Instead:

1. When set: `password` → `bcrypt_hash` (stored)
2. When verified: `password + hash` → `True/False`

**Example:**
```
Password: "Admin@123"
Hash:     "$2b$12$lrwnCzM5qOF.gRGAGELTZ.IKdlW.RJOiIIio3x/mUcDEqc97V1wv."
```

### Changing Admin Password

Edit `.env`:
```env
ADMIN_PASSWORD=YourNewPassword123!@#
```

Then restart the app.

---

## Environment Configuration

### .env File

Location: Project root directory

```env
# Database
DATABASE_NAME=mascan_attendance.db
DB_PASSWORD=SecureDbPass123!@#$%

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin@123

# API
API_KEY=QRAttendanceAPI_SecureKey_789!@#$%
API_SERVER_URL=http://localhost:5000
USE_REMOTE_API=false

# App
DEBUG_MODE=false
```

### Important

- ⚠️ Never commit `.env` to git
- ⚠️ Change all default passwords
- ⚠️ Use strong passwords (16+ characters)
- ⚠️ Mix uppercase, lowercase, numbers, symbols

---

## API Authentication

### API Key

All API requests (except login) require:

```
Header: X-API-Key: <your-api-key>
```

### Example Request

```bash
curl -X GET http://localhost:5000/api/events \
  -H "X-API-Key: QRAttendanceAPI_SecureKey_789!@#$%"
```

### Invalid Key

Returns: `401 Unauthorized`

Change key in `.env` and restart API server.

---

## Role-Based Access

### Scanner Role
- Login
- View events
- Scan QR codes
- View attendance

### Admin Role
- All scanner permissions
- Create/delete events
- Generate QR codes
- Manage users
- View activity logs
- Change passwords

---

## Activity Logging

All activities are recorded:

- ✅ User logins/logouts
- ✅ QR code scans (with scanner name)
- ✅ Events created/deleted
- ✅ Users added/modified

View in app: **Menu → Activity Log**

---

## Security Best Practices

### ✓ DO
- Change default passwords immediately
- Use strong passwords (16+ chars, mix of types)
- Keep `.env` private (never share)
- Regularly backup database
- Use HTTPS in production
- Change API key regularly

### ✗ DON'T
- Commit `.env` to git
- Share passwords in chat/email
- Use same password everywhere
- Leave default credentials
- Run on untrusted networks
- Store credentials in code

---

## Troubleshooting

### "Login fails with correct password"
- Delete mascan_attendance.db
- Restart app

### "API key invalid"
- Check `.env` has correct `API_KEY`
- Restart API server
- Verify header is `X-API-Key` (not `API-Key`)

### ".env not found error"
- Create `.env` in project root
- Copy configuration from .env setup

---

For more help, see Troubleshooting Guide
```

Once done, commit with:
```powershell
git add docs/SECURITY.md
git commit -m "docs: add security guide with authentication and best practices"
git push origin main
```