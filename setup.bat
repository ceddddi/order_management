@echo off
echo Installing Order Management System
echo ==============================
echo.

:: Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo Python is not installed!
    echo Please install Python from https://www.python.org/downloads/
    echo And make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error creating virtual environment!
    pause
    exit /b 1
)

:: Activate virtual environment and install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error installing dependencies!
    pause
    exit /b 1
)

:: Initialize database
echo Initializing database...
python database.py
if errorlevel 1 (
    echo Error initializing database!
    pause
    exit /b 1
)

echo.
echo ==============================
echo Installation completed successfully!
echo.
echo Use start_app.bat to run the application
echo.
pause
