#!/bin/bash

# ============================================================================
# AWS DEPLOYMENT SCRIPT FOR TELEGRAM BOT SYSTEM
# Optimized for Ubuntu 24.04 LTS on AWS EC2 Free Tier
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_error() {
    echo -e "${RED}[✗] $1${NC}"
}

print_info() {
    echo -e "${BLUE}[i] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_header() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}\n"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "This script should not be run as root. Run as ubuntu user."
    exit 1
fi

print_header "TELEGRAM BOT SYSTEM - AWS DEPLOYMENT"

# ============================================================================
# 1. SYSTEM UPDATE
# ============================================================================
print_header "Step 1: System Update"

print_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System updated"

# ============================================================================
# 2. INSTALL REQUIRED SOFTWARE
# ============================================================================
print_header "Step 2: Installing Required Software"

print_info "Installing Python and development tools..."
sudo apt install python3 python3-pip python3-venv git curl wget unzip -y

print_info "Installing Node.js and PM2..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
sudo npm install -g pm2

print_info "Installing Nginx for reverse proxy..."
sudo apt install nginx certbot python3-certbot-nginx -y

print_success "Required software installed"

# ============================================================================
# 3. INSTALL MONGODB
# ============================================================================
print_header "Step 3: Installing MongoDB"

read -p "Do you want to install local MongoDB? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Installing MongoDB..."
    
    # Import MongoDB public key
    wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
    
    # Add MongoDB repository
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    
    # Install MongoDB
    sudo apt update
    sudo apt install -y mongodb-org
    
    # Start and enable MongoDB
    sudo systemctl start mongod
    sudo systemctl enable mongod
    
    print_success "MongoDB installed and started"
else
    print_info "Skipping MongoDB installation (you'll need to configure MongoDB Atlas)"
fi

# ============================================================================
# 4. SETUP PROJECT
# ============================================================================
print_header "Step 4: Setting Up Project"

# Create project directory
PROJECT_DIR="/home/ubuntu/telegram-bot"
if [ ! -d "$PROJECT_DIR" ]; then
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown ubuntu:ubuntu "$PROJECT_DIR"
    print_success "Created project directory"
fi

# Navigate to project directory
cd "$PROJECT_DIR"

# Clone repository
print_info "Cloning repository..."
git clone https://github.com/Sanjay-off/finally-main.git .

# Create virtual environment
print_info "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs data backups

print_success "Project setup completed"

# ============================================================================
# 5. CONFIGURE ENVIRONMENT
# ============================================================================
print_header "Step 5: Environment Configuration"

# Copy environment template
if [ ! -f ".env" ]; then
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_success "Created .env file"
else
    print_info ".env file already exists"
fi

print_warning "Please edit .env file with your configuration:"
echo ""
echo "Required settings:"
echo "  - ADMIN_BOT_TOKEN (from @BotFather)"
echo "  - USER_BOT_TOKEN (from @BotFather)"
echo "  - USER_BOT_USERNAME (your user bot username)"
echo "  - MONGODB_URI (MongoDB connection string)"
echo "  - PRIVATE_STORAGE_CHANNEL_ID (negative channel ID)"
echo "  - PUBLIC_GROUP_ID (negative group ID)"
echo "  - ADMIN_IDS (your Telegram user ID)"
echo "  - VERIFICATION_SERVER_URL (your EC2 public IP)"
echo "  - ENCRYPTION_KEY (generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo ""
echo "URL Shortener (choose one):"
echo "  - For Just2Earn: SHORTLINK_API_KEY=your_token, SHORTLINK_BASE_URL=https://just2earn.com"
echo "  - For Get2Short: SHORTLINK_API_KEY=your_token, SHORTLINK_BASE_URL=https://get2short.com"
echo ""

read -p "Do you want to edit .env file now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    nano .env
fi

# ============================================================================
# 6. SETUP FIREWALL
# ============================================================================
print_header "Step 6: Firewall Configuration"

print_info "Configuring UFW firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 5000/tcp  # Verification server port
sudo ufw --force enable
print_success "Firewall configured"

# ============================================================================
# 7. SETUP NGINX REVERSE PROXY
# ============================================================================
print_header "Step 7: Nginx Configuration"

read -p "Do you have a domain name? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your domain name: " DOMAIN_NAME
    
    if [ ! -z "$DOMAIN_NAME" ]; then
        print_info "Creating Nginx configuration for $DOMAIN_NAME..."
        
        # Create Nginx site configuration
        sudo tee /etc/nginx/sites-available/telegram-bot > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF
        
        # Enable site
        sudo ln -sf /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
        
        # Test and restart Nginx
        sudo nginx -t
        sudo systemctl restart nginx
        
        print_success "Nginx configured for $DOMAIN_NAME"
        
        # Setup SSL
        read -p "Do you want to setup SSL with Let's Encrypt? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Setting up SSL certificate..."
            sudo certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME
            print_success "SSL certificate installed"
        fi
    fi
else
    print_info "Skipping domain configuration (using IP address)"
fi

# ============================================================================
# 8. DEPLOY WITH PM2
# ============================================================================
print_header "Step 8: Deploying with PM2"

print_info "Starting services with PM2..."
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu

print_success "Services deployed with PM2"

# ============================================================================
# 9. SETUP LOG ROTATION
# ============================================================================
print_header "Step 9: Log Rotation"

print_info "Setting up log rotation..."
sudo tee /etc/logrotate.d/telegram-bot > /dev/null <<EOF
$PROJECT_DIR/logs/*.log {
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
EOF

print_success "Log rotation configured"

# ============================================================================
# 10. SETUP BACKUP SCRIPT
# ============================================================================
print_header "Step 10: Backup Script"

print_info "Creating backup script..."
cat > backup.sh << 'EOF'
#!/bin/bash

# Backup script for Telegram Bot System
PROJECT_DIR="/home/ubuntu/telegram-bot"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup MongoDB (if local)
if systemctl is-active --quiet mongod; then
    mongodump --db telegram_bot_db --out "$BACKUP_DIR/mongodb_$DATE"
    tar -czf "$BACKUP_DIR/mongodb_$DATE.tar.gz" -C "$BACKUP_DIR" "mongodb_$DATE"
    rm -rf "$BACKUP_DIR/mongodb_$DATE"
fi

# Backup configuration files
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" .env ecosystem.config.js

# Clean old backups (keep last 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

print_success "Backup script created"

# ============================================================================
# 11. SETUP CRON JOB
# ============================================================================
print_header "Step 11: Cron Jobs"

read -p "Do you want to setup automatic backup cron job? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Add cron job for daily backup at 2 AM
    (crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/backup.sh") | crontab -
    print_success "Daily backup cron job added (2 AM)"
else
    print_info "Skipping cron job setup"
fi

# ============================================================================
# 12. VALIDATION
# ============================================================================
print_header "Step 12: Validation"

print_info "Checking service status..."
sleep 5

# Check PM2 status
if pm2 list | grep -q "online"; then
    print_success "PM2 services are running"
else
    print_error "Some PM2 services are not running"
    pm2 status
fi

# Check verification server
if curl -s http://localhost:5000/health > /dev/null; then
    print_success "Verification server is responding"
else
    print_warning "Verification server is not responding (may need more time)"
fi

# Check MongoDB
if systemctl is-active --quiet mongod; then
    print_success "MongoDB is running"
else
    print_warning "MongoDB is not running (or using MongoDB Atlas)"
fi

# ============================================================================
# 13. FINAL INSTRUCTIONS
# ============================================================================
print_header "Deployment Complete!"

print_success "Telegram Bot System deployed successfully!"

echo ""
print_info "Service Status:"
pm2 status

echo ""
print_info "Important URLs:"
if [ ! -z "$DOMAIN_NAME" ]; then
    echo "  Verification Server: https://$DOMAIN_NAME/health"
else
    echo "  Verification Server: http://$(curl -s ifconfig.me):5000/health"
fi

echo ""
print_info "Useful Commands:"
echo "  View logs:        pm2 logs"
echo "  Restart services:  pm2 restart all"
echo "  Monitor system:    pm2 monit"
echo "  Run backup:       ./backup.sh"
echo "  Check status:      pm2 status"

echo ""
print_warning "Next Steps:"
echo "1. Configure your .env file if not done already"
echo "2. Test your Telegram bots by sending /start command"
echo "3. Check logs for any errors: pm2 logs --err"
echo "4. Monitor system resources: htop"

echo ""
print_info "URL Shortener Configuration:"
echo "  For Just2Earn: Set SHORTLINK_API_KEY and SHORTLINK_BASE_URL=https://just2earn.com"
echo "  For Get2Short: Set SHORTLINK_API_KEY and SHORTLINK_BASE_URL=https://get2short.com"

echo ""
print_success "Your Telegram Bot System is ready! 🚀"

# Get public IP for reference
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "unknown")
echo ""
print_info "Your Public IP: $PUBLIC_IP"
echo "Make sure to update VERIFICATION_SERVER_URL in .env with this IP"