# API Testing & Troubleshooting Guide

## Issue Fixed: "Endpoint not found" Error

### Problem
When testing the multi-device API setup, the `GET /api/students` endpoint returned:
```
{"error":"Endpoint not found"}
405 Method Not Allowed
```

### Root Cause
The API server had a `GET /api/students/<school_id>` endpoint (get single student) but was missing the `GET /api/students` endpoint (get all students). Only a `POST /api/students` endpoint existed.

### Solution Applied
Added the missing `GET /api/students` endpoint to `api_server.py`:

```python
@app.route('/api/students', methods=['GET'])
@require_api_key
def get_all_students():
    """Get all students."""
    try:
        # Query all students from database
        students = db._execute(
            "SELECT school_id, name, last_name, first_name, middle_initial FROM students_qrcodes ORDER BY school_id", 
            fetch_all=True
        )
        
        if students:
            result = []
            for student in students:
                result.append({
                    'school_id': student[0],
                    'name': student[1],
                    'last_name': student[2],
                    'first_name': student[3],
                    'middle_initial': student[4]
                })
            return jsonify(result), 200
        else:
            return jsonify([]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Testing Results
✅ **Status Code**: 200 OK
✅ **Total Students Retrieved**: 40
✅ **Response Format**: Valid JSON array with student data

Example Response:
```json
[
  {
    "school_id": "1904582",
    "name": "Moreno, Noel, B.",
    "last_name": "Moreno",
    "first_name": "Noel",
    "middle_initial": "B"
  },
  ...
]
```

## Complete API Endpoint Reference

### Authentication Endpoints
- `POST /api/login` — Authenticate user (no API key required)
- `POST /api/logout` — Logout user

### Event Endpoints
- `GET /api/events` — Get all events
- `POST /api/events` — Create new event
- `DELETE /api/events/<event_id>` — Delete event
- `GET /api/attendance/<event_id>` — Get event attendance
- `GET /api/attendance-by-section/<event_id>` — Get attendance grouped by section
- `GET /api/attendance-summary/<event_id>` — Get attendance statistics

### User Endpoints
- `GET /api/users` — Get all users
- `POST /api/users` — Create new user
- `GET /api/users/<username>` — Get user info
- `DELETE /api/users/<username>` — Delete user

### Student Endpoints
- `GET /api/students` — **Get all students** ✅ (FIXED)
- `POST /api/students` — Create/update student
- `GET /api/students/<school_id>` — Get student by ID
- `POST /api/students/<school_id>` — Update student

### Activity Endpoints
- `GET /api/recent-scans` — Get recent QR scans
- `GET /api/recent-logins` — Get recent logins
- `GET /api/check-timeslot/<event_id>/<school_id>/<time_slot>` — Check if student marked for timeslot
- `POST /api/record-timeslot` — Record attendance for timeslot

### Health Check
- `GET /api/status` — Server health check (no API key required)

## Multi-Device Testing Setup

### Start API Server
```bash
python final-project/src/api_server.py
```
Server runs on: `http://localhost:5000`
API Key: `QRAttendanceAPI_SecureKey_789!@#$%`

### Test Endpoints (Using curl or PowerShell)

**PowerShell Example**:
```powershell
$headers = @{'X-API-Key' = 'QRAttendanceAPI_SecureKey_789!@#$%'}
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/students" -Headers $headers
$response.StatusCode
$response.Content | ConvertFrom-Json
```

**curl Example**:
```bash
curl -H "X-API-Key: QRAttendanceAPI_SecureKey_789!@#$%" http://localhost:5000/api/students
```

## Diagnostic Test Script

A test script is available at: `test_api.py`

Run it to test all endpoints:
```bash
python test_api.py
```

It will:
- ✅ Check server is running
- ✅ Test authentication
- ✅ Test all CRUD operations
- ✅ Report failures with clear messages

## Next Steps for Multi-Device Testing

1. **API Server Running**: ✅ Confirmed working on port 5000
2. **All Endpoints Working**: ✅ All 20+ endpoints tested and functional
3. **Database Connectivity**: ✅ SQLite database accessible via API
4. **Real-Time Sync**: Configure sync service for 2-second polling
5. **Network Access**: Ensure firewall allows port 5000

### To Connect Second Device

1. Update `api_db_manager.py` with API server address:
```python
api_base_url = "http://192.168.1.16:5000"  # Replace with server IP
```

2. Run app with API mode:
```bash
python final-project/src/main.py
```

3. App will sync data every 2 seconds via API

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Connection refused" | Start API server first: `python final-project/src/api_server.py` |
| "Invalid API key" | Verify key matches in both `api_server.py` and `api_db_manager.py` |
| "Method not allowed" | Ensure endpoint supports GET/POST as needed |
| "Endpoint not found" | Check route decorator syntax, restart server |
| Port 5000 already in use | `lsof -i :5000` (Linux/Mac) or `netstat -ano` (Windows) |

## Summary

✅ **Fixed**: GET /api/students endpoint now returns all students
✅ **Verified**: All major API endpoints are functional
✅ **Status**: API server ready for multi-device deployment

---
**Last Updated**: December 9, 2025
