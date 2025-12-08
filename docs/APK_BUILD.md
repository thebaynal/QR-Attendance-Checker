Paste this into **APK_BUILD.md**:

```markdown
# 📦 Building APK for Android

## Prerequisites

- Android SDK installed
- Buildozer installed
- Python 3.9+
- Virtual environment activated

---

## Installation

```powershell
pip install buildozer cython
```

---

## Build APK

```powershell
cd final-project
buildozer android debug
```

This will take 5-15 minutes on first build.

Generated file: `bin/qrattendance-1.0.0-debug.apk`

---

## Install on Phone

### Via ADB (Fastest)

```powershell
adb install bin\qrattendance-1.0.0-debug.apk
```

### Via USB Transfer

1. Copy APK to phone via USB
2. Open file manager on phone
3. Tap APK to install

### Via Email/Download

1. Email APK to yourself
2. Download on phone
3. Tap to install

---

## Configure Phone App

After installation:

1. **Open app**
2. **Settings** (⚙️ icon)
3. **Configure:**

| Setting | Value |
|---------|-------|
| API Server | `http://192.168.1.100:5000` |
| API Key | `QRAttendanceAPI_SecureKey_789!@#$%` |
| Username | `admin` |
| Password | `Admin@123` |

Replace `192.168.1.100` with your laptop IP.

---

## Troubleshooting

### "buildozer: command not found"
```powershell
pip install buildozer
```

### "Build fails - Java not found"
Install Java Development Kit (JDK)

### "APK too large"
Normal - includes Python runtime + dependencies

### "App crashes on startup"
- Check console output in buildozer
- Verify `.env` configuration
- Check API server is running

### "Phone can't connect"
See Phone Setup Guide

---

For more help, see Troubleshooting Guide
```
