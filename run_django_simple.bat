@echo off
REM Simple Django runner that uses virtual environment to avoid system Python corruption
REM Usage: run_django_simple.bat [django_command]
REM Example: run_django_simple.bat runserver
REM Example: run_django_simple.bat check

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found.
    echo Please run setup_environment.bat first.
    pause
    exit /b 1
)

if "%1"=="" (
    echo Starting Django development server...
    venv\Scripts\python.exe manage.py runserver
) else (
    echo Running Django command: %*
    venv\Scripts\python.exe manage.py %*
)

if errorlevel 1 (
    echo.
    echo Django command failed with error code %errorlevel%
    pause
)
