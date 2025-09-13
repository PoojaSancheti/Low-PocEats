@echo off
echo Setting up clean Django environment...

REM Remove existing virtual environment if it exists
if exist venv rmdir /s /q venv

REM Create new virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install Django
echo Installing Django...
pip install Django==5.1.3

REM Run Django checks
echo Running Django project checks...
python manage.py check

REM Run migrations
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

REM Create superuser (optional)
echo To create a superuser, run: python manage.py createsuperuser

echo Setup complete! To start the server, run: python manage.py runserver
pause
