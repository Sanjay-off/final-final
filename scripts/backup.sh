#!/bin/bash

# ============================================================================
# Backup Script
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_info() {
    echo -e "${YELLOW}[i] $1${NC}"
}

# Configuration
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="backup_${TIMESTAMP}"
DB_NAME="telegram_bot_db"

mkdir -p "$BACKUP_DIR"

print_info "Creating database backup..."

mongodump --db="$DB_NAME" --out="$BACKUP_DIR/$BACKUP_NAME" --quiet

if [ $? -eq 0 ]; then
    print_success "Backup created: $BACKUP_DIR/$BACKUP_NAME"
else
    echo "Backup failed"
    exit 1
fi

# Compress backup
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

print_success "Backup compressed: ${BACKUP_NAME}.tar.gz"

# Keep only last 7 backups
ls -1t backup_*.tar.gz | tail -n +8 | xargs rm -f 2>/dev/null || true

print_success "Old backups cleaned up"