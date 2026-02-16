#!/bin/bash
# Wrapper to run MTD Controller with sudo using the correct virtual environment

# Ensure we are in the script's directory or find the venv
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "Error: 'venv' directory not found in $SCRIPT_DIR"
    exit 1
fi

echo "[*] Starting MTD Controller with sudo..."
echo "Command: sudo ./venv/bin/python3 mtd_controller.py"
sudo ./venv/bin/python3 mtd_controller.py
