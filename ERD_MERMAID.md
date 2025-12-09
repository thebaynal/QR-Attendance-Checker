```mermaid
erDiagram
    USERS ||--o{ LOGIN_HISTORY : generates
    USERS ||--o{ SCAN_HISTORY : performs
    EVENTS ||--o{ ATTENDANCE : contains
    EVENTS ||--o{ SCAN_HISTORY : records
    EVENTS ||--o{ ATTENDANCE_TIMESLOTS : tracks
    STUDENTS_QRCODES ||--o{ SCAN_HISTORY : "is_scanned_in"
    STUDENTS_QRCODES ||--o{ ATTENDANCE_TIMESLOTS : "attends"

    USERS {
        string username PK
        string password
        string full_name
        string role
        string created_at
    }

    EVENTS {
        string id PK
        string name
        string date
        string description
    }

    ATTENDANCE {
        string event_id FK, PK
        string user_id PK
        string user_name
        string timestamp
        string status
        string time_slot PK
    }

    LOGIN_HISTORY {
        int id PK
        string username FK
        string login_time
        string logout_time
    }

    SCAN_HISTORY {
        int id PK
        string scanner_username FK
        string scanned_user_id FK
        string scanned_user_name
        string event_id FK
        string scan_time
    }

    STUDENTS_QRCODES {
        int id PK
        string school_id UK
        string name
        string year_level
        string section
        string qr_data UK
        string qr_data_encoded
        string csv_data
        string created_at
    }

    ATTENDANCE_TIMESLOTS {
        int id PK
        string event_id FK
        string user_id FK
        string morning_time
        string morning_status
        string lunch_time
        string lunch_status
        string afternoon_time
        string afternoon_status
        string date_recorded
    }
```

## Entity Relationship Legend

### Symbols
- `||` = One
- `o{` = Zero or more
- `||--o{` = One-to-Many relationship

### Notation
- **PK** = Primary Key (unique identifier)
- **FK** = Foreign Key (references another table)
- **UK** = Unique Key (must be unique, but not primary key)

## Relationships Explained

| From | To | Relationship | Meaning |
|------|-----|--------------|---------|
| USERS | LOGIN_HISTORY | 1:N | One user can have many login sessions |
| USERS | SCAN_HISTORY | 1:N | One user (scanner) can perform many scans |
| EVENTS | ATTENDANCE | 1:N | One event can have many attendance records |
| EVENTS | SCAN_HISTORY | 1:N | One event can have many scans recorded |
| EVENTS | ATTENDANCE_TIMESLOTS | 1:N | One event tracks multiple students |
| STUDENTS_QRCODES | SCAN_HISTORY | 1:N | One student can be scanned multiple times |
| STUDENTS_QRCODES | ATTENDANCE_TIMESLOTS | 1:N | One student has records per event |

## Quick Summary

**Core Tables (3)**
- USERS: User accounts and authentication
- EVENTS: Attendance events
- STUDENTS_QRCODES: Student records with QR codes

**Attendance Tables (2)**
- ATTENDANCE: Legacy attendance records
- ATTENDANCE_TIMESLOTS: New structure with morning/lunch/afternoon support

**Audit Tables (2)**
- LOGIN_HISTORY: User session tracking
- SCAN_HISTORY: Complete scan audit trail

