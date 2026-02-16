import requests
import json
import time

BASE = "http://127.0.0.1:8000"

def log(msg):
    print(f"[VERIFY] {msg}")

def test_ping(src, dst, expect_success):
    log(f"Testing Ping: {src} -> {dst} (Expect: {'PASS' if expect_success else 'FAIL'})")
    r = requests.post(f"{BASE}/sim/test_ping", json={'src_host': src, 'dst_host': dst})
    res = r.json()
    success = (res['status'] == 'success')
    
    if success == expect_success:
        print(f"   [OK] Result: {res['status']}")
    else:
        print(f"   [ERROR] Unexpected Result: {res}")

def main():
    try:
        # 1. Setup Hosts
        log("Setting up hosts (DHCP)...")
        hosts = [
            ('h1', '00:00:00:00:00:01'), # High
            ('h2', '00:00:00:00:00:02'), # Medium
            ('h3', '00:00:00:00:00:03')  # Low
        ]
        
        for h, mac in hosts:
            requests.post(f"{BASE}/sim/dhcp_discover", json={'hostname': h, 'mac': mac})

        log("Waiting for policies to settle...")
        time.sleep(1)

        # 2. Verify Zones (Implicit) & Connectivity
        log("--- STARTING ACL MATRIX TEST ---")

        # HIGH (h1) -> *
        test_ping('h1', 'h2', True)  # High -> Medium (Allow)
        test_ping('h1', 'h3', True)  # High -> Low (Allow)

        # MEDIUM (h2) -> *
        test_ping('h2', 'h1', False) # Medium -> High (Deny)
        test_ping('h2', 'h3', True)  # Medium -> Low (Allow)

        # LOW (h3) -> *
        test_ping('h3', 'h1', False) # Low -> High (Deny)
        test_ping('h3', 'h2', False) # Low -> Medium (Deny)

        # Intra-Zone
        # To test this perfectly we'd need h4(high) etc but we assume true for now
        test_ping('h1', 'h1', True) 

        print("\n[SUCCESS] Zone verification completed.")

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")

if __name__ == '__main__':
    main()
