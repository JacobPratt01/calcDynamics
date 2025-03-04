# Deployment Guide for AWS Elastic Beanstalk

This guide will walk you through the process of deploying the Differential Equation Solver application to AWS Elastic Beanstalk.

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. EB CLI installed
4. Node.js and npm
5. Python 3.x

## Step 1: Configure AWS Credentials

If you haven't already configured your AWS credentials, run:

```bash
aws configure
```

You'll be prompted to enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (e.g., us-east-1)
- Default output format (json)

## Step 2: Deploy the Backend

1. Navigate to the backend directory:

```bash
cd backend
```

2. Initialize Elastic Beanstalk:

```bash
eb init
```

Follow the prompts:
- Select your region
- Create a new application or select an existing one
- Select Python as the platform
- Choose the Python version (3.9 recommended)
- Set up SSH for your instances (optional)

3. Create an environment and deploy:

```bash
eb create differential-equation-backend
```

This will create a new environment and deploy your application. The process may take a few minutes.

4. Once deployed, get the URL of your backend:

```bash
eb status
```

Note the CNAME value, which is your backend URL (e.g., `differential-equation-backend.elasticbeanstalk.com`).

## Step 3: Update Frontend Configuration

1. Create a `.env.production` file in the frontend directory:

```bash
cd ../frontend
touch .env.production
```

2. Add the backend URL to the `.env.production` file:

```
REACT_APP_API_URL=https://your-backend-url.elasticbeanstalk.com
```

Replace `your-backend-url.elasticbeanstalk.com` with your actual backend URL.

## Step 4: Build and Deploy the Frontend

1. Build the frontend:

```bash
npm run build
```

This will create a `build` directory with the production-ready files.

2. Initialize Elastic Beanstalk for the frontend:

```bash
eb init
```

Follow the prompts:
- Select your region
- Create a new application or select an existing one
- Select Node.js as the platform
- Choose the Node.js version
- Set up SSH for your instances (optional)

3. Create an environment and deploy:

```bash
eb create differential-equation-frontend
```

4. Once deployed, get the URL of your frontend:

```bash
eb status
```

Note the CNAME value, which is your frontend URL.

## Step 5: Configure CORS (if needed)

If you encounter CORS issues, you may need to update the backend to allow requests from your frontend domain:

1. Update the CORS configuration in `backend/app.py`:

```python
CORS(app, resources={r"/api/*": {"origins": "https://your-frontend-url.elasticbeanstalk.com"}})
```

2. Redeploy the backend:

```bash
cd ../backend
eb deploy
```

## Step 6: Verify the Deployment

1. Open your frontend URL in a browser
2. Test the application by solving differential equations
3. Check that the visualizations are displayed correctly

## Troubleshooting

### Backend Issues

- Check the logs:
  ```bash
  cd backend
  eb logs
  ```

- SSH into the instance:
  ```bash
  eb ssh
  ```

### Frontend Issues

- Check the logs:
  ```bash
  cd frontend
  eb logs
  ```

- Verify environment variables:
  ```bash
  eb printenv
  ```

## Scaling and Monitoring

- To scale your application:
  ```bash
  eb scale 2
  ```
  This will scale to 2 instances.

- To monitor your application, use the AWS Elastic Beanstalk console or AWS CloudWatch.

## Cleanup

To avoid incurring charges, terminate your environments when not in use:

```bash
cd backend
eb terminate differential-equation-backend

cd ../frontend
eb terminate differential-equation-frontend
```

## Additional Resources

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/Welcome.html)
- [EB CLI Command Reference](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-getting-started.html)

## Virtual Environment Setup

1. **Create and activate a virtual environment**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

2. **Now install Flask and Flask-CORS in the virtual environment**:
```bash
pip install flask flask-cors
```

3. **Create a requirements.txt file for Elastic Beanstalk**:
```bash
pip freeze > requirements.txt
```

The virtual environment (`venv`) will:
- Keep your project dependencies isolated
- Prevent conflicts with system Python packages
- Make it easier to deploy to Elastic Beanstalk
- Be ignored by git (it should be in .gitignore)

Would you like me to help you run these commands? After we set up the virtual environment and install Flask, we can test your backend locally before deploying to Elastic Beanstalk.

Also, make sure to always activate the virtual environment (`source venv/bin/activate`) when working on the backend. You'll know it's activated when you see `(venv)` at the start of your terminal prompt. 