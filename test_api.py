#!/usr/bin/env python
"""Test API server startup"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'final-project', 'src'))

print('Testing API Server Import...')
print('=' * 60)

try:
    from api_server import app, db, API_KEY
    print('✓ API Server imported successfully')
    print(f'✓ Flask app initialized: {app.name}')
    print(f'✓ Database connected: {db.db_name}')
    print(f'✓ API Key configured: {API_KEY[:20]}...')
    print('=' * 60)
    print('API Server is ready to run!')
    print('\nTo start the server, run:')
    print('  python final-project/src/api_server.py')
except Exception as e:
    print(f'✗ Error importing API server: {e}')
    import traceback
    traceback.print_exc()
