# Software Requirements Specification for MaScan: QR Attendance Checker System

**Prepared by:** thebaynal  
**Date:** December 8, 2025  
**Version:** 1.0  

---

## 1. Introduction
This section provides an overview of the SRS document.

### 1.1 Purpose
The purpose of this Software Requirements Specification (SRS) document is to describe in detail all the requirements for the MaScan: QR Attendance Checker System. This document serves as a guide for the development team, testers, and future system maintainers to understand what the system must do and how it should function.

This SRS aims to:
- Provide a clear and precise description of system requirements (functional and non-functional)
- Serve as a foundation for system design, implementation, verification, and validation
- Reduce risks related to ambiguous, incomplete, or conflicting requirements
- Enable stakeholders to confirm that the system meets their needs before major development begins
- Clearly explain the system's functional and non-functional requirements
- Serve as a reference for development, testing, and future improvements
- Ensure the team has a shared understanding of the system's purpose and limitations
- Help verify that the final output meets the needs of its intended users

### 1.2 Scope
MaScan is a desktop/web application built with Flet (Python UI framework) intended to simplify and automate attendance management for academic or organizational events. The system allows administrators to create events, manage user accounts, generate personalized QR codes, and verify attendance through real-time scanning. It also provides comprehensive reporting capabilities and activity monitoring.

This document covers:
- All functional modules (authentication, event management, QR generation, scanning, user management, reporting)
- Non-functional requirements (performance, usability, security, reliability, scalability, compatibility)
- Interfaces with external systems and hardware components
- Database design and security requirements

This document does not address:
- Detailed internal design (classes, data structures, algorithms)
- Specific implementation technologies beyond the chosen framework
- Post-release maintenance, enhancements beyond version 1.0, or training manuals

### 1.3 Definitions, Acronyms, and Abbreviations

| Abbreviation/Term | Meaning/Definition |
|-------------------|--------------------|
| SRS | Software Requirements Specification |
| QR | Quick Response (code) |
| API | Application Programming Interface |
| UI | User Interface |
| SQLite | SQL Database Engine |
| Flet | Python UI framework based on Flutter |
| BCrypt | Password hashing function |
| ADMIN | A user who manages events, handles attendance, and manages users |
| SCANNER | A user who registers attendees via QR code scanning |
| CSV | Comma-Separated Value |
| PDF | Portable Document Format |

### 1.4 References
- ISO/IEC/IEEE 29148:2018 - Systems and software engineering — Life cycle processes — Requirements engineering
- Flet Framework Documentation
- SQLite Database Documentation
- bcrypt Password Hashing Library
- ReportLab PDF Generation Library

### 1.5 Overview
This document is organized into three main sections. Section 1 provides an introduction. Section 2 gives an overall description of the product, its users, and its operational constraints. Section 3 details the specific functional and non-functional requirements.

## 2. Overall Description
This section describes the general factors that affect the product and its requirements.

### 2.1 Product Perspective
MaScan is a desktop/web-based system developed to streamline and digitize attendance management for schools and organizations. It replaces manual attendance sheets with a QR code-based system where each participant is assigned a unique QR code. Administrators can create and manage events within the system, generating distinct attendance records per event. During events, scanner users scan the participants' QR codes to log their participation.

This system serves as a unified platform for event management and attendance tracking, enhancing accuracy, efficiency, and accountability within organizations.

### 2.2 Product Functions
The system provides the following core functions:
- **User Registration and Authentication**: Allows both participants and organizers to register, log in, and securely access their respective dashboards
- **QR Code Generation**: Generates unique QR codes for each participant for attendance tracking
- **Event Creation and Management**: Enables administrators to create, edit, and delete events. Each event has its own attendance list and record
- **QR Code Scanning**: Organizers can scan participants' QR codes to mark attendance for specific events with time-slot support (Morning, Afternoon, Lunch)
- **Attendance Recording**: Logs attendance data automatically into the system database, including event name, time, date, and participant information
- **User Management**: Administrators can create and manage user accounts with role-based permissions
- **Attendance Reports and Export**: Provides comprehensive attendance summaries for each event, allowing organizers to view, filter, and export data to PDF and CSV formats
- **Activity Monitoring**: Tracks user logins, scans, and system activities for audit purposes
- **Real-Time Data Processing**: Updates attendance records instantly to ensure accurate tracking

### 2.3 User Characteristics
**System Administrator**: Tech-literate individual comfortable using desktop and web applications. Primary goals are to manage the entire system, create events, manage users, and generate comprehensive reports. Has full system access and administrative privileges.

**Scanner User**: Technologically proficient user with access to scanning devices. Primary goal is to efficiently record attendance through QR code scanning. Has limited permissions focused on attendance recording and viewing.

### 2.4 Constraints
- **Device Compatibility**: Scanner users must have devices with cameras capable of QR code scanning
- **Data Privacy**: The system must comply with institutional data protection standards and privacy regulations
- **Database Limitations**: The system relies on SQLite database capacity for storing user, event, and attendance data
- **Platform Requirements**: System requires Python 3.8+ and compatible operating system (Windows, macOS, Linux)
- **User Access Management**: Proper authentication must be maintained to prevent unauthorized access to event or user data
- **Camera Access**: QR code scanning functionality depends on camera hardware availability and permissions

### 2.5 Assumptions and Dependencies
- Each participant can be registered in the system and provided with a unique QR code for events
- Administrators are authorized users who can create and manage events within the system
- Scanning devices with camera capabilities are available during events
- The system depends on stable third-party libraries for QR code generation and scanning (qrcode, OpenCV)
- Users are expected to cooperate in presenting valid QR codes and maintaining accurate registration data
- Python runtime environment and required dependencies are properly installed and configured

## 3. Specific Requirements
This section contains the detailed requirements necessary to build the system.

### 3.1 Functional Requirements
This details what the system should do.

**FR-001: User Authentication**  
The system shall allow users (administrators and scanner users) to log in using their credentials. After login, the system shall identify the user's role (Admin or Scanner) and display the appropriate interface and permissions. The system shall hash passwords using bcrypt with 12 rounds and create a default admin account on first run.

**FR-002: Event Management (Administrator)**  
An authenticated Administrator must be able to create and manage events. For each event, they must be able to define event details including name, date, and description. The system shall generate unique event IDs automatically and display all events in chronological order. Administrators shall be able to delete events and associated attendance data.

**FR-003: QR Code Generation and Management**  
The system shall generate unique QR codes containing user identification data. Upon successful user creation, the system shall generate a unique QR code for each user. The system must support bulk QR code generation and allow QR code download as image files, including "Download All QR" functionality.

**FR-004: Attendance Verification via Scanning**  
During an event, an authenticated Scanner user must use the application's camera to read a participant's QR code. A successful scan shall validate the code and mark the participant as "Present" in the event roster with timestamp. The system must support time-slot based attendance (Morning, Afternoon, Lunch) and prevent duplicate attendance entries per time slot.

**FR-005: User Management (Administrator)**  
An Administrator shall be able to create and manage user accounts within the system. They must be able to assign roles (Admin/Scanner) to users, store user full names and usernames, and prevent duplicate username creation. The system shall display a list of all system users to administrators.

**FR-006: Manual Check-In (Scanner)**  
A Scanner user shall be able to look up a registered participant by name or ID in the event roster and manually mark them as "Present." This serves as a backup for participants who cannot present their QR code or in case of technical difficulties.

**FR-007: Export Attendance Reports**  
Administrators shall be able to export attendance reports for specific events in multiple formats (PDF and CSV). The reports should include participant details, attendance status, check-in timestamps, and attendance statistics. The system shall support time-slot based reporting.

**FR-008: Activity Monitoring and Audit Trail**  
The system shall log all user activities including login/logout events and QR code scan activities. Administrators shall be able to view recent login history and scan activities. Activity logs shall include timestamps, user details, and action descriptions for audit purposes.

### 3.2 Non-Functional Requirements
This details how the system should perform its functions.

**NFR-001: Performance**  
The system must validate a QR code scan and provide feedback to the Scanner within 2 seconds. User authentication shall complete within 2 seconds. Database queries shall execute within 3 seconds, and report generation shall complete within 10 seconds under normal operating conditions.

**NFR-002: Usability**  
The user interfaces for both the scanning interface and the administrator's management dashboard must be intuitive. A new Scanner should be able to perform core tasks (scan QR codes, mark attendance) without needing extensive training. Navigation shall be consistent and provide clear error messages and guidance.

**NFR-003: Security**  
All passwords shall be hashed using bcrypt with minimum 12 rounds. The system must protect all Personally Identifiable Information (PII), both in transit and at rest. API access shall require valid API key authentication, and failed login attempts shall be logged for security monitoring.

**NFR-004: Reliability**  
The system shall maintain stable operation during normal use. Core functionalities, especially QR code scanning and attendance recording, must be fully operational during events. The system shall recover gracefully from camera disconnection and handle unexpected shutdowns without data loss.

**NFR-005: Scalability**  
The system must support up to 1000 concurrent attendance records and handle up to 50 simultaneous QR code scans per minute. The database size shall not impact performance for up to 10,000 records. Multiple Scanner users must be able to operate concurrently without performance degradation.

**NFR-006: Compatibility**  
The system must run on Windows, macOS, and Linux operating systems. It shall work with Python 3.8 or higher and be compatible with various camera devices for QR code scanning. Database files shall be portable across operating systems.

---

*This SRS document serves as the definitive specification for the MaScan QR Attendance Checker system. All development and testing activities should align with the requirements outlined in this document.*

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

*This SRS document serves as the definitive specification for the MaScan QR Attendance Checker system. All development and testing activities should align with the requirements outlined in this document.*