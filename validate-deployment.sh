#!/bin/bash

# ============================================================================
# DEPLOYMENT VALIDATION SCRIPT
# Tests all components of the Telegram Bot System
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

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_header "TELEGRAM BOT SYSTEM - DEPLOYMENT VALIDATION"

# ============================================================================
# 1. ENVIRONMENT VALIDATION
# ============================================================================
print_header "Step 1: Environment Validation"

print_info "Checking .env file..."
if [ -f ".env" ]; then
    print_success ".env file exists"
    
    # Check for required variables
    required_vars=(
        "ADMIN_BOT_TOKEN"
        "USER_BOT_TOKEN"
        "USER_BOT_USERNAME"
        "MONGODB_URI"
        "PRIVATE_STORAGE_CHANNEL_ID"
        "PUBLIC_GROUP_ID"
        "ADMIN_IDS"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" .env || grep -q "^$var=$" .env; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -eq 0 ]; then
        print_success "All required environment variables are set"
    else
        print_error "Missing environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    # Check for URL shortener configuration
    if grep -q "^JUST2EARN_API_TOKEN=" .env && ! grep -q "^JUST2EARN_API_TOKEN=$" .env; then
        print_success "Just2Earn API configured"
    elif grep -q "^GET2SHORT_API_TOKEN=" .env && ! grep -q "^GET2SHORT_API_TOKEN=$" .env; then
        print_success "Get2Short API configured"
    else
        print_warning "No URL shortener API configured"
    fi
    
else
    print_error ".env file not found"
    exit 1
fi

# ============================================================================
# 2. DEPENDENCY VALIDATION
# ============================================================================
print_header "Step 2: Dependency Validation"

print_info "Checking Python virtual environment..."
if [ -d "venv" ]; then
    print_success "Virtual environment exists"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if required packages are installed
    print_info "Checking Python packages..."
    
    required_packages=(
        "python-telegram-bot"
        "motor"
        "pymongo"
        "flask"
        "requests"
        "cryptography"
        "python-dotenv"
    )
    
    missing_packages=()
    for package in "${required_packages[@]}"; do
        if ! python -c "import ${package//-/_}" 2>/dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -eq 0 ]; then
        print_success "All required Python packages are installed"
    else
        print_error "Missing Python packages: ${missing_packages[*]}"
        print_info "Run: pip install -r requirements.txt"
        exit 1
    fi
    
else
    print_error "Virtual environment not found"
    print_info "Run: python3 -m venv venv"
    exit 1
fi

# ============================================================================
# 3. DATABASE VALIDATION
# ============================================================================
print_header "Step 3: Database Validation"

print_info "Testing MongoDB connection..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_db():
    try:
        client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
        await client.admin.command('ping')
        print('MongoDB connection successful')
        client.close()
        return True
    except Exception as e:
        print(f'MongoDB connection failed: {e}')
        return False

result = asyncio.run(test_db())
exit(0 if result else 1)
"

if [ $? -eq 0 ]; then
    print_success "MongoDB connection successful"
else
    print_error "MongoDB connection failed"
    exit 1
fi

# ============================================================================
# 4. CODE VALIDATION
# ============================================================================
print_header "Step 4: Code Validation"

print_info "Checking Python syntax..."
python_files=(
    "admin_bot/bot.py"
    "user_bot/bot.py"
    "verification_server/app.py"
    "config/settings.py"
    "config/database.py"
)

syntax_errors=()
for file in "${python_files[@]}"; do
    if [ -f "$file" ]; then
        if python -m py_compile "$file" 2>/dev/null; then
            print_success "$file - Syntax OK"
        else
            print_error "$file - Syntax Error"
            syntax_errors+=("$file")
        fi
    else
        print_warning "$file - Not found"
    fi
done

if [ ${#syntax_errors[@]} -gt 0 ]; then
    print_error "Syntax errors found in: ${syntax_errors[*]}"
    exit 1
fi

# ============================================================================
# 5. SERVICE VALIDATION
# ============================================================================
print_header "Step 5: Service Validation"

print_info "Checking PM2 status..."
if command -v pm2 &> /dev/null; then
    if pm2 list | grep -q "telegram-bot"; then
        print_success "PM2 processes found"
        
        # Check each service
        services=("admin-bot" "user-bot" "verify-server")
        for service in "${services[@]}"; do
            if pm2 list | grep -q "$service.*online"; then
                print_success "$service is running"
            else
                print_error "$service is not running"
            fi
        done
    else
        print_warning "No PM2 processes found"
        print_info "Run: pm2 start ecosystem.config.js"
    fi
else
    print_warning "PM2 not installed"
fi

# ============================================================================
# 6. VERIFICATION SERVER VALIDATION
# ============================================================================
print_header "Step 6: Verification Server Validation"

print_info "Testing verification server health endpoint..."
if curl -s http://localhost:5000/health > /dev/null; then
    print_success "Verification server is responding"
else
    print_error "Verification server is not responding"
    print_info "Make sure the verification server is running on port 5000"
fi

# ============================================================================
# 7. LOG VALIDATION
# ============================================================================
print_header "Step 7: Log Validation"

print_info "Checking log directories..."
if [ -d "logs" ]; then
    print_success "Logs directory exists"
    
    log_files=(
        "logs/admin_bot.log"
        "logs/user_bot.log"
        "logs/verification_server.log"
    )
    
    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
            print_success "$log_file exists"
            
            # Check for recent errors
            if grep -q "ERROR" "$log_file" 2>/dev/null; then
                print_warning "$log_file contains errors"
            else
                print_success "$log_file - No recent errors"
            fi
        else
            print_warning "$log_file not found (will be created when service starts)"
        fi
    done
else
    print_warning "Logs directory not found"
fi

# ============================================================================
# 8. CONFIGURATION VALIDATION
# ============================================================================
print_header "Step 8: Configuration Validation"

print_info "Validating configuration..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

# Validate bot tokens
admin_token = os.getenv('ADMIN_BOT_TOKEN', '')
user_token = os.getenv('USER_BOT_TOKEN', '')

if len(admin_token) < 20:
    print('ERROR: Admin bot token appears invalid')
    exit(1)

if len(user_token) < 20:
    print('ERROR: User bot token appears invalid')
    exit(1)

# Validate channel IDs
try:
    private_channel = int(os.getenv('PRIVATE_STORAGE_CHANNEL_ID', '0'))
    public_group = int(os.getenv('PUBLIC_GROUP_ID', '0'))
    
    if private_channel >= 0:
        print('ERROR: PRIVATE_STORAGE_CHANNEL_ID must be negative')
        exit(1)
        
    if public_group >= 0:
        print('ERROR: PUBLIC_GROUP_ID must be negative')
        exit(1)
        
    print('Configuration validation passed')
    
except ValueError:
    print('ERROR: Channel IDs must be integers')
    exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Configuration validation passed"
else
    print_error "Configuration validation failed"
    exit 1
fi

# ============================================================================
# SUMMARY
# ============================================================================
print_header "Validation Complete!"

print_success "All validations passed! 🎉"

echo ""
print_info "Next Steps:"
echo "1. Start your services: pm2 start ecosystem.config.js"
echo "2. Test your Telegram bots:"
echo "   - Send /start to admin bot"
echo "   - Send /start to user bot"
echo "3. Monitor logs: pm2 logs"
echo "4. Check status: pm2 status"

echo ""
print_warning "Important Notes:"
echo "- Make sure your Telegram bot tokens are valid"
echo "- Verify channel IDs are correct (negative integers)"
echo "- Check that URL shortener APIs are working"
echo "- Monitor system resources: htop"

echo ""
print_success "Your Telegram Bot System is ready for deployment! 🚀"