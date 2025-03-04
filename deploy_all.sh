#!/bin/bash

# deploy_all.sh - Comprehensive deployment script for CalcDynamics
# This script handles Git versioning and deploys both backend and frontend

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

# Function to check if command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for required commands
if ! command_exists git; then
  print_error "Git is not installed. Please install Git and try again."
  exit 1
fi

if ! command_exists eb; then
  print_error "AWS Elastic Beanstalk CLI is not installed. Please install it and try again."
  exit 1
fi

# Check if we're in a Git repository
if [ ! -d .git ]; then
  print_error "Not in a Git repository. Please run this script from the root of your Git repository."
  exit 1
fi

# Get current timestamp for commit message
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
  print_message "Uncommitted changes detected. Adding to Git..."
  
  # Ask for commit message
  echo "Enter a commit message (or press Enter to use default):"
  read COMMIT_MSG
  
  if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Deployment update - $TIMESTAMP"
  fi
  
  # Add all changes
  git add .
  
  # Commit changes
  print_message "Committing changes with message: '$COMMIT_MSG'"
  git commit -m "$COMMIT_MSG"
else
  print_message "No uncommitted changes detected."
fi

# Push to GitHub
print_message "Pushing changes to GitHub..."
git push

# Deploy backend
print_message "Deploying backend..."
cd backend
eb deploy
if [ $? -ne 0 ]; then
  print_error "Backend deployment failed!"
  exit 1
fi
print_message "Backend deployed successfully!"
cd ..

# Build and deploy frontend
print_message "Building and deploying frontend..."
cd frontend
npm run build
if [ $? -ne 0 ]; then
  print_error "Frontend build failed!"
  exit 1
fi

eb deploy
if [ $? -ne 0 ]; then
  print_error "Frontend deployment failed!"
  exit 1
fi
print_message "Frontend deployed successfully!"
cd ..

# Create a deployment tag
TAG_NAME="deployment-$(date +"%Y%m%d-%H%M%S")"
print_message "Creating deployment tag: $TAG_NAME"
git tag -a "$TAG_NAME" -m "Deployment on $TIMESTAMP"
git push origin "$TAG_NAME"

print_message "Deployment completed successfully!"
print_message "Backend and frontend have been deployed, and changes have been pushed to GitHub."
print_message "Deployment tagged as: $TAG_NAME" 