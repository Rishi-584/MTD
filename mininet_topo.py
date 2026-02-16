import requests
import time
import json
import argparse
from mininet.topo import Topo

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink

CONTROLLER_API = "http://127.0.0.1:8000"

class ZoneTopology(Topo):
    def build(self, hosts=4, switches=1, zone_split=(2,2)):
        # zone_split: tuple for high, low counts (simple default)
        s = self.addSwitch('s1', protocols='OpenFlow13')
        
        for i in range(1, hosts+1):
            # INITIAL STATE: No IP assigned (0.0.0.0)
            # This mimics a fresh boot where the host needs DHCP
            h = self.addHost(f'h{i}', ip='0.0.0.0/24')
            self.addLink(h, s)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--topo', type=int, default=6, help='number of hosts')
    args = parser.parse_args()
    
    topo = ZoneTopology(hosts=args.topo)
    net = Mininet(topo=topo, controller=RemoteController, switch=OVSSwitch, link=TCLink, autoSetMacs=True)
    net.start()
    
    print("Mininet started. Hosts initialized with 0.0.0.0.")
    print("Waiting for Controller...")
    import time
    time.sleep(2) # Allow connection to stabilize
    
    # ---------------------------------------------------------
    # SIMULATED DHCP HANDSHAKE
    # ---------------------------------------------------------
    print("\n>>> STARTING DHCP DISCOVERY PHASE <<<")
    for h in net.hosts:
        print(f"[*] Host {h.name} ({h.MAC()}) broadcasting DHCP Discover...")
        
        # 1. Host sends "Discover" (simulated via API call here for stability)
        # In a real scenario, 'dhclient' would run on 'h' and send a UDP packet.
        # Here, we ask the Controller (DHCP Server) what IP to use.
        try:
            payload = {'hostname': h.name, 'mac': h.MAC()}
            # Note: In a real SDN, the packet goes to Controller -> Controller Logic -> Reply
            # We skip the packet serialization for the *assignment* phase to ensure robustness in this prototype
            r = requests.post(f"{CONTROLLER_API}/sim/dhcp_discover", json=payload, timeout=2)
            
            if r.status_code == 200:
                data = r.json()
                assigned_ip = data.get('ip')
                # 2. Apply the assigned IP to the interface
                h.setIP(assigned_ip, prefixLen=24)
                print(f"    --> DHCP ACK: Assigned {assigned_ip}/24 to {h.name}")
                
                # 3. Add Default Route to Gateway (Managed by Controller)
                # This ensures hosts can talk to 172.16.x.x (Outside World)
                h.cmd('ip route add default via 10.0.0.254')
            else:
                print(f"    --> DHCP FAIL: Controller rejected request ({r.status_code})")
        
        except Exception as e:
            print(f"    --> DHCP ERROR: Could not talk to Controller ({e})")
            # Fallback for offline testing
            fallback_ip = f"10.0.0.{10+int(h.name[1:])}"
            print(f"    --> FALLBACK: Assigning {fallback_ip}")
            h.setIP(fallback_ip, prefixLen=24)

    print(">>> DHCP PHASE COMPLETE <<<\n")

    # ---------------------------------------------------------
    # TOPOLOGY AGENT (Real Command Execution)
    # ---------------------------------------------------------
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import threading

    class TopologyAgent(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path == '/exec':
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                try:
                    data = json.loads(body.decode())
                    host_name = data.get('host')
                    cmd = data.get('cmd')
                    
                    if not host_name or not cmd:
                        self.send_error(400, "Missing host or cmd")
                        return

                    host_obj = net.get(host_name)
                    if not host_obj:
                        self.send_error(404, "Host not found")
                        return
                    
                    print(f"[TopologyAgent] Executing on {host_name}: {cmd}")
                    # Run the command and get output
                    # time.sleep(0.1) # Small delay for stability
                    output = host_obj.cmd(cmd)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'output': output, 'status': 'success'}).encode())
                    
                except Exception as e:
                    self.send_error(500, str(e))
            else:
                self.send_error(404)

    def run_agent():
        server = HTTPServer(('0.0.0.0', 8888), TopologyAgent)
        print(f"[*] Topology Agent active on 0.0.0.0:8888")
        server.serve_forever()

    t_agent = threading.Thread(target=run_agent, daemon=True)
    t_agent.start()

    # ---------------------------------------------------------
    # AUTO-START HOST AGENTS (HTTP Servers)
    # ---------------------------------------------------------
    print("\n>>> STARTING HOST AGENTS (HTTP :8080) <<<")
    for h in net.hosts:
        # Start the agent in server mode in background
        # Log to /tmp to avoid cluttering console
        cmd = f"python3 scripts/host_agent.py --host {h.name} --server > /tmp/{h.name}_agent.log 2>&1 &"
        print(f"[*] {h.name}: Starting Host Agent...")
        h.cmd(cmd)

    print("\n✅ SIMULATION FULLY RUNNING")
    print("   - Controller API: http://127.0.0.1:8000")
    print("   - Topology Agent: http://127.0.0.1:8888")
    print("   - Host Agents:    Port 8080 (Background)")
    
    # ---------------------------------------------------------
    # WARM-UP: FORCE PACKET-IN FOR CONTROLLER LEARNING
    # ---------------------------------------------------------
    # Send a single ARP from every host to the Gateway.
    # This ensures the Controller learns the correct OFPort and installs NAT flows
    # BEFORE the user tries to run any tests.
    print(">>> WARMING UP ARP CACHE & FLOW TABLES <<<")
    for h in net.hosts:
        # 1. Disable ALL Checksum/Segmentation Offloading (Sledgehammer Fix)
        # Fixes "Ping works, Curl fails" caused by virtual NICs corrupting checksums.
        h.cmd('ethtool -K {} tx off rx off tso off gso off gro off lro off'.format(h.defaultIntf()))
        
        # 2. Arping for Gateway (10.0.0.254) - fires a PacketIn
        h.cmd('arping -c 1 -I {} -U 10.0.0.254 > /dev/null 2>&1 &'.format(h.defaultIntf()))
    time.sleep(2) # Give controller time to process
    
    print("   - Verify: 'pingall' or use Web UI Validator")
    
    # If running interactively, start CLI.
    # If running in background (no TTY), sleep forever to keep network alive.
    import sys
    if sys.stdin.isatty():
        CLI(net)
    else:
        print("[*] Running in headless mode. Keeping network alive...")
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
    net.stop()

if __name__ == '__main__':
    main()
