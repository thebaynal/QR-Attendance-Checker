# Food Attendance Feature Documentation

## Overview

The **Food Attendance** feature allows separate tracking of food distribution from class attendance. This is useful for events where you need to track:
- Breakfast distribution
- Lunch distribution
- Dinner/Snack distribution
- Separate from actual attendance

## Features

### ✅ Separate Tracking
- Food attendance is stored in a **separate `food_attendance` table**
- Completely independent from class attendance records
- Both can be tracked simultaneously for the same event

### ✅ Multiple Food Types
Supported food types:
- Breakfast
- Lunch
- Dinner
- Snack
- (Easily extendable)

### ✅ QR Code Scanning
- Scan student QR codes to record food attendance
- Automatic timestamp recording
- Scanner username tracking for audit trail
- Real-time display of recent scans

### ✅ Data Export
- Generate separate reports for food attendance
- Filter by food type
- View attendance counts per food type
- Complete audit trail

---

## How to Use

### Accessing Food Attendance

1. **From Home Screen:**
   - Click on an event
   - Click the **menu button** (three dots)
   - Select **"Food Attendance"**

2. **Or directly visit:**
   ```
   /food-attendance/{event_id}
   ```

### Recording Food Attendance

1. **Select Food Type:**
   - Use dropdown menu at top of screen
   - Choose: Breakfast, Lunch, Dinner, or Snack

2. **Scan QR Code:**
   - Point camera at student QR code
   - Scan will be recorded automatically
   - Green notification confirms success

3. **View Recent Scans:**
   - Displayed in real-time list
   - Shows: Student name, time, food type
   - Sorted by most recent first

---

## Database Schema

### food_attendance Table

```sql
CREATE TABLE food_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,              -- Event ID
    user_id TEXT NOT NULL,               -- Student school ID
    user_name TEXT NOT NULL,             -- Student name
    food_time TEXT NOT NULL,             -- Time of scan (HH:MM:SS)
    food_type TEXT DEFAULT 'Breakfast',  -- Type: Breakfast, Lunch, Dinner, Snack
    scanner_username TEXT,               -- Who scanned (for audit)
    date_recorded TEXT NOT NULL,         -- Date (YYYY-MM-DD)
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (user_id) REFERENCES students_qrcodes(school_id),
    FOREIGN KEY (scanner_username) REFERENCES users(username)
)
```

### Key Differences from Attendance Table

| Feature | Attendance | Food Attendance |
|---------|-----------|-----------------|
| Table | `attendance_timeslots` | `food_attendance` |
| Time Slots | Morning, Lunch, Afternoon | Single time per scan |
| Multiple Records | One per time slot | One per scan |
| Food Types | N/A | Breakfast, Lunch, etc. |
| Purpose | Class attendance | Food distribution |
| Reports | Separate export | Separate export |

---

## API Endpoints

### Record Food Attendance
```
POST /api/food-attendance/record
Headers: X-API-Key: <your_key>

Body:
{
    "event_id": "EID1702262837",
    "school_id": "1904582",
    "user_name": "Moreno, Noel, B.",
    "food_type": "Breakfast",
    "scanner_username": "admin"
}
```

### Get Food Attendance Records
```
GET /api/food-attendance/{event_id}
GET /api/food-attendance/{event_id}?food_type=Breakfast
```

### Get Food Attendance Count
```
GET /api/food-attendance/{event_id}/count
GET /api/food-attendance/{event_id}/count?food_type=Lunch
```

### Get Available Food Types
```
GET /api/food-attendance/{event_id}/types
```

Returns:
```json
{
    "event_id": "EID1702262837",
    "food_types": ["Breakfast", "Lunch", "Snack"]
}
```

### Get Recent Food Scans
```
GET /api/food-attendance/{event_id}/recent?limit=20
```

---

## Database Methods

### Recording Food Attendance
```python
db.record_food_attendance(
    event_id="EID123",
    school_id="1904582",
    user_name="Moreno, Noel",
    food_type="Breakfast",
    scanner_username="admin"
)
```

### Retrieving Records
```python
# Get all food attendance for event
records = db.get_food_attendance_by_event(event_id)

# Filter by food type
records = db.get_food_attendance_by_event(event_id, food_type="Lunch")

# Get count
count = db.get_food_attendance_count(event_id, food_type="Breakfast")

# Get food types in event
types = db.get_food_types_by_event(event_id)
# Returns: ["Breakfast", "Lunch", "Snack"]

# Get recent scans
scans = db.get_recent_food_scans(event_id, limit=20)
```

---

## Sample Data

### Sample Food Attendance Record

```json
{
    "user_id": "1904582",
    "user_name": "Moreno, Noel, B.",
    "food_time": "08:30:45",
    "food_type": "Breakfast",
    "scanner_username": "admin",
    "date_recorded": "2025-12-19"
}
```

### Sample Recent Scans

```json
[
    {
        "user_id": "1904582",
        "user_name": "Moreno, Noel, B.",
        "food_time": "08:45:32",
        "food_type": "Breakfast",
        "scanner_username": "admin"
    },
    {
        "user_id": "1904583",
        "user_name": "Santos, Maria, R.",
        "food_time": "08:44:15",
        "food_type": "Breakfast",
        "scanner_username": "admin"
    }
]
```

---

## Workflow

```
Event Created
    ↓
    ├─→ Class Attendance Scanning (/scan/{event_id})
    │   └─→ Records to: attendance_timeslots
    │
    └─→ Food Attendance Scanning (/food-attendance/{event_id})
        └─→ Records to: food_attendance
            (Completely separate tracking)

Both can be run simultaneously or at different times
Both have independent reports and exports
```

---

## Example Usage Scenarios

### Scenario 1: School Event
- **Morning:** Record class attendance with morning time slot
- **Breakfast:** Record food attendance (Breakfast type)
- **Mid-morning:** Record lunch time slot attendance
- **Lunch:** Record food attendance (Lunch type)
- Both tracked separately for different purposes

### Scenario 2: Conference
- **Registration:** Record main attendance
- **Lunch Break:** Record food attendance (Lunch)
- **Dinner:** Record food attendance (Dinner)
- Generate separate reports for attendance vs. catering

### Scenario 3: Training Program
- **Session Attendance:** Track who attended training
- **Meal Service:** Track who took breakfast, lunch, or snacks
- Reconcile separately for training credit vs. catering count

---

## Audit Trail

Each food attendance record includes:
- ✅ **Scanner Username**: Who scanned the QR code
- ✅ **Timestamp**: Exact time (HH:MM:SS)
- ✅ **Date**: When recorded (YYYY-MM-DD)
- ✅ **Student ID**: Which student scanned
- ✅ **Event ID**: Which event
- ✅ **Food Type**: What meal was distributed

This provides complete traceability for compliance and verification.

---

## Advantages Over Combined Attendance

| Aspect | Combined | Separate (Food Attendance) |
|--------|----------|---------------------------|
| Data Clarity | Mixed purposes | Distinct purposes |
| Reporting | Single report | Separate reports |
| Flexibility | Limited | Multiple food types |
| Export | All or nothing | Filter by food type |
| Compliance | Confusing | Clear audit trail |
| Scalability | Difficult | Easy to extend |

---

## Future Enhancements

- [ ] Food attendance analytics dashboard
- [ ] Nutritional tracking integration
- [ ] Automated dietary preference tracking
- [ ] Integration with catering systems
- [ ] Mobile app support
- [ ] Real-time inventory updates
- [ ] Bulk food type import
- [ ] Statistical reports on food distribution

---

## Implementation Details

### Technology Stack
- **Database**: SQLite (separate table)
- **Backend**: Flask REST API (6 endpoints)
- **Frontend**: Flet UI (dedicated view)
- **Camera**: OpenCV + pyzbar (same QR scanner)
- **Architecture**: Multi-layer separation of concerns

### File Changes
- `final-project/src/database/db_manager.py` — Added 5 food attendance methods
- `final-project/src/api_server.py` — Added 5 API endpoints
- `final-project/src/views/food_attendance_view.py` — New dedicated view
- `final-project/src/app.py` — Route handler for /food-attendance/
- `final-project/src/views/home_view.py` — Menu item for food attendance

---

## Testing Checklist

- [ ] Create event
- [ ] Navigate to Food Attendance
- [ ] Select different food types
- [ ] Scan multiple QR codes
- [ ] Verify records in food_attendance table
- [ ] Check API endpoints return correct data
- [ ] Verify audit trail (scanner username, timestamps)
- [ ] Test with multiple users
- [ ] Verify separation from class attendance
- [ ] Check export functionality
- [ ] Test on different devices

---

## Troubleshooting

### Issue: Food attendance not recording
**Solution**: 
- Check if event_id is valid
- Verify student QR code exists
- Check database connectivity
- Review error logs

### Issue: Camera not working in food attendance view
**Solution**:
- Same as main scan view
- Ensure camera permissions granted
- Try ngrok for web access with HTTPS

### Issue: Food types not showing
**Solution**:
- First scan to create a food type
- Refresh the dropdown
- Check database for records

---

## Support

For issues or enhancements, contact the development team:
- macmac-12: Backend & Database
- thebaynal: Full Stack & DevOps

---

**Last Updated**: December 19, 2025
**Version**: 1.0
**Status**: Stable
