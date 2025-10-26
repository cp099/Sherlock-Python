# sherlock-python/run.py

"""
Production Server Entry Point for Sherlock.

This script is the main entry point when running the application from a 
packaged executable (via PyInstaller). It performs two key functions:

1.  Checks if the database exists on first run and, if not,
    automatically runs the initial Django migrations to create it.
2.  Starts the production-grade Waitress WSGI server to serve the
    Sherlock application.
"""

import os
import sys
import socket
from waitress import serve


def discover_and_set_host_ip():
    """Discovers the primary network IP and sets it as an environment variable."""
    detected_ip = '127.0.0.1'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        detected_ip = s.getsockname()[0]
        print(f"--- Automatically detected server IP: {detected_ip} ---")
    except Exception:
        print("--- Warning: Could not auto-detect network IP. Defaulting to localhost. ---")
    finally:
        s.close()
    os.environ['SHERLOCK_ALLOWED_IP'] = detected_ip
    return detected_ip

def run_migrations():
    """Checks if the database exists and runs migrations if it doesn't."""
    from django.core.management import execute_from_command_line
    if not os.path.exists(DB_FILE):
        print("--- Database not found. Running initial setup... ---")
        args = [sys.argv[0], 'migrate']
        execute_from_command_line(args)
        print("--- Database created successfully. ---")
    else:
        print("--- Database found. ---")

if __name__ == "__main__":
    server_ip = discover_and_set_host_ip()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sherlock.settings')

    DB_FILE = 'db.sqlite3'
    run_migrations()

    from sherlock.wsgi import application

    HOST = '0.0.0.0'
    PORT = 8000
    print("--- Starting Sherlock Production Server ---")
    print(f"Your application should be available at: http://{server_ip}:{PORT}")
    print("Press Ctrl+C to stop the server.")
    serve(application, host=HOST, port=PORT)