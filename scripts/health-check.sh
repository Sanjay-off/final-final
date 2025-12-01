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

print_warn() {
    echo -e "${YELLOW}[⚠] $1${NC}"
}

echo -e "\n${GREEN}====== System Health Check ======${NC}\n"

# MongoDB Check
print_warn "Checking MongoDB..."
if pgrep -x "mongod" > /dev/null; then
    print_success "MongoDB is running"
else
    print_error "MongoDB is NOT running"
fi

# PM2 Status
print_warn "Checking PM2 services..."
pm2 status

# Check disk space
print_warn "Disk Space:"
df -h | grep -E 'Filesystem|/$'

# Check memory
print_warn "Memory Usage:"
free -h | head -2

# Check if services are working
print_warn "Checking service connectivity..."

# Admin Bot
curl -s http://localhost:8000/health > /dev/null 2>&1 && print_success "Admin Bot responding" || print_error "Admin Bot not responding"

# Verification Server
curl -s http://localhost:5000/health > /dev/null 2>&1 && print_success "Verification Server responding" || print_error "Verification Server not responding"

echo ""
