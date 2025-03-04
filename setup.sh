#!/bin/bash

# Exit on error
set -e

# Create and activate virtual environment for backend
echo "Setting up backend virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "Installing development dependencies..."
pip install pytest pytest-cov black flake8

# Set up frontend
echo "Setting up frontend..."
cd ../frontend
npm install

# Return to root directory
cd ..

echo "Setup complete!"
echo "To run the backend: cd backend && source venv/bin/activate && python app.py"
echo "To run the frontend: cd frontend && npm start" 