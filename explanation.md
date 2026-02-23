# Moving Target Defense (MTD) Hospital Network Simulation - Project Explanation

## 1️⃣ Project Overview
This project implements a **Moving Target Defense (MTD)** strategy for a simulated hospital network. The primary goal is to **reduce the attack surface** and improve resilience against reconnaissance and persistent attacks (APTs).

In traditional static networks, IP addresses remain constant, allowing attackers ample time to scan, map, and launch targeted exploits. This project counters that by ensuring:
*   **Dynamic IP Rotation**: Public-facing IP addresses change frequently based on risk levels.
*   **Unpredictability**: Attackers cannot rely on static targets.
*   **Service Continuity**: Secure communication sessions (TLS/HTTPS) are maintained even while the underlying IP addresses change.

## 2️⃣ Network Architecture
The system is built using a Software-Defined Networking (SDN) approach:

*   **Hospital LAN (Mininet)**: A virtual network topology simulating hospital devices (Hosts `h1` to `h6`).
*   **OpenFlow Switches**: Manage packet forwarding dynamically based on rules from the controller.
*   **Ryu SDN Controller**: The "brain" of the network. It manages flow tables, handles ARP/DHCP, and enforces security policies.
*   **MTD Gateway**: Acts as the Network Address Translation (NAT) point and security enforcement boundary. All external communication flows through here.

## 3️⃣ Backend Components
The backend logic is implemented in Python, integrated with the Ryu controller.

### 🔹 MTD Controller
*   **Host Discovery**: Automatically detects devices connected to the network.
*   **DHCP Simulation**: Assigns static **Private IPs** (e.g., `10.0.0.x`) to internal hosts.
*   **DNS Management**: Maintains a mapping of Hostnames → Current Public IPs.

### 🔹 Risk-Based Zones
Hosts are classified into zones based on their criticality, determining their IP hopping frequency:
*   **High Risk (ICU, Servers)**: Hosts `h1, h2`. Hopping Interval: **40s**.
*   **Medium Risk (Staff Stations)**: Hosts `h3, h4`. Hopping Interval: **20s**.
*   **Low Risk (Guest WiFi, IoT)**: Hosts `h5, h6`. Hopping Interval: **10s**.

## 4️⃣ NAT & IP Hopping Mechanism
This is the core MTD engine:
1.  **Private Assignment**: Hosts connect with a private IP (e.g., `10.0.0.1`) which is never exposed.
2.  **Public Mapping**: The MTD Gateway assigns a temporary **Public IP** (e.g., `172.16.0.50`) from a virtual pool.
3.  **Flow Installation**: The controller installs OpenFlow rules in the switches to translate `Private IP ↔ Public IP` on the fly.
4.  **Rotation (Hopping)**:
    *   When the timer expires (or threat is detected), a **NEW** Public IP is selected.
    *   New flow rules are installed.
    *   **Grace Period**: Old rules act as a "shadow" for a few seconds to allow in-flight packets to finish, preventing dropped connections.

## 5️⃣ Secure Communication (HTTPS + TLS)
The system simulates a modern, secure encryption stack for all data transfers:
*   **Protocol**: HTTPS over TLS 1.3.
*   **Encryption**: **AES-256-GCM** is used for the payload. This provides confidentiality (attackers seeing the packet only see random bytes).
*   **Key Exchange**: **ECDHE** (Elliptic Curve Diffie-Hellman Ephemeral) is simulated to derive shared secrets.
*   **Integrity**: **SHA-384** ensures data hasn't been tampered with.

Crucially, the TLS session ID allows the connection to **resume** seamlessly even after the MTD controller changes the host's IP address mid-session.

## 6️⃣ Zone-Based Security Policy
Communication is restricted based on trust levels:
*   **High Zone**: Can talk to **Everyone** (needs access to all patient data).
*   **Medium Zone**: Can talk to **Medium & Low** (Staff usage).
*   **Low Zone**: Can ONLY talk to **Low** (Guest/IoT isolation).

Attempts to violate these rules (e.g., Guest trying to access ICU) are **blocked** instantly by the controller.

## 7️⃣ Host-to-Host Communication Flow
When a user sends data (e.g., `h1` sending to `h2`):
1.  **Policy Check**: Controller verifies if `Source Zone` is allowed to contact `Destination Zone`.
2.  **TLS Handshake**: A secure session is established. Keys are generated.
3.  **NAT Encapsulation**: Source Private IP is translated to its **Current Public IP**.
4.  **Traversal**: Packet moves through the switch fabric.
5.  **MTD Event (Optional)**: If an IP hop occurs during transfer, the NAT mapping updates, but the encrypted tunnel persists.
6.  **Delivery**: Destination receives the packet, decrypts it, and verifying the contents.

## 8️⃣ Backend Execution Trace
To make the "black box" of SDN transparent, the system generates real-time traces:
*   **POLICY**: Shows "Access Granted" or "BLOCKED".
*   **TLS**: Logs handshake steps (Client Hello, Key Exchange).
*   **CRYPTO**: Displays details of encryption (AES-256).
*   **NAT**: Shows the exact IP translation (`10.0.0.1 → 172.16.0.55`).
*   **MTD**: Highlights if an IP rotation happened during the transfer.

This trace is streamed via API to the frontend for visualization.

## 9️⃣ Web UI Visualization
The web dashboard provides a "God's Eye View" of the network:
*   **Operations Center**: A unified panel to run Ping tests and sends Secure Data.
*   **Packet Construction**: Visually compares **Cleartext** vs **Encrypted** hex dumps.
*   **Flow Diagram**: Animates the packet path from Source → Gateway → Dest.
*   **Live NAT Table**: Shows the current Active Public IP for every host.
*   **Hopping History**: A timeline log of every IP rotation event.

## 🔟 Why This Design Matters
This project is significant because it:
1.  **Demonstrates Feasibility**: Proves MTD can be implemented with standard technologies (SDN, Python) without breaking TCP/IP.
2.  **Enhances Security**: Adds a moving layer of defense that static firewalls cannot provide.
3.  **Educational Tool**: The visualization breaks down complex abstract concepts (NAT, Encryption, SDN flows) into understandable graphics.
