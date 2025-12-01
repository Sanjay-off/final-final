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

echo -e "\n${GREEN}====== Initializing Database ======${NC}\n"

# Navigate to project directory
cd "$(dirname "$0")/.."

# Activate venv
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Run setup.sh first."
    exit 1
fi

source venv/bin/activate

# Check MongoDB connection
print_info "Testing MongoDB connection..."

python3 << 'EOF'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys

async def test_connection():
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        print("✅ MongoDB connection successful")
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

result = asyncio.run(test_connection())
sys.exit(0 if result else 1)
EOF

if [ $? -ne 0 ]; then
    print_error "MongoDB not running. Start MongoDB first:"
    echo "sudo systemctl start mongod"
    exit 1
fi

# Initialize database with migrations
print_info "Creating collections and indexes..."

python3 << 'EOF'
import asyncio
from config.database import connect_database, create_indexes
from database.migrations.init_db import initialize_database

async def init_db():
    try:
        # Connect to database
        db = connect_database()
        print("✅ Connected to database")
        
        # Create indexes
        await create_indexes()
        print("✅ Indexes created")
        
        # Run migrations
        success = await initialize_database()
        if success:
            print("✅ Database initialized successfully")
        else:
            print("❌ Database initialization failed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(init_db())
EOF

print_success "Database initialization complete!"
echo ""
