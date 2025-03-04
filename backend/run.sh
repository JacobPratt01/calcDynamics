#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the application with gunicorn
# Use python3 explicitly
exec python3 -m gunicorn --bind 0.0.0.0:5001 app:app 