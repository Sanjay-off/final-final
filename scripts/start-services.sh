#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

echo -e "\n${GREEN}====== Starting Services ======${NC}\n"

# Navigate to project directory
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# Check if .env exists
if [ ! -f .env ]; then
    print_error ".env file not found"
    exit 1
fi

# Start MongoDB if not running
print_info "Checking MongoDB..."
if ! pgrep -x "mongod" > /dev/null; then
    print_info "Starting MongoDB..."
    sudo systemctl start mongod
    sleep 2
fi

if pgrep -x "mongod" > /dev/null; then
    print_success "MongoDB is running"
else
    print_error "MongoDB failed to start"
    exit 1
fi

# Start PM2 services
print_info "Starting PM2 services..."

pm2 start ecosystem.config.js

# Check status
sleep 2
pm2 status

# Save PM2 configuration
pm2 save

print_success "All services started!"
print_info "View logs: pm2 logs"
print_info "Monitor: pm2 monit"

echo ""
