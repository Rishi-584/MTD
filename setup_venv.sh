#!/bin/bash
# setup_venv.sh
# Sets up a local isolated environment for MTD Controller

set -e # Exit on error

echo "[*] Creating Python Virtual Environment (venv)..."
# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "[*] Activating Environment..."
source venv/bin/activate

echo "[*] Upgrading pip..."
pip install --upgrade pip

echo "[*] Pinning 'setuptools' to v59.6.0 and installing 'wheel'..."
# wheel is required for allow-no-build-isolation to work with setuptools backend
pip install "setuptools==59.6.0" "wheel"

echo "[*] Installing Ryu and sub-dependencies..."
# We explicitly install oslo.config and force eventlet version
# We use --no-build-isolation to ensure it uses our pinned setuptools
pip install --no-build-isolation "eventlet<0.34.0" "oslo.config" "msgpack" ryu

echo "[*] Installing Project Dependencies..."
pip install requests pyyaml

echo ""
echo "========================================"
echo "[+] DONE! Environment is ready."
echo "========================================"
echo "To run the controller now, use this command:"
echo "sudo ./venv/bin/python3 mtd_controller.py"
echo ""
