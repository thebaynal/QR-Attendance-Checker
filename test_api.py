#!/usr/bin/env python3
"""
API Endpoint Tester
Diagnose API server connectivity and endpoint issues.
"""

import requests
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "final-project" / "src"))

# Configuration
API_BASE_URL = "http://localhost:5000"
API_KEY = "QRAttendanceAPI_SecureKey_789!@#$%"

headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
}

def test_endpoint(method, endpoint, data=None):
    """Test a single API endpoint."""
    url = f"{API_BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"URL: {url}")
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method.upper() == 'POST':
            print(f"Data: {json.dumps(data, indent=2)}")
            response = requests.post(url, headers=headers, json=data, timeout=5)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ PASSED")
            return True
        else:
            print("❌ FAILED")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - API server not running")
        print(f"   Make sure to start the API server first:")
        print(f"   python final-project/src/api_server.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout - API server not responding")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("="*60)
    print("QR Attendance Checker - API Endpoint Tester")
    print("="*60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"API Key: {'*' * 20}...{API_KEY[-10:]}")
    
    # Test 1: Health check
    print("\n" + "="*60)
    print("TEST 1: HEALTH CHECK (No API Key Required)")
    print("="*60)
    try:
        response = requests.get(f"{API_BASE_URL}/api/status", timeout=5)
        print(f"✅ Server is running!")
        print(f"Status: {response.json()}")
    except:
        print("❌ Cannot connect to API server")
        print("Start the API server in another terminal:")
        print("  python final-project/src/api_server.py")
        return
    
    # Test 2: Authentication endpoints
    print("\n" + "="*60)
    print("TEST 2: AUTHENTICATION ENDPOINTS")
    print("="*60)
    
    # Test login
    test_endpoint('POST', '/api/login', {
        'username': 'admin',
        'password': 'Admin@123'
    })
    
    # Test 3: Events endpoints
    print("\n" + "="*60)
    print("TEST 3: EVENTS ENDPOINTS")
    print("="*60)
    
    test_endpoint('GET', '/api/events')
    
    # Test 4: Users endpoints
    print("\n" + "="*60)
    print("TEST 4: USERS ENDPOINTS")
    print("="*60)
    
    test_endpoint('GET', '/api/users')
    
    # Test 5: Students endpoints
    print("\n" + "="*60)
    print("TEST 5: STUDENTS ENDPOINTS")
    print("="*60)
    
    test_endpoint('GET', '/api/students')
    
    # Test 6: Activity endpoints
    print("\n" + "="*60)
    print("TEST 6: ACTIVITY ENDPOINTS")
    print("="*60)
    
    test_endpoint('GET', '/api/recent-scans')
    test_endpoint('GET', '/api/recent-logins')
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("If you see any '❌ FAILED' or 'Connection Error' messages:")
    print("\n1. Check if API server is running:")
    print("   python final-project/src/api_server.py")
    print("\n2. Verify the API key matches in:")
    print("   - api_server.py (API_KEY variable)")
    print("   - api_db_manager.py (api_key parameter)")
    print("\n3. Check firewall settings - port 5000 must be accessible")
    print("\n4. Review API server logs for detailed error messages")

if __name__ == '__main__':
    main()
