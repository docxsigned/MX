# Troubleshooting Guide for Email Redirector

## Common Issues and Solutions

### 1. 404 Not Found Error

**Problem**: You're getting a 404 error when accessing your website.

**Solution**: Follow these steps in order:

#### Step A: Check if the service is running
```bash
systemctl status email-redirector
```

If it's not running or has errors:
```bash
# Check logs
journalctl -u email-redirector -e

# Restart the service
systemctl restart email-redirector
```

#### Step B: Check if the service is listening on port 5000
```bash
netstat -tlnp | grep :5000
```

You should see something like:
```
tcp6       0      0 :::5000                 :::*                    LISTEN      12345/python3
```

#### Step C: Test the service directly
```bash
curl http://localhost:5000/redirect|dXNlckBleGFtcGxlLmNvbQ==
```

If this works, the issue is with Nginx. If it doesn't work, the issue is with the Python service.

#### Step D: Check Nginx configuration
```bash
nginx -t
systemctl status nginx
```

#### Step E: Check Nginx logs
```bash
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### 2. Service Won't Start

**Problem**: The email-redirector service fails to start.

**Solution**:
```bash
# Check the service file
cat /etc/systemd/system/email-redirector.service

# Check if the paths exist
ls -la /root/email-redirector/
ls -la /root/email-redirector/venv/bin/gunicorn

# Check if the script exists
ls -la /root/email-redirector/email_redirector.py

# Check permissions
chmod +x /root/email-redirector/email_redirector.py
chown -R root:root /root/email-redirector
```

### 3. Port Already in Use

**Problem**: Port 5000 is already occupied.

**Solution**:
```bash
# Find what's using port 5000
netstat -tlnp | grep :5000
lsof -i :5000

# Kill the process if needed
kill -9 <PID>

# Or change the port in the service file and nginx config
```

### 4. File Path Issues

**Problem**: Service can't find the script or virtual environment.

**Solution**: Update the service file with correct paths:
```bash
nano /etc/systemd/system/email-redirector.service
```

Make sure these paths match your actual setup:
- `WorkingDirectory=/root/email-redirector`
- `Environment=PATH=/root/email-redirector/venv/bin`
- `ExecStart=/root/email-redirector/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 email_redirector:app`

### 5. Permission Issues

**Problem**: Permission denied errors.

**Solution**:
```bash
# Set correct ownership
chown -R root:root /root/email-redirector

# Set correct permissions
chmod +x /root/email-redirector/email_redirector.py
chmod +x /root/email-redirector/venv/bin/gunicorn

# Check SELinux if applicable
sestatus
```

## Complete Reset and Redeploy

If nothing else works, do a complete reset:

```bash
# Stop services
systemctl stop email-redirector
systemctl stop nginx

# Remove old configurations
rm -f /etc/systemd/system/email-redirector.service
rm -f /etc/nginx/sites-enabled/email-redirector
rm -f /etc/nginx/sites-available/email-redirector

# Clean up
systemctl daemon-reload

# Run the fixed deployment script
chmod +x deploy-fixed.sh
./deploy-fixed.sh
```

## Testing Your Setup

After deployment, test with:

```bash
# Test the service directly
curl http://localhost:5000/redirect|dXNlckBleGFtcGxlLmNvbQ==

# Test through Nginx
curl http://your-server-ip/redirect|dXNlckBleGFtcGxlLmNvbQ==

# Test with your domain (if configured)
curl http://your-domain.com/redirect|dXNlckBleGFtcGxlLmNvbQ==
```

## Expected Response

You should see a redirect response (302) to one of your configured URLs based on the email domain.

## Still Having Issues?

Check these logs in order:
1. `journalctl -u email-redirector -f` (service logs)
2. `tail -f /var/log/nginx/error.log` (Nginx errors)
3. `tail -f /var/log/nginx/access.log` (Nginx access)
4. `systemctl status email-redirector` (service status)
5. `systemctl status nginx` (Nginx status)

