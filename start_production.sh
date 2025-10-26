#!/bin/bash


set -e

echo "--- Starting Sherlock in PRODUCTION mode (HTTPS) ---"


IP_ADDRESS=$(python -c "import socket;s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM);s.settimeout(0);s.connect(('10.254.254.254', 1));print(s.getsockname()[0]);s.close()")
HOSTNAME=$(hostname)
export SHERLOCK_ALLOWED_IP=$IP_ADDRESS

echo "--- Detected IP: $IP_ADDRESS ---"
echo "--- Detected Hostname: $HOSTNAME ---"


echo "--- Generating Caddyfile... ---"

cat > Caddyfile <<- EOM
# Caddyfile for Sherlock (auto-generated)

$IP_ADDRESS:8443, $HOSTNAME:8443, localhost:8443, 127.0.0.1:8443 {
    # 'tls internal' goes INSIDE the site block to apply a self-signed certificate.
    tls internal

    # Forward all traffic to our Waitress server.
    reverse_proxy 127.0.0.1:8000
}
EOM


echo "--- Running database migrations... ---"
python manage.py migrate --noinput
echo "--- Collecting static files... ---"
python manage.py collectstatic --noinput


cleanup() {
    echo -e "\n--- Shutting down Caddy server... ---"
    caddy stop
    exit
}
trap cleanup SIGINT SIGTERM

echo "--- Starting Caddy in the background... ---"
caddy start

echo "--- Starting Sherlock application server (Waitress)... ---"
echo
echo "====================================================================="
echo "  Sherlock is now running securely!"
echo "  Access it from any device at: https://$IP_ADDRESS:8443"
echo "  Or on this machine at:         https://localhost:8443"
echo "====================================================================="
echo
echo "Waitress is running in the foreground. Press Ctrl+C to stop everything."


python run.py