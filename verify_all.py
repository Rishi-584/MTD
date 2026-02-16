import requests
import time
import json
import sys

BASE = "http://127.0.0.1:8000"

def test_system():
    print(">>> Starting System Verification...")
    
    # 1. Check Status (Is Controller Up?)
    try:
        r = requests.get(f"{BASE}/status", timeout=2)
        print("[PASS] Controller is ONLINE.")
    except Exception as e:
        print(f"[FAIL] Controller unreachable: {e}")
        sys.exit(1)

    # 2. Simulate DHCP Discovery (Host 1)
    print("\n>>> Simulating DHCP for h1...")
    payload = {'hostname': 'h1', 'mac': '00:00:00:00:00:01'}
    r = requests.post(f"{BASE}/sim/dhcp_discover", json=payload)
    if r.status_code == 200:
        data = r.json()
        print(f"[PASS] DHCP Bound: {data['hostname']} -> {data['ip']}")
    else:
        print(f"[FAIL] DHCP Failed: {r.text}")

    # 3. Simulate DHCP Discovery (Host 2)
    print("\n>>> Simulating DHCP for h2...")
    payload = {'hostname': 'h2', 'mac': '00:00:00:00:00:02'}
    r = requests.post(f"{BASE}/sim/dhcp_discover", json=payload)
    if r.status_code == 200:
        data = r.json()
        print(f"[PASS] DHCP Bound: {data['hostname']} -> {data['ip']}")
    else:
        print(f"[FAIL] DHCP Failed: {r.text}")

    # 4. Check Initial Status (History should be empty or have init events)
    r = requests.get(f"{BASE}/status")
    status = r.json()
    if 'history' in status:
         print(f"[PASS] History Field Present. Count: {len(status['history'])}")
    else:
         print("[FAIL] 'history' field MISSING in /status response!")

    # 5. Trigger Shuffle
    print("\n>>> Triggering MTD Shuffle for h1...")
    r = requests.post(f"{BASE}/shuffle", json={'hosts': ['h1'], 'policy': 'manual'})
    if r.status_code == 200:
         print("[PASS] Shuffle Triggered.")
    else:
         print(f"[FAIL] Shuffle Error: {r.text}")
    
    time.sleep(2) # Wait for thread

    # 6. Verify History Update
    print("\n>>> Verifying History Log...")
    r = requests.get(f"{BASE}/status")
    final_status = r.json()
    history = final_status.get('history', [])
    
    found = False
    for evt in history:
        if evt['host'] == 'h1' and evt.get('new_ip'):
            print(f"[PASS] Found History Event: {evt['time_str']} | {evt['host']} | {evt['old_ip']} -> {evt['new_ip']} | Zone: {evt['zone']}")
            found = True
            break
            
    if not found:
        print("[FAIL] MTD Event NOT found in history!")
        print("Full History:", json.dumps(history, indent=2))
    
    print("\n>>> Verification Complete.")

if __name__ == "__main__":
    test_system()
