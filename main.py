# Wrapper entry point for Flet build
# This imports and runs the actual main app from final-project/src/

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'final-project', 'src'))

# Import Flet
import flet as ft
from main import main as app_main

if __name__ == '__main__':
    ft.app(target=app_main)
