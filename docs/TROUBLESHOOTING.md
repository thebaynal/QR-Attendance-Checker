# 🔧 Troubleshooting Guide

## Common Issues

### Login Problems

**"Login fails with correct password"**
- Delete `mascan_attendance.db`
- Restart application
- Database will be recreated with default admin

**"Wrong password" error**
- Check CAPS LOCK
- Verify password in `.env`
- Default: `Admin@123`

---

### Installation Issues

**"ModuleNotFoundError: No module named..."**
```powershell
pip install -r requirements.txt
```

**"pip: command not found"**
- Verify Python installed: `python --version`
- Try: `python -m pip install -r requirements.txt`

**"Virtual environment not activated"**
```powershell
Activate.ps1
```

You should see `(.venv)` at start of prompt.

---

### Camera Issues

**"Camera not available"**
- Check camera permissions
- Try restarting app
- Unplug/replug camera

**"QR codes not scanning"**
- Better lighting
- Hold camera steady
- QR code should fill ~50% of screen
- Try: `pip install --upgrade opencv-python pyzbar`

---

### Network Issues

**"Port 5000 already in use"**
```powershell
netstat -ano | findstr :5000
taskkill /PID <pid> /F
```

**"API server won't start"**
```powershell
python api_server.py
```

Check console for error messages.

**"Phone can't connect to laptop IP"**
1. Check WiFi connection
2. Verify IP address is correct
3. Check Windows Firewall
4. Test with: `curl http://192.168.1.100:5000/api/status`

---

### Configuration Issues

**".env not found"**
- Create `.env` in project root
- Copy template from [Security Guide](./SECURITY.md)

**"API key invalid"**
- Check spelling in `.env`
- No spaces before/after
- Restart API server

**"API_SERVER_URL wrong"**
- Find IP: `ipconfig`
- Format: `http://192.168.x.x:5000`
- Update `.env`

---

### Database Issues

**"Database file corrupted"**
1. Stop application
2. Delete `mascan_attendance.db`
3. Restart app (recreates database)

**"Attendance not saving"**
- Check camera/QR code working
- Verify event exists
- Check console for errors

**"Can't export to PDF"**
- Install: `pip install reportlab pillow`
- Verify event has attendance records

---

### APK/Phone Issues

**"buildozer: command not found"**
```powershell
pip install buildozer cython
```

**"APK installation fails"**
- Try older Android version (API 28+)
- Use: `buildozer android debug`
- Check phone storage space

**"App crashes on phone"**
- Check API server running on laptop
- Verify WiFi connection
- Check API configuration in app settings
- Try reinstalling APK

---

## Debug Mode

Enable debug output:

Edit `.env`:
```env
DEBUG_MODE=true
```

Check console for detailed error messages.

---

## Getting Help

1. **Check console output** - Often shows exact error
2. **Review these docs** - Most issues documented
3. **Check error message** - Usually tells you what's wrong
4. **Verify configuration** - .env, IP addresses, passwords
5. **Test components separately** - API server, app, camera

---

## Report Issues

If stuck:

1. Note exact error message
2. Check console output
3. Verify all steps completed
4. Try examples in Getting Started

---

## Performance Tips

**Slow QR scanning:**
- Better lighting
- Clean camera lens
- Higher quality QR codes

**Slow database:**
- Delete old attendance records (not recommended)
- Check disk space available
- Restart app

**Phone connection slow:**
- Check WiFi signal strength
- Restart API server
- Use 5GHz WiFi if available

---

Still stuck? Check Security Guide or Phone Setup
```
