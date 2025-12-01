#!/bin/bash

# ============================================================================
# Deployment Script
# ============================================================================

set -e

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

print_header "DEPLOYMENT SCRIPT"

# ============================================================================
# 1. Pre-deployment Checks
# ============================================================================
print_header "Step 1: Pre-deployment Checks"

if [ ! -f .env ]; then
    print_error ".env file not found!"
    exit 1
fi

if ! command -v pm2 &> /dev/null; then
    print_error "PM2 not installed. Run setup.sh first."
    exit 1
fi

print_success "Pre-deployment checks passed"

# ============================================================================
# 2. Backup Database
# ============================================================================
print_header "Step 2: Creating Backup"

./scripts/backup.sh

print_success "Backup created"

# ============================================================================
# 3. Update Dependencies
# ============================================================================
print_header "Step 3: Updating Dependencies"

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

print_success "Dependencies updated"

# ============================================================================
# 4. Restart Services
# ============================================================================
print_header "Step 4: Restarting Services"

pm2 reload ecosystem.config.js
sleep 5
pm2 status

print_success "Services restarted"

# ============================================================================
# DEPLOYMENT COMPLETE
# ============================================================================
print_header "DEPLOYMENT COMPLETE!"

echo ""
print_success "Deployment completed successfully!"
print_info "View logs: pm2 logs"
print_info "Monitor: pm2 monit"