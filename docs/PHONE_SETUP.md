# 📱 Phone Setup & API Server

## Overview

Run the app on your phone while keeping the database on your laptop.

- Desktop: Main app + Database
- Phone: Scanner interface
- Network: WiFi connection between devices

---

## Step 1: Find Your Laptop IP

Open PowerShell:

```powershell
ipconfig
```

Look for "IPv4 Address" (example: `192.168.1.100`)

**Write this down!** You'll need it later.

---

## Step 2: Update Configuration

Edit `.env` file:

Find this line:
```env
API_SERVER_URL=http://localhost:5000
```

Change to your IP:
```env
API_SERVER_URL=http://192.168.1.100:5000
```

Replace `192.168.1.100` with **your actual IP**.

---

## Step 3: Start API Server

Terminal 1:
```powershell
cd final-project/src
python api_server.py
```

You should see:
```
========================================================
QR ATTENDANCE CHECKER - API SERVER
========================================================
Starting server on http://0.0.0.0:5000
Press Ctrl+C to stop
========================================================
```

⚠️ **Keep this terminal open!**

---

## Step 4: Start Desktop App

Terminal 2:
```powershell
cd final-project
flet run
```

App starts normally. Both can run simultaneously.

---

## Step 5: Build APK for Phone

See APK Build Guide

---

## Step 6: Configure Phone App

After installing APK on phone:

1. Open app
2. Go to Settings
3. Configure:
   - **API Server:** `http://192.168.1.100:5000`
   - **API Key:** `QRAttendanceAPI_SecureKey_789!@#$%`
   - **Username:** `admin`
   - **Password:** `Admin@123`

---

## Verify Connection

### On Laptop

```powershell
# Check API is running
curl http://localhost:5000/api/status
```

Should return: `{"status": "ok"}`

### On Phone

1. Connect to same WiFi as laptop
2. Test API access:
   ```
   http://192.168.1.100:5000/api/status
   ```

---

## Troubleshooting

### "Phone can't connect to API"

1. **Check WiFi**
   - Phone and laptop on same network?
   - Type laptop IP in phone browser

2. **Check Firewall**
   - Windows Firewall blocking port 5000?
   - Allow Python.exe through firewall

3. **Check API Server**
   - Terminal still running?
   - Any error messages?

4. **Check Configuration**
   - Is API_SERVER_URL correct in `.env`?
   - Restart API server after changes

### "Wrong API key on phone"
- Copy exact key from `.env`
- Paste in phone settings
- Verify no spaces before/after

### "Port 5000 already in use"
```powershell
netstat -ano | findstr :5000
taskkill /PID <pid> /F
```

Then restart API server.

---

For more help, see Troubleshooting Guide
```

