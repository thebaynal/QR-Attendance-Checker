# MaScan — QR Attendance Checker (Developer Documentation)

<h2>To-Do List</h2>
<ul>
    <li>Make export to CSV per event.</li> - DONE
    <li>Add "Download All QR" in the Generate QR Codes section.</li> - DONE
    <li>Add time options: Morning, Afternoon.
        <ul>
            <li>If food, also add Lunch (clickable).</li>
        </ul>
    </li>
    <li>Fix: Ensure students can only mark attendance <strong>once per session</strong> (e.g., Morning 1, Afternoon 1).</li>
    <li>Add category of attendance (Food or Attendance).</li>
    <li>UI improvements.</li>
</ul>

# MaScan — QR Attendance Checker (Developer Documentation)

This document describes the architecture, key components, data model, runtime flows, and developer guidelines for the MaScan application contained in this workspace.

Table of contents
- Overview
- Quick start
- Project layout (files & symbols)
- Core components and responsibilities
- Data model & database access
- Key runtime flows
  - App startup & routing
  - Authentication (login)
  - Event lifecycle (create / delete / view)
  - Scanning & QR processing
  - QR generation & download
  - User management
  - Export (PDF) flow
- Extending the app (adding views / features)
- Troubleshooting & notes

---

Overview
- MaScan is a desktop / web app built with Flet that provides event-based attendance tracking using QR codes.
- Main entry: [`main.main`](final-project/src/main.py) — see [final-project/src/main.py](final-project/src/main.py).
- App orchestrator: [`app.MaScanApp`](final-project/src/app.py) — see [final-project/src/app.py](final-project/src/app.py).

Quick start
1. Install dependencies (see project metadata): [final-project/pyproject.toml](final-project/pyproject.toml)
2. Run locally (development):
   - Using uv: `uv run flet run` (see [final-project/README.md](final-project/README.md))
   - Using poetry: `poetry run flet run`
3. Entry point: [`main.main`](final-project/src/main.py) (launches the Flet app).

Project layout (top-level)
- Application metadata: [final-project/pyproject.toml](final-project/pyproject.toml)
- App root: [final-project/src/main.py](final-project/src/main.py)
- Main application class: [`app.MaScanApp`](final-project/src/app.py)
- Views: [final-project/src/views/](final-project/src/views/)
- Database manager: [`database.db_manager.Database`](final-project/src/database/db_manager.py)
- Utilities: [`utils.qr_scanner.QRCameraScanner`](final-project/src/utils/qr_scanner.py)
- Configuration & constants: [`config.constants`](final-project/src/config/constants.py)

Core components and responsibilities

- Application shell
  - [`app.MaScanApp`](final-project/src/app.py)
    - Sets up Flet page, window, routing, and view instances.
    - Manages the current logged-in user, drawer/menu, and the active `QRCameraScanner`.
    - Key methods: route handling [`app.MaScanApp.route_change`](final-project/src/app.py), view pop handling [`app.MaScanApp.view_pop`](final-project/src/app.py), UI helpers like [`app.MaScanApp.create_app_bar`](final-project/src/app.py).

- Database manager
  - [`database.db_manager.Database`](final-project/src/database/db_manager.py)
    - Handles SQLite creation, schema migrations, and all DB operations.
    - Key methods:
      - Table creation & migration: [`database.db_manager.Database.create_tables`](final-project/src/database/db_manager.py)
      - Event CRUD: [`database.db_manager.Database.create_event`](final-project/src/database/db_manager.py), [`database.db_manager.Database.delete_event`](final-project/src/database/db_manager.py), [`database.db_manager.Database.get_all_events`](final-project/src/database/db_manager.py), [`database.db_manager.Database.get_event_by_id`](final-project/src/database/db_manager.py)
      - Attendance: [`database.db_manager.Database.record_attendance`](final-project/src/database/db_manager.py), [`database.db_manager.Database.get_attendance_by_event`](final-project/src/database/db_manager.py), [`database.db_manager.Database.is_user_checked_in`](final-project/src/database/db_manager.py)
      - Users / auth: [`database.db_manager.Database.authenticate_user`](final-project/src/database/db_manager.py), [`database.db_manager.Database.create_user`](final-project/src/database/db_manager.py), [`database.db_manager.Database.get_user_role`](final-project/src/database/db_manager.py)

- Views (UI)
  - Base helper: [`views.base_view.BaseView`](final-project/src/views/base_view.py) — common helpers for views.
  - Authentication: [`views.login_view.LoginView`](final-project/src/views/login_view.py)
  - Home / events list: [`views.home_view.HomeView`](final-project/src/views/home_view.py)
  - Create event: [`views.create_event_view.CreateEventView`](final-project/src/views/create_event_view.py)
  - Event detail & export: [`views.event_view.EventView`](final-project/src/views/event_view.py)
  - QR scanning: [`views.scan_view.ScanView`](final-project/src/views/scan_view.py)
  - QR generator: [`views.qr_generator_view.QRGeneratorView`](final-project/src/views/qr_generator_view.py)
  - User management (admin): [`views.user_management_view.UserManagementView`](final-project/src/views/user_management_view.py)

- Utilities
  - Camera scanner & QR detection: [`utils.qr_scanner.QRCameraScanner`](final-project/src/utils/qr_scanner.py)

- Configuration
  - UI and app constants: [`config.constants`](final-project/src/config/constants.py)

Data model & database access
- The SQLite schema is created in [`database.db_manager.Database.create_tables`](final-project/src/database/db_manager.py).
- Tables:
  - events: (id TEXT PRIMARY KEY, name TEXT, date TEXT, description TEXT)
  - attendance: (event_id, user_id, user_name, timestamp, status) — composite PK of (event_id, user_id)
  - users: (username PRIMARY KEY, password, full_name, role, created_at)
- Database helper: all SQL should use [`database.db_manager.Database._execute`](final-project/src/database/db_manager.py) to centralize error handling & connection management.
- Admin account: default admin is ensured/created in [`database.db_manager.Database.create_tables`](final-project/src/database/db_manager.py) and `_ensure_admin_role` (called in constructor).

Key runtime flows

1) App startup & routing
- Startup entry: [`main.main`](final-project/src/main.py).
- `MaScanApp` initializes and navigates to `/` which renders the login view by calling [`app.MaScanApp.route_change`](final-project/src/app.py) that invokes view builds.
- Views are registered as singletons in `MaScanApp.__init__` (e.g., [`views.home_view.HomeView`](final-project/src/views/home_view.py)).

2) Authentication (login)
- UI: [`views.login_view.LoginView.build`](final-project/src/views/login_view.py).
- On submit, it calls [`database.db_manager.Database.authenticate_user`](final-project/src/database/db_manager.py). If successful, sets `MaScanApp.current_user` and navigates to `/home` via [`app.MaScanApp.route_change`](final-project/src/app.py).

3) Event lifecycle
- Create event: [`views.create_event_view.CreateEventView.build`](final-project/src/views/create_event_view.py) → uses [`database.db_manager.Database.create_event`](final-project/src/database/db_manager.py).
- List events: [`views.home_view.HomeView.build`](final-project/src/views/home_view.py) → uses [`database.db_manager.Database.get_all_events`](final-project/src/database/db_manager.py).
- View event details & attendance: [`views.event_view.EventView.build`](final-project/src/views/event_view.py) → uses [`database.db_manager.Database.get_event_by_id`](final-project/src/database/db_manager.py) and [`database.db_manager.Database.get_attendance_by_event`](final-project/src/database/db_manager.py).
- Delete event: [`views.home_view.delete_event_handler`](final-project/src/views/home_view.py) calls [`database.db_manager.Database.delete_event`](final-project/src/database/db_manager.py).

4) Scanning & QR processing
- Scan UI: [`views.scan_view.ScanView.build`](final-project/src/views/scan_view.py).
- Camera scanning implementation: [`utils.qr_scanner.QRCameraScanner`](final-project/src/utils/qr_scanner.py)
  - Starts/stops the camera thread via `start()` / `stop()`.
  - Decodes QR codes using `pyzbar` and returns decoded payloads via `on_qr_detected` callback.
- Scan flow: scan view receives QR payloads (format expected: `ID|Name` or `ID`) and calls:
  - Check for duplicate: [`database.db_manager.Database.is_user_checked_in`](final-project/src/database/db_manager.py).
  - Record attendance: [`database.db_manager.Database.record_attendance`](final-project/src/database/db_manager.py).
- Manual entry: scan view provides text input and calls the same `process_scan`.

5) QR generation & download
- UI: [`views.qr_generator_view.QRGeneratorView.build`](final-project/src/views/qr_generator_view.py).
- Loads CSV via Flet file picker; uses `qrcode` and PIL to generate PNGs, encodes base64 for preview and offers download (saves to `~/Downloads/QR_Codes`).
- Download helper: `download_qr` (in the same view file) writes decoded base64 bytes to disk.

6) User management (admin)
- UI: [`views.user_management_view.UserManagementView.build`](final-project/src/views/user_management_view.py).
- CRUD: `create_user_handler` uses [`database.db_manager.Database.create_user`](final-project/src/database/db_manager.py).
- Listing: reads users through a raw SQL call via [`database.db_manager.Database._execute`](final-project/src/database/db_manager.py).

7) Export (PDF) flow
- Export implemented in [`views.event_view.EventView.build`](final-project/src/views/event_view.py) via `reportlab`.
- `export_data` builds a PDF saved to `~/Downloads/Attendance_Reports` with attendance table for the event.

Extending the app — adding a new view (concise checklist)
1. Create view class as subclass of [`views.base_view.BaseView`](final-project/src/views/base_view.py) under `final-project/src/views/`.
   - Implement `build()` to return `ft.View`.
2. Register the new view instance in [`app.MaScanApp.__init__`](final-project/src/app.py) (e.g., self.my_view = MyView(self)).
3. Add route handling in [`app.MaScanApp.route_change`](final-project/src/app.py) to return the view when `page.route` matches the route.
4. Optionally add navigation menu item in [`app.MaScanApp.create_drawer`](final-project/src/app.py).

Developer notes & troubleshooting
- Camera errors: ensure `opencv-python` and `pyzbar` are installed and system camera permissions are granted. Camera handling logic lives in [`utils.qr_scanner.QRCameraScanner`](final-project/src/utils/qr_scanner.py).
- Database file: `DATABASE_NAME` constant at [`config.constants.DATABASE_NAME`](final-project/src/config/constants.py) defaults to `mascan_attendance.db`. Use SQLite tools for debugging.
- Default credentials: see [`config.constants.DEFAULT_USERNAME`](final-project/src/config/constants.py) and [`config.constants.DEFAULT_PASSWORD`](final-project/src/config/constants.py). Database initialization ensures an admin user exists at startup in [`database.db_manager.Database.create_tables`](final-project/src/database/db_manager.py).
- Snacbkars and page updates are centralized via [`app.MaScanApp.show_snackbar`](final-project/src/app.py) and [`views.base_view.BaseView.show_snackbar`](final-project/src/views/base_view.py).
- If modifying views, avoid calling `page.go()` recursively inside route handling — `app.MaScanApp.route_change` contains protective patterns and fallback error view.

References (files & symbols)
- App entry & main
  - File: [final-project/src/main.py](final-project/src/main.py)
  - Symbol: [`main.main`](final-project/src/main.py)
- App orchestrator
  - File: [final-project/src/app.py](final-project/src/app.py)
  - Symbol: [`app.MaScanApp`](final-project/src/app.py)
- Database
  - File: [final-project/src/database/db_manager.py](final-project/src/database/db_manager.py)
  - Symbol: [`database.db_manager.Database`](final-project/src/database/db_manager.py)
  - Key methods:
    - [`database.db_manager.Database.create_tables`](final-project/src/database/db_manager.py)
    - [`database.db_manager.Database.create_event`](final-project/src/database/db_manager.py)
    - [`database.db_manager.Database.delete_event`](final-project/src/database/db_manager.py)
    - [`database.db_manager.Database.record_attendance`](final-project/src/database/db_manager.py)
    - [`database.db_manager.Database.get_attendance_by_event`](final-project/src/database/db_manager.py)
    - [`database.db_manager.Database.is_user_checked_in`](final-project/src/database/db_manager.py)
    - [`database.db_manager.Database.authenticate_user`](final-project/src/database/db_manager.py)
    - [`database.db_manager.Database.create_user`](final-project/src/database/db_manager.py)
- Views
  - [final-project/src/views/base_view.py](final-project/src/views/base_view.py) — [`views.base_view.BaseView`](final-project/src/views/base_view.py)
  - [final-project/src/views/login_view.py](final-project/src/views/login_view.py) — [`views.login_view.LoginView`](final-project/src/views/login_view.py)
  - [final-project/src/views/home_view.py](final-project/src/views/home_view.py) — [`views.home_view.HomeView`](final-project/src/views/home_view.py)
  - [final-project/src/views/create_event_view.py](final-project/src/views/create_event_view.py) — [`views.create_event_view.CreateEventView`](final-project/src/views/create_event_view.py)
  - [final-project/src/views/event_view.py](final-project/src/views/event_view.py) — [`views.event_view.EventView`](final-project/src/views/event_view.py)
  - [final-project/src/views/scan_view.py](final-project/src/views/scan_view.py) — [`views.scan_view.ScanView`](final-project/src/views/scan_view.py)
  - [final-project/src/views/qr_generator_view.py](final-project/src/views/qr_generator_view.py) — [`views.qr_generator_view.QRGeneratorView`](final-project/src/views/qr_generator_view.py)
  - [final-project/src/views/user_management_view.py](final-project/src/views/user_management_view.py) — [`views.user_management_view.UserManagementView`](final-project/src/views/user_management_view.py)
- Utilities
  - [final-project/src/utils/qr_scanner.py](final-project/src/utils/qr_scanner.py) — [`utils.qr_scanner.QRCameraScanner`](final-project/src/utils/qr_scanner.py)
- Config & constants
  - [final-project/src/config/constants.py](final-project/src/config/constants.py) — [`config.constants`](final-project/src/config/constants.py)
- Project docs
  - [final-project/README.md](final-project/README.md)
  - [final-project/pyproject.toml](final-project/pyproject.toml)

If you want, I can:
- Generate inline documentation comments for targeted modules (e.g., expand SQL docstrings in [`database.db_manager.Database`](final-project/src/database/db_manager.py)).
- Produce a concise developer quickstart checklist (scripts, test runners).
- Create unit test scaffolding for the DB layer and core view logic.
