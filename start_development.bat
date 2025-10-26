@echo off
echo --- Starting Sherlock in DEVELOPMENT mode (HTTP) ---
echo --- Access at: http://127.0.0.1:8000
echo --- Press Ctrl+C to stop the server.

REM
call venv\Scripts\activate.bat
python manage.py runserver