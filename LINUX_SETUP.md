# Linux (Kali) Setup & Verification Guide

This guide ensures the MTD system runs correctly on Linux environments like Kali, Ubuntu, or Mininet VM.

## 1. Prerequisites
Install core SDN tools using system packages (do NOT use pip for Mininet).

```bash
# Update repositories
sudo apt-get update

# Install Mininet and OpenFlow tools
sudo apt-get install -y mininet openvswitch-switch

# Install Python 3 pip if missing
sudo apt-get install -y python3-pip
```

## 2. Python Dependencies
Install Ryu and other required libraries.

```bash
# Install Ryu SDN Controller
pip install ryu eventlet

# Install Project Dependencies
pip install -r requirements.txt
```

> **Note**: If you get an error about "externally managed environment", use a virtual environment:
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate
> pip install ryu eventlet -r requirements.txt
> ```

## 3. Running the System (3-Terminal Setup)

Open **3 separate terminal windows** (or tabs) to run the full system.

### Terminal 1: The Controller (Brain)
This runs the Ryu Controller with our logic and the Web API.

```bash
# Activate venv if used
source venv/bin/activate

# Start Controller
# If using a virtual environment (venv), you MUST point sudo to the venv's python:
sudo ./venv/bin/python3 mtd_controller.py
```
*Wait until you see `REST API started. Dashboard: http://0.0.0.0:8000/`*

### Terminal 2: The Network (Topology)
This simulates the switches and hosts using Mininet. **Must run as root**.

```bash
# Start Topology
sudo python3 mininet_topo.py --topo 4
```
*You should see the Mininet `mininet>` prompt.*

### Terminal 3: The Scheduler (MTD Logic)
This runs the zone-based shuffling logic.

```bash
source venv/bin/activate
python3 zone_scheduler.py
```
*You should see the Mininet `mininet>` prompt.*

> **Note**: The MTD Scheduler is now integrated into the Controller. You do **NOT** need a 3rd terminal to run `zone_scheduler.py`.


## 4. Verification Steps

1.  **Web Dashboard**: Open Firefox/Chrome inside Kali and go to `http://127.0.0.1:8000/`.
2.  **Ping Test**: In the **Mininet Terminal (Terminal 2)**, type:
    ```bash
    mininet> h1 ping h3
    ```
3.  **Shuffle Test**:
    *   Watch the Dashboard "Live Logs".
    *   In **Terminal 3**, the scheduler should be printing "Shuffle ID..." events.
    *   The IPs in Mininet should change (you can verify in Mininet with `h1 ifconfig`).

## 5. Troubleshooting Common Linux Errors

### "Address already in use"
If the controller fails to start:
```bash
sudo fuser -k 6633/tcp
sudo fuser -k 8000/tcp
```

### "ModuleNotFoundError: No module named ryu"
Ensure you activated your virtual environment (`source .venv/bin/activate`) before running `ryu-manager`.

### "gnome-terminal not found"
If `scripts/run_mtd.sh` fails, it's likely because you don't have Gnome Terminal. Use the "3-Terminal Setup" above manually.
