# sherlock-python/run.py
"""
This script's ONLY job is to start the production Waitress server.
All configuration and setup is handled by the start_production.sh script.
"""
import os
from waitress import serve
from sherlock.wsgi import application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sherlock.settings')


HOST = '127.0.0.1'
PORT = 8000


serve(application, host=HOST, port=PORT)