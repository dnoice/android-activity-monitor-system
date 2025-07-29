# Android Monitor API Documentation

## Overview

The Android Monitor system provides a Python API for monitoring various aspects of Android devices through Termux. This document describes the main classes and functions available for programmatic use.

## Core Classes

### MonitorConfig

Central configuration class for all monitoring modules.

```python
from android_monitor import MonitorConfig

config = MonitorConfig(
    output_dir="/path/to/output",
    db_path="monitor.db",
    log_level="INFO",
    enable_logcat=True,
    enable_network=True,
    # ... other options
)
```

#### Key Parameters:
- `output_dir`: Directory for logs and database
- `db_path`: SQLite database filename
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `enable_*`: Boolean flags to enable/disable modules
- `*_interval`: Monitoring intervals in seconds
- `alert_*_threshold`: Threshold values for alerts

### AndroidMonitor

Main monitoring orchestrator that manages all monitoring modules.

```python
from android_monitor import AndroidMonitor

monitor = AndroidMonitor(config_path="config.yaml")
monitor.start()  # Start all enabled monitors
monitor.stop()   # Stop all monitors
```

### DatabaseManager

Handles all database operations.

```python
from android_monitor import DatabaseManager

db = DatabaseManager("monitor.db")
db.insert_batch("table_name", data_list)
results = db.query("SELECT * FROM table WHERE condition", params)
db.close()
```

## Monitor Modules

### LogcatMonitor

Monitors Android system logs.

```python
from android_monitor import LogcatMonitor

logcat = LogcatMonitor(config, db)
logcat.start()
recent_logs = logcat.get_recent_logs(count=100)
logcat.stop()
```

### NetworkMonitor

Monitors network interfaces and traffic.

```python
from android_monitor import NetworkMonitor

network = NetworkMonitor(config, db)
network.start()
# Automatically collects stats at configured intervals
network.stop()
```

### ProcessMonitor

Monitors running processes and resource usage.

```python
from android_monitor import ProcessMonitor

process = ProcessMonitor(config, db)
process.start()
# Tracks top N processes by CPU/memory usage
process.stop()
```

### MemoryMonitor

Monitors system memory usage.

```python
from android_monitor import MemoryMonitor

memory = MemoryMonitor(config, db)
memory.start()
# Collects detailed memory statistics
memory.stop()
```

### BatteryMonitor

Monitors battery status and power usage.

```python
from android_monitor import BatteryMonitor

battery = BatteryMonitor(config, db)
battery.start()
# Tracks battery level, temperature, charging status
battery.stop()
```

### FilesystemMonitor

Monitors file system changes.

```python
from android_monitor import FilesystemMonitor

fs = FilesystemMonitor(config, db)
fs.start()
# Detects file creation, modification, deletion
fs.stop()
```

### AppMonitor

Monitors application events.

```python
from android_monitor import AppMonitor

apps = AppMonitor(config, db)
apps.start()
# Tracks app launches, crashes, ANRs
apps.stop()
```

## Query Interface

### MonitorQuery

Query interface for analyzing collected data.

```python
from android_query import MonitorQuery

query = MonitorQuery("monitor.db")

# Get time range of data
start_time, end_time = query.get_time_range()

# Query specific data types
logs = query.query_logcat(
    start_time=datetime(2025, 1, 1),
    end_time=datetime(2025, 1, 31),
    level="E",
    tag="System",
    search="error"
)

network_stats = query.query_network_stats(
    interface="wlan0"
)

process_stats = query.query_process_stats(
    process_name="chrome",
    min_cpu=50.0
)

# Get summary statistics
summary = query.get_summary_stats()
```

### DataAnalyzer

Advanced analysis functions.

```python
from android_query import DataAnalyzer

analyzer = DataAnalyzer(query)

# Analyze network usage patterns
network_analysis = analyzer.analyze_network_usage(
    start_time, end_time
)

# Analyze specific process behavior
process_analysis = analyzer.analyze_process_behavior(
    "com.android.chrome",
    start_time, end_time
)

# Analyze memory pressure
memory_analysis = analyzer.analyze_memory_pressure(
    start_time, end_time
)

# Analyze battery drain
battery_analysis = analyzer.analyze_battery_drain(
    start_time, end_time
)

# Correlate events across monitors
correlations = analyzer.correlate_events(
    start_time, end_time
)
```

### Visualizer

Data visualization functions.

```python
from android_query import Visualizer

viz = Visualizer(query)

# Plot network usage
viz.plot_network_usage(
    interface="wlan0",
    save_path="network.png"
)

# Plot CPU usage by top processes
viz.plot_cpu_usage(
    top_n=10,
    save_path="cpu.png"
)

# Plot memory usage over time
viz.plot_memory_usage(save_path="memory.png")

# Plot battery status
viz.plot_battery_status(save_path="battery.png")

# Plot alert timeline
viz.plot_alert_timeline(save_path="alerts.png")
```

## Dashboard Interface

### Dashboard

Terminal-based real-time dashboard.

```python
from android_dashboard import Dashboard, DashboardData

data = DashboardData("monitor.db")
dashboard = Dashboard(data)
dashboard.run()  # Runs interactive terminal UI
```

### LiveMonitor

Live monitoring without database storage.

```python
from android_dashboard import LiveMonitor

monitor = LiveMonitor()
monitor.run()  # Shows real-time stats without persistence
```

## Utility Functions

### DatabaseOptimizer

Database maintenance utilities.

```python
from android_monitor_utils import DatabaseOptimizer

optimizer = DatabaseOptimizer("monitor.db")

# Analyze database
stats = optimizer.analyze_database()

# Optimize performance
results = optimizer.optimize(vacuum=True, reindex=True)

# Archive old data
archive_path = optimizer.archive_old_data(
    days_to_keep=30,
    archive_path="archive.db.zip"
)
```

### AlertManager

Alert management and notifications.

```python
from android_monitor_utils import AlertManager

alerts = AlertManager("config.yaml")

# Setup email alerts
alerts.setup_email_alerts(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    email="sender@gmail.com",
    password="app_password",
    recipients=["admin@example.com"]
)

# Send custom alert
alerts.send_alert(
    alert_type="CUSTOM",
    message="Custom alert message",
    data={"key": "value"}
)
```

### ReportGenerator

Generate reports from collected data.

```python
from android_monitor_utils import ReportGenerator

reporter = ReportGenerator("monitor.db")

# Generate executive summary
summary = reporter.generate_executive_summary(
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 31)
)
```

## Database Schema

### Tables

1. **logcat_entries**
   - `id`: Primary key
   - `timestamp`: Unix timestamp
   - `level`: Log level (V/D/I/W/E)
   - `tag`: Log tag
   - `pid`: Process ID
   - `message`: Log message
   - `raw_entry`: Original log line

2. **network_stats**
   - `id`: Primary key
   - `timestamp`: Unix timestamp
   - `interface`: Network interface name
   - `bytes_sent`: Total bytes sent
   - `bytes_recv`: Total bytes received
   - `packets_sent`: Total packets sent
   - `packets_recv`: Total packets received
   - `errors_in`: Input errors
   - `errors_out`: Output errors

3. **process_stats**
   - `id`: Primary key
   - `timestamp`: Unix timestamp
   - `pid`: Process ID
   - `name`: Process name
   - `cpu_percent`: CPU usage percentage
   - `memory_percent`: Memory usage percentage
   - `memory_rss`: Resident Set Size
   - `memory_vms`: Virtual Memory Size
   - `num_threads`: Number of threads
   - `status`: Process status

4. **memory_stats**
   - `id`: Primary key
   - `timestamp`: Unix timestamp
   - `total`: Total memory
   - `available`: Available memory
   - `percent`: Usage percentage
   - `used`: Used memory
   - `free`: Free memory
   - `swap_total`: Total swap
   - `swap_used`: Used swap
   - `swap_free`: Free swap

5. **battery_stats**
   - `id`: Primary key
   - `timestamp`: Unix timestamp
   - `level`: Battery level (0-100)
   - `status`: Charging status
   - `temperature`: Temperature in Celsius
   - `voltage`: Voltage in Volts
   - `technology`: Battery technology
   - `health`: Battery health

6. **filesystem_events**
   - `id`: Primary key
   - `timestamp`: Unix timestamp
   - `event_type`: created/modified/deleted
   - `path`: File path
   - `size`: File size
   - `permissions`: File permissions
   - `owner`: File owner UID

7. **app_events**
   - `id`: Primary key
   - `timestamp`: Unix timestamp
   - `package_name`: App package name
   - `event_type`: Event type
   - `component`: Component name
   - `data`: Additional data

8. **alerts**
   - `id`: Primary key
   - `timestamp`: Unix timestamp
   - `module`: Source module
   - `severity`: INFO/WARNING/ERROR/CRITICAL
   - `message`: Alert message
   - `data`: JSON data

---

# docs/MODULES.md
# Android Monitor Modules Documentation

## Overview

The Android Monitor system consists of multiple specialized monitoring modules, each responsible for tracking specific aspects of the Android system. This document provides detailed information about each module.

## Module Architecture

All modules follow a consistent architecture:

1. **Initialization**: Accept configuration and database manager
2. **Start/Stop**: Thread-based operation with graceful shutdown
3. **Data Collection**: Periodic data gathering based on intervals
4. **Storage**: Batch writes to SQLite database
5. **Alerting**: Threshold-based alert generation

## Logcat Monitor

### Purpose
Monitors Android system logs to capture application and system events, errors, and debugging information.

### Features
- Real-time log streaming
- Configurable log level filtering
- Tag-based filtering
- Pattern matching for specific events
- Circular buffer to limit memory usage

### Configuration
```yaml
enable_logcat: true
logcat_buffer_size: 1000  # Number of entries to keep in memory
logcat_filters:           # List of tag:priority filters
  - "ActivityManager:I"
  - "System:W"
logcat_priority: V        # Minimum priority (V/D/I/W/E)
```

### Data Collected
- Timestamp
- Log level (Verbose/Debug/Info/Warning/Error)
- Tag (source component)
- Process ID
- Log message
- Raw log entry

### Use Cases
- Application debugging
- Error tracking
- Security monitoring
- Performance analysis
- Crash investigation

## Network Monitor

### Purpose
Tracks network interface statistics and connection information to monitor data usage and network activity.

### Features
- Per-interface statistics
- Bandwidth calculation
- Connection tracking (optional)
- Error monitoring
- Data rate alerting

### Configuration
```yaml
enable_network: true
network_interval: 5        # Seconds between checks
network_capture_packets: false  # Enable connection tracking
network_interfaces: []     # Empty = all interfaces
```

### Data Collected
- Interface name
- Bytes sent/received
- Packets sent/received
- Errors in/out
- Active connections (if enabled)

### Use Cases
- Data usage monitoring
- Network performance analysis
- Bandwidth throttling detection
- Connection troubleshooting
- Security monitoring

## Process Monitor

### Purpose
Monitors running processes to track CPU and memory usage, identify resource-intensive applications.

### Features
- Top N processes by CPU usage
- Memory usage tracking
- Thread count monitoring
- Process status tracking
- Historical trending

### Configuration
```yaml
enable_process: true
process_interval: 10       # Seconds between checks
process_top_n: 20         # Number of top processes to track
process_track_threads: true  # Include thread information
```

### Data Collected
- Process ID and name
- CPU usage percentage
- Memory usage (percentage and absolute)
- Number of threads
- Process status
- RSS (Resident Set Size)
- VMS (Virtual Memory Size)

### Use Cases
- Performance optimization
- Resource leak detection
- Application profiling
- System health monitoring
- Malware detection

## Memory Monitor

### Purpose
Tracks system memory usage to identify memory pressure situations and optimize performance.

### Features
- System-wide memory statistics
- Swap usage monitoring
- Detailed memory breakdown
- Memory pressure detection
- Historical analysis

### Configuration
```yaml
enable_memory: true
memory_interval: 30        # Seconds between checks
memory_detailed: true      # Include detailed /proc/meminfo data
```

### Data Collected
- Total/Used/Free/Available memory
- Memory usage percentage
- Swap usage
- Detailed memory categories (if enabled)
- Cache and buffer sizes

### Use Cases
- Memory leak detection
- OOM (Out of Memory) prevention
- Performance tuning
- Capacity planning
- Application memory profiling

## Battery Monitor

### Purpose
Monitors battery status and power consumption to optimize battery life and detect power issues.

### Features
- Battery level tracking
- Charging status monitoring
- Temperature monitoring
- Voltage tracking
- Drain rate calculation

### Configuration
```yaml
enable_battery: true
battery_interval: 60       # Seconds between checks
battery_track_apps: true   # Track per-app battery usage
```

### Data Collected
- Battery level (0-100%)
- Charging status
- Temperature (Celsius)
- Voltage
- Battery technology
- Health status

### Use Cases
- Battery life optimization
- Charging behavior analysis
- Temperature monitoring
- Power consumption profiling
- Battery health tracking

## Filesystem Monitor

### Purpose
Monitors file system changes to track file creation, modification, and deletion events.

### Features
- Directory watching
- Recursive monitoring
- Change detection
- Permission tracking
- Size monitoring

### Configuration
```yaml
enable_filesystem: true
fs_watch_paths:           # Paths to monitor
  - /data/data/com.termux/files/home
  - /sdcard/Download
fs_interval: 5            # Seconds between scans
fs_recursive: true        # Monitor subdirectories
```

### Data Collected
- Event type (created/modified/deleted)
- File path
- File size
- Permissions
- Owner UID
- Timestamp

### Use Cases
- Security monitoring
- Data loss prevention
- Change tracking
- Backup verification
- Compliance monitoring

## App Monitor

### Purpose
Monitors application lifecycle events including launches, crashes, and ANRs (Application Not Responding).

### Features
- App launch detection
- Crash monitoring
- ANR detection
- Force stop tracking
- Launch time measurement

### Configuration
```yaml
enable_apps: true
# Uses logcat ActivityManager for monitoring
```

### Data Collected
- Package name
- Event type (start/crash/ANR/force_stop)
- Component name
- Launch time (for activity launches)
- Event details

### Use Cases
- App stability monitoring
- Performance tracking
- Crash analysis
- User behavior analysis
- Quality assurance

## Alert System

### Purpose
Provides configurable alerting based on thresholds and conditions across all modules.

### Features
- Threshold-based alerts
- Multiple severity levels
- Custom actions
- Alert history
- Correlation detection

### Configuration
```yaml
# Threshold settings
alert_cpu_threshold: 80.0      # CPU usage %
alert_memory_threshold: 85.0   # Memory usage %
alert_battery_threshold: 20.0  # Battery level %
alert_network_threshold: 100.0 # Network rate MB/s

# Custom alert actions
alert_actions:
  high_cpu:
    threshold: 90
    command: "termux-notification -t 'High CPU Alert'"
```

### Alert Types
- HIGH_CPU_USAGE
- HIGH_MEMORY_USAGE
- LOW_BATTERY
- HIGH_NETWORK_USAGE
- FILESYSTEM_CHANGE
- APP_CRASH
- SECURITY_EVENT

### Alert Channels
- Database storage
- Termux notifications
- Email (if configured)
- Webhooks
- Custom commands

## Module Interactions

### Data Correlation
Modules can work together to provide comprehensive insights:

1. **Performance Analysis**
   - Process Monitor + Memory Monitor + Battery Monitor
   - Identify apps causing high resource usage and battery drain

2. **Security Monitoring**
   - Logcat Monitor + Filesystem Monitor + Network Monitor
   - Detect suspicious activities across multiple vectors

3. **App Profiling**
   - App Monitor + Process Monitor + Memory Monitor
   - Complete application performance profile

### Event Correlation
The query tool can correlate events across modules:
- High CPU → Increased battery drain
- App launch → Memory spike
- Network activity → Process activity
- File changes → App events

## Performance Considerations

### Resource Usage
Each module has different resource requirements:

| Module | CPU Impact | Memory Impact | Storage Impact |
|--------|------------|---------------|----------------|
| Logcat | Low-Medium | Medium | High |
| Network | Low | Low | Medium |
| Process | Medium | Low | Medium |
| Memory | Low | Low | Low |
| Battery | Low | Low | Low |
| Filesystem | Medium | Medium | Medium |
| Apps | Low | Low | Low |

### Optimization Tips

1. **Adjust Intervals**
   - Increase intervals for lower resource usage
   - Balance between data granularity and performance

2. **Limit Scope**
   - Reduce process_top_n for fewer processes
   - Limit filesystem paths monitored
   - Use specific logcat filters

3. **Disable Unused Modules**
   - Only enable modules you need
   - Use preset configurations

4. **Database Maintenance**
   - Regular cleanup of old data
   - Periodic optimization
   - Archive historical data

---

# docs/CONTRIBUTING.md
# Contributing to Android Activity Monitor System

Thank you for your interest in contributing to the Android Activity Monitor System! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [How to Contribute](#how-to-contribute)
5. [Code Style Guidelines](#code-style-guidelines)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Submitting Changes](#submitting-changes)
9. [Adding New Modules](#adding-new-modules)
10. [Release Process](#release-process)

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Expected Behavior

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

## Getting Started

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/android-activity-monitor-system.git
   cd android-activity-monitor-system
   ```

2. **Set Up Development Environment**
   ```bash
   # Add upstream remote
   git remote add upstream https://github.com/dnoice/android-activity-monitor-system.git
   
   # Install in development mode
   ./setup.sh --dev
   ```

3. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

## Development Setup

### Prerequisites

- Termux with proot-distro Ubuntu
- Python 3.8+
- Git
- SQLite3

### Development Installation

```bash
# Clone the repository
git clone https://github.com/dnoice/android-activity-monitor-system.git
cd android-activity-monitor-system

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install pre-commit hooks
pre-commit install
```

### Development Tools

```bash
# Run tests
python -m pytest tests/

# Run linting
flake8 src/ utils/
pylint src/ utils/

# Format code
black src/ utils/

# Type checking
mypy src/ utils/
```

## How to Contribute

### Types of Contributions

1. **Bug Fixes**
   - Check existing issues
   - Create a new issue if needed
   - Reference issue number in PR

2. **New Features**
   - Discuss in issues first
   - Follow module architecture
   - Include tests and documentation

3. **Documentation**
   - Fix typos or clarify existing docs
   - Add examples
   - Improve API documentation

4. **Performance Improvements**
   - Profile before and after
   - Document improvements
   - Ensure compatibility

### Contribution Workflow

1. **Find or Create an Issue**
   - Check existing issues
   - Create new issue for discussion
   - Get feedback before major work

2. **Develop Your Changes**
   - Write clean, documented code
   - Follow style guidelines
   - Add tests for new functionality

3. **Test Your Changes**
   - Run existing tests
   - Add new tests
   - Test on actual device

4. **Submit Pull Request**
   - Clear description
   - Reference related issues
   - Include test results

## Code Style Guidelines

### Python Style

We follow PEP 8 with some modifications:

```python
# Imports
import os
import sys
from typing import Dict, List, Optional

import third_party_module

from android_monitor import local_module

# Constants
MAX_BUFFER_SIZE = 1000
DEFAULT_INTERVAL = 10

# Classes
class MonitorModule:
    """
    Brief description.
    
    Longer description if needed.
    
    Args:
        config: Configuration object
        db: Database manager
    """
    
    def __init__(self, config: MonitorConfig, db: DatabaseManager):
        self.config = config
        self.db = db
        self._private_var = None
    
    def public_method(self, param: str) -> Dict[str, Any]:
        """
        Method description.
        
        Args:
            param: Parameter description
            
        Returns:
            Dictionary containing results
        """
        pass
    
    def _private_method(self):
        """Private methods start with underscore."""
        pass

# Functions
def process_data(data: List[Dict]) -> List[Dict]:
    """
    Process data with clear type hints.
    
    Args:
        data: List of data dictionaries
        
    Returns:
        Processed data list
    """
    return [process_item(item) for item in data]

# Constants for type checking
if TYPE_CHECKING:
    from typing import TypeAlias
    
    DataPoint: TypeAlias = Dict[str, Union[str, int, float]]
```

### Naming Conventions

- **Files**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions**: `lowercase_with_underscores`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Private**: `_leading_underscore`

### Documentation

```python
def complex_function(
    param1: str,
    param2: Optional[int] = None,
    *args: Any,
    **kwargs: Any
) -> Tuple[bool, str]:
    """
    Brief one-line description.
    
    Longer description explaining the function's purpose,
    behavior, and any important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: None)
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments
        
    Returns:
        Tuple containing:
            - Success status (bool)
            - Result or error message (str)
            
    Raises:
        ValueError: If param1 is empty
        ConnectionError: If database is unavailable
        
    Example:
        >>> result, message = complex_function("test", param2=42)
        >>> print(f"Success: {result}, Message: {message}")
    """
    pass
```

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── test_monitors/
│   ├── test_logcat.py
│   ├── test_network.py
│   └── ...
├── test_database.py
├── test_query.py
└── test_utils.py
```

### Writing Tests

```python
# tests/test_monitors/test_network.py
import pytest
from unittest.mock import Mock, patch

from android_monitor import NetworkMonitor, MonitorConfig

class TestNetworkMonitor:
    """Test cases for NetworkMonitor."""
    
    @pytest.fixture
    def monitor(self):
        """Create monitor instance for testing."""
        config = MonitorConfig(
            enable_network=True,
            network_interval=1
        )
        db = Mock()
        return NetworkMonitor(config, db)
    
    def test_start_stop(self, monitor):
        """Test monitor can start and stop."""
        monitor.start()
        assert monitor.running
        
        monitor.stop()
        assert not monitor.running
    
    @patch('psutil.net_io_counters')
    def test_collect_stats(self, mock_net_io, monitor):
        """Test network statistics collection."""
        mock_net_io.return_value = {
            'eth0': Mock(
                bytes_sent=1000,
                bytes_recv=2000,
                packets_sent=10,
                packets_recv=20
            )
        }
        
        stats = monitor._collect_network_stats()
        assert len(stats) == 1
        assert stats[0]['interface'] == 'eth0'
        assert stats[0]['bytes_sent'] == 1000
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov=utils

# Run specific test file
pytest tests/test_monitors/test_network.py

# Run with verbose output
pytest -v

# Run only marked tests
pytest -m "not slow"
```

## Documentation

### Documentation Standards

1. **Docstrings**: All public functions and classes
2. **Type Hints**: Use for all parameters and returns
3. **Examples**: Include usage examples
4. **README**: Keep updated with new features

### Adding Documentation

1. **API Documentation**
   - Update `docs/API.md` for new functions
   - Include type information
   - Add usage examples

2. **Module Documentation**
   - Update `docs/MODULES.md` for new modules
   - Explain configuration options
   - Document data collected

3. **User Documentation**
   - Update README.md
   - Add to troubleshooting if needed
   - Include in examples

## Submitting Changes

### Pull Request Process

1. **Prepare Your Branch**
   ```bash
   # Update from upstream
   git fetch upstream
   git rebase upstream/main
   
   # Run tests
   pytest
   
   # Check code style
   flake8 src/ utils/
   black --check src/ utils/
   ```

2. **Create Pull Request**
   - Use descriptive title
   - Reference issue numbers
   - Describe changes made
   - Include test results

3. **PR Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Related Issues
   Fixes #123
   
   ## Testing
   - [ ] Tests pass locally
   - [ ] Added new tests
   - [ ] Tested on device
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No new warnings
   ```

### Code Review

- Be open to feedback
- Respond to all comments
- Make requested changes
- Re-request review when ready

## Adding New Modules

### Module Template

```python
# src/monitors/example_monitor.py
"""
Example Monitor Module
Monitors example metrics from the system
"""

import time
import threading
from typing import Dict, List, Any, Optional

from android_monitor.base import BaseMonitor
from android_monitor.config import MonitorConfig
from android_monitor.database import DatabaseManager

class ExampleMonitor(BaseMonitor):
    """
    Monitor for example metrics.
    
    This monitor collects example data and stores it in the database.
    """
    
    def __init__(self, config: MonitorConfig, db: DatabaseManager):
        super().__init__(config, db)
        self.interval = config.example_interval
        
    def start(self) -> None:
        """Start the monitor."""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        self.logger.info("Example monitor started")
    
    def stop(self) -> None:
        """Stop the monitor."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=self.interval + 1)
        self.logger.info("Example monitor stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.running:
            try:
                data = self._collect_data()
                if data:
                    self.db.insert_batch('example_stats', data)
                    self._check_thresholds(data)
                
                time.sleep(self.interval)
                
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
                time.sleep(self.interval)
    
    def _collect_data(self) -> List[Dict[str, Any]]:
        """
        Collect example data.
        
        Returns:
            List of data points to store
        """
        # Implement data collection
        return [{
            'timestamp': time.time(),
            'metric': 42,
            'status': 'active'
        }]
    
    def _check_thresholds(self, data: List[Dict[str, Any]]) -> None:
        """Check thresholds and create alerts."""
        for item in data:
            if item['metric'] > self.config.alert_example_threshold:
                self._create_alert(
                    'HIGH_EXAMPLE_METRIC',
                    f"Example metric too high: {item['metric']}",
                    item
                )
```

### Integration Steps

1. **Create Monitor Class**
   - Inherit from BaseMonitor
   - Implement required methods
   - Add data collection logic

2. **Update Database Schema**
   ```python
   # In DatabaseManager.__init__
   'example_stats': '''
       CREATE TABLE IF NOT EXISTS example_stats (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           timestamp REAL,
           metric INTEGER,
           status TEXT
       )
   '''
   ```

3. **Update Configuration**
   ```python
   # In MonitorConfig
   enable_example: bool = False
   example_interval: int = 30
   alert_example_threshold: float = 100.0
   ```

4. **Register Monitor**
   ```python
   # In AndroidMonitor._init_monitors
   if self.config.enable_example:
       self.monitors[MonitorModule.EXAMPLE] = ExampleMonitor(
           self.config, self.db
       )
   ```

5. **Add Query Support**
   ```python
   # In MonitorQuery
   def query_example_stats(self, ...):
       # Add query method
   ```

6. **Update Documentation**
   - Add to MODULES.md
   - Update API.md
   - Add configuration example

7. **Add Tests**
   ```python
   # tests/test_monitors/test_example.py
   # Add comprehensive tests
   ```

## Release Process

### Version Numbering

We use Semantic Versioning (MAJOR.MINOR.PATCH):
- MAJOR: Incompatible API changes
- MINOR: New functionality, backwards compatible
- PATCH: Bug fixes, backwards compatible

### Release Checklist

1. **Update Version**
   - Update version in `setup.py`
   - Update version in `__init__.py`
   - Update CHANGELOG.md

2. **Test Release**
   ```bash
   # Run full test suite
   pytest --cov
   
   # Test installation
   python setup.py sdist bdist_wheel
   pip install dist/*.whl
   ```

3. **Create Release**
   - Tag version: `git tag -a v1.2.3 -m "Release version 1.2.3"`
   - Push tag: `git push upstream v1.2.3`
   - Create GitHub release
   - Upload artifacts

### Changelog Format

```markdown
# Changelog

## [1.2.3] - 2025-01-30

### Added
- New feature description

### Changed
- Changed behavior description

### Fixed
- Bug fix description

### Deprecated
- Deprecated feature notice

### Removed
- Removed feature description

### Security
- Security fix description
```

## Questions?

If you have questions:
1. Check existing documentation
2. Search closed issues
3. Ask in discussions
4. Create a new issue

Thank you for contributing!
