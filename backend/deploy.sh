#!/bin/bash

# Exit on error
set -e

echo "Deploying backend to AWS Elastic Beanstalk..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "EB CLI is not installed. Please install it first."
    exit 1
fi

# Ensure we're in the backend directory
if [ ! -f "app.py" ]; then
    echo "Please run this script from the backend directory."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated virtual environment."
fi

# Skip updating requirements.txt to avoid overwriting our custom requirements
# echo "Updating requirements.txt..."
# pip freeze > requirements.txt

# Initialize EB if not already done
if [ ! -d ".elasticbeanstalk" ]; then
    echo "Initializing Elastic Beanstalk..."
    eb init
else
    echo "Elastic Beanstalk already initialized."
fi

# Deploy to EB
echo "Deploying to Elastic Beanstalk..."
eb deploy

echo "Backend deployment completed successfully!" 