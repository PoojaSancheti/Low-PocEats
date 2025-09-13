#!/usr/bin/env python
"""
Direct Django server starter that works around system Python corruption.
This script can be run directly with: python start_server.py
"""
import os
import sys
from pathlib import Path

# Add project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject2.settings')

def main():
    """Start Django development server directly."""
    try:
        # Import Django management utilities
        from django.core.management import execute_from_command_line
        
        # Check if this is being run directly
        if len(sys.argv) == 1:
            # Default to runserver if no arguments provided
            sys.argv = ['start_server.py', 'runserver']
        
        # Execute Django command
        execute_from_command_line(sys.argv)
        
    except ImportError as exc:
        print("Error: Django is not installed or not accessible.")
        print("Please install Django with: pip install Django==5.1.3")
        print(f"Original error: {exc}")
        return 1
    except Exception as e:
        print(f"Error starting Django server: {e}")
        return 1

if __name__ == '__main__':
    main()
