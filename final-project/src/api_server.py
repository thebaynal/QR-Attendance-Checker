# api_server.py
"""REST API server for QR Attendance Checker - provides network access to database."""

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import os
from dotenv import load_dotenv
from database.db_manager import Database

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
db = Database()

# Configuration
API_KEY = os.getenv('API_KEY', 'QRAttendanceAPI_SecureKey_789!@#$%')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ============================================================================
# API KEY AUTHENTICATION
# ============================================================================

def require_api_key(f):
    """Decorator to require API key for endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# PUBLIC ENDPOINTS (No API key required)
# ============================================================================

# ============================================================================
# PUBLIC ENDPOINTS (No API key required)
# ============================================================================

@app.route('/api/status', methods=['GET'])
def status():
    """Health check endpoint - no auth required."""
    return jsonify({
        'status': 'ok',
        'service': 'QR Attendance Checker API',
        'version': '1.0.0'
    }), 200

@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint - authenticate user with username and password."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Authenticate user
        authenticated_user = db.authenticate_user(username, password)
        
        if authenticated_user:
            # Record login
            db.record_login(username)
            return jsonify({
                'success': True,
                'username': authenticated_user,
                'message': 'Login successful'
            }), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PROTECTED ENDPOINTS (API key required)
# ============================================================================

@app.route('/api/logout', methods=['POST'])
@require_api_key
def logout():
    """Logout endpoint - record logout event."""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if username:
            db.record_logout(username)
        
        return jsonify({'success': True, 'message': 'Logout recorded'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events', methods=['GET'])
@require_api_key
def get_events():
    """Get all events."""
    try:
        events = db.get_all_events()
        return jsonify(events), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events', methods=['POST'])
@require_api_key
def create_event():
    """Create new event."""
    try:
        data = request.get_json()
        name = data.get('name')
        date = data.get('date')
        description = data.get('description', '')
        
        if not all([name, date]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Use the database's create_event which generates the ID
        event_id = db.create_event(name, date, description)
        return jsonify({'success': True, 'message': 'Event created', 'event_id': event_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<event_id>', methods=['DELETE'])
@require_api_key
def delete_event_endpoint(event_id):
    """Delete an event."""
    try:
        db._execute("DELETE FROM attendance_timeslots WHERE event_id = ?", (event_id,))
        db._execute("DELETE FROM events WHERE id = ?", (event_id,))
        return jsonify({'success': True, 'message': 'Event deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
@require_api_key
def get_users():
    """Get all users."""
    try:
        users = db.get_all_users()
        # Convert list of tuples to dict format
        users_dict = {}
        for username, full_name, role in users:
            users_dict[username] = {
                'full_name': full_name,
                'role': role
            }
        return jsonify(users_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
@require_api_key
def create_user():
    """Create new user."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        full_name = data.get('full_name')
        role = data.get('role', 'scanner')
        
        if not all([username, password, full_name]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        db.create_user(username, password, full_name, role)
        return jsonify({'success': True, 'message': 'User created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<username>', methods=['GET'])
@require_api_key
def get_user_by_username(username):
    """Get user role by username."""
    try:
        role = db.get_user_role(username)
        if role:
            return jsonify({'username': username, 'role': role}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<username>', methods=['DELETE'])
@require_api_key
def delete_user(username):
    """Delete a user."""
    try:
        db._execute("DELETE FROM users WHERE username = ?", (username,))
        return jsonify({'success': True, 'message': 'User deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/record-scan', methods=['POST'])
@require_api_key
def record_scan():
    """Record a QR code scan."""
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        scanned_user_id = data.get('scanned_user_id')
        scanned_user_name = data.get('scanned_user_name')
        scanner_username = data.get('scanner_username')
        
        if not all([event_id, scanned_user_id, scanner_username]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Record attendance
        db.record_attendance(event_id, scanned_user_id, scanned_user_name, 'present', 'morning')
        
        # Record scan in activity log
        db.record_scan(scanner_username, scanned_user_id, scanned_user_name)
        
        return jsonify({'success': True, 'message': 'Scan recorded'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent-scans', methods=['GET'])
@require_api_key
def recent_scans():
    """Get recent scan activity."""
    try:
        limit = request.args.get('limit', 10, type=int)
        scans = db.get_recent_scans(limit)
        return jsonify(scans), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent-logins', methods=['GET'])
@require_api_key
def recent_logins():
    """Get recent login activity."""
    try:
        limit = request.args.get('limit', 10, type=int)
        logins = db.get_recent_logins(limit)
        return jsonify(logins), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance/<event_id>', methods=['GET'])
@require_api_key
def get_attendance(event_id):
    """Get attendance for an event."""
    try:
        attendance = db.get_attendance_by_event(event_id)
        return jsonify(attendance), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<school_id>', methods=['GET'])
@require_api_key
def get_student(school_id):
    """Get student information by school ID."""
    try:
        student = db.get_student_by_id(school_id)
        if student:
            return jsonify(student), 200
        else:
            return jsonify({'error': 'Student not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students', methods=['POST'])
@require_api_key
def create_student():
    """Create or update student."""
    try:
        data = request.get_json()
        school_id = data.get('school_id')
        name = data.get('name')
        qr_data = data.get('qr_data')
        qr_data_encoded = data.get('qr_data_encoded')
        csv_data = data.get('csv_data')
        last_name = data.get('last_name')
        first_name = data.get('first_name')
        middle_initial = data.get('middle_initial')
        
        if not all([school_id, name, qr_data, qr_data_encoded]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Ensure table exists with new columns
        db._execute("""
        CREATE TABLE IF NOT EXISTS students_qrcodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            last_name TEXT,
            first_name TEXT,
            middle_initial TEXT,
            qr_data TEXT NOT NULL UNIQUE,
            qr_data_encoded TEXT NOT NULL,
            csv_data TEXT,
            created_at TEXT NOT NULL
        )
        """)
        
        # Ensure new columns exist (migration)
        try:
            db._add_column_if_not_exists('students_qrcodes', 'last_name', 'TEXT')
            db._add_column_if_not_exists('students_qrcodes', 'first_name', 'TEXT')
            db._add_column_if_not_exists('students_qrcodes', 'middle_initial', 'TEXT')
        except:
            pass
        
        # Check if student exists
        existing = db._execute("SELECT id FROM students_qrcodes WHERE school_id = ?", (school_id,), fetch_one=True)
        
        if existing:
            # Update
            db._execute("""
            UPDATE students_qrcodes 
            SET name = ?, qr_data = ?, qr_data_encoded = ?, csv_data = ?, last_name = ?, first_name = ?, middle_initial = ?
            WHERE school_id = ?
            """, (name, qr_data, qr_data_encoded, csv_data, last_name, first_name, middle_initial, school_id))
        else:
            # Insert
            from datetime import datetime
            db._execute("""
            INSERT INTO students_qrcodes 
            (school_id, name, qr_data, qr_data_encoded, csv_data, last_name, first_name, middle_initial, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (school_id, name, qr_data, qr_data_encoded, csv_data, last_name, first_name, middle_initial, datetime.now().isoformat()))
        
        return jsonify({'success': True, 'message': 'Student saved', 'school_id': school_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<school_id>', methods=['POST'])
@require_api_key
def update_student(school_id):
    """Update student."""
    try:
        data = request.get_json()
        name = data.get('name')
        qr_data = data.get('qr_data')
        qr_data_encoded = data.get('qr_data_encoded')
        csv_data = data.get('csv_data')
        
        db._execute("""
        UPDATE students_qrcodes 
        SET name = ?, qr_data = ?, qr_data_encoded = ?, csv_data = ?
        WHERE school_id = ?
        """, (name, qr_data, qr_data_encoded, csv_data, school_id))
        
        return jsonify({'success': True, 'message': 'Student updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance-by-section/<event_id>', methods=['GET'])
@require_api_key
def get_attendance_by_section(event_id):
    """Get attendance grouped by year and section."""
    try:
        attendance = db.get_attendance_by_section(event_id)
        return jsonify(attendance), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-timeslot/<event_id>/<school_id>/<time_slot>', methods=['GET'])
@require_api_key
def check_timeslot(event_id, school_id, time_slot):
    """Check if student already checked in for time slot."""
    try:
        checked_in = db.check_timeslot_attendance(event_id, school_id, time_slot)
        return jsonify({'checked_in': checked_in}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/record-timeslot', methods=['POST'])
@require_api_key
def record_timeslot():
    """Record attendance for specific time slot."""
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        school_id = data.get('school_id')
        time_slot = data.get('time_slot')
        
        if not all([event_id, school_id, time_slot]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success = db.record_timeslot_attendance(event_id, school_id, time_slot)
        if success:
            return jsonify({'success': True, 'message': 'Timeslot attendance recorded'}), 200
        else:
            return jsonify({'error': 'Failed to record attendance'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance-summary/<event_id>', methods=['GET'])
@require_api_key
def get_attendance_summary(event_id):
    """Get attendance summary for an event."""
    try:
        summary = db.get_attendance_summary(event_id)
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("QR ATTENDANCE CHECKER - API SERVER")
    print("=" * 60)
    print(f"API Key: {API_KEY}")
    print(f"Debug Mode: {DEBUG}")
    print(f"Database: mascan_attendance.db")
    print("=" * 60)
    print("Starting server on http://0.0.0.0:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)
