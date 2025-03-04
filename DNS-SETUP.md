# DNS Configuration for CalcDynamics.com

This guide will help you set up DNS records for calcdynamics.com using AWS Route 53.

## Prerequisites

1. AWS account with access to Route 53
2. Domain name registered (calcdynamics.com)
3. Elastic Beanstalk environments for frontend and backend

## Step 1: Create a Hosted Zone

1. Go to the AWS Route 53 console
2. Click on "Hosted zones" in the left navigation pane
3. Click "Create hosted zone"
4. Enter "calcdynamics.com" as the domain name
5. Select "Public hosted zone" as the type
6. Click "Create"

## Step 2: Update Name Servers

1. After creating the hosted zone, Route 53 will assign name servers to your domain
2. Copy these name servers (they will look like ns-xxx.awsdns-xx.com)
3. Go to your domain registrar's website
4. Update the name servers for calcdynamics.com to use the AWS name servers

## Step 3: Create DNS Records for Frontend

1. In the Route 53 console, select your hosted zone (calcdynamics.com)
2. Click "Create record"
3. Leave the "Record name" field empty (for the apex domain)
4. Select "A - Routes traffic to an IPv4 address and some AWS resources" as the record type
5. Enable "Alias"
6. In the "Route traffic to" dropdown, select "Alias to Elastic Beanstalk environment"
7. Select your region and then your frontend Elastic Beanstalk environment
8. Click "Create records"

## Step 4: Create DNS Records for www Subdomain

1. Click "Create record" again
2. Enter "www" in the "Record name" field
3. Select "A - Routes traffic to an IPv4 address and some AWS resources" as the record type
4. Enable "Alias"
5. In the "Route traffic to" dropdown, select "Alias to Elastic Beanstalk environment"
6. Select your region and then your frontend Elastic Beanstalk environment
7. Click "Create records"

## Step 5: Create DNS Records for API Subdomain

1. Click "Create record" again
2. Enter "api" in the "Record name" field
3. Select "A - Routes traffic to an IPv4 address and some AWS resources" as the record type
4. Enable "Alias"
5. In the "Route traffic to" dropdown, select "Alias to Elastic Beanstalk environment"
6. Select your region and then your backend Elastic Beanstalk environment
7. Click "Create records"

## Step 6: Set Up SSL Certificates

1. Go to the AWS Certificate Manager (ACM) console
2. Click "Request a certificate"
3. Select "Request a public certificate"
4. Add the following domain names:
   - calcdynamics.com
   - www.calcdynamics.com
   - api.calcdynamics.com
5. Select "DNS validation" as the validation method
6. Click "Request"
7. Follow the instructions to validate your domain ownership
8. Once validated, the certificate will be issued

## Step 7: Configure Elastic Beanstalk to Use HTTPS

1. Go to the Elastic Beanstalk console
2. Select your frontend environment
3. Click on "Configuration" in the left navigation pane
4. Under "Load balancer", click "Edit"
5. Add a listener with the following settings:
   - Port: 443
   - Protocol: HTTPS
   - SSL certificate: Select the certificate you created in Step 6
6. Click "Apply"
7. Repeat steps 2-6 for your backend environment

## Step 8: Test Your Configuration

1. Wait for the DNS changes to propagate (this can take up to 48 hours, but often happens within a few minutes to a few hours)
2. Test your website by visiting:
   - https://calcdynamics.com
   - https://www.calcdynamics.com
   - https://api.calcdynamics.com

## Troubleshooting

- If you encounter DNS issues, use tools like `dig` or `nslookup` to check your DNS records
- If you encounter SSL issues, check that your certificate is properly associated with your load balancer
- If you encounter routing issues, check your Elastic Beanstalk environment's health and configuration 