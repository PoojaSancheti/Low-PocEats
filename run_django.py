#!/usr/bin/env python
"""
Standalone Django runner that bypasses system Python corruption issues.
This script allows running the Django project without virtual environment dependencies.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run Django using the virtual environment Python to avoid system corruption."""
    project_root = Path(__file__).parent
    venv_python = project_root / "venv" / "Scripts" / "python.exe"
    manage_py = project_root / "manage.py"
    
    # Check if virtual environment exists
    if not venv_python.exists():
        print("Error: Virtual environment not found.")
        print("Please run setup_environment.bat first to create the virtual environment.")
        return 1
    
    # Check if manage.py exists
    if not manage_py.exists():
        print("Error: manage.py not found in project directory.")
        return 1
    
    # Get command line arguments (excluding script name)
    django_args = sys.argv[1:] if len(sys.argv) > 1 else ["runserver"]
    
    # Construct command
    cmd = [str(venv_python), str(manage_py)] + django_args
    
    try:
        # Run Django command
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode
    except KeyboardInterrupt:
        print("\nDjango server stopped.")
        return 0
    except Exception as e:
        print(f"Error running Django: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
