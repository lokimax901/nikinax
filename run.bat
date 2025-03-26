@echo off
echo Starting the application...

REM Check if virtual environment exists
if not exist .venv (
    echo Virtual environment not found!
    echo Please run setup.bat first to set up the application.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if app.py exists
if not exist src\app.py (
    echo Application file not found!
    echo Please make sure src\app.py exists.
    pause
    exit /b 1
)

REM Run the application
echo Starting Flask application...
python src/app.py

REM Deactivate virtual environment when done
call deactivate

echo.
echo Application stopped.
pause 