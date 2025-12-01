# AWS EC2 Deployment Guide

## Prerequisites
- AWS Account (Free Tier)
- SSH Key Pair
- Basic terminal knowledge

## Step 1: Launch EC2 Instance

1. **Login to AWS Console**
   - Go to EC2 Dashboard
   - Click "Launch Instance"

2. **Configure Instance**
   - Name: `telegram-bot-server`
   - AMI: Ubuntu Server 22.04 LTS (Free tier eligible)
   - Instance type: `t2.micro` (Free tier)
   - Key pair: Create or select existing
   - Storage: 30 GB (Free tier limit)

3. **Security Group Settings**
   Allow these ports:
   - SSH (22) - Your IP only
   - HTTP (80) - Optional
   - HTTPS (443) - Optional
   - Custom TCP (5000) - For verification server

4. **Launch Instance**

## Step 2: Connect to Instance
```bash
# Make key private
chmod 400 your-key.pem

# Connect
ssh -i your-key.pem ubuntu@<your-ec2-ip>
```

## Step 3: Initial Server Setup
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Create project directory
mkdir -p ~/telegram-file-system
cd ~/telegram-file-system
```

## Step 4: Upload Project Files

From your local machine:
```bash
# Using SCP
scp -i your-key.pem -r /path/to/project/* ubuntu@<ec2-ip>:~/telegram-file-system/

# Or using rsync
rsync -avz -e "ssh -i your-key.pem" /path/to/project/ ubuntu@<ec2-ip>:~/telegram-file-system/
```

## Step 5: Run Setup Script
```bash
cd ~/telegram-file-system

# Make scripts executable
chmod +x scripts/*.sh

# Run setup
./scripts/setup.sh
```

During setup:
- Provide your bot tokens
- Set channel IDs
- Configure admin IDs
- Set verification server URL (use your EC2 public IP)

## Step 6: Configure Environment

Edit `.env` file:
```bash
nano .env
```

Update these values:
```env
ADMIN_BOT_TOKEN=<your_admin_bot_token>
USER_BOT_TOKEN=<your_user_bot_token>
USER_BOT_USERNAME=<your_user_bot_username>

PRIVATE_STORAGE_CHANNEL_ID=-1001234567890
PUBLIC_GROUP_ID=-1001234567890

ADMIN_IDS=123456789,987654321

VERIFICATION_SERVER_URL=http://<your_ec2_public_ip>:5000

ENCRYPTION_KEY=<generate_secure_key>

SHORTLINK_API_KEY=<your_api_key>
SHORTLINK_BASE_URL=http://your-shortlink-domain
```

## Step 7: Start Services
```bash
# Start with PM2
pm2 start ecosystem.config.js

# Save PM2 processes
pm2 save

# View status
pm2 status

# View logs
pm2 logs
```

## Step 8: Setup Auto-start on Reboot
```bash
# Generate startup script
pm2 startup

# Follow the command PM2 outputs

# Save process list
pm2 save
```

## Step 9: Monitor Services
```bash
# Real-time monitoring
pm2 monit

# View specific logs
pm2 logs admin-bot
pm2 logs user-bot
pm2 logs verify-server

# Restart services
pm2 restart all

# Stop services
pm2 stop all
```

## Step 10: Setup Domain (Optional but Recommended)

1. **Get a domain** (e.g., from Namecheap, GoDaddy)

2. **Point A record to EC2 IP**
   - Add A record: `@` → `<your_ec2_ip>`
   - Add A record: `verify` → `<your_ec2_ip>`

3. **Install SSL Certificate** (Let's Encrypt)
```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Install Nginx
sudo apt-get install -y nginx

# Configure Nginx for verification server
sudo nano /etc/nginx/sites-available/verify

# Add:
server {
    listen 80;
    server_name verify.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/verify /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL
sudo certbot --nginx -d verify.yourdomain.com
```

4. **Update .env**
```env
VERIFICATION_SERVER_URL=https://verify.yourdomain.com
```

## Monitoring & Maintenance

### Daily Checks
```bash
# Check PM2 status
pm2 status

# Check logs for errors
pm2 logs --lines 100

# Check MongoDB status
sudo systemctl status mongod

# Check disk space
df -h
```

### Weekly Tasks
```bash
# Create backup
./scripts/backup.sh

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Restart services
pm2 restart all
```

### Monthly Tasks
```bash
# Clean old logs
pm2 flush

# Clean old backups (keep last 30 days)
find backups/ -name "backup_*.tar.gz" -mtime +30 -delete

# Check system resources
htop
```

## Troubleshooting

### Bots not starting
```bash
# Check logs
pm2 logs admin-bot --lines 50
pm2 logs user-bot --lines 50

# Check .env file
cat .env

# Restart
pm2 restart all
```

### Database connection issues
```bash
# Check MongoDB
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod

# Check connection
mongo telegram_bot_db --eval "db.stats()"
```

### High CPU/Memory usage
```bash
# Check resource usage
htop

# Check PM2 metrics
pm2 monit

# Restart problematic process
pm2 restart <process_name>
```

### Verification server not accessible
```bash
# Check if running
pm2 status

# Check firewall
sudo ufw status

# Check port
sudo netstat -tulpn | grep :5000

# Test locally
curl http://localhost:5000
```

## Scaling (When needed)

### Upgrade Instance Type
1. Stop EC2 instance
2. Actions → Instance Settings → Change Instance Type
3. Select `t3.small` or `t3.medium`
4. Start instance
5. Verify services: `pm2 status`

### Add More Workers
Edit `ecosystem.config.js`:
```javascript
{
  name: 'user-bot',
  instances: 2,  // Run 2 instances
  exec_mode: 'cluster'
}
```

## Security Best Practices

1. **Keep System Updated**
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

2. **Use SSH Keys Only**
```bash
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

3. **Configure UFW Firewall**
```bash
sudo ufw enable
sudo ufw allow from <your_ip> to any port 22
```

4. **Regular Backups**
```bash
# Add to crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/ubuntu/telegram-file-system/scripts/backup.sh
```

5. **Monitor Logs**
```bash
# Set up log monitoring
pm2 install pm2-logrotate
```

## Cost Optimization

### Free Tier Limits (Monthly)
- 750 hours t2.micro instance
- 30 GB EBS storage
- 15 GB data transfer out

### Stay Within Free Tier
- Use t2.micro only
- Monitor data transfer in AWS console
- Use compression for file transfers
- Implement caching where possible

### When to Upgrade
- Consistent CPU > 80%
- Memory usage > 90%
- User complaints about slowness
- More than 10K requests/day

## Backup & Recovery

### Manual Backup
```bash
./scripts/backup.sh
```

### Automated Daily Backups
```bash
# Add to crontab