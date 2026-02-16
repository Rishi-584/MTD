# Moving Target Defense (MTD) — Turnkey Repo

This repository contains a production-ready implementation skeleton for the MTD system described in your action plan.
It includes a Ryu controller, Mininet topology generator, DHCP/DNS configs, policy examples, tests, and helper scripts.

**Important:** Running Mininet, dnsmasq, and Ryu requires root privileges and a Linux environment. This repo is designed for Ubuntu 20.04+.

## Quick start (example)
1. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3.10-venv dnsmasq isc-dhcp-server nmap
   sudo pip3 install -r requirements.txt
   ```

2. Start topology:
   ```bash
   sudo python3 mininet_topo.py --topo 4
   ```

3. Start controller:
   ```bash
   sudo ryu-manager mtd_controller.py
   ```

4. Start dnsmasq (use provided dnsmasq.conf) and dhcp server (or dnsmasq can handle DHCP):
   ```bash
   sudo systemctl stop NetworkManager
   sudo dnsmasq --conf-file=dnsmasq.conf
   ```

5. Run tests (from a root terminal):
   ```bash
   sudo python3 -m pytest tests
   ```

See `docs/troubleshooting.md` for common issues.

