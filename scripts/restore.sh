#!/bin/bash

# ============================================================================
# Telegram File Distribution System - Restore Script
# ============================================================================
# This script restores MongoDB database from a backup
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

print_header "RESTORE SCRIPT"

# Configuration
BACKUP_DIR="backups"
DB_NAME="telegram_bot_db"

# ============================================================================
# 1. List Available Backups
# ============================================================================
print_header "Available Backups"

if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR/*.tar.gz 2>/dev/null)" ]; then
    print_error "No backups found in $BACKUP_DIR"
    exit 1
fi

echo "Available backup files:"
ls -lh "$BACKUP_DIR"/*.tar.gz | awk '{print NR". "$9" ("$5")"}'

# ============================================================================
# 2. Select Backup
# ============================================================================
echo ""
print_info "Enter the number of the backup to restore (or 'q' to quit):"
read -r selection

if [ "$selection" = "q" ]; then
    print_info "Restore cancelled"
    exit 0
fi

# Get selected backup file
BACKUP_FILE=$(ls -1 "$BACKUP_DIR"/*.tar.gz | sed -n "${selection}p")

if [ -z "$BACKUP_FILE" ]; then
    print_error "Invalid selection"
    exit 1
fi

print_info "Selected backup: $BACKUP_FILE"

# ============================================================================
# 3. Confirmation
# ============================================================================
echo ""
print_error "WARNING: This will replace the current database!"
print_info "Current database '$DB_NAME' will be dropped and restored from backup."
print_info "Do you want to continue? (yes/no)"
read -r confirmation

if [ "$confirmation" != "yes" ]; then
    print_info "Restore cancelled"
    exit 0
fi

# ============================================================================
# 4. Stop Services
# ============================================================================
print_header "Step 1: Stopping Services"

if command -v pm2 &> /dev/null; then
    pm2 stop all
    print_success "Services stopped"
else
    print_info "PM2 not found, skipping service stop"
fi

# ============================================================================
# 5. Extract Backup
# ============================================================================
print_header "Step 2: Extracting Backup"

TEMP_DIR=$(mktemp -d)
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

BACKUP_NAME=$(basename "$BACKUP_FILE" .tar.gz)

if [ ! -d "$TEMP_DIR/$BACKUP_NAME/mongodb" ]; then
    print_error "Invalid backup file: MongoDB backup not found"
    rm -rf "$TEMP_DIR"
    exit 1
fi

print_success "Backup extracted"

# ============================================================================
# 6. Restore Database
# ============================================================================
print_header "Step 3: Restoring Database"

# Drop existing database
mongo "$DB_NAME" --eval "db.dropDatabase()" --quiet

# Restore from backup
mongorestore --db="$DB_NAME" "$TEMP_DIR/$BACKUP_NAME/mongodb/$DB_NAME" --quiet

if [ $? -eq 0 ]; then
    print_success "Database restored successfully"
else
    print_error "Database restore failed"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# ============================================================================
# 7. Restore Environment File (Optional)
# ============================================================================
print_header "Step 4: Restoring Environment File"

if [ -f "$TEMP_DIR/$BACKUP_NAME/env_backup" ]; then
    print_info "Environment file found in backup. Restore it? (yes/no)"
    read -r restore_env
    
    if [ "$restore_env" = "yes" ]; then
        cp "$TEMP_DIR/$BACKUP_NAME/env_backup" .env
        print_success "Environment file restored"
    else
        print_info "Keeping current .env file"
    fi
else
    print_info "No environment file in backup"
fi

# ============================================================================
# 8. Cleanup
# ============================================================================
print_header "Step 5: Cleanup"

rm -rf "$TEMP_DIR"
print_success "Temporary files cleaned up"

# ============================================================================
# 9. Restart Services
# ============================================================================
print_header "Step 6: Restarting Services"

if command -v pm2 &> /dev/null; then
    pm2 restart all
    sleep 3
    pm2 status
    print_success "Services restarted"
else
    print_info "PM2 not found, please start services manually"
fi

# ============================================================================
# RESTORE COMPLETE
# ============================================================================
print_header "RESTORE COMPLETE!"

echo ""
print_success "Database restored successfully from: $BACKUP_FILE"
echo ""
print_info "Next steps:"
echo "  1. Verify database integrity: mongo telegram_bot_db"
echo "  2. Check bot functionality"
echo "  3. Monitor logs: pm2 logs"
echo ""