import requests
import time
import json
import sys

BASE = "http://127.0.0.1:8000"

# -------------------------------
# Zone Configuration
# -------------------------------
ZONES = {
    "high": {
        "hosts": ["h1", "h2"],
        "interval": 40,
        "last_run": 0
    },
    "medium": {
        "hosts": ["h3", "h4"],
        "interval": 20,
        "last_run": 0
    },
    "low": {
        "hosts": ["h5", "h6"],
        "interval": 10,
        "last_run": 0
    }
}

def log(msg):
    print(f"[ZONE-MTD] {msg}")

def safe_get(endpoint):
    r = requests.get(f"{BASE}{endpoint}", timeout=10)
    r.raise_for_status()
    return r.json()

def safe_post(endpoint, payload):
    r = requests.post(f"{BASE}{endpoint}", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

# -------------------------------
# Initial DHCP (ONE TIME)
# -------------------------------
def initial_dhcp():
    log("Starting initial DHCP assignment...")
    for i in range(1, 7):
        hostname = f"h{i}"
        mac = f"00:00:00:00:00:0{i}"

        resp = safe_post("/sim/dhcp_discover", {
            "hostname": hostname,
            "mac": mac
        })

        log(f"{hostname} assigned IP {resp['ip']}")
    log("Initial DHCP completed.\n")

# -------------------------------
# MAIN SCHEDULER LOOP
# -------------------------------
def scheduler():
    log("Zone-based MTD scheduler started")
    log("Different zones hop at different intervals")
    log("Press Ctrl+C to stop\n")

    while True:
        now = time.time()

        for zone_name, zone in ZONES.items():
            if now - zone["last_run"] >= zone["interval"]:
                try:
                    resp = safe_post("/shuffle", {
                        "hosts": zone["hosts"],
                        "policy": f"{zone_name}_zone"
                    })

                    shuffle_id = resp.get("shuffle_id", "N/A")
                    zone["last_run"] = now

                    logs = safe_get("/logs")[-len(zone["hosts"]):]

                    log(f"[{zone_name.upper()}] Shuffle ID: {shuffle_id}")
                    for entry in logs:
                        if entry.get("host") in zone["hosts"]:
                            old = entry.get('old_ip', 'N/A')
                            new = entry.get('new_ip', entry.get('public', 'N/A'))
                            print(
                                f"  {entry.get('host')}: {old} → {new}"
                            )

                except Exception as e:
                    log(f"[{zone_name.upper()} ERROR] {e}")

                # Small gap to avoid back-to-back requests
                time.sleep(1)

        time.sleep(1)

# -------------------------------
# ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    try:
        log("Checking MTD Controller status...")
        status = safe_get("/status")
        print(json.dumps(status, indent=2))

        initial_dhcp()
        scheduler()

    except KeyboardInterrupt:
        print("\n[STOPPED] Zone-based MTD stopped by user.")
        print("[INFO] Network and controller remain running.")
        sys.exit(0)
