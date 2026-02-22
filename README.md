# Moving Target Defense (MTD) — Hospital Network Simulation

A **Moving Target Defense** system for a simulated hospital network, built on Software-Defined Networking (SDN). The system dynamically rotates public-facing IP addresses to reduce attack surface and improve resilience against reconnaissance and persistent attacks (APTs), while maintaining service continuity.

> **Platform:** Linux (Ubuntu 20.04+ / Kali). Requires root privileges for Mininet, Ryu, and OVS.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Running the System](#running-the-system)
- [Web Dashboard](#web-dashboard)
- [API Reference](#api-reference)
- [Zone Policies & Access Control](#zone-policies--access-control)
- [Packet Transfer & Verification](#packet-transfer--verification)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)

---

## How It Works

In traditional static networks, IP addresses remain constant, giving attackers time to scan, map, and exploit targets. This project counters that by:

1. **Assigning Private IPs** — Hosts get static private addresses (`10.0.0.x`) that are never exposed externally.
2. **Mapping to Public IPs** — The MTD Gateway assigns temporary public IPs (`172.16.0.50–99`) via NAT.
3. **Rotating (Hopping)** — When a zone timer fires (or a threat is detected), a new public IP is selected and new OpenFlow rules are installed on the switches.
4. **Grace Period** — Old rules remain briefly ("shadow period") so in-flight packets are not dropped.
5. **DNS Update** — Other hosts resolve to the new IP automatically.

Secure communication is simulated with **TLS 1.3 / AES-256-GCM / ECDHE / SHA-384**. TLS session IDs allow connections to resume seamlessly after an IP rotation.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Control Plane                     │
│           mtd_controller.py (Ryu SDN)               │
│  DHCP/DNS · NAT · Flow Tables · Policies · REST API │
│              SQLite (mtd_state.db)                  │
└──────────────────────┬──────────────────────────────┘
                       │ OpenFlow 1.3
┌──────────────────────▼──────────────────────────────┐
│                    Data Plane                       │
│            mininet_topo.py (Mininet)                │
│    h1,h2 (High) · h3,h4 (Med) · h5,h6 (Low)       │
│         OpenFlow Switches · Topology Agent          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                   MTD Engine                        │
│     zone_scheduler.py (integrated in controller)    │
│   High: 40s · Medium: 20s · Low: 10s rotation      │
└─────────────────────────────────────────────────────┘
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| Controller | `mtd_controller.py` | Ryu SDN controller — DHCP/DNS, NAT, flow management, REST API (port 8000), SQLite persistence |
| Topology | `mininet_topo.py` | Virtual network with hosts h1–h6, OVS switches, topology agent (port 8888) |
| Scheduler | `zone_scheduler.py` | Zone-based IP rotation orchestration (also runs inside the controller) |
| Host Agent | `scripts/host_agent.py` | HTTP server/client on each host (port 8080) — handles data transfer, ACKs, crypto verification |
| Policies | `policies.yml` | Zone assignments, ACL rules, shuffle intervals |
| Web UI | `web/` | Dashboard with live NAT table, hopping history, log viewer |
| Docker | `Dockerfile` | Containerized controller (Python 3.8, pinned Ryu + eventlet) |

---

## Project Structure

```
MTD/
├── mtd_controller.py       # Ryu SDN controller (core)
├── mininet_topo.py          # Mininet topology generator
├── zone_scheduler.py        # MTD zone-based scheduler
├── policies.yml             # Zone & ACL configuration
├── Dockerfile               # Containerized controller
├── requirements.txt         # Python dependencies
├── dhcpd.conf / dnsmasq.conf
├── scripts/
│   ├── host_agent.py        # Host HTTP agent (server + client)
│   ├── gen_certs.sh         # TLS certificate generation
│   └── verify_secure_transfer.py
├── web/
│   ├── index.html           # Main dashboard
│   ├── logs.html            # Real-time log viewer (SSE streaming)
│   ├── script.js            # Dashboard logic
│   └── style.css            # Styles
├── debug_policy.py          # Policy debugging utility
├── verify_all.py            # Verification suite
├── verify_zones.py          # Zone config checker
├── demo_packet_transfer.sh  # Automated demo script
├── test_error_cases.sh      # Error handling tests
└── mtd_state.db             # SQLite state database
```

---

## Setup

### Option A: Docker (Recommended for Kali)

```bash
# Build controller image
sudo docker build -t mtd-controller .
```

### Option B: Native Install

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv mininet openvswitch-switch dnsmasq nmap

# Virtual environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# If Ryu fails with setuptools error:
pip install "setuptools<70"
pip install ryu eventlet==0.30.2
```

---

## Running the System

### Terminal 1 — Controller

**Docker:**
```bash
sudo docker run --rm -it --network host --name mtd-controller mtd-controller
```

**Native:**
```bash
sudo ./venv/bin/python3 mtd_controller.py
```

Wait for: `REST API started. Dashboard: http://0.0.0.0:8000/`

### Terminal 2 — Mininet Topology

```bash
sudo python3 mininet_topo.py --topo 6
```

Wait for the `mininet>` prompt. Host agents start automatically on port 8080.

### Verify

```bash
# In Mininet CLI
mininet> pingall
mininet> h1 ps aux | grep host_agent    # Confirm agents running
mininet> h1 curl http://10.0.0.2:8080   # Direct connectivity test
```

### Open Dashboard

Navigate to **http://127.0.0.1:8000/** in a browser.

---

## Web Dashboard

- **Operations Center** — Run ping tests, send secure data between hosts
- **Live NAT Table** — Current public IP for every host
- **Hopping History** — Timeline of every IP rotation event
- **Packet Construction** — Compare cleartext vs encrypted hex dumps
- **Flow Diagram** — Animated packet path (Source → Gateway → Dest)
- **Host Agent Logs** — Real-time streaming via SSE at `/logs.html`

---

## API Reference

### Controller REST API (`http://127.0.0.1:8000`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/status` | All hosts, NAT mappings, active flows |
| `GET` | `/logs` | Shuffle history and events |
| `GET` | `/dns?q=h2` | Resolve hostname → current public IP |
| `GET` | `/host_logs?host=h5&lines=100` | Host agent logs |
| `GET` | `/host_logs_stream?host=h5` | SSE stream of host logs |
| `POST` | `/shuffle` | Trigger IP rotation: `{"hosts":["h1","h2"]}` |
| `POST` | `/sim/dhcp_discover` | Simulate DHCP discovery |
| `POST` | `/sim/secure_transfer` | Secure data transfer: `{"src":"h1","dst":"h2","payload":"..."}` |

### Topology Agent (`http://127.0.0.1:8888`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/exec` | Execute command on host: `{"host":"h1","cmd":"ping -c 1 10.0.0.2"}` |

---

## Zone Policies & Access Control

### Zone Assignments

| Zone | Hosts | Hopping Interval | Description |
|------|-------|-------------------|-------------|
| **High** | h1, h2 | 40s | ICU, critical servers |
| **Medium** | h3, h4 | 20s | Staff workstations |
| **Low** | h5, h6 | 10s | Guest WiFi, IoT |

### Access Control Matrix

| Source ↓ / Dest → | High | Medium | Low |
|-------------------|------|--------|-----|
| **High** | ✅ | ✅ | ✅ |
| **Medium** | ❌ | ✅ | ✅ |
| **Low** | ❌ | ❌ | ✅ |

ACLs are defined in `policies.yml` and evaluated sequentially (first match wins).

---

## Packet Transfer & Verification

### Send via Controller API

```bash
curl -X POST http://127.0.0.1:8000/sim/secure_transfer \
  -H "Content-Type: application/json" \
  -d '{"src":"h1","dst":"h2","payload":"Hello from h1"}' | jq
```

### Send via Host Agent (Mininet CLI)

```bash
mininet> h1 python3 scripts/host_agent.py --host h1 --client --target h2 --count 5 --interval 2
```

### Monitor Receiver

```bash
tail -f /tmp/h2_agent.log
```

### Verification Layers

The controller performs multi-layer verification on each transfer:

1. **Policy** — Zone-based ACL check
2. **Network** — ICMP ping connectivity
3. **Crypto** — AES-256-GCM encryption
4. **NAT** — Private ↔ Public IP translation
5. **Delivery** — TCP + HTTP to destination agent
6. **Integrity** — SHA-256 payload hash match
7. **Session** — UUID session ID verification
8. **Signature** — HMAC-SHA256 authenticity check

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Address already in use** | `sudo fuser -k 6633/tcp && sudo fuser -k 8000/tcp` |
| **Ryu setuptools error** | `pip install "setuptools<70"` then reinstall ryu |
| **Hosts show 0.0.0.0** | Run `pingall` in Mininet to trigger DHCP registration |
| **Host agent not running** | `mininet> h2 python3 scripts/host_agent.py --host h2 --server > /tmp/h2_agent.log 2>&1 &` |
| **NetworkManager conflicts** | `sudo systemctl stop NetworkManager` |
| **Flow table conflicts** | `sudo ovs-ofctl del-flows s1` then restart controller |
| **Connection refused on 8080** | Verify agent: `mininet> h2 ps aux \| grep host_agent` |
| **DNS resolution fails** | `curl http://127.0.0.1:8000/dns?q=h2` — ensure controller is running |
| **ModuleNotFoundError: ryu** | Activate venv: `source venv/bin/activate` |
| **Mock mode warning** | Ryu not installed — controller runs without packet handling |

### Inspect Flow Tables

```bash
sudo ovs-ofctl dump-flows s1
```

**Flow priority hierarchy:** ARP (1000) > ICMP (500) > NAT per-host (100) > Default (1).

---

## Security Notes

- `SECRET` key in `mtd_controller.py` is hardcoded for demo — use an env variable in production.
- HTTPS simulation uses AES-256-GCM with random keys per session (demonstrative, not actual TLS).
- Zone policies are examples — real hospital networks require more granular rules.
- The system runs with root privileges (required by Mininet/OVS) — use caution in non-lab environments.

---

## Database Schema

SQLite database (`mtd_state.db`):

| Table | Key Columns |
|-------|-------------|
| `hosts` | hostname, mac, private_ip, zone, last_seen |
| `nat_mappings` | private_ip, public_ip, timestamp, active |
| `shuffle_log` | host, old_ip, new_ip, timestamp, shuffle_id |
| `dns_records` | hostname, public_ip, ttl, last_updated |
