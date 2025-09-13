#!/usr/bin/env python
"""
Wrapper script to run Django server without virtual environment issues
"""
import subprocess
import sys
import os

def main():
    # Use the virtual environment Python but make it transparent to user
    venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'Scripts', 'python.exe')
    
    if os.path.exists(venv_python):
        # Run Django server using clean virtual environment Python
        cmd = [venv_python, 'manage.py', 'runserver']
        try:
            subprocess.run(cmd, cwd=os.path.dirname(__file__))
        except KeyboardInterrupt:
            print("\nServer stopped.")
    else:
        print("Virtual environment not found. Please run setup_environment.bat first.")

if __name__ == '__main__':
    main()
