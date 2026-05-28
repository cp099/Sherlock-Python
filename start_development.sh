#!/bin/bash
echo "--- Starting Sherlock in DEVELOPMENT mode (HTTP) ---"
echo "Access at: http://127.0.0.1:8000"
export DEBUG=True
./venv/bin/python manage.py runserver