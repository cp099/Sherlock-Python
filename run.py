# sherlock-python/run.py

import os
import sys
from waitress import serve
from sherlock.wsgi import application
from django.core.management import execute_from_command_line

# --- Configuration ---
HOST = '0.0.0.0'
PORT = 8000
DB_FILE = 'db.sqlite3'

def run_migrations():
    """Checks if the database exists and runs migrations if it doesn't."""
    if not os.path.exists(DB_FILE):
        print("--- Database not found. Running initial setup... ---")
        # We need to tell Django which settings file to use.
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sherlock.settings')
        
        # Prepare the arguments for the 'migrate' command
        args = [sys.argv[0], 'migrate']
        
        # Run the migration command
        execute_from_command_line(args)
        print("--- Database created successfully. ---")
    else:
        print("--- Database found. ---")

if __name__ == "__main__":
    # Run the database check and migration first
    run_migrations()
    
    print("--- Starting Sherlock Production Server ---")
    print(f"Your application will be available at: http://<your_server_ip>:{PORT}")
    print("Press Ctrl+C to stop the server.")
    
    # Start the production server
    serve(application, host=HOST, port=PORT)