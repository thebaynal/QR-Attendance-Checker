# Software Requirements Specification (SRS)
## MaScan — QR Attendance Checker System

**Document Version:** 1.0  
**Date:** December 8, 2025  
**Project:** QR-Attendance-Checker  
**Owner:** thebaynal  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features](#3-system-features)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [System Requirements](#5-system-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Security Requirements](#7-security-requirements)
8. [Database Design](#8-database-design)
9. [Appendices](#9-appendices)

---

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for MaScan, a comprehensive QR code-based attendance management system designed for schools, organizations, and events. The system enables administrators to manage events, generate QR codes for participants, and track attendance through QR code scanning.

### 1.2 Scope
MaScan is a desktop/web application built with Flet (Python UI framework) that provides:
- Event-based attendance tracking using QR codes
- Role-based user management (Admin/Scanner)
- Real-time QR code scanning via camera
- PDF and CSV export capabilities
- Activity monitoring and audit trails
- RESTful API for mobile access

### 1.3 Definitions, Acronyms, and Abbreviations
- **SRS**: Software Requirements Specification
- **QR**: Quick Response (code)
- **API**: Application Programming Interface
- **UI**: User Interface
- **SQLite**: SQL Database Engine
- **Flet**: Python UI framework based on Flutter
- **BCrypt**: Password hashing function
- **Admin**: Administrator user with full system access
- **Scanner**: Standard user with limited scanning privileges

### 1.4 References
- Flet Framework Documentation
- SQLite Database Documentation
- bcrypt Password Hashing Library
- ReportLab PDF Generation Library

---

## 2. Overall Description

### 2.1 Product Perspective
MaScan is a standalone desktop application with optional API server for mobile access. The system operates independently but can be extended to work in networked environments.

### 2.2 Product Functions
- **User Authentication**: Secure login system with role-based access control
- **Event Management**: Create, view, edit, and delete events
- **QR Code Generation**: Generate unique QR codes for participants
- **Attendance Tracking**: Real-time QR code scanning and attendance recording
- **Time-Slot Management**: Support for multiple attendance sessions (Morning, Afternoon, Lunch)
- **User Management**: Create and manage user accounts with different roles
- **Reporting**: Export attendance data to PDF and CSV formats
- **Activity Monitoring**: Track user logins, scans, and system activities
- **API Access**: RESTful API for mobile device integration

### 2.3 User Classes and Characteristics
1. **System Administrator**
   - Full system access
   - Event management privileges
   - User account creation and management
   - System configuration access
   - Activity log monitoring

2. **Scanner User**
   - Limited access to scanning functions
   - View-only access to attendance data
   - Cannot create or delete events
   - Cannot manage user accounts

### 2.4 Operating Environment
- **Operating System**: Windows, macOS, Linux
- **Python Version**: 3.8 or higher
- **Database**: SQLite 3.x
- **Web Browser**: Any modern browser (for web deployment)
- **Camera**: Required for QR code scanning functionality

### 2.5 Design and Implementation Constraints
- Must use Python and Flet framework
- SQLite database for local data storage
- Cross-platform compatibility required
- Offline operation capability
- Responsive UI design

---

## 3. System Features

### 3.1 User Authentication and Authorization

#### 3.1.1 Description
Secure login system with bcrypt password hashing and role-based access control.

#### 3.1.2 Functional Requirements
- **REQ-AUTH-001**: System shall authenticate users with username and password
- **REQ-AUTH-002**: System shall hash passwords using bcrypt with 12 rounds
- **REQ-AUTH-003**: System shall support two user roles: Admin and Scanner
- **REQ-AUTH-004**: System shall create default admin account on first run
- **REQ-AUTH-005**: System shall record login/logout activities in audit log
- **REQ-AUTH-006**: System shall display appropriate error messages for failed authentication

#### 3.1.3 Priority
High

### 3.2 Event Management

#### 3.2.1 Description
Comprehensive event creation, management, and deletion functionality for administrators.

#### 3.2.2 Functional Requirements
- **REQ-EVENT-001**: System shall allow admins to create new events with name, date, and description
- **REQ-EVENT-002**: System shall generate unique event IDs automatically
- **REQ-EVENT-003**: System shall display all events in chronological order
- **REQ-EVENT-004**: System shall allow admins to delete events and associated attendance data
- **REQ-EVENT-005**: System shall prevent deletion of events with existing attendance records (optional warning)
- **REQ-EVENT-006**: System shall validate event data before creation

#### 3.2.3 Priority
High

### 3.3 QR Code Generation

#### 3.3.1 Description
Generate QR codes for participants to enable attendance tracking.

#### 3.3.2 Functional Requirements
- **REQ-QR-001**: System shall generate unique QR codes containing user identification data
- **REQ-QR-002**: System shall support bulk QR code generation
- **REQ-QR-003**: System shall allow QR code download as image files
- **REQ-QR-004**: System shall provide "Download All QR" functionality
- **REQ-QR-005**: QR codes shall contain JSON-formatted user data
- **REQ-QR-006**: System shall validate QR code data format

#### 3.3.3 Priority
High

### 3.4 Attendance Scanning

#### 3.4.1 Description
Real-time QR code scanning using device camera with immediate attendance recording.

#### 3.4.2 Functional Requirements
- **REQ-SCAN-001**: System shall access device camera for QR code scanning
- **REQ-SCAN-002**: System shall decode QR codes in real-time
- **REQ-SCAN-003**: System shall record attendance with timestamp and user details
- **REQ-SCAN-004**: System shall support time-slot based attendance (Morning, Afternoon, Lunch)
- **REQ-SCAN-005**: System shall prevent duplicate attendance entries per time slot
- **REQ-SCAN-006**: System shall display immediate feedback for successful/failed scans
- **REQ-SCAN-007**: System shall record scanner identity with each attendance entry
- **REQ-SCAN-008**: System shall update attendance statistics in real-time

#### 3.4.3 Priority
High

### 3.5 User Management

#### 3.5.1 Description
Administrative functionality for creating and managing user accounts.

#### 3.5.2 Functional Requirements
- **REQ-USER-001**: System shall allow admins to create new user accounts
- **REQ-USER-002**: System shall assign roles (Admin/Scanner) to users
- **REQ-USER-003**: System shall store user full names and usernames
- **REQ-USER-004**: System shall prevent duplicate username creation
- **REQ-USER-005**: System shall validate user input data
- **REQ-USER-006**: System shall display list of all system users to admins

#### 3.5.3 Priority
Medium

### 3.6 Reporting and Export

#### 3.6.1 Description
Generate and export attendance reports in multiple formats.

#### 3.6.2 Functional Requirements
- **REQ-REPORT-001**: System shall export attendance data to PDF format
- **REQ-REPORT-002**: System shall export attendance data to CSV format
- **REQ-REPORT-003**: System shall generate per-event attendance reports
- **REQ-REPORT-004**: System shall include attendance statistics in reports
- **REQ-REPORT-005**: System shall support time-slot based reporting
- **REQ-REPORT-006**: Reports shall include event details, participant lists, and timestamps

#### 3.6.3 Priority
Medium

### 3.7 Activity Monitoring

#### 3.7.1 Description
Track and display system activities for audit and monitoring purposes.

#### 3.7.2 Functional Requirements
- **REQ-ACTIVITY-001**: System shall log all user login/logout events
- **REQ-ACTIVITY-002**: System shall log all QR code scan activities
- **REQ-ACTIVITY-003**: System shall display recent login history to admins
- **REQ-ACTIVITY-004**: System shall display recent scan activities to admins
- **REQ-ACTIVITY-005**: Activity logs shall include timestamps and user details
- **REQ-ACTIVITY-006**: System shall limit activity log display to prevent performance issues

#### 3.7.3 Priority
Low

### 3.8 API Access

#### 3.8.1 Description
RESTful API server for mobile device integration and remote access.

#### 3.8.2 Functional Requirements
- **REQ-API-001**: System shall provide REST API endpoints for all major functions
- **REQ-API-002**: API shall require authentication via API key
- **REQ-API-003**: API shall support user authentication endpoints
- **REQ-API-004**: API shall provide event and attendance data access
- **REQ-API-005**: API shall support CORS for web browser access
- **REQ-API-006**: API shall return JSON-formatted responses
- **REQ-API-007**: API shall include proper error handling and status codes

#### 3.8.3 Priority
Medium

---

## 4. External Interface Requirements

### 4.1 User Interfaces

#### 4.1.1 General UI Requirements
- **UI-001**: Interface shall be responsive and work on different screen sizes
- **UI-002**: Interface shall follow Material Design principles
- **UI-003**: Interface shall provide clear navigation between all functions
- **UI-004**: Interface shall display appropriate loading indicators for operations
- **UI-005**: Interface shall use consistent color scheme and typography

#### 4.1.2 Specific Interface Requirements
- **Login View**: Username/password fields, login button, error messages
- **Home View**: Event list, navigation menu, role-based action buttons
- **Event View**: Attendance list, statistics, export options
- **Scan View**: Camera feed, scan results, real-time feedback
- **Admin Views**: User management, QR generation, activity logs

### 4.2 Hardware Interfaces
- **HW-001**: System shall interface with device camera for QR code scanning
- **HW-002**: System shall work with USB cameras and built-in webcams
- **HW-003**: System shall handle camera initialization and error states

### 4.3 Software Interfaces

#### 4.3.1 Database Interface
- **SW-001**: System shall interface with SQLite database engine
- **SW-002**: System shall handle database connection errors gracefully
- **SW-003**: System shall support database migration and schema updates

#### 4.3.2 File System Interface
- **SW-004**: System shall read/write QR code images to file system
- **SW-005**: System shall export reports to user-specified directories
- **SW-006**: System shall handle file permission and access errors

### 4.4 Communication Interfaces
- **COMM-001**: API server shall communicate via HTTP/HTTPS protocols
- **COMM-002**: System shall support JSON data interchange format
- **COMM-003**: API shall support standard HTTP status codes and methods

---

## 5. System Requirements

### 5.1 Functional Requirements

#### 5.1.1 Authentication System
- Support for secure login/logout
- Password hashing with bcrypt
- Role-based access control
- Session management

#### 5.1.2 Data Management
- Event CRUD operations
- User CRUD operations
- Attendance tracking with time slots
- Data validation and integrity checks

#### 5.1.3 QR Code Processing
- QR code generation with user data
- Real-time QR code scanning
- Data extraction and validation
- Duplicate detection

#### 5.1.4 Reporting System
- PDF report generation
- CSV data export
- Attendance statistics calculation
- Time-based filtering

### 5.2 Performance Requirements

#### 5.2.1 Response Time
- **PERF-001**: User authentication shall complete within 2 seconds
- **PERF-002**: QR code scanning shall provide feedback within 1 second
- **PERF-003**: Database queries shall execute within 3 seconds
- **PERF-004**: Report generation shall complete within 10 seconds

#### 5.2.2 Throughput
- **PERF-005**: System shall support up to 1000 concurrent attendance records
- **PERF-006**: System shall handle up to 50 simultaneous QR code scans per minute
- **PERF-007**: API shall support up to 100 requests per minute

#### 5.2.3 Resource Usage
- **PERF-008**: Application shall use maximum 500MB RAM during normal operation
- **PERF-009**: Database size shall not impact performance for up to 10,000 records
- **PERF-010**: Camera access shall not exceed 30% CPU usage

---

## 6. Non-Functional Requirements

### 6.1 Reliability
- **REL-001**: System shall have 99% uptime during operational hours
- **REL-002**: System shall recover gracefully from camera disconnection
- **REL-003**: Database operations shall include transaction management
- **REL-004**: System shall handle unexpected shutdowns without data loss

### 6.2 Availability
- **AVAIL-001**: System shall be available for use 24/7 when deployed
- **AVAIL-002**: System shall continue operating during network outages (offline mode)
- **AVAIL-003**: Database shall be accessible even during heavy load periods

### 6.3 Maintainability
- **MAINT-001**: Code shall follow Python PEP 8 style guidelines
- **MAINT-002**: System shall include comprehensive error logging
- **MAINT-003**: Database schema shall support migration and updates
- **MAINT-004**: Configuration shall be externalized in .env files

### 6.4 Portability
- **PORT-001**: System shall run on Windows, macOS, and Linux
- **PORT-002**: System shall work with Python 3.8 or higher
- **PORT-003**: Database files shall be portable across operating systems
- **PORT-004**: System shall not require specific hardware dependencies

### 6.5 Usability
- **USE-001**: New users shall be able to perform basic operations within 5 minutes
- **USE-002**: Interface shall provide clear error messages and guidance
- **USE-003**: System shall include tooltips and help text for complex operations
- **USE-004**: Navigation shall be intuitive and consistent

---

## 7. Security Requirements

### 7.1 Authentication and Authorization
- **SEC-001**: All passwords shall be hashed using bcrypt with minimum 12 rounds
- **SEC-002**: User sessions shall timeout after 24 hours of inactivity
- **SEC-003**: API access shall require valid API key authentication
- **SEC-004**: Failed login attempts shall be logged for security monitoring

### 7.2 Data Protection
- **SEC-005**: Sensitive configuration data shall be stored in .env files
- **SEC-006**: .env files shall never be committed to version control
- **SEC-007**: Database access shall use parameterized queries to prevent SQL injection
- **SEC-008**: User data shall be validated and sanitized before storage

### 7.3 Audit and Logging
- **SEC-009**: System shall maintain audit logs of all user activities
- **SEC-010**: Logs shall include timestamps, user identities, and action details
- **SEC-011**: Security events shall be logged with appropriate severity levels
- **SEC-012**: Log files shall be protected from unauthorized modification

### 7.4 API Security
- **SEC-013**: API endpoints shall use HTTPS in production environments
- **SEC-014**: API keys shall be randomly generated with sufficient entropy
- **SEC-015**: API responses shall not expose sensitive system information
- **SEC-016**: Rate limiting shall be implemented to prevent abuse

---

## 8. Database Design

### 8.1 Database Schema

#### 8.1.1 Core Tables

**users**
- username (TEXT, PRIMARY KEY)
- password (TEXT, bcrypt hashed)
- full_name (TEXT)
- role (TEXT: 'admin' or 'scanner')
- created_at (TEXT, ISO format)

**events**
- id (TEXT, PRIMARY KEY, format: EID{timestamp}{random})
- name (TEXT, NOT NULL)
- date (TEXT, NOT NULL)
- description (TEXT)

**attendance**
- event_id (TEXT, FOREIGN KEY)
- user_id (TEXT)
- user_name (TEXT)
- timestamp (TEXT, ISO format)
- status (TEXT, default: 'Checked In')
- time_slot (TEXT, default: 'morning')
- PRIMARY KEY (event_id, user_id, time_slot)

#### 8.1.2 Activity Tracking Tables

**login_history**
- id (INTEGER, PRIMARY KEY)
- username (TEXT, FOREIGN KEY)
- login_time (TEXT, ISO format)

**scan_history**
- id (INTEGER, PRIMARY KEY)
- scanner_username (TEXT, FOREIGN KEY)
- scanned_user_id (TEXT)
- scanned_user_name (TEXT)
- event_id (TEXT, FOREIGN KEY)
- scan_time (TEXT, ISO format)

### 8.2 Data Integrity Constraints
- **DI-001**: Foreign key constraints shall be enforced
- **DI-002**: Unique constraints shall prevent duplicate usernames
- **DI-003**: NOT NULL constraints shall ensure required fields
- **DI-004**: Check constraints shall validate data ranges and formats

### 8.3 Database Operations
- **DB-001**: All operations shall use transactions for consistency
- **DB-002**: Database connections shall be properly closed
- **DB-003**: Error handling shall prevent database corruption
- **DB-004**: Backup and recovery procedures shall be implemented

---

## 9. Appendices

### 9.1 Technology Stack
- **Frontend Framework**: Flet (Python UI framework based on Flutter)
- **Database**: SQLite 3.x
- **Programming Language**: Python 3.8+
- **Password Hashing**: bcrypt
- **QR Code Processing**: qrcode library
- **PDF Generation**: ReportLab
- **API Framework**: Flask with CORS support
- **Environment Management**: python-dotenv

### 9.2 Development Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
cd final-project/src
python init_db.py

# Run application
python main.py

# Run API server (optional)
python api_server.py
```

### 9.3 Configuration Files
- **.env**: Environment variables (API keys, admin credentials)
- **requirements.txt**: Python package dependencies
- **pyproject.toml**: Project metadata and build configuration
- **.gitignore**: Version control exclusions (includes .env and database files)

### 9.4 Default Credentials
- **Username**: admin
- **Password**: Admin@123 (configurable via .env)
- **Role**: admin

### 9.5 API Endpoints
- `GET /api/status` - Health check
- `POST /api/login` - User authentication
- `GET /api/events` - List all events
- `POST /api/events` - Create new event
- `GET /api/attendance/{event_id}` - Get event attendance
- `POST /api/scan` - Record attendance scan
- `GET /api/recent-scans` - Get recent scan activity
- `GET /api/recent-logins` - Get recent login activity

### 9.6 Error Codes
- **E001**: Authentication failure
- **E002**: Insufficient permissions
- **E003**: Database connection error
- **E004**: Invalid QR code data
- **E005**: Camera access denied
- **E006**: File system access error
- **E007**: API key validation failure

---

**Document Control:**
- **Created by**: GitHub Copilot Assistant
- **Review Status**: Draft
- **Approval Status**: Pending
- **Next Review Date**: [To be determined]

---

*This SRS document serves as the definitive specification for the MaScan QR Attendance Checker system. All development and testing activities should align with the requirements outlined in this document.*