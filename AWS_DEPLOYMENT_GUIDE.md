# AWS Ubuntu Deployment Guide

This guide will help you deploy your Telegram bot system on AWS EC2 Ubuntu 24.04 LTS.

## Prerequisites

- AWS Account with EC2 access
- Domain name (optional, but recommended)
- Telegram Bot Tokens (Admin and User bots)
- URL Shortener API tokens (Just2Earn and/or Get2Short)
- MongoDB (local or MongoDB Atlas)

## Step 1: Launch EC2 Instance

1. Go to AWS EC2 Console
2. Click "Launch Instances"
3. Choose Ubuntu Server 24.04 LTS (HVM), SSD Volume Type
4. Select instance type: `t2.micro` or `t3.micro` (Free Tier eligible)
5. Configure Key Pair (create a new one if needed)
6. Configure Security Group with these rules:
   - SSH (Port 22): Your IP address
   - HTTP (Port 80): 0.0.0.0/0
   - HTTPS (Port 443): 0.0.0.0/0
   - Custom (Port 5000): 0.0.0.0/0 (for verification server)
7. Launch instance

## Step 2: Connect to Instance

```bash
# SSH into your instance
ssh -i your-key-pair.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y
```

## Step 3: Install Required Software

```bash
# Install Python and development tools
sudo apt install python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx -y

# Install Node.js and PM2
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
sudo npm install -g pm2

# Install MongoDB (if using local MongoDB)
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start and enable MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

## Step 4: Clone and Setup Project

```bash
# Clone your repository
git clone https://github.com/Sanjay-off/finally-main.git telegram-bot
cd telegram-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Copy environment template
cp .env.example .env
nano .env  # Edit with your configuration
```

## Step 5: Configure Environment Variables

Edit `.env` file with your actual values:

```bash
# Required Configuration
ADMIN_BOT_TOKEN=your_admin_bot_token
USER_BOT_TOKEN=your_user_bot_token
USER_BOT_USERNAME=youruserbot

# URL Shorteners (choose one or both)
JUST2EARN_API_TOKEN=your_just2earn_token
GET2SHORT_API_TOKEN=your_get2short_token

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/telegram_bot_db

# Channel Configuration
PRIVATE_STORAGE_CHANNEL_ID=-100xxxxxxxxxx
PUBLIC_GROUP_ID=-100xxxxxxxxxx
ADMIN_IDS=123456789,987654321

# Security
ENCRYPTION_KEY=generate_with_python_secrets_module
```

## Step 6: Test the Application

```bash
# Test each component individually
python admin_bot/bot.py &
python user_bot/bot.py &
python verification_server/app.py &

# Check logs
tail -f logs/admin_bot.log
tail -f logs/user_bot.log
tail -f logs/verification_server.log

# Stop test processes
pkill -f "python.*bot.py"
pkill -f "python.*app.py"
```

## Step 7: Deploy with PM2

```bash
# Start all services with PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save
pm2 startup

# Check status
pm2 status
pm2 logs
```

## Step 8: Setup Nginx Reverse Proxy (Optional)

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/telegram-bot

# Add this configuration:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

## Step 9: Setup Auto-start and Monitoring

```bash
# Ensure PM2 starts on boot
pm2 startup systemd
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu

# Setup log rotation
sudo nano /etc/logrotate.d/telegram-bot

# Add this content:
/home/ubuntu/telegram-bot/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        pm2 reloadLogs
    endscript
}
```

## Step 10: Final Testing

```bash
# Test all services are running
pm2 status

# Test verification server
curl http://localhost:5000/health

# Check logs for errors
pm2 logs --err

# Test Telegram bots
# Send /start to both bots
# Test file upload and download
# Test verification flow
```

## Troubleshooting

### Common Issues:

1. **Bot Token Error**
   - Verify tokens in .env file
   - Check bot tokens are valid and not expired

2. **MongoDB Connection Error**
   - Check MongoDB is running: `sudo systemctl status mongod`
   - Verify connection string in .env
   - Check firewall settings

3. **URL Shortener Error**
   - Verify API tokens are correct
   - Check API endpoints are accessible
   - Review shortlink service logs

4. **Permission Issues**
   - Ensure proper file permissions: `chmod +x startup.sh`
   - Check log directory permissions

5. **Memory Issues**
   - Monitor memory usage: `free -h`
   - Adjust PM2 memory limits in ecosystem.config.js

### Useful Commands:

```bash
# View real-time logs
pm2 logs --lines 100

# Restart specific service
pm2 restart admin-bot
pm2 restart user-bot
pm2 restart verify-server

# Monitor system resources
htop
df -h
free -h

# Check MongoDB
mongo --eval "db.adminCommand('ismaster')"

# Backup database
mongodump --db telegram_bot_db --out /backup/$(date +%Y%m%d)
```

## Security Recommendations

1. **Firewall Configuration**
   ```bash
   sudo ufw enable
   sudo ufw allow ssh
   sudo ufw allow 'Nginx Full'
   ```

2. **Regular Updates**
   ```bash
   # Set up automatic security updates
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

3. **Database Security**
   - Use strong MongoDB passwords
   - Enable MongoDB authentication
   - Consider MongoDB Atlas for better security

4. **SSL/TLS**
   - Always use HTTPS for verification server
   - Use valid SSL certificates

## Monitoring and Maintenance

1. **Setup Monitoring**
   ```bash
   # Install monitoring tools
   sudo apt install htop iotop nethogs
   
   # Setup PM2 monitoring
   pm2 install pm2-server-monit
   ```

2. **Regular Backups**
   ```bash
   # Create backup script
   nano backup.sh
   
   # Add content for database and file backups
   # Make it executable: chmod +x backup.sh
   
   # Setup cron job
   crontab -e
   # Add: 0 2 * * * /home/ubuntu/telegram-bot/backup.sh
   ```

3. **Log Management**
   - Regularly check application logs
   - Setup log rotation
   - Monitor error rates

Your Telegram bot system is now deployed and ready to use!