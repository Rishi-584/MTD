#!/bin/bash
# MTD Hospital Network Simulation - Unified Run Script

echo "=================================================="
echo "   MTD HOSPITAL NETWORK SIMULATION - LAUNCHER"
echo "=================================================="

# 1. Cleanup
echo "[*] Cleaning up old Mininet and Docker processes..."
sudo mn -c > /dev/null 2>&1
sudo docker stop mtd-controller > /dev/null 2>&1

# 2. Build Controller
echo "[*] Building MTD Controller Docker Image..."
sudo docker build -t mtd-controller .

# 3. Instructions
echo ""
echo "=================================================="
echo "   READY TO START!"
echo "=================================================="
echo "Please follow these steps exactly:"
echo ""
echo "1. Run the Controller in THIS terminal:"
echo "   sudo docker run --rm -it --network host --name mtd-controller mtd-controller"
echo ""
echo "2. Open a NEW MESSAGE TERMINAL (Terminal 2) and run Mininet:"
echo "   cd $(pwd)"
echo "   sudo python3 mininet_topo.py"
echo ""
echo "3. In Mininet (Terminal 2), type:"
echo "   pingall"
echo "   (This connects everyone and populates the dashboard)"
echo ""
echo "4. Dashboard: http://localhost:8000"
echo "=================================================="
