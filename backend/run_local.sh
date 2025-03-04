#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the application with python3
echo "Starting backend server with python3..."
python3 app.py 