# Web UI for Host Agent Logs

## Overview

The MTD system now includes a beautiful web UI to view host agent logs in real-time. This makes it easy to monitor packet transfers, acknowledgments, and any errors without using the command line.

## Features

✅ **Real-time Log Viewing** - View logs from any host (h1-h6)
✅ **Auto-Refresh Mode** - Automatically update every 2 seconds
✅ **Syntax Highlighting** - Color-coded log levels and patterns
✅ **Adjustable Lines** - View 50-1000 lines at once
✅ **Live Stats** - Total lines, log file location, last update time
✅ **Auto-Scroll** - Automatically scrolls to newest logs
✅ **Beautiful Dark UI** - Easy on the eyes with gradient design

## How to Access

### From Dashboard
1. Start the controller: `sudo docker run --rm -it --network host mtd-controller`
2. Open your browser: http://127.0.0.1:8000/
3. Click the **"📋 Host Logs"** button in the header

### Direct Access
Simply navigate to: http://127.0.0.1:8000/logs.html

## Using the Log Viewer

### Controls

**Host Selector**
- Choose which host's logs to view (h1-h6)
- Each option shows the zone: h1 (High), h5 (Low), etc.
- Automatically refreshes when you change hosts

**Lines Selector**
- Choose how many recent lines to display
- Options: 50, 100, 200, 500, 1000
- Higher values show more history but may be slower

**Refresh Button** (🔄)
- Manually refresh the logs
- Use this to get the latest logs on demand

**Auto-Refresh Button** (⏱️)
- Toggle automatic refresh every 2 seconds
- Button shows green when active
- Click again to disable

**Clear Button** (🗑️)
- Shows command to clear log file
- Currently requires manual deletion via terminal

**Back to Dashboard** (←)
- Returns to the main MTD dashboard

### Status Indicator

The colored dot next to "Host Agent Logs" shows connection status:
- 🟢 **Green** - Successfully fetching logs
- 🔴 **Red** - Error fetching logs or log file not found

### Statistics Cards

**Total Lines**
- Total number of lines in the log file
- Shows complete history since host agent started

**Displayed**
- Number of lines currently shown
- Will be less than total if you selected fewer lines

**Log File**
- Full path to the log file being monitored
- Example: `/tmp/h5_agent.log`

**Last Update**
- Timestamp of the last successful refresh
- Updates every time logs are fetched

## Log Syntax Highlighting

The viewer automatically highlights different log patterns:

### Log Levels
- **ERROR** - Red color, bold
- **SUCCESS** - Green color, bold
- **WARN** - Orange color, bold
- **INFO** - Blue color

### Special Elements
- **Timestamps** `[12:34:56]` - Purple color
- **Hostnames** `[h5]` - Green color, bold
- **Emojis** - Larger size for visibility
  - 📥 Packet received
  - 📤 Packet sent
  - ✅ Success/ACK
  - ❌ Error/failure
  - 🔍 DNS resolution
  - ⚠️ Warning

### Example Log Rendering

**Raw log:**
```
[12:34:56] [h5] SUCCESS: 📥 PACKET RECEIVED
```

**Displayed as:**
- Purple timestamp: `[12:34:56]`
- Green host: `[h5]`
- Green level: `SUCCESS:`
- Emoji: 📥
- White message: `PACKET RECEIVED`

## Typical Use Cases

### 1. Monitor Packet Transfers

**Scenario:** Watch packets being sent between hosts

**Steps:**
1. Select sender host (e.g., h1)
2. Enable Auto-Refresh
3. Send packets: `curl -X POST http://127.0.0.1:8000/sim/secure_transfer -d '{"src":"h1","dst":"h2","payload":"test"}'`
4. Watch logs update in real-time
5. Switch to receiver (h2) to see acknowledgments

**What You'll See:**
```
[12:34:56] [h1] INFO: 📤 SENDING PACKET
[12:34:56] [h1] INFO:    To: h2 (172.16.0.198:8080)
[12:34:56] [h1] SUCCESS: ✅ ACKNOWLEDGMENT RECEIVED
[12:34:56] [h1] SUCCESS:    Status: ACK
```

### 2. Debug Connection Failures

**Scenario:** Packet transfer failing, need to see why

**Steps:**
1. Select the source host having issues
2. Set lines to 200+ to see more history
3. Click Refresh to get latest logs
4. Look for ERROR or WARN messages
5. Switch to destination host to see if it received anything

**Common Error Patterns:**
```
[12:34:56] [h1] ERROR: ❌ Connection refused to 172.16.0.198:8080
[12:34:56] [h1] ERROR: ⏱️ Timeout connecting to 172.16.0.198:8080
[12:34:56] [h1] ERROR: DNS resolution failed for h2
```

### 3. Verify Host Agent Status

**Scenario:** Check if host agents are running

**Steps:**
1. Select a host
2. Click Refresh
3. Check if logs exist

**Status Indicators:**
- ✅ Logs present → Agent is running
- ❌ "Log file not found" → Agent not started
- 📭 "No logs available" → Agent running but no activity

### 4. Watch MTD IP Rotation Impact

**Scenario:** See how IP changes affect transfers

**Steps:**
1. Select h1, enable Auto-Refresh
2. Start continuous transfers: `mininet> h1 python3 scripts/host_agent.py --host h1 --client --target h2 --count 20`
3. Open second browser tab with h2 logs
4. Trigger shuffle: `curl -X POST http://127.0.0.1:8000/shuffle -d '{"hosts":["h1","h2"]}'`
5. Watch both tabs - transfers should continue despite IP changes

**Expected Log Pattern:**
```
[12:34:00] [h1] INFO: 🔍 Resolving h2...
[12:34:00] [h1] INFO: ✓ Resolved h2 -> 172.16.0.198
[12:34:01] [h1] SUCCESS: ✅ ACKNOWLEDGMENT RECEIVED
...IP rotates...
[12:34:10] [h1] INFO: 🔍 Resolving h2...
[12:34:10] [h1] INFO: ✓ Resolved h2 -> 172.16.0.245  ← New IP!
[12:34:11] [h1] SUCCESS: ✅ ACKNOWLEDGMENT RECEIVED  ← Still works!
```

## Troubleshooting

### "Log file not found"

**Cause:** Host agent not started on that host

**Fix:**
```bash
# In Mininet CLI:
mininet> h5 python3 scripts/host_agent.py --host h5 --server > /tmp/h5_agent.log 2>&1 &

# Or start all agents:
mininet> sh for i in {1..6}; do h$i python3 scripts/host_agent.py --host h$i --server > /tmp/h${i}_agent.log 2>&1 & done
```

### No new logs appearing

**Cause:** No activity or agent crashed

**Check:**
```bash
# Verify agent is running:
mininet> h5 ps aux | grep host_agent

# Test with manual packet:
curl -X POST http://127.0.0.1:8000/sim/secure_transfer \
  -d '{"src":"h1","dst":"h5","payload":"test"}'
```

### Logs not updating with Auto-Refresh

**Cause:** Browser cache or connection issue

**Fix:**
- Click Refresh manually
- Check status indicator (should be green)
- Open browser console (F12) to check for errors
- Restart browser

### Old logs still showing

**Cause:** Log file contains old entries

**Clear logs:**
```bash
# Stop agent first:
mininet> h5 killall python3

# Remove log file:
sudo rm /tmp/h5_agent.log

# Restart agent:
mininet> h5 python3 scripts/host_agent.py --host h5 --server > /tmp/h5_agent.log 2>&1 &
```

## API Endpoint

The logs are fetched via REST API:

**Endpoint:** `GET /host_logs?host={host}&lines={lines}`

**Parameters:**
- `host` - Hostname (h1-h6)
- `lines` - Number of recent lines to return (default: 100)

**Response:**
```json
{
  "host": "h5",
  "lines": ["[12:34:56] [h5] INFO: Server started", "..."],
  "total_lines": 523,
  "log_file": "/tmp/h5_agent.log"
}
```

**Error Response:**
```json
{
  "error": "log_file_not_found",
  "host": "h5",
  "log_file": "/tmp/h5_agent.log"
}
```

### Example API Usage

```bash
# Get last 50 lines from h5:
curl "http://127.0.0.1:8000/host_logs?host=h5&lines=50" | jq

# Get all logs from h2:
curl "http://127.0.0.1:8000/host_logs?host=h2&lines=10000" | jq

# Check if agent is running:
curl "http://127.0.0.1:8000/host_logs?host=h5&lines=1" | jq '.error'
```

## Advanced Features

### Multiple Tabs

Open multiple browser tabs to watch different hosts simultaneously:
- Tab 1: http://127.0.0.1:8000/logs.html?host=h1
- Tab 2: http://127.0.0.1:8000/logs.html?host=h2
- Tab 3: http://127.0.0.1:8000/logs.html?host=h5

### URL Parameters (Future Enhancement)

The logs page will support URL parameters:
- `?host=h5` - Pre-select host
- `&lines=500` - Pre-select line count
- `&auto=true` - Start with auto-refresh enabled

Example: `http://127.0.0.1:8000/logs.html?host=h5&lines=200&auto=true`

### Keyboard Shortcuts (Planned)

- `R` - Refresh logs
- `A` - Toggle auto-refresh
- `1-6` - Switch to host h1-h6
- `↑/↓` - Scroll logs
- `Home/End` - Jump to top/bottom

## Tips & Best Practices

1. **Use Auto-Refresh for Active Testing**
   - Turn on during packet transfer tests
   - Disable when reading historical logs

2. **Increase Line Count for Debugging**
   - Use 500-1000 lines to see full error context
   - Use 50-100 for quick status checks

3. **Watch Both Sender and Receiver**
   - Open two browser tabs
   - Tab 1: Sender host
   - Tab 2: Receiver host
   - See complete packet flow

4. **Check Timestamps**
   - Logs show HH:MM:SS format
   - Useful for correlating events
   - Compare with controller logs

5. **Monitor During MTD Rotation**
   - Enable auto-refresh on sender
   - Watch DNS resolution messages
   - Verify new IPs after rotation
   - Confirm transfers still work

## Summary

The web-based log viewer provides:
- ✅ Real-time monitoring without command line
- ✅ Beautiful, easy-to-read interface
- ✅ Auto-refresh for live updates
- ✅ Syntax highlighting for quick scanning
- ✅ Multiple host monitoring
- ✅ Historical log viewing

Access it at: **http://127.0.0.1:8000/logs.html**

Perfect for demonstrations, debugging, and understanding packet flow!
