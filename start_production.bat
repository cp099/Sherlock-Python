@echo off
echo --- Starting Sherlock in PRODUCTION mode (HTTPS) ---

echo --- Detecting network IP... ---
for /f "tokens=1,2 delims=: " %%a in ('ipconfig^|find "IPv4 Address"') do set IP_ADDRESS=%%b
set IP_ADDRESS=%IP_ADDRESS:~1%
set SHERLOCK_ALLOWED_IP=%IP_ADDRESS%
echo --- Detected IP: %IP_ADDRESS% ---

echo --- Generating Caddyfile... ---
(
    echo # Caddyfile for Sherlock (auto-generated)
    echo 
    echo :8443 {
    echo     tls internal
    echo     reverse_proxy 127.0.0.1:8000
    echo }
) > Caddyfile


echo --- Running database migrations... ---
call venv\Scripts\activate.bat
python manage.py migrate --noinput
echo --- Collecting static files... ---
python manage.py collectstatic --noinput


echo --- Starting Caddy in the background... ---
start /b caddy run

echo.
echo =====================================================================
echo   Sherlock is now running securely!
echo   Access it from any device at: https://%IP_ADDRESS%:8443
echo   Or on this machine at:         https://localhost:8443
echo =====================================================================
echo.
echo Waitress is running in the foreground. Press Ctrl+C to stop the server.
echo When you are done, run the 'stop_production.bat' script to shut down Caddy.


python run.py