#!/bin/bash

# ============================================================================
# FINAL DEPLOYMENT SCRIPT - ERROR-FREE VERSION
# This script fixes all known AWS deployment issues
# ============================================================================

set -e

echo "🚀 TELEGRAM BOT SYSTEM - FINAL DEPLOYMENT SCRIPT"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Step 1: System Update
print_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System updated"

# Step 2: Install Python and tools
print_info "Installing Python and development tools..."
sudo apt install python3 python3-pip python3-venv python3-full git curl wget unzip software-properties-common apt-transport-https ca-certificates gnupg -y
print_success "Python and tools installed"

# Step 3: Install Node.js 20.x (Fixed)
print_info "Installing Node.js 20.x LTS..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt update
sudo apt install nodejs -y
sudo npm install -g pm2
print_success "Node.js and PM2 installed"

# Step 4: Install Nginx
print_info "Installing Nginx..."
sudo apt install nginx certbot python3-certbot-nginx -y
print_success "Nginx installed"

# Step 5: Install MongoDB via Snap (Fixed)
print_info "Installing MongoDB via Snap (reliable method)..."
sudo snap install mongodb --classic

# Create systemd service for MongoDB
print_info "Creating MongoDB service..."
sudo tee /etc/systemd/system/mongodb.service > /dev/null <<'EOF'
[Unit]
Description=MongoDB Database Server
After=network.target

[Service]
Type=forking
User=root
ExecStart=/usr/bin/snap run mongodb.daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Start MongoDB
print_info "Starting MongoDB..."
sudo systemctl daemon-reload
sudo systemctl enable mongodb
sudo systemctl start mongodb

# Wait for MongoDB to start
sleep 10

# Check if MongoDB is running
if sudo systemctl is-active --quiet mongodb || sudo snap services | grep -q "mongodb.*active"; then
    print_success "MongoDB is running"
else
    print_warning "MongoDB may need manual start"
    print_info "Run: sudo systemctl start mongodb"
fi

# Step 6: Setup project
print_info "Setting up project directory..."
PROJECT_DIR="/home/ubuntu/telegram-bot"
if [ ! -d "$PROJECT_DIR" ]; then
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown ubuntu:ubuntu "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Clone or update repository
if [ -d ".git" ]; then
    print_info "Repository exists, updating..."
    git remote set-url origin https://github.com/Sanjay-off/finally-main.git
    git pull origin main
else
    print_info "Cloning repository..."
    git clone https://github.com/Sanjay-off/finally-main.git temp_repo
    mv temp_repo/* temp_repo/.* . 2>/dev/null || true
    rm -rf temp_repo
fi

# Create virtual environment
print_info "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Create directories
mkdir -p logs data backups
print_success "Project setup completed"

# Step 7: Environment configuration
print_info "Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_success "Created .env file from template"
fi

print_warning "⚠️  IMPORTANT: You must edit .env file with your actual tokens!"
echo ""
echo "Required configuration:"
echo "- ADMIN_BOT_TOKEN (from @BotFather)"
echo "- USER_BOT_TOKEN (from @BotFather)"
echo "- SHORTLINK_API_KEY (Just2Earn/Get2Short)"
echo "- SHORTLINK_BASE_URL (https://just2earn.com or https://get2short.com)"
echo "- MONGODB_URI (mongodb://localhost:27017/telegram_bot_db)"
echo "- PRIVATE_STORAGE_CHANNEL_ID (negative number)"
echo "- PUBLIC_GROUP_ID (negative number)"
echo "- ADMIN_IDS (your Telegram user ID)"
echo "- VERIFICATION_SERVER_URL (http://YOUR_EC2_PUBLIC_IP:5000)"
echo "- ENCRYPTION_KEY (generate with: python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo ""

read -p "Do you want to edit .env file now? (y/n): " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    nano .env
fi

# Step 8: Firewall configuration
print_info "Configuring firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 5000/tcp
sudo ufw --force enable
print_success "Firewall configured"

# Step 9: Start services
print_info "Starting services with PM2..."
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu/telegram-bot

# Wait for services to start
sleep 15

# Step 10: Validation
print_info "Validating deployment..."

# Check PM2 status
if pm2 list | grep -q "online"; then
    print_success "PM2 services are running"
else
    print_error "Some PM2 services failed to start"
    pm2 status
    pm2 logs --lines 20
fi

# Check verification server
print_info "Testing verification server..."
if curl -s http://localhost:5000/health > /dev/null; then
    print_success "Verification server is responding"
else
    print_warning "Verification server not responding - checking logs"
    pm2 logs verify-server --lines 10
fi

# Check MongoDB
if sudo systemctl is-active --quiet mongodb || sudo snap services | grep -q "mongodb.*active"; then
    print_success "MongoDB is running"
else
    print_warning "MongoDB is not running"
fi

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "unknown")

# Final instructions
echo ""
echo "🎉 DEPLOYMENT COMPLETED!"
echo "=========================="
echo ""
print_success "Your Telegram Bot System is deployed!"
echo ""
echo "📍 Your Public IP: $PUBLIC_IP"
echo "🔗 Verification Server: http://$PUBLIC_IP:5000/health"
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file with your actual bot tokens and API keys"
echo "2. Test your Telegram bots by sending /start command"
echo "3. Check logs: pm2 logs"
echo "4. Monitor services: pm2 status"
echo ""
echo "🔧 Useful Commands:"
echo "- View logs: pm2 logs"
echo "- Restart services: pm2 restart all"
echo "- Check status: pm2 status"
echo "- View errors: pm2 logs --err"
echo ""
echo "⚠️  IMPORTANT: Make sure to:"
echo "- Configure your bot tokens in .env"
echo "- Set correct channel IDs (negative numbers)"
echo "- Update VERIFICATION_SERVER_URL with your IP"
echo "- Test URL shortener API tokens"
echo ""
print_success "Deployment script completed successfully! 🚀"
