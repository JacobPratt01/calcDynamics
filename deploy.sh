#!/bin/bash

# Exit on error
set -e

echo "=== CalcDynamics.com Deployment ==="
echo "This script will deploy both the backend and frontend to AWS Elastic Beanstalk."

# Deploy backend
echo -e "\n=== Deploying Backend ==="
cd backend
./deploy.sh
cd ..

# Deploy frontend
echo -e "\n=== Deploying Frontend ==="
cd frontend
./deploy.sh
cd ..

echo -e "\n=== Deployment Completed Successfully! ==="
echo "Your application should now be available at:"
echo "  - Frontend: https://calcdynamics.com"
echo "  - Backend API: https://api.calcdynamics.com"
echo ""
echo "Don't forget to set up your custom domains in Route 53 and configure SSL certificates." 