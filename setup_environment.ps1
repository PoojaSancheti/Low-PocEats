# PowerShell script to setup clean Django environment
Write-Host "Setting up clean Django environment..." -ForegroundColor Green

# Remove existing virtual environment if it exists
if (Test-Path "venv") {
    Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

# Create new virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Cyan
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install Django
Write-Host "Installing Django..." -ForegroundColor Cyan
pip install Django==5.1.3

# Run Django checks
Write-Host "Running Django project checks..." -ForegroundColor Cyan
python manage.py check

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Cyan
python manage.py makemigrations
python manage.py migrate

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "To create a superuser, run: python manage.py createsuperuser" -ForegroundColor Yellow
Write-Host "To start the server, run: python manage.py runserver" -ForegroundColor Yellow
