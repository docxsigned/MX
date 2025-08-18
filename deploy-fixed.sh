#!/bin/bash

# Fixed Email Redirector Deployment Script for Ubuntu
# Run this script as root

set -e

echo "Setting up Email Redirector on Ubuntu (Fixed Version)..."

# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y python3 python3-pip python3-venv nginx

# Create application directory in root's home (as per your setup)
mkdir -p /root/email-redirector
cd /root/email-redirector

# Copy all files to the directory (assuming you're running this from the directory with your files)
cp -r * /root/email-redirector/ 2>/dev/null || echo "Files already in place"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set proper permissions
chown -R root:root /root/email-redirector
chmod +x /root/email-redirector/email_redirector.py

# Copy service file
cp email-redirector.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable email-redirector
systemctl start email-redirector

# Configure Nginx
cp nginx-config /etc/nginx/sites-available/email-redirector
ln -sf /etc/nginx/sites-available/email-redirector /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx

# Check service status
echo "Checking service status..."
systemctl status email-redirector

echo "Deployment completed!"
echo "Service is running on port 5000"
echo "Nginx is configured to proxy requests from port 80"
echo "Check logs with: journalctl -u email-redirector -f"
echo ""
echo "Test your setup with:"
echo "http://your-server-ip/redirect|dXNlckBleGFtcGxlLmNvbQ=="
echo "(This tests with user@example.com)"

