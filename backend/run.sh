#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the application with gunicorn
exec gunicorn --bind 0.0.0.0:5001 app:app 