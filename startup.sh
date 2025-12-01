#!/bin/bash

echo "=========================================="
echo "  Telegram File System - Startup Script"
echo "=========================================="

# ----------------------------
# PATH CONFIGURATION
# ----------------------------
PROJECT_DIR="$(pwd)"
VENV_DIR="$PROJECT_DIR/venv"

ADM_BOT="admin_bot/bot.py"
USR_BOT="user_bot/bot.py"
VERIFY_SERVER="verification_server/app.py"

LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

# ----------------------------
# CREATE VENV IF NOT EXISTS
# ----------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creating virtual environment..."
    python3 -m venv venv
fi

# ----------------------------
# ACTIVATE VENV
# ----------------------------
echo "[+] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# ----------------------------
# INSTALL REQUIREMENTS
# ----------------------------
echo "[+] Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# ----------------------------
# CHECK .env FILE
# ----------------------------
if [ ! -f .env ]; then
    echo "[!] .env file not found. Creating from template..."
    cp .env.example .env
    echo "[!] Please edit .env file with your configuration"
    echo "[!] Then run this script again"
    exit 1
fi

echo ""
echo "-------------------------------------------"
echo " Starting Admin Bot"
echo "-------------------------------------------"

nohup python3 "$ADM_BOT" > "$LOG_DIR/admin_bot.log" 2>&1 &
ADMIN_PID=$!
echo "[+] Admin Bot running in background (PID: $ADMIN_PID)"

echo ""
echo "-------------------------------------------"
echo " Starting User Bot"
echo "-------------------------------------------"

nohup python3 "$USR_BOT" > "$LOG_DIR/user_bot.log" 2>&1 &
USER_PID=$!
echo "[+] User Bot running in background (PID: $USER_PID)"

echo ""
echo "-------------------------------------------"
echo " Starting Verification Server (Port 5000)"
echo "-------------------------------------------"

nohup python3 "$VERIFY_SERVER" > "$LOG_DIR/verification_server.log" 2>&1 &
VERIFY_PID=$!
echo "[+] Verification Server running in background (PID: $VERIFY_PID)"

echo ""
echo "=========================================="
echo " All services started successfully! 🔥"
echo " Logs available in: $LOG_DIR"
echo ""
echo " PIDs:"
echo "  Admin Bot: $ADMIN_PID"
echo "  User Bot: $USER_PID"
echo "  Verification Server: $VERIFY_PID"
echo ""
echo " To stop all services, run:"
echo "  kill $ADMIN_PID $USER_PID $VERIFY_PID"
echo "=========================================="
