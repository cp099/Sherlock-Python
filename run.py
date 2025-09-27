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
from waitress import serve
from sherlock.wsgi import application
from django.core.management import execute_from_command_line

HOST = '0.0.0.0'
PORT = 8000
DB_FILE = 'db.sqlite3'

def run_migrations():
    """Checks if the database exists and runs migrations if it doesn't."""
    if not os.path.exists(DB_FILE):
        print("--- Database not found. Running initial setup... ---")
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sherlock.settings')
        
        args = [sys.argv[0], 'migrate']
        
        execute_from_command_line(args)
        print("--- Database created successfully. ---")
    else:
        print("--- Database found. ---")

if __name__ == "__main__":
    run_migrations()
    
    print("--- Starting Sherlock Production Server ---")
    print(f"Your application will be available at: http://<your_server_ip>:{PORT}")
    print("Press Ctrl+C to stop the server.")
    
    serve(application, host=HOST, port=PORT)