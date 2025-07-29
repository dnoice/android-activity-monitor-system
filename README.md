# Android Activity Monitor System

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/dnoice/android-activity-monitor-system/blob/main/LICENSE)
[![Platform](https://img.shields.io/badge/platform-Android%20(Termux)-orange.svg)](https://termux.com/)
[![GitHub issues](https://img.shields.io/github/issues/dnoice/android-activity-monitor-system)](https://github.com/dnoice/android-activity-monitor-system/issues)
[![GitHub stars](https://img.shields.io/github/stars/dnoice/android-activity-monitor-system)](https://github.com/dnoice/android-activity-monitor-system/stargazers)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](https://github.com/dnoice/android-activity-monitor-system/pulls)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/dnoice/android-activity-monitor-system/graphs/commit-activity)

A comprehensive, modular monitoring solution for Android devices running in Termux proot-distro Ubuntu environment. This system provides real-time monitoring, data collection, analysis, and visualization of Android device activity.

## 🔗 Quick Links

📖 [Documentation](https://github.com/dnoice/android-activity-monitor-system/wiki) | 
🐛 [Report Bug](https://github.com/dnoice/android-activity-monitor-system/issues/new?template=bug_report.md) | 
✨ [Request Feature](https://github.com/dnoice/android-activity-monitor-system/issues/new?template=feature_request.md) | 
💬 [Discussions](https://github.com/dnoice/android-activity-monitor-system/discussions)

## 📚 Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Dashboard Navigation](#dashboard-navigation)
- [Data Management](#data-management)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Monitoring Modules

- 📱 **Logcat Monitor** - System log monitoring with filtering and alerting
- 🌐 **Network Monitor** - Interface statistics, connection tracking, bandwidth monitoring
- ⚙️ **Process Monitor** - CPU/memory usage, top processes, thread tracking
- 💾 **Memory Monitor** - System memory usage, pressure detection, detailed statistics
- 🔋 **Battery Monitor** - Battery level, temperature, charging status, drain analysis
- 📁 **Filesystem Monitor** - File system changes, access patterns, storage usage
- 📲 **App Monitor** - Application lifecycle events, crashes, ANRs
- 📡 **Sensor Monitor** - Device sensor data collection (optional)

### Analysis & Visualization

- 📊 **Real-time Dashboard** - Terminal-based live monitoring interface
- 🔍 **Query Tool** - Interactive data exploration and analysis
- 📈 **Data Export** - CSV, JSON, and HTML report generation
- 🔗 **Correlation Analysis** - Cross-module event correlation
- 🚨 **Alert System** - Configurable thresholds and notifications

### Key Features

- ✅ **Modular Architecture** - Enable/disable modules as needed
- ⚡ **Performance Optimized** - Batch processing, configurable intervals
- 🧠 **Smart Analytics** - Anomaly detection, trend analysis
- 🔔 **Flexible Alerts** - Email, webhooks, Termux notifications
- 💽 **Data Management** - Auto cleanup, compression, archiving
- 🎯 **Multiple Interfaces** - CLI, TUI dashboard, web reports

## 📸 Screenshots

<details>
<summary>Real-time Dashboard</summary>

```
┌─────────────────────────────────────────────────────────────┐
│        Android Activity Monitor - Real-time Dashboard        │
├─────────────────────────────────────────────────────────────┤
│ CPU: 45.2% | Mem: 72.3% | Net: 1.24 MB/s | Bat: 85%       │
├─────────────────────────────────────────────────────────────┤
│ [System Resources]                                          │
│                                                             │
│ CPU     ████████████░░░░░░░░░░░░░ 45.2%                   │
│ Memory  ██████████████████░░░░░░░ 72.3%                   │
│                                                             │
│ [Top Processes (by CPU)]                                    │
│ com.android.chrome         CPU: 15.2% MEM:  8.5%          │
│ com.termux                 CPU: 12.1% MEM:  3.2%          │
│ system_server              CPU:  8.7% MEM: 12.1%          │
│                                                             │
│ [Recent Alerts]                                             │
│ 14:23:05 [memory] System memory usage: 85.2%              │
│ 14:20:12 [network] High network usage on wlan0: 125 MB/s  │
└─────────────────────────────────────────────────────────────┘
│ [1] Overview [2] Processes [3] Network [4] Logs [5] Alerts │
└─────────────────────────────────────────────────────────────┘
```

</details>

<details>
<summary>Query Tool Interface</summary>

```
Android Monitor Query Tool
==================================================

Database Summary:
--------------------------------------------------
Time range: 2025-07-25T10:00:00 to 2025-07-28T16:30:00
Duration: 78.50 hours

Record counts:
  logcat_entries: 125,432
  network_stats: 45,234
  process_stats: 89,123
  memory_stats: 15,234
  battery_stats: 1,234
  filesystem_events: 34,567
  app_events: 12,345
  alerts: 234

Options:
1. Query logcat          9. Analyze network usage
2. Query network stats   10. Analyze process behavior
3. Query process stats   11. Analyze memory pressure
4. Query memory stats    12. Analyze battery drain
5. Query battery stats   13. Correlate events
6. Query filesystem      14. Visualize data
7. Query app events      15. Export data
8. Query alerts          0. Exit

Select option: _
```

</details>

## 🔧 System Requirements

### Minimum Requirements
- 📱 **Android** 7.0+ (API 24+)
- 💾 **Storage**: 500MB free space
- 🧮 **RAM**: 2GB+ recommended
- 🐍 **Python**: 3.8+

### Required Apps
- [**Termux**](https://termux.com/) - Terminal emulator
- **Termux:API** (optional) - For enhanced features
- **Termux:Boot** (optional) - For auto-start on boot

### Permissions
- ✅ Storage access
- ✅ Network access
- ✅ System log reading (logcat)
- 🔓 Root access (optional, for enhanced monitoring)

## Installation

1. **Install Termux and proot-distro Ubuntu:**
```bash
# In Termux
pkg update && pkg upgrade
pkg install proot-distro git
proot-distro install ubuntu
```

2. **Enter Ubuntu environment:**
```bash
proot-distro login ubuntu
```

3. **Clone the repository and run setup:**
```bash
# Clone the repository
git clone https://github.com/dnoice/android-activity-monitor-system.git
cd android-activity-monitor-system

# Run the setup script
chmod +x setup.sh
./setup.sh
```

4. **The setup script will automatically:**
   - Install all required dependencies
   - Create directory structure
   - Copy monitoring scripts to appropriate locations
   - Set up configuration files
   - Create convenience aliases

## 📁 Project Structure

```
android-activity-monitor-system/
│
├── 📄 README.md              # This file
├── 📄 LICENSE                # MIT License
├── 🔧 setup.sh               # Automated installation script
│
├── 📂 src/                   # Source code
│   ├── 🐍 android-monitor.py     # Main monitoring engine
│   ├── 🐍 android-query.py       # Data query and analysis tool
│   └── 🐍 android-dashboard.py   # Real-time terminal dashboard
│
├── 📂 configs/               # Configuration presets
│   ├── ⚙️ default.yaml          # Default configuration
│   ├── ⚡ minimal.yaml          # Low resource configuration
│   ├── 🚀 performance.yaml      # Performance monitoring focus
│   └── 🔒 security.yaml         # Security monitoring focus
│
├── 📂 utils/                 # Utility scripts
│   └── 🛠️ android-monitor-utils.py  # Database optimization, alerts, etc.
│
└── 📂 docs/                  # Documentation
    ├── 📖 API.md                # API documentation
    ├── 📖 MODULES.md            # Module documentation
    └── 📖 CONTRIBUTING.md       # Contribution guidelines
```

## Quick Start

## 🚀 Quick Start

### Basic Commands

```bash
# 🟢 Start monitoring with default configuration
am-start

# 📊 View real-time dashboard
am-dash

# 🔍 Interactive data analysis
am-query -i

# 💻 Live system monitoring (no database)
am-live

# 🛑 Stop monitoring
am-stop

# 📈 Check monitoring status
am-status
```

### Common Workflows

```bash
# 🎯 Start with specific configuration
am-start configs/performance.yaml

# 📄 Generate HTML report for the last 7 days
am-query --export html --output report.html

# 🔎 Query high CPU processes
am-query --query process --min-cpu 50

# 📊 Visualize network usage
am-query --visualize network --output network-graph.png
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

## 📊 Performance Benchmarks

| Configuration | CPU Usage | Memory Usage | Battery Impact |
|--------------|-----------|--------------|----------------|
| Minimal      | ~2-3%     | ~50MB        | Low           |
| Default      | ~5-7%     | ~100MB       | Moderate      |
| Performance  | ~8-10%    | ~150MB       | Moderate      |
| Security     | ~10-12%   | ~200MB       | High          |

*Tested on: Snapdragon 865, 8GB RAM, Android 11*

## 🐛 Troubleshooting

### Common Issues

<details>
<summary>❌ Permission Denied</summary>

```bash
# Fix script permissions
chmod +x /data/data/com.termux/files/home/android_monitor/bin/*.py
chmod +x /data/data/com.termux/files/home/android_monitor/*.sh

# Fix Termux storage permissions
termux-setup-storage
```
</details>

<details>
<summary>⚠️ High CPU Usage</summary>

- Reduce `process_top_n` value in configuration
- Increase monitoring intervals
- Disable `process_track_threads`
- Use minimal configuration preset
</details>

<details>
<summary>💾 Database Growing Too Large</summary>

```bash
# Run cleanup for data older than 7 days
/data/data/com.termux/files/home/android_monitor/cleanup.sh 7

# Archive old data
python3 android-monitor-utils.py optimize monitor_data.db --archive 30

# Set up automatic cleanup (crontab)
0 3 * * * /data/data/com.termux/files/home/android_monitor/cleanup.sh 7
```
</details>

<details>
<summary>📉 Missing Data</summary>

```bash
# Check if monitoring is running
am-status

# Check database exists
ls -la /data/data/com.termux/files/home/android_monitor/monitor_data.db

# Check logs for errors
tail -f /data/data/com.termux/files/home/android_monitor/logs/monitor.log

# Run diagnostics
python3 android-monitor-utils.py diagnose
```
</details>

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

## ❓ FAQ

<details>
<summary>Can I run this without root?</summary>

Yes! The monitor works without root, though some features may be limited:
- ✅ Most monitoring features work normally
- ⚠️ Some system logs may be restricted
- ⚠️ Deep process inspection may be limited
</details>

<details>
<summary>How much battery does it use?</summary>

Battery impact depends on configuration:
- **Minimal config**: ~1-2% per hour
- **Default config**: ~2-3% per hour
- **Full monitoring**: ~3-5% per hour

Use battery optimization tips in the Performance Optimization section.
</details>

<details>
<summary>Can I monitor multiple devices?</summary>

Each device needs its own installation. For centralized monitoring:
1. Export data from each device
2. Use the HTML report feature
3. Consider setting up a central collection point
</details>

<details>
<summary>Is my data secure?</summary>

- ✅ All data stored locally on device
- ✅ No external data transmission by default
- ✅ Data stored in Termux private directory
- ✅ Optional encryption available
</details>

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

### Submitting Pull Requests

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](https://github.com/dnoice/android-activity-monitor-system/blob/main/docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

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

This project is licensed under the MIT License - see the [LICENSE](https://github.com/dnoice/android-activity-monitor-system/blob/main/LICENSE) file for details.

## Support

For issues, questions, or contributions:
1. Check the [troubleshooting](#troubleshooting) section
2. Search [existing issues](https://github.com/dnoice/android-activity-monitor-system/issues)
3. Create a new issue with:
   - System information
   - Configuration used
   - Error logs
   - Steps to reproduce

## Acknowledgments

- Termux community for the amazing terminal emulator
- Contributors and testers
- Open source projects that make this possible

---

**Note:** This tool is designed for legitimate monitoring of your own Android device. Always respect privacy laws and obtain necessary permissions when monitoring devices.

