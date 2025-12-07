"""
api_server.py - REST API Server for QR Attendance Checker
Runs on localhost:5000 and provides secure database access via HTTP
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from functools import wraps

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import Database

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
db = Database()

# Security configuration
API_KEY = os.getenv('API_KEY', 'default_api_key_change_me')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# Request logging
request_count = 0

def log_request(endpoint, method, status):
    """Log API requests for monitoring"""
    global request_count
    request_count += 1
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Request #{request_count}: {method} {endpoint} - Status: {status}")

def require_api_key(f):
    """Decorator to require API key for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            log_request(request.path, request.method, 401)
            return jsonify({'error': 'Missing API key', 'status': 'unauthorized'}), 401
        
        if api_key != API_KEY:
            log_request(request.path, request.method, 401)
            return jsonify({'error': 'Invalid API key', 'status': 'unauthorized'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint - authenticates user and records login time"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            log_request('/api/login', 'POST', 400)
            return jsonify({'error': 'Missing username or password'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # Authenticate user
        authenticated_user = db.authenticate_user(username, password)
        
        if authenticated_user:
            # Record login
            db.record_login(authenticated_user)
            
            # Get user role
            user_role = db.get_user_role(authenticated_user)
            
            log_request('/api/login', 'POST', 200)
            return jsonify({
                'status': 'success',
                'message': f'Welcome, {authenticated_user}!',
                'username': authenticated_user,
                'role': user_role
            }), 200
        else:
            log_request('/api/login', 'POST', 401)
            return jsonify({
                'status': 'failed',
                'message': 'Invalid username or password'
            }), 401
    
    except Exception as e:
        print(f"Error in login endpoint: {e}")
        log_request('/api/login', 'POST', 500)
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/logout', methods=['POST'])
@require_api_key
def logout():
    """Logout endpoint - records logout time"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username'):
            log_request('/api/logout', 'POST', 400)
            return jsonify({'error': 'Missing username'}), 400
        
        username = data.get('username')
        db.record_logout(username)
        
        log_request('/api/logout', 'POST', 200)
        return jsonify({
            'status': 'success',
            'message': f'User {username} logged out'
        }), 200
    
    except Exception as e:
        print(f"Error in logout endpoint: {e}")
        log_request('/api/logout', 'POST', 500)
        return jsonify({'error': str(e), 'status': 'error'}), 500

# ============================================================================
# EVENT ENDPOINTS
# ============================================================================

@app.route('/api/events', methods=['GET'])
@require_api_key
def get_events():
    """Get all events"""
    try:
        events = db.get_all_events()
        log_request('/api/events', 'GET', 200)
        return jsonify({
            'status': 'success',
            'events': events,
            'count': len(events)
        }), 200
    
    except Exception as e:
        print(f"Error getting events: {e}")
        log_request('/api/events', 'GET', 500)
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/event/<event_id>', methods=['GET'])
@require_api_key
def get_event(event_id):
    """Get specific event by ID"""
    try:
        event = db.get_event_by_id(event_id)
        
        if not event:
            log_request(f'/api/event/{event_id}', 'GET', 404)
            return jsonify({'error': 'Event not found', 'status': 'not_found'}), 404
        
        log_request(f'/api/event/{event_id}', 'GET', 200)
        return jsonify({
            'status': 'success',
            'event': event
        }), 200
    
    except Exception as e:
        print(f"Error getting event: {e}")
        log_request(f'/api/event/{event_id}', 'GET', 500)
        return jsonify({'error': str(e), 'status': 'error'}), 500

# ============================================================================
# SCAN ENDPOINTS
# ============================================================================

@app.route('/api/record-scan', methods=['POST'])
@require_api_key
def record_scan():
    """Record a scan event (who scanned whom)"""
    try:
        data = request.get_json()
        
        required_fields = ['scanner_username', 'scanned_user_id', 'scanned_user_name', 'event_id']
        if not all(field in data for field in required_fields):
            log_request('/api/record-scan', 'POST', 400)
            return jsonify({'error': 'Missing required fields'}), 400
        
        db.record_scan(
            scanner_username=data.get('scanner_username'),
            scanned_user_id=data.get('scanned_user_id'),
            scanned_user_name=data.get('scanned_user_name'),
            event_id=data.get('event_id')
        )
        
        log_request('/api/record-scan', 'POST', 200)
        return jsonify({
            'status': 'success',
            'message': 'Scan recorded successfully'
        }), 200
    
    except Exception as e:
        print(f"Error recording scan: {e}")
        log_request('/api/record-scan', 'POST', 500)
        return jsonify({'error': str(e), 'status': 'error'}), 500

# ============================================================================
# ACTIVITY LOG ENDPOINTS
# ============================================================================

@app.route('/api/recent-logins', methods=['GET'])
@require_api_key
def recent_logins():
    """Get recent login history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        logins = db.get_recent_logins(limit)
        
        log_request('/api/recent-logins', 'GET', 200)
        return jsonify({
            'status': 'success',
            'logins': logins,
            'count': len(logins)
        }), 200
    
    except Exception as e:
        print(f"Error getting logins: {e}")
        log_request('/api/recent-logins', 'GET', 500)
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/recent-scans', methods=['GET'])
@require_api_key
def recent_scans():
    """Get recent scan history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        scans = db.get_recent_scans(limit)
        
        log_request('/api/recent-scans', 'GET', 200)
        return jsonify({
            'status': 'success',
            'scans': scans,
            'count': len(scans)
        }), 200
    
    except Exception as e:
        print(f"Error getting scans: {e}")
        log_request('/api/recent-scans', 'GET', 500)
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/scans-by-user/<username>', methods=['GET'])
@require_api_key
def scans_by_user(username):
    """Get scans performed by a specific user"""
    try:
        limit = request.args.get('limit', 50, type=int)
        scans = db.get_scans_by_scanner(username, limit)
        
        log_request(f'/api/scans-by-user/{username}', 'GET', 200)
        return jsonify({
            'status': 'success',
            'username': username,
            'scans': scans,
            'count': len(scans)
        }), 200
    
    except Exception as e:
        print(f"Error getting scans by user: {e}")
        log_request(f'/api/scans-by-user/{username}', 'GET', 500)
        return jsonify({'error': str(e), 'status': 'error'}), 500

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/create-user', methods=['POST'])
@require_api_key
def create_user():
    """Create a new user (admin only)"""
    try:
        data = request.get_json()
        
        required_fields = ['username', 'password', 'full_name', 'role']
        if not all(field in data for field in required_fields):
            log_request('/api/create-user', 'POST', 400)
            return jsonify({'error': 'Missing required fields'}), 400
        
        success = db.create_user(
            username=data.get('username'),
            password=data.get('password'),
            full_name=data.get('full_name'),
            role=data.get('role', 'scanner')
        )
        
        if success:
            log_request('/api/create-user', 'POST', 201)
            return jsonify({
                'status': 'success',
                'message': f'User {data.get("username")} created successfully'
            }), 201
        else:
            log_request('/api/create-user', 'POST', 400)
            return jsonify({
                'status': 'failed',
                'message': 'User already exists or creation failed'
            }), 400
    
    except Exception as e:
        print(f"Error creating user: {e}")
        log_request('/api/create-user', 'POST', 500)
        return jsonify({'error': str(e), 'status': 'error'}), 500

# ============================================================================
# HEALTH CHECK & STATUS ENDPOINTS
# ============================================================================

@app.route('/api/status', methods=['GET'])
def status():
    """Health check endpoint - no API key required"""
    try:
        return jsonify({
            'status': 'online',
            'message': 'QR Attendance API is running',
            'requests_processed': request_count,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/info', methods=['GET'])
@require_api_key
def info():
    """Get API information"""
    return jsonify({
        'status': 'success',
        'api': 'QR Attendance Checker API',
        'version': '1.0.0',
        'endpoints': {
            'auth': ['/api/login', '/api/logout'],
            'events': ['/api/events', '/api/event/<id>'],
            'scans': ['/api/record-scan', '/api/recent-scans', '/api/scans-by-user/<username>'],
            'users': ['/api/create-user'],
            'logs': ['/api/recent-logins', '/api/recent-scans'],
            'health': ['/api/status', '/api/info']
        }
    }), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'path': request.path
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("QR ATTENDANCE CHECKER - API SERVER")
    print("=" * 70)
    print(f"API Key: {API_KEY}")
    print(f"Debug Mode: {DEBUG_MODE}")
    print(f"Database: {os.getenv('DATABASE_NAME', 'mascan_attendance.db')}")
    print("=" * 70)
    print("Starting server on http://0.0.0.0:5000")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    
    # Run on all interfaces (accessible from phone on same network)
    app.run(host='0.0.0.0', port=5000, debug=DEBUG_MODE, use_reloader=False)
