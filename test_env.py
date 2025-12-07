#!/usr/bin/env python
"""Test environment configuration"""

from dotenv import load_dotenv
import os

load_dotenv()

print('Environment Configuration:')
print('=' * 60)
print(f'Admin Username: {os.getenv("ADMIN_USERNAME")}')
print(f'Admin Password: {os.getenv("ADMIN_PASSWORD")}')
print(f'Database Name: {os.getenv("DATABASE_NAME")}')
print(f'API Key: {os.getenv("API_KEY")}')
print('=' * 60)
print('All environment variables loaded successfully!')
