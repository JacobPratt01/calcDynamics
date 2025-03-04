#!/bin/bash

# Exit on error
set -e

echo "Deploying frontend to AWS Elastic Beanstalk..."

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

# Ensure we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "Please run this script from the frontend directory."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the application
echo "Building the application..."
npm run build

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

echo "Frontend deployment completed successfully!" 