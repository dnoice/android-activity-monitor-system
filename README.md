# Android Activity Monitor for Termux

A comprehensive, modular monitoring solution for Android devices running in Termux proot-distro Ubuntu environment. This system provides real-time monitoring, data collection, analysis, and visualization of Android device activity.

## Features

### Core Monitoring Modules

1. **Logcat Monitor** - System log monitoring with filtering and alerting
2. **Network Monitor** - Interface statistics, connection tracking, bandwidth monitoring
3. **Process Monitor** - CPU/memory usage, top processes, thread tracking
4. **Memory Monitor** - System memory usage, pressure detection, detailed statistics
5. **Battery Monitor** - Battery level, temperature, charging status, drain analysis
6. **Filesystem Monitor** - File system changes, access patterns, storage usage
7. **App Monitor** - Application lifecycle events, crashes, ANRs
8. **Sensor Monitor** - Device sensor data collection (optional)

### Analysis & Visualization

- **Real-time Dashboard** - Terminal-based live monitoring interface
- **Query Tool** - Interactive data exploration and analysis
- **Data Export** - CSV, JSON, and HTML report generation
- **Correlation Analysis** - Cross-module event correlation
- **Alert System** - Configurable thresholds and notifications

## System Requirements

- Android device with Termux installed
- Termux proot-distro with Ubuntu
- Python 3.8+
- Root access (optional, for enhanced monitoring)
- Minimum 500MB free storage for data collection

## Installation

1. **Install Termux and proot-distro Ubuntu:**
```bash
# In Termux
pkg update && pkg upgrade
pkg install proot-distro
proot-distro install ubuntu
```

2. **Enter Ubuntu environment:**
```bash
proot-distro login ubuntu
```

3. **Run the setup script:**
```bash
# Download and run setup
curl -O https://your-repo/setup.sh
chmod +x setup.sh
./setup.sh
```

4. **Copy the monitoring scripts to the bin directory:**
```bash
# Copy the three main Python scripts
cp android-monitor.py /data/data/com.termux/files/home/android_monitor/bin/
cp android-query.py /data/data/com.termux/files/home/android_monitor/bin/
cp android-dashboard.py /data/data/com.termux/files/home/android_monitor/bin/
```

## Quick Start

### Basic Monitoring

```bash
# Start with default configuration
am-start

# Start with specific configuration
am-start /path/to/config.yaml

# View real-time dashboard
am-dash

# Stop monitoring
am-stop
```

### Live Monitoring (No Database)

```bash
# Quick system overview without data storage
am-live
```

### Data Analysis

```bash
# Interactive query mode
am-query -i

# Generate HTML report
am-query --export html --output report.html

# Query specific data
am-query --query network --start-time "2025-01-01 00:00:00"
```

## Configuration

Configuration files are stored in `/data/data/com.termux/files/home/android_monitor/configs/`

### Available Presets

1. **default.yaml** - All modules enabled, balanced settings
2. **minimal.yaml** - Low resource usage, essential monitoring only
3. **performance.yaml** - Focus on CPU/memory/process monitoring
4. **security.yaml** - Enhanced logging, file system monitoring, app tracking

### Key Configuration Parameters

```yaml
# General Settings
output_dir: /data/data/com.termux/files/home/android_monitor
db_path: monitor_data.db
log_level: INFO  # DEBUG, INFO, WARNING, ERROR

# Module Toggles
enable_logcat: true
enable_network: true
enable_process: true
enable_memory: true
enable_battery: true
enable_filesystem: true
enable_apps: true

# Monitoring Intervals (seconds)
network_interval: 5
process_interval: 10
memory_interval: 30
battery_interval: 60
fs_interval: 5

# Alert Thresholds
alert_cpu_threshold: 80.0      # Percentage
alert_memory_threshold: 85.0   # Percentage
alert_battery_threshold: 20.0  # Percentage
alert_network_threshold: 100.0 # MB/s
```

## Usage Examples

### 1. Monitor High CPU Usage

```bash
# Start monitoring with performance preset
am-start configs/performance.yaml

# Query processes using >50% CPU
am-query
> Select option: 3 (Query process stats)
> Min CPU: 50
```

### 2. Track Network Usage

```bash
# View network dashboard
am-dash
# Press '3' for network view

# Analyze network usage for specific time period
python3 android-query.py -a network --start-time "2025-01-28 00:00:00"
```

### 3. Battery Drain Analysis

```bash
# Query battery drain patterns
am-query
> Select option: 12 (Analyze battery drain)
```

### 4. Security Monitoring

```bash
# Start with security configuration
am-start configs/security.yaml

# Check for suspicious file system activity
am-query
> Select option: 6 (Query filesystem events)
> Event type: created
```

### 5. Generate Daily Reports

```bash
# Add to crontab for daily reports
0 8 * * * /data/data/com.termux/files/home/android_monitor/query-data.sh \
  --export html --output /sdcard/report-$(date +\%Y\%m\%d).html
```

## Dashboard Navigation

The real-time dashboard provides multiple views:

- **[1] Overview** - System summary, alerts, top processes
- **[2] Processes** - Detailed process list with resource usage
- **[3] Network** - Network activity graphs and interface stats
- **[4] Logs** - Recent warning/error logs
- **[5] Alerts** - System alerts and threshold violations
- **[q] Quit** - Exit dashboard

## Data Management

### Database Location
- Default: `/data/data/com.termux/files/home/android_monitor/monitor_data.db`
- SQLite format for easy querying and backup

### Data Retention
```bash
# Clean data older than 7 days
/data/data/com.termux/files/home/android_monitor/cleanup.sh 7

# Set up automatic cleanup (crontab)
0 3 * * * /data/data/com.termux/files/home/android_monitor/cleanup.sh 7
```

### Backup
```bash
# Backup database
cp monitor_data.db monitor_data_backup_$(date +%Y%m%d).db

# Export all data to CSV
am-query --export csv --output ./backup/
```

## Performance Optimization

### For Low-End Devices

1. Use minimal configuration:
```bash
am-start configs/minimal.yaml
```

2. Increase monitoring intervals:
```yaml
network_interval: 30
process_interval: 60
memory_interval: 120
```

3. Disable non-essential modules:
```yaml
enable_logcat: false
enable_filesystem: false
enable_sensors: false
```

### For Battery Life

1. Reduce monitoring frequency
2. Disable network packet capture
3. Use larger buffer sizes to reduce I/O
4. Schedule monitoring during charging periods

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Ensure scripts are executable: `chmod +x *.sh`
   - Check Termux storage permissions: `termux-setup-storage`

2. **High CPU Usage**
   - Reduce `process_top_n` value
   - Increase monitoring intervals
   - Disable `process_track_threads`

3. **Database Growing Too Large**
   - Run cleanup script regularly
   - Reduce `logcat_buffer_size`
   - Disable verbose modules

4. **Missing Data**
   - Check if monitoring is running: `am-status`
   - Verify database path exists
   - Check log files for errors

### Debug Mode

```bash
# Enable debug logging
python3 android-monitor.py -c config.yaml --log-level DEBUG

# Check logs
tail -f /data/data/com.termux/files/home/android_monitor/logs/monitor.log
```

## Advanced Features

### Custom Queries

```python
# Direct SQL queries on the database
sqlite3 monitor_data.db << SQL
SELECT 
    datetime(timestamp, 'unixepoch', 'localtime') as time,
    name, 
    cpu_percent
FROM process_stats 
WHERE cpu_percent > 50
ORDER BY timestamp DESC
LIMIT 20;
SQL
```

### Integration with Other Tools

```bash
# Export to Grafana-compatible format
am-query --export json | jq '.[] | {timestamp:.timestamp, value:.cpu_percent}'

# Send alerts to webhook
am-query --query alerts | \
  jq -r '.[] | select(.severity=="CRITICAL") | .message' | \
  xargs -I {} curl -X POST https://webhook.url -d "alert={}"
```

### Custom Alert Actions

Add to configuration:
```yaml
alert_actions:
  high_cpu:
    threshold: 90
    command: "notify-send 'High CPU Alert' 'CPU usage exceeded 90%'"
  low_battery:
    threshold: 15
    command: "termux-notification -t 'Low Battery' -c 'Battery at 15%'"
```

## Architecture

### Data Flow
```
Android System
    ↓
Monitoring Modules → SQLite Database → Query/Analysis Tools
    ↓                                          ↓
Real-time Dashboard                    Reports & Exports
```

### Module Design
- Each module runs in its own thread
- Configurable intervals and thresholds
- Batch database writes for efficiency
- Graceful shutdown handling

### Database Schema
- Optimized for time-series queries
- Indexed on timestamps
- Separate tables per data type
- Supports concurrent access

## Contributing

### Adding New Modules

1. Create module class inheriting from base monitor
2. Implement `start()`, `stop()`, and `_monitor_loop()`
3. Add database schema in `DatabaseManager`
4. Register in `AndroidMonitor._init_monitors()`

### Module Template
```python
class CustomMonitor:
    def __init__(self, config: MonitorConfig, db: DatabaseManager):
        self.config = config
        self.db = db
        self.running = False
        
    def start(self):
        self.running = True
        # Start monitoring thread
        
    def stop(self):
        self.running = False
        # Clean shutdown
        
    def _monitor_loop(self):
        while self.running:
            # Collect data
            # Store in database
            time.sleep(self.config.custom_interval)
```

## Security Considerations

1. **Data Privacy**
   - All data stored locally
   - No external transmission by default
   - Configurable data retention

2. **Access Control**
   - Files stored in Termux private directory
   - Database can be encrypted if needed
   - Sensitive data filtering in logcat

3. **Resource Limits**
   - Configurable buffer sizes
   - Automatic cleanup options
   - CPU/memory usage monitoring

## License

This project is provided as-is for educational and monitoring purposes. Use responsibly and in accordance with your device's terms of service.

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review log files for errors
3. Run diagnostic tests
4. Submit detailed bug reports with configuration and logs

---

**Note:** This tool is designed for legitimate monitoring of your own Android device. Always respect privacy laws and obtain necessary permissions when monitoring devices.
