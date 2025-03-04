#!/bin/bash

# commit_to_github.sh - Script to commit the entire DYNAMIC_WEBSITE to GitHub
# For user JacobPratt01 and repository calcDynamics

# Set error handling
set -e  # Exit immediately if a command exits with a non-zero status

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

# Check if git is installed
if ! command -v git &> /dev/null; then
  print_error "Git is not installed. Please install Git and try again."
  exit 1
fi

# Check if we're in a Git repository
if [ ! -d .git ]; then
  print_message "Initializing Git repository..."
  git init
  
  # Set remote repository
  print_message "Setting remote repository to github.com/JacobPratt01/calcDynamics.git"
  git remote add origin https://github.com/JacobPratt01/calcDynamics.git
else
  print_message "Git repository already initialized."
  
  # Check if the remote is set correctly
  REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
  if [[ "$REMOTE_URL" != *"JacobPratt01/calcDynamics"* ]]; then
    print_warning "Remote URL doesn't match expected repository."
    print_message "Current remote: $REMOTE_URL"
    print_message "Setting remote to github.com/JacobPratt01/calcDynamics.git"
    git remote set-url origin https://github.com/JacobPratt01/calcDynamics.git || git remote add origin https://github.com/JacobPratt01/calcDynamics.git
  fi
fi

# Get current timestamp for commit message
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Add all files
print_message "Adding all files to Git..."
git add .

# Ask for commit message
echo "Enter a commit message (or press Enter to use default):"
read COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
  COMMIT_MSG="Update DYNAMIC_WEBSITE - $TIMESTAMP"
fi

# Commit changes
print_message "Committing changes with message: '$COMMIT_MSG'"
git commit -m "$COMMIT_MSG"

# Push to GitHub
print_message "Pushing changes to GitHub repository (JacobPratt01/calcDynamics)..."
git push -u origin master || git push -u origin main

print_message "Commit and push completed successfully!"
print_message "Your DYNAMIC_WEBSITE has been pushed to github.com/JacobPratt01/calcDynamics" 