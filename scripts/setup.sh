#!/bin/bash

# ============================================================================
# Telegram File Distribution System - Setup Script
# ============================================================================
# This script sets up the entire system on a fresh Ubuntu EC2 instance
# ============================================================================

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_error() {
    echo -e "${RED}[✗] $1${NC}"
}

print_info() {
    echo -e "${YELLOW}[i] $1${NC}"
}

print_header() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}\n"
}

print_header "TELEGRAM FILE DISTRIBUTION SYSTEM - SETUP"

# ============================================================================
# 1. Update System
# ============================================================================
print_header "Step 1: Updating System"

sudo apt-get update -y
sudo apt-get upgrade -y

print_success "System updated"

# ============================================================================
# 2. Install Python 3.10+
# ============================================================================
print_header "Step 2: Installing Python 3.10+"

sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update -y
sudo apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip

# Set Python 3.10 as default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

python3 --version
pip3 --version

print_success "Python 3.10+ installed"

# ============================================================================
# 3. Install MongoDB
# ============================================================================
print_header "Step 3: Installing MongoDB"

# Import MongoDB public GPG key
curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-archive-keyring.gpg

# Create list file for MongoDB
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-archive-keyring.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Update package database
sudo apt-get update -y

# Install MongoDB
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Check MongoDB status
if sudo systemctl is-active --quiet mongod; then
    print_success "MongoDB installed and running"
else
    print_error "MongoDB failed to start"
    exit 1
fi

# ============================================================================
# 4. Install Node.js and PM2
# ============================================================================
print_header "Step 4: Installing Node.js and PM2"

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 globally
sudo npm install -g pm2

# Setup PM2 to start on boot
sudo pm2 startup systemd -u $USER --hp /home/$USER
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u $USER --hp /home/$USER

node --version
pm2 --version

print_success "Node.js and PM2 installed"

# ============================================================================
# 5. Install Project Dependencies
# ============================================================================
print_header "Step 5: Installing Project Dependencies"

# Navigate to project directory
cd "$(dirname "$0")/.."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

print_success "Python dependencies installed"

# ============================================================================
# 6. Setup Environment Variables
# ============================================================================
print_header "Step 6: Setting up Environment Variables"

if [ ! -f .env ]; then
    print_info "Creating .env file..."
    
    cat > .env << 'EOF'
# Bot Tokens
ADMIN_BOT_TOKEN=your_admin_bot_token_here
USER_BOT_TOKEN=your_user_bot_token_here
USER_BOT_USERNAME=your_user_bot_username

# MongoDB
MONGODB_URI=mongodb://localhost:27017/telegram_bot_db

# Telegram Channels
PRIVATE_STORAGE_CHANNEL_ID=-1001234567890
PUBLIC_GROUP_ID=-1001234567890

# Admin User IDs (comma separated)
ADMIN_IDS=123456789,987654321

# Verification Server
VERIFICATION_SERVER_URL=http://your_ec2_ip:5000
VERIFICATION_TOKEN_EXPIRY=600

# Encryption
ENCRYPTION_KEY=generate_a_secure_random_key_here

# Shortlink API
SHORTLINK_API_KEY=your_shortlink_api_key
SHORTLINK_BASE_URL=http://your_shortlink_domain

# File Settings
FILE_PASSWORD=default123
FILE_ACCESS_LIMIT=3
VERIFICATION_PERIOD_HOURS=24
EOF

    print_info "Please edit .env file with your actual values:"
    print_info "  nano .env"
    print_info ""
    print_info "Press Enter after editing..."
    read -r
else
    print_info ".env file already exists"
fi

print_success "Environment configured"

# ============================================================================
# 7. Initialize Database
# ============================================================================
print_header "Step 7: Initializing Database"

python3 << 'EOF'
import asyncio
from database.migrations.init_db import initialize_database

async def main():
    await initialize_database()

asyncio.run(main())
EOF

print_success "Database initialized"

# ============================================================================
# 8. Setup Firewall
# ============================================================================
print_header "Step 8: Configuring Firewall"

sudo apt-get install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow verification server
sudo ufw allow 5000/tcp

print_info "Enable UFW firewall? (y/n)"
read -r enable_ufw

if [ "$enable_ufw" = "y" ]; then
    sudo ufw --force enable
    print_success "Firewall configured"
else
    print_info "Firewall setup skipped"
fi

# ============================================================================
# 9. Setup PM2
# ============================================================================
print_header "Step 9: Setting up PM2 Processes"

# Start all processes
pm2 start ecosystem.config.js

# Save PM2 process list
pm2 save

print_success "PM2 processes started"

# ============================================================================
# 10. Setup Log Rotation
# ============================================================================
print_header "Step 10: Setting up Log Rotation"

sudo bash -c "cat > /etc/logrotate.d/telegram-bot << 'EOFLOG'
/home/$USER/telegram-file-system/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0644 $USER $USER
}
EOFLOG"

print_success "Log rotation configured"

# ============================================================================
# SETUP COMPLETE
# ============================================================================
print_header "SETUP COMPLETE!"

echo ""
print_success "Installation completed successfully!"
echo ""
print_info "Next steps:"
echo "  1. Edit .env file: nano .env"
echo "  2. Check PM2 status: pm2 status"
echo "  3. View logs: pm2 logs"
echo "  4. Monitor: pm2 monit"
echo ""
print_info "Useful commands:"
echo "  - Restart bots: pm2 restart all"
echo "  - Stop bots: pm2 stop all"
echo "  - View logs: pm2 logs"
echo ""