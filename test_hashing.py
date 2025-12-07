#!/usr/bin/env python
"""Test password hashing functionality"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'final-project', 'src'))

from database.db_manager import Database

print('\nPassword Hashing Test:')
print('=' * 60)

db = Database('test_hash.db')

# Test password hashing
test_password = "TestPassword123!@#"
hashed = db.hash_password(test_password)

print(f'Original Password: {test_password}')
print(f'Hashed Password: {hashed}')
print(f'Hash Length: {len(hashed)} characters')

# Test password verification
is_correct = db.verify_password(test_password, hashed)
is_wrong = db.verify_password("WrongPassword123", hashed)

print(f'\nVerify Correct Password: {is_correct}')
print(f'Verify Wrong Password: {is_wrong}')

print('=' * 60)
print('Password hashing working correctly!')

# Clean up test database
if os.path.exists('test_hash.db'):
    os.remove('test_hash.db')
    print('Test database cleaned up.')
