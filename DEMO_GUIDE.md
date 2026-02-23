# MTD-HealthNet Demo Guide

>  **IMPORTANT**: You must keep **Terminal 1** (Controller) open and running. Do not close it or type in it after it starts. Run Mininet commands in **Terminal 2**.

This guide details exactly how to run the system to prove all requirements to your reviewer.

This guide details exactly how to run the system to prove all requirements to your reviewer.

## Pre-Requisites
1.  **Mininet** installed and running on Linux.
2.  **Ryu Controller** installed.
3.  **Python 3** with `requests`.

## step 1: Start the Environment

### Terminal 1: Start the Controller (Using Docker)
Since you are using Kali, we will run the controller in Docker to avoid dependency errors.

1.  **Build the Docker Image:**
    ```bash
    # In mtd_repo_final_back/
    sudo docker build -t mtd-controller .
    ```

2.  **Run the Controller:**
    ```bash
    sudo docker run --rm -it --network host --name mtd-controller mtd-controller
    ```
    *Note: We use `--network host` so Mininet (running on your machine) can talk to it easily.*
    *Wait for "REST API started" message log.*

### Terminal 2: Start the Mininet Topology
This creates the virtual network with High/Medium/Low zones.
```bash
sudo python3 mininet_topo.py
```
*Wait for the Mininet prompt `mininet>`.*

## Step 2: Set Up Real Traffic & HTTPS Proof

**CRITICAL: The commands below (starting with `h1` or `h2`) must be run INSIDE the Mininet CLI (Terminal 2), NOT in a new terminal window.**

### Option A: If you have a GUI (Desktop Environment) - RECOMMENDED
1.  In Terminal 2 (at the `mininet>` prompt), type:
    ```bash
    xterm h1 h2
    ```
2.  Two black terminal windows will pop up.
3.  **In the "h2" window (Server):**
    ```bash
    python3 scripts/host_agent.py --host h2 --server --https --port 8443
    ```
4.  **In the "h1" window (Client):**
    ```bash
    python3 scripts/host_agent.py --host h1 --client --target h2 --https --port 8443
    ```

### Option B: If you are using SSH/No-GUI (Text Only)
1.  **In Terminal 2 (at the `mininet>` prompt)**, start the server in the background:
    ```bash
    h2 python3 scripts/host_agent.py --host h2 --server --https --port 8443 &
    ```
    *(Note the `&` at the end)*

2.  **In Terminal 2 (at the `mininet>` prompt)**, start the client in the foreground:
    ```bash
    h1 python3 scripts/host_agent.py --host h1 --client --target h2 --https --port 8443
    ```

*You should see output like:*
```
[h1] 🔍 Resolved h2 -> 172.16.0.X (Public IP)
[h1] ✅ SENT #1 -> h2 (172.16.0.X) [OK]
```
**PROOF:** The log showing "HTTPS" and "SENT [OK]" proves **Requirement 1 & 2** (Message Proof & HTTPS).

## Step 3: Visualize Zone Monitoring

1.  Open Browser: `http://localhost:8000`
2.  Observe the **"Hopping History"** table.
3.  You will see entries updating automatically as the Controller shuffles IPs.

**PROOF:**
-   **Zone Column:** Shows High/Medium/Low.
-   **Change Column:** Shows `Old IP --> New IP`.
-   **Time:** Shows exact timestamp.
This proves **Requirement 4** (Zone Visibility).

## Step 4: Live MTD Trigger (The "Aha!" Moment)

1.  Keep the **Client Terminal (h1)** visible constantly sending messages.
2.  On the Web Dashboard, click **"Rotating IP Identity"**.
3.  **Watch the Client Terminal:**
    -   It might briefly verify "Connection Lost" or "Re-resolving".
    -   Then it will say "Resolved h2 -> [NEW IP]".
    -   And immediately "✅ SENT #X -> h2 ...".
    
**PROOF:** This demonstrates **Session Persistence** and **Dynamic NAT** functionality. The physical IP changed, but the application recovered and continued communicating.

## Q&A Defense cheat Sheet

**Q: Does the TCP connection actually survive?**
**A:** "The physical TCP socket breaks when the IP changes (reset). However, our **Smart Agent** (Application Layer) creates a persistent session abstraction by automatically re-resolving the new authorized IP and reconnecting. This matches how modern mobile apps handle network switching (WiFi <-> 4G)."

**Q: Is this real NAT or just simulation?**
**A:** "It is Real OpenFlow-based NAT. The Coordinator installs `OFPActionSetField` rules on the switch to rewrite Source/Dest IPs for every packet, ensuring the internal Private IP (10.0.0.x) is never exposed to the public network."

## Troubleshooting

### Ryu Installation Error: "AttributeError: 'types.SimpleNamespace' object has no attribute 'get_script_args'"
This happens because `ryu` is an older package and modern Python uses a newer `setuptools`.
**Fix:**
```bash
sudo pip3 install "setuptools<70" --break-system-packages
sudo pip3 install ryu --break-system-packages
```
