# Docker Setup for MTD Controller

## Quick Start

### 1. Build the Image

```bash
sudo docker build -t mtd-controller .
```

This uses the existing `Dockerfile` which installs Python 3.8, Ryu 4.34, eventlet 0.30.2, and all project dependencies.

### 2. Run the Controller

```bash
sudo docker run --rm -it \
  --name mtd-controller \
  --network host \
  -v $(pwd):/app \
  mtd-controller
```

> **`--network host`** is required so the controller can:
> - Listen on port `6653` for OpenFlow (Mininet switch connection)
> - Serve REST API on port `8000`
> - Reach the Topology Agent on port `8888`

### 3. Run Mininet (separate terminal)

```bash
sudo python3 mininet_topo.py
```

### 4. Test a Transfer

```bash
curl -s -X POST http://127.0.0.1:8000/sim/secure_transfer \
  -H "Content-Type: application/json" \
  -d '{"src":"h1","dst":"h2","payload":"test"}' | python3 -m json.tool
```

---

## Using `osrg/ryu` Base Image (Alternative)

If you prefer the official Ryu image instead of building from `python:3.8-slim`:

```bash
sudo docker run --rm -it \
  --name mtd-controller \
  --network host \
  -v $(pwd):/app \
  -w /app \
  osrg/ryu bash -c "pip install -r requirements.txt && ryu-manager --ofp-tcp-listen-port 6653 mtd_controller.py"
```

> **Note:** `osrg/ryu` already includes Ryu, so you only need to install the extra project dependencies.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `permission denied` on docker | Use `sudo docker` or add user to docker group: `sudo usermod -aG docker $USER` |
| Port 6653 already in use | Kill existing controller: `sudo fuser -k 6653/tcp` |
| Port 8000 already in use | Kill existing process: `sudo fuser -k 8000/tcp` |
| `ModuleNotFoundError: No module named 'ryu'` | You're running outside Docker — use the Docker commands above |
| Mininet can't connect to controller | Ensure `--network host` is used, and controller shows `Switch connected: 1` |

## Logs

Controller logs appear in the terminal. Previous run logs: [`controller_docker.log`](controller_docker.log)
