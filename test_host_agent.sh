#!/bin/bash
# Quick test script to verify host_agent.py functionality

echo "=========================================="
echo "MTD Host Agent Test Script"
echo "=========================================="

# Check if scripts directory exists
if [ ! -d "scripts" ]; then
    echo "❌ ERROR: scripts/ directory not found"
    exit 1
fi

# Check if host_agent.py exists
if [ ! -f "scripts/host_agent.py" ]; then
    echo "❌ ERROR: scripts/host_agent.py not found"
    exit 1
fi

echo "✓ scripts/host_agent.py found"

# Check if executable
if [ ! -x "scripts/host_agent.py" ]; then
    echo "⚠️  Making host_agent.py executable..."
    chmod +x scripts/host_agent.py
fi

echo "✓ host_agent.py is executable"

# Test help output
echo ""
echo "Testing --help output:"
echo "----------------------------------------"
python3 scripts/host_agent.py --help | head -10

# Test syntax (should fail with missing args, but syntax should be OK)
echo ""
echo "Testing script syntax..."
python3 -m py_compile scripts/host_agent.py 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Python syntax valid"
else
    echo "❌ Python syntax error"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Host agent script is ready!"
echo "=========================================="
echo ""
echo "To test in Mininet:"
echo "  1. Start controller: sudo docker run --rm -it --network host mtd-controller"
echo "  2. Start Mininet: sudo python3 mininet_topo.py"
echo "  3. Check agents: mininet> h1 ps aux | grep host_agent"
echo "  4. View logs: mininet> h1 cat /tmp/h1_agent.log"
echo "  5. Test connection: mininet> h1 curl http://10.0.0.2:8080"
echo ""
