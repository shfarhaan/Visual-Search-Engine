@echo off
REM Startup script for Visual Search Engine (Windows)

echo Starting Visual Search Engine...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
if not exist "data\" mkdir data
if not exist "uploads\" mkdir uploads
if not exist "sample_images\" mkdir sample_images

REM Start the application
echo Starting application on http://localhost:5000
python app.py

pause
