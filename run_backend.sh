#!/bin/bash

# run_backend.sh - Script to run the backend with python3

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
  print_error "python3 is not installed. Please install Python 3 and try again."
  exit 1
fi

# Change to backend directory
cd backend || { print_error "Backend directory not found!"; exit 1; }

# Activate virtual environment if it exists
if [ -d "venv" ]; then
  print_message "Activating virtual environment..."
  source venv/bin/activate
else
  print_warning "No virtual environment found. Running with system Python."
fi

# Check if requirements are installed
print_message "Checking if requirements are installed..."
if [ -f "requirements.txt" ]; then
  python3 -m pip install -r requirements.txt
else
  print_warning "No requirements.txt file found. Skipping package installation."
fi

# Run the backend with python3
print_message "Starting backend server with python3..."
python3 app.py

# Note: The script will not reach this point unless the server is stopped
print_message "Backend server stopped." 