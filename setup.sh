#!/bin/bash
# Android Monitor Setup Script for Termux proot-distro Ubuntu

set -e

echo "=================================="
echo "Android Monitor Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}Error: This script must be run in Termux${NC}"
    exit 1
fi

# Check if in proot-distro Ubuntu
if ! command -v apt &> /dev/null; then
    echo -e "${RED}Error: This script must be run in proot-distro Ubuntu${NC}"
    echo "Run: proot-distro login ubuntu"
    exit 1
fi

echo -e "${GREEN}Detected Termux proot-distro Ubuntu environment${NC}"

# Update package list
echo -e "\n${YELLOW}Updating package list...${NC}"
apt update

# Install required system packages
echo -e "\n${YELLOW}Installing system dependencies...${NC}"
apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    git \
    curl \
    sqlite3 \
    htop

# Install Python packages
echo -e "\n${YELLOW}Installing Python packages...${NC}"
pip3 install --upgrade pip

# Core packages
pip3 install \
    psutil \
    requests \
    pyyaml \
    python-dateutil

# Data analysis packages
pip3 install \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    tabulate

# Create directories
echo -e "\n${YELLOW}Creating directory structure...${NC}"
MONITOR_HOME="/data/data/com.termux/files/home/android_monitor"
mkdir -p "$MONITOR_HOME"
mkdir -p "$MONITOR_HOME/logs"
mkdir -p "$MONITOR_HOME/exports"
mkdir -p "$MONITOR_HOME/configs"

# Download monitor scripts
echo -e "\n${YELLOW}Installing monitor scripts...${NC}"

# Create script directory
SCRIPT_DIR="/data/data/com.termux/files/home/android_monitor/bin"
mkdir -p "$SCRIPT_DIR"

# Copy the main scripts (in real deployment, these would be downloaded)
cat > "$SCRIPT_DIR/android-monitor.py" << 'EOF'
# Main monitor script would be inserted here
# For now, create a placeholder
#!/usr/bin/env python3
print("Main monitor script - replace with actual content")
EOF

cat > "$SCRIPT_DIR/android-query.py" << 'EOF'
# Query tool script would be inserted here
#!/usr/bin/env python3
print("Query tool script - replace with actual content")
EOF

cat > "$SCRIPT_DIR/android-dashboard.py" << 'EOF'
# Dashboard script would be inserted here
#!/usr/bin/env python3
print("Dashboard script - replace with actual content")
EOF

# Make scripts executable
chmod +x "$SCRIPT_DIR"/*.py

# Create default configuration
echo -e "\n${YELLOW}Creating default configuration...${NC}"
cat > "$MONITOR_HOME/configs/default.yaml" << 'EOF'
# Android Monitor Configuration
# Default configuration with all modules enabled

# General settings
output_dir: /data/data/com.termux/files/home/android_monitor
db_path: monitor_data.db
log_level: INFO

# Module toggles
enable_logcat: true
enable_network: true
enable_process: true
enable_memory: true
enable_battery: true
enable_filesystem: true
enable_sensors: true
enable_apps: true

# Logcat settings
logcat_buffer_size: 1000
logcat_filters: []
logcat_priority: V  # V=Verbose, D=Debug, I=Info, W=Warning, E=Error

# Network settings
network_interval: 5
network_capture_packets: false
network_interfaces: []  # Empty = all interfaces

# Process settings
process_interval: 10
process_top_n: 20
process_track_threads: true

# Memory settings
memory_interval: 30
memory_detailed: true

# Battery settings
battery_interval: 60
battery_track_apps: true

# Filesystem settings
fs_watch_paths:
  - /data/data/com.termux/files/home
  - /sdcard/Download
  - /sdcard/DCIM
fs_interval: 5
fs_recursive: true

# Alert thresholds
alert_cpu_threshold: 80.0
alert_memory_threshold: 85.0
alert_battery_threshold: 20.0
alert_network_threshold: 100.0  # MB/s
EOF

# Create minimal configuration
cat > "$MONITOR_HOME/configs/minimal.yaml" << 'EOF'
# Minimal configuration for low resource usage
output_dir: /data/data/com.termux/files/home/android_monitor
db_path: monitor_data.db
log_level: WARNING

enable_logcat: false
enable_network: true
enable_process: true
enable_memory: true
enable_battery: true
enable_filesystem: false
enable_sensors: false
enable_apps: false

network_interval: 30
process_interval: 30
process_top_n: 10
memory_interval: 60
battery_interval: 120
EOF

# Create performance monitoring configuration
cat > "$MONITOR_HOME/configs/performance.yaml" << 'EOF'
# Configuration focused on performance monitoring
output_dir: /data/data/com.termux/files/home/android_monitor
db_path: monitor_data.db
log_level: INFO

enable_logcat: false
enable_network: true
enable_process: true
enable_memory: true
enable_battery: false
enable_filesystem: false
enable_sensors: false
enable_apps: true

process_interval: 5
process_top_n: 50
process_track_threads: true
memory_interval: 10
memory_detailed: true
network_interval: 5
alert_cpu_threshold: 70.0
alert_memory_threshold: 80.0
EOF

# Create security monitoring configuration
cat > "$MONITOR_HOME/configs/security.yaml" << 'EOF'
# Configuration focused on security monitoring
output_dir: /data/data/com.termux/files/home/android_monitor
db_path: monitor_data.db
log_level: DEBUG

enable_logcat: true
enable_network: true
enable_process: true
enable_memory: false
enable_battery: false
enable_filesystem: true
enable_sensors: false
enable_apps: true

logcat_filters:
  - "AuthService:*"
  - "PackageManager:*"
  - "ActivityManager:*"
  - "SecurityLog:*"

network_capture_packets: true
fs_recursive: true
fs_watch_paths:
  - /data/data/com.termux/files/home
  - /sdcard
EOF

# Create convenience scripts
echo -e "\n${YELLOW}Creating convenience scripts...${NC}"

# Start script
cat > "$MONITOR_HOME/start-monitor.sh" << 'EOF'
#!/bin/bash
# Start Android Monitor

SCRIPT_DIR="/data/data/com.termux/files/home/android_monitor/bin"
CONFIG_FILE="${1:-/data/data/com.termux/files/home/android_monitor/configs/default.yaml}"

echo "Starting Android Monitor with config: $CONFIG_FILE"
python3 "$SCRIPT_DIR/android-monitor.py" -c "$CONFIG_FILE"
EOF
chmod +x "$MONITOR_HOME/start-monitor.sh"

# Dashboard script
cat > "$MONITOR_HOME/start-dashboard.sh" << 'EOF'
#!/bin/bash
# Start Android Monitor Dashboard

SCRIPT_DIR="/data/data/com.termux/files/home/android_monitor/bin"
DB_PATH="${1:-/data/data/com.termux/files/home/android_monitor/monitor_data.db}"

if [ ! -f "$DB_PATH" ]; then
    echo "Database not found. Start monitor first or use live mode:"
    echo "  python3 $SCRIPT_DIR/android-dashboard.py --live"
    exit 1
fi

python3 "$SCRIPT_DIR/android-dashboard.py" -d "$DB_PATH"
EOF
chmod +x "$MONITOR_HOME/start-dashboard.sh"

# Query script
cat > "$MONITOR_HOME/query-data.sh" << 'EOF'
#!/bin/bash
# Query Android Monitor Data

SCRIPT_DIR="/data/data/com.termux/files/home/android_monitor/bin"
DB_PATH="/data/data/com.termux/files/home/android_monitor/monitor_data.db"

if [ ! -f "$DB_PATH" ]; then
    echo "Database not found. Start monitor first."
    exit 1
fi

python3 "$SCRIPT_DIR/android-query.py" "$DB_PATH" "$@"
EOF
chmod +x "$MONITOR_HOME/query-data.sh"

# Create systemd-style service script (for persistent monitoring)
cat > "$MONITOR_HOME/monitor-service.sh" << 'EOF'
#!/bin/bash
# Android Monitor Service Script

MONITOR_HOME="/data/data/com.termux/files/home/android_monitor"
PIDFILE="$MONITOR_HOME/monitor.pid"
LOGFILE="$MONITOR_HOME/logs/monitor-service.log"

start() {
    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Monitor already running (PID: $PID)"
            return 1
        fi
    fi
    
    echo "Starting Android Monitor..."
    nohup "$MONITOR_HOME/start-monitor.sh" >> "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    echo "Monitor started (PID: $(cat $PIDFILE))"
}

stop() {
    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")
        echo "Stopping Android Monitor (PID: $PID)..."
        kill "$PID" 2>/dev/null
        rm -f "$PIDFILE"
        echo "Monitor stopped"
    else
        echo "Monitor not running"
    fi
}

status() {
    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Monitor running (PID: $PID)"
        else
            echo "Monitor not running (stale PID file)"
        fi
    else
        echo "Monitor not running"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
EOF
chmod +x "$MONITOR_HOME/monitor-service.sh"

# Create cleanup script
cat > "$MONITOR_HOME/cleanup.sh" << 'EOF'
#!/bin/bash
# Cleanup old monitoring data

MONITOR_HOME="/data/data/com.termux/files/home/android_monitor"
DB_PATH="$MONITOR_HOME/monitor_data.db"
DAYS_TO_KEEP=${1:-7}

echo "Cleaning up data older than $DAYS_TO_KEEP days..."

if [ -f "$DB_PATH" ]; then
    # Calculate timestamp
    CUTOFF_TIMESTAMP=$(date -d "$DAYS_TO_KEEP days ago" +%s)
    
    # Clean each table
    sqlite3 "$DB_PATH" << SQL
DELETE FROM logcat_entries WHERE timestamp < $CUTOFF_TIMESTAMP;
DELETE FROM network_stats WHERE timestamp < $CUTOFF_TIMESTAMP;
DELETE FROM process_stats WHERE timestamp < $CUTOFF_TIMESTAMP;
DELETE FROM memory_stats WHERE timestamp < $CUTOFF_TIMESTAMP;
DELETE FROM battery_stats WHERE timestamp < $CUTOFF_TIMESTAMP;
DELETE FROM filesystem_events WHERE timestamp < $CUTOFF_TIMESTAMP;
DELETE FROM app_events WHERE timestamp < $CUTOFF_TIMESTAMP;
DELETE FROM alerts WHERE timestamp < $CUTOFF_TIMESTAMP;
VACUUM;
SQL
    
    echo "Cleanup complete"
else
    echo "Database not found"
fi

# Clean old logs
find "$MONITOR_HOME/logs" -name "*.log" -mtime +$DAYS_TO_KEEP -delete
echo "Old logs cleaned"
EOF
chmod +x "$MONITOR_HOME/cleanup.sh"

# Create cron job example
cat > "$MONITOR_HOME/crontab.example" << 'EOF'
# Example crontab entries for Android Monitor
# Add these to your crontab with: crontab -e

# Start monitor on boot
@reboot /data/data/com.termux/files/home/android_monitor/monitor-service.sh start

# Cleanup old data daily at 3 AM
0 3 * * * /data/data/com.termux/files/home/android_monitor/cleanup.sh 7

# Generate daily report at 8 AM
0 8 * * * /data/data/com.termux/files/home/android_monitor/query-data.sh --export html --output /sdcard/android-monitor-report-$(date +\%Y\%m\%d).html
EOF

# Set up Termux permissions
echo -e "\n${YELLOW}Setting up Termux permissions...${NC}"

# Create Termux boot script
TERMUX_BOOT_DIR="/data/data/com.termux/files/home/.termux/boot"
mkdir -p "$TERMUX_BOOT_DIR"

cat > "$TERMUX_BOOT_DIR/start-android-monitor.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# Auto-start Android Monitor on boot

# Wait for system to settle
sleep 30

# Start proot-distro Ubuntu and run monitor
proot-distro login ubuntu -- /data/data/com.termux/files/home/android_monitor/monitor-service.sh start
EOF
chmod +x "$TERMUX_BOOT_DIR/start-android-monitor.sh"

# Create aliases
echo -e "\n${YELLOW}Creating aliases...${NC}"
cat >> ~/.bashrc << 'EOF'

# Android Monitor aliases
alias am-start='/data/data/com.termux/files/home/android_monitor/start-monitor.sh'
alias am-stop='/data/data/com.termux/files/home/android_monitor/monitor-service.sh stop'
alias am-status='/data/data/com.termux/files/home/android_monitor/monitor-service.sh status'
alias am-dash='/data/data/com.termux/files/home/android_monitor/start-dashboard.sh'
alias am-query='/data/data/com.termux/files/home/android_monitor/query-data.sh'
alias am-live='python3 /data/data/com.termux/files/home/android_monitor/bin/android-dashboard.py --live'
EOF

# Test installation
echo -e "\n${YELLOW}Testing installation...${NC}"

# Test Python imports
python3 -c "
import psutil
import pandas
import matplotlib
import yaml
print('All Python packages imported successfully')
" && echo -e "${GREEN}✓ Python packages OK${NC}" || echo -e "${RED}✗ Python packages FAILED${NC}"

# Test directory structure
[ -d "$MONITOR_HOME" ] && echo -e "${GREEN}✓ Directory structure OK${NC}" || echo -e "${RED}✗ Directory structure FAILED${NC}"

# Test script permissions
[ -x "$MONITOR_HOME/start-monitor.sh" ] && echo -e "${GREEN}✓ Scripts executable OK${NC}" || echo -e "${RED}✗ Scripts not executable${NC}"

# Final instructions
echo -e "\n${GREEN}=================================="
echo "Installation Complete!"
echo "==================================${NC}"
echo
echo "Quick Start Guide:"
echo "1. Start monitoring:    am-start"
echo "2. View dashboard:      am-dash"
echo "3. Query data:          am-query -i"
echo "4. Live monitoring:     am-live"
echo "5. Stop monitoring:     am-stop"
echo
echo "Configuration files in: $MONITOR_HOME/configs/"
echo "Logs will be in:       $MONITOR_HOME/logs/"
echo "Database will be in:   $MONITOR_HOME/monitor_data.db"
echo
echo -e "${YELLOW}Note: Replace the placeholder scripts in $SCRIPT_DIR with the actual monitoring scripts${NC}"
echo
echo "For auto-start on boot, install Termux:Boot app and run:"
echo "  termux-wake-lock"
echo
echo "To reload aliases, run: source ~/.bashrc"
