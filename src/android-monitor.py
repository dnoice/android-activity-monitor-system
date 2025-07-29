#!/usr/bin/env python3
"""
Android Activity Monitor for Termux proot-distro Ubuntu
Comprehensive monitoring solution with modular architecture
"""

import os
import sys
import json
import time
import signal
import sqlite3
import argparse
import threading
import subprocess
from datetime import datetime
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional, Any
import logging
from pathlib import Path
import re
import psutil
import requests
from dataclasses import dataclass, asdict
from enum import Enum
import yaml

# Configuration Management
@dataclass
class MonitorConfig:
    """Central configuration for all monitoring modules"""
    # General settings
    output_dir: str = "/data/data/com.termux/files/home/android_monitor"
    db_path: str = "monitor_data.db"
    log_level: str = "INFO"
    
    # Module toggles
    enable_logcat: bool = True
    enable_network: bool = True
    enable_process: bool = True
    enable_memory: bool = True
    enable_battery: bool = True
    enable_filesystem: bool = True
    enable_sensors: bool = True
    enable_apps: bool = True
    
    # Logcat settings
    logcat_buffer_size: int = 1000
    logcat_filters: List[str] = None
    logcat_priority: str = "V"  # V=Verbose, D=Debug, I=Info, W=Warning, E=Error
    
    # Network settings
    network_interval: int = 5
    network_capture_packets: bool = False
    network_interfaces: List[str] = None
    
    # Process settings
    process_interval: int = 10
    process_top_n: int = 20
    process_track_threads: bool = True
    
    # Memory settings
    memory_interval: int = 30
    memory_detailed: bool = True
    
    # Battery settings
    battery_interval: int = 60
    battery_track_apps: bool = True
    
    # Filesystem settings
    fs_watch_paths: List[str] = None
    fs_interval: int = 5
    fs_recursive: bool = True
    
    # Alert settings
    alert_cpu_threshold: float = 80.0
    alert_memory_threshold: float = 85.0
    alert_battery_threshold: float = 20.0
    alert_network_threshold: float = 100.0  # MB/s
    
    def __post_init__(self):
        if self.logcat_filters is None:
            self.logcat_filters = []
        if self.network_interfaces is None:
            self.network_interfaces = []
        if self.fs_watch_paths is None:
            self.fs_watch_paths = [
                "/data/data/com.termux/files/home",
                "/sdcard/Download",
                "/sdcard/DCIM"
            ]

class MonitorModule(Enum):
    """Enumeration of all monitoring modules"""
    LOGCAT = "logcat"
    NETWORK = "network"
    PROCESS = "process"
    MEMORY = "memory"
    BATTERY = "battery"
    FILESYSTEM = "filesystem"
    SENSORS = "sensors"
    APPS = "apps"

class DatabaseManager:
    """Manages SQLite database for storing monitoring data"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables
        schemas = {
            'logcat_entries': '''
                CREATE TABLE IF NOT EXISTS logcat_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    level TEXT,
                    tag TEXT,
                    pid INTEGER,
                    message TEXT,
                    raw_entry TEXT
                )
            ''',
            'network_stats': '''
                CREATE TABLE IF NOT EXISTS network_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    interface TEXT,
                    bytes_sent INTEGER,
                    bytes_recv INTEGER,
                    packets_sent INTEGER,
                    packets_recv INTEGER,
                    errors_in INTEGER,
                    errors_out INTEGER
                )
            ''',
            'process_stats': '''
                CREATE TABLE IF NOT EXISTS process_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    pid INTEGER,
                    name TEXT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_rss INTEGER,
                    memory_vms INTEGER,
                    num_threads INTEGER,
                    status TEXT
                )
            ''',
            'memory_stats': '''
                CREATE TABLE IF NOT EXISTS memory_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    total INTEGER,
                    available INTEGER,
                    percent REAL,
                    used INTEGER,
                    free INTEGER,
                    swap_total INTEGER,
                    swap_used INTEGER,
                    swap_free INTEGER
                )
            ''',
            'battery_stats': '''
                CREATE TABLE IF NOT EXISTS battery_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    level INTEGER,
                    status TEXT,
                    temperature REAL,
                    voltage REAL,
                    technology TEXT,
                    health TEXT
                )
            ''',
            'filesystem_events': '''
                CREATE TABLE IF NOT EXISTS filesystem_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    event_type TEXT,
                    path TEXT,
                    size INTEGER,
                    permissions TEXT,
                    owner TEXT
                )
            ''',
            'app_events': '''
                CREATE TABLE IF NOT EXISTS app_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    package_name TEXT,
                    event_type TEXT,
                    component TEXT,
                    data TEXT
                )
            ''',
            'alerts': '''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    module TEXT,
                    severity TEXT,
                    message TEXT,
                    data TEXT
                )
            '''
        }
        
        for table_sql in schemas.values():
            self.conn.execute(table_sql)
        
        # Create indexes
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_logcat_timestamp ON logcat_entries(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_network_timestamp ON network_stats(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_process_timestamp ON process_stats(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_memory_timestamp ON memory_stats(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_battery_timestamp ON battery_stats(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_fs_timestamp ON filesystem_events(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_app_timestamp ON app_events(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)'
        ]
        
        for idx_sql in indexes:
            self.conn.execute(idx_sql)
        
        self.conn.commit()
    
    def insert_batch(self, table: str, data: List[Dict[str, Any]]):
        """Insert batch of records"""
        if not data:
            return
        
        columns = list(data[0].keys())
        placeholders = ','.join(['?' for _ in columns])
        query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
        
        values = [[row.get(col) for col in columns] for row in data]
        self.conn.executemany(query, values)
        self.conn.commit()
    
    def query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Execute query and return results"""
        cursor = self.conn.execute(query, params)
        return cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

class LogcatMonitor:
    """Monitors Android system logs via logcat"""
    
    def __init__(self, config: MonitorConfig, db: DatabaseManager):
        self.config = config
        self.db = db
        self.buffer = deque(maxlen=config.logcat_buffer_size)
        self.running = False
        self.thread = None
        self.process = None
        
        # Compile regex patterns for parsing
        self.log_pattern = re.compile(
            r'(\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})\s+'
            r'(\d+)\s+(\d+)\s+([VDIWEF])\s+'
            r'([^:]+):\s*(.*)'
        )
    
    def start(self):
        """Start logcat monitoring"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logging.info("Logcat monitor started")
    
    def stop(self):
        """Stop logcat monitoring"""
        self.running = False
        if self.process:
            self.process.terminate()
        if self.thread:
            self.thread.join()
        logging.info("Logcat monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        cmd = ['logcat', '-v', 'time']
        
        # Add filters if specified
        for filter_spec in self.config.logcat_filters:
            cmd.extend(['-s', filter_spec])
        
        # Add priority filter
        if self.config.logcat_priority != 'V':
            cmd.extend(['*:' + self.config.logcat_priority])
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            batch = []
            last_flush = time.time()
            
            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    break
                
                entry = self._parse_logcat_line(line.strip())
                if entry:
                    self.buffer.append(entry)
                    batch.append(entry)
                    
                    # Flush to database periodically
                    if len(batch) >= 100 or time.time() - last_flush > 5:
                        self.db.insert_batch('logcat_entries', batch)
                        batch = []
                        last_flush = time.time()
            
            # Final flush
            if batch:
                self.db.insert_batch('logcat_entries', batch)
                
        except Exception as e:
            logging.error(f"Logcat monitoring error: {e}")
        finally:
            if self.process:
                self.process.terminate()
    
    def _parse_logcat_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single logcat line"""
        match = self.log_pattern.match(line)
        if match:
            timestamp_str, pid, tid, level, tag, message = match.groups()
            
            # Convert timestamp
            now = datetime.now()
            time_parts = timestamp_str.split()
            date_parts = time_parts[0].split('-')
            time_str = time_parts[1]
            
            timestamp = datetime(
                now.year,
                int(date_parts[0]),
                int(date_parts[1]),
                *[int(x) for x in time_str.replace(':', ' ').replace('.', ' ').split()][:3]
            ).timestamp()
            
            return {
                'timestamp': timestamp,
                'level': level,
                'tag': tag,
                'pid': int(pid),
                'message': message,
                'raw_entry': line
            }
        return None
    
    def get_recent_logs(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries from buffer"""
        return list(self.buffer)[-count:]

class NetworkMonitor:
    """Monitors network activity and connections"""
    
    def __init__(self, config: MonitorConfig, db: DatabaseManager):
        self.config = config
        self.db = db
        self.running = False
        self.thread = None
        self.last_stats = {}
    
    def start(self):
        """Start network monitoring"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logging.info("Network monitor started")
    
    def stop(self):
        """Stop network monitoring"""
        self.running = False
        if self.thread:
            self.thread.join()
        logging.info("Network monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                stats = self._collect_network_stats()
                if stats:
                    self.db.insert_batch('network_stats', stats)
                    self._check_thresholds(stats)
                
                time.sleep(self.config.network_interval)
                
            except Exception as e:
                logging.error(f"Network monitoring error: {e}")
                time.sleep(self.config.network_interval)
    
    def _collect_network_stats(self) -> List[Dict[str, Any]]:
        """Collect network statistics"""
        stats = []
        timestamp = time.time()
        
        # Get network IO counters
        net_io = psutil.net_io_counters(pernic=True)
        
        interfaces = self.config.network_interfaces or list(net_io.keys())
        
        for iface in interfaces:
            if iface in net_io:
                counters = net_io[iface]
                stats.append({
                    'timestamp': timestamp,
                    'interface': iface,
                    'bytes_sent': counters.bytes_sent,
                    'bytes_recv': counters.bytes_recv,
                    'packets_sent': counters.packets_sent,
                    'packets_recv': counters.packets_recv,
                    'errors_in': counters.errin,
                    'errors_out': counters.errout
                })
        
        # Monitor active connections
        if self.config.network_capture_packets:
            self._monitor_connections()
        
        return stats
    
    def _monitor_connections(self):
        """Monitor active network connections"""
        try:
            connections = psutil.net_connections(kind='inet')
            
            # Group by process
            conn_by_process = defaultdict(list)
            for conn in connections:
                if conn.pid:
                    conn_by_process[conn.pid].append({
                        'laddr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        'raddr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        'status': conn.status,
                        'type': conn.type
                    })
            
            # Log connection data
            for pid, conns in conn_by_process.items():
                try:
                    proc = psutil.Process(pid)
                    logging.debug(f"Process {proc.name()} (PID: {pid}) has {len(conns)} connections")
                except:
                    pass
                    
        except Exception as e:
            logging.error(f"Connection monitoring error: {e}")
    
    def _check_thresholds(self, stats: List[Dict[str, Any]]):
        """Check network usage thresholds"""
        for stat in stats:
            iface = stat['interface']
            
            if iface in self.last_stats:
                # Calculate rate (bytes per second)
                time_diff = stat['timestamp'] - self.last_stats[iface]['timestamp']
                if time_diff > 0:
                    bytes_rate = (
                        (stat['bytes_sent'] - self.last_stats[iface]['bytes_sent']) +
                        (stat['bytes_recv'] - self.last_stats[iface]['bytes_recv'])
                    ) / time_diff
                    
                    # Convert to MB/s
                    mb_rate = bytes_rate / (1024 * 1024)
                    
                    if mb_rate > self.config.alert_network_threshold:
                        self._create_alert(
                            'HIGH_NETWORK_USAGE',
                            f"Network usage on {iface}: {mb_rate:.2f} MB/s",
                            {'interface': iface, 'rate_mbps': mb_rate}
                        )
            
            self.last_stats[iface] = stat
    
    def _create_alert(self, alert_type: str, message: str, data: Dict[str, Any]):
        """Create network alert"""
        alert = {
            'timestamp': time.time(),
            'module': 'network',
            'severity': 'WARNING',
            'message': message,
            'data': json.dumps(data)
        }
        self.db.insert_batch('alerts', [alert])

class ProcessMonitor:
    """Monitors running processes and resource usage"""
    
    def __init__(self, config: MonitorConfig, db: DatabaseManager):
        self.config = config
        self.db = db
        self.running = False
        self.thread = None
    
    def start(self):
        """Start process monitoring"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logging.info("Process monitor started")
    
    def stop(self):
        """Stop process monitoring"""
        self.running = False
        if self.thread:
            self.thread.join()
        logging.info("Process monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                stats = self._collect_process_stats()
                if stats:
                    self.db.insert_batch('process_stats', stats)
                    self._check_thresholds(stats)
                
                time.sleep(self.config.process_interval)
                
            except Exception as e:
                logging.error(f"Process monitoring error: {e}")
                time.sleep(self.config.process_interval)
    
    def _collect_process_stats(self) -> List[Dict[str, Any]]:
        """Collect process statistics"""
        stats = []
        timestamp = time.time()
        
        # Get all processes
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                pinfo['cpu_percent'] = proc.cpu_percent(interval=0.1)
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage and get top N
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        
        for proc_info in processes[:self.config.process_top_n]:
            try:
                proc = psutil.Process(proc_info['pid'])
                memory_info = proc.memory_info()
                
                stat = {
                    'timestamp': timestamp,
                    'pid': proc_info['pid'],
                    'name': proc_info['name'],
                    'cpu_percent': proc_info['cpu_percent'],
                    'memory_percent': proc_info['memory_percent'],
                    'memory_rss': memory_info.rss,
                    'memory_vms': memory_info.vms,
                    'status': proc.status()
                }
                
                if self.config.process_track_threads:
                    stat['num_threads'] = proc.num_threads()
                
                stats.append(stat)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return stats
    
    def _check_thresholds(self, stats: List[Dict[str, Any]]):
        """Check process resource thresholds"""
        for stat in stats:
            # Check CPU threshold
            if stat['cpu_percent'] > self.config.alert_cpu_threshold:
                self._create_alert(
                    'HIGH_CPU_USAGE',
                    f"Process {stat['name']} (PID: {stat['pid']}) using {stat['cpu_percent']:.1f}% CPU",
                    stat
                )
            
            # Check memory threshold
            if stat['memory_percent'] > self.config.alert_memory_threshold:
                self._create_alert(
                    'HIGH_MEMORY_USAGE',
                    f"Process {stat['name']} (PID: {stat['pid']}) using {stat['memory_percent']:.1f}% memory",
                    stat
                )
    
    def _create_alert(self, alert_type: str, message: str, data: Dict[str, Any]):
        """Create process alert"""
        alert = {
            'timestamp': time.time(),
            'module': 'process',
            'severity': 'WARNING',
            'message': message,
            'data': json.dumps(data)
        }
        self.db.insert_batch('alerts', [alert])

class MemoryMonitor:
    """Monitors system memory usage"""
    
    def __init__(self, config: MonitorConfig, db: DatabaseManager):
        self.config = config
        self.db = db
        self.running = False
        self.thread = None
    
    def start(self):
        """Start memory monitoring"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logging.info("Memory monitor started")
    
    def stop(self):
        """Stop memory monitoring"""
        self.running = False
        if self.thread:
            self.thread.join()
        logging.info("Memory monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                stats = self._collect_memory_stats()
                if stats:
                    self.db.insert_batch('memory_stats', [stats])
                    self._check_thresholds(stats)
                
                time.sleep(self.config.memory_interval)
                
            except Exception as e:
                logging.error(f"Memory monitoring error: {e}")
                time.sleep(self.config.memory_interval)
    
    def _collect_memory_stats(self) -> Dict[str, Any]:
        """Collect memory statistics"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        stats = {
            'timestamp': time.time(),
            'total': mem.total,
            'available': mem.available,
            'percent': mem.percent,
            'used': mem.used,
            'free': mem.free,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_free': swap.free
        }
        
        if self.config.memory_detailed:
            # Get additional memory info from /proc/meminfo
            try:
                meminfo = self._parse_meminfo()
                stats.update(meminfo)
            except Exception as e:
                logging.error(f"Error parsing meminfo: {e}")
        
        return stats
    
    def _parse_meminfo(self) -> Dict[str, int]:
        """Parse /proc/meminfo for detailed memory info"""
        meminfo = {}
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) == 2:
                        key = parts[0]
                        value = parts[1].strip().split()[0]
                        meminfo[f'meminfo_{key}'] = int(value) * 1024  # Convert KB to bytes
        except Exception as e:
            logging.error(f"Error reading meminfo: {e}")
        
        return meminfo
    
    def _check_thresholds(self, stats: Dict[str, Any]):
        """Check memory usage thresholds"""
        if stats['percent'] > self.config.alert_memory_threshold:
            self._create_alert(
                'HIGH_MEMORY_USAGE',
                f"System memory usage: {stats['percent']:.1f}%",
                stats
            )
    
    def _create_alert(self, alert_type: str, message: str, data: Dict[str, Any]):
        """Create memory alert"""
        alert = {
            'timestamp': time.time(),
            'module': 'memory',
            'severity': 'WARNING',
            'message': message,
            'data': json.dumps(data)
        }
        self.db.insert_batch('alerts', [alert])

class BatteryMonitor:
    """Monitors battery status and power usage"""
    
    def __init__(self, config: MonitorConfig, db: DatabaseManager):
        self.config = config
        self.db = db
        self.running = False
        self.thread = None
    
    def start(self):
        """Start battery monitoring"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logging.info("Battery monitor started")
    
    def stop(self):
        """Stop battery monitoring"""
        self.running = False
        if self.thread:
            self.thread.join()
        logging.info("Battery monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                stats = self._collect_battery_stats()
                if stats:
                    self.db.insert_batch('battery_stats', [stats])
                    self._check_thresholds(stats)
                
                time.sleep(self.config.battery_interval)
                
            except Exception as e:
                logging.error(f"Battery monitoring error: {e}")
                time.sleep(self.config.battery_interval)
    
    def _collect_battery_stats(self) -> Dict[str, Any]:
        """Collect battery statistics"""
        stats = {'timestamp': time.time()}
        
        try:
            # Try to get battery info from dumpsys
            result = subprocess.run(
                ['dumpsys', 'battery'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Parse battery information
                for line in output.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'level':
                            stats['level'] = int(value)
                        elif key == 'status':
                            stats['status'] = value
                        elif key == 'temperature':
                            stats['temperature'] = int(value) / 10.0  # Convert to Celsius
                        elif key == 'voltage':
                            stats['voltage'] = int(value) / 1000.0  # Convert to Volts
                        elif key == 'technology':
                            stats['technology'] = value
                        elif key == 'health':
                            stats['health'] = value
            
            # Try psutil as fallback
            if 'level' not in stats:
                battery = psutil.sensors_battery()
                if battery:
                    stats['level'] = battery.percent
                    stats['status'] = 'Charging' if battery.power_plugged else 'Discharging'
        
        except Exception as e:
            logging.error(f"Error collecting battery stats: {e}")
        
        return stats
    
    def _check_thresholds(self, stats: Dict[str, Any]):
        """Check battery thresholds"""
        if 'level' in stats and stats['level'] < self.config.alert_battery_threshold:
            self._create_alert(
                'LOW_BATTERY',
                f"Battery level: {stats['level']}%",
                stats
            )
    
    def _create_alert(self, alert_type: str, message: str, data: Dict[str, Any]):
        """Create battery alert"""
        alert = {
            'timestamp': time.time(),
            'module': 'battery',
            'severity': 'WARNING',
            'message': message,
            'data': json.dumps(data)
        }
        self.db.insert_batch('alerts', [alert])

class FilesystemMonitor:
    """Monitors filesystem changes and activity"""
    
    def __init__(self, config: MonitorConfig, db: DatabaseManager):
        self.config = config
        self.db = db
        self.running = False
        self.thread = None
        self.file_stats = {}
    
    def start(self):
        """Start filesystem monitoring"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logging.info("Filesystem monitor started")
    
    def stop(self):
        """Stop filesystem monitoring"""
        self.running = False
        if self.thread:
            self.thread.join()
        logging.info("Filesystem monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        # Initial scan
        self._scan_directories()
        
        while self.running:
            try:
                events = self._detect_changes()
                if events:
                    self.db.insert_batch('filesystem_events', events)
                
                time.sleep(self.config.fs_interval)
                
            except Exception as e:
                logging.error(f"Filesystem monitoring error: {e}")
                time.sleep(self.config.fs_interval)
    
    def _scan_directories(self):
        """Scan monitored directories"""
        for watch_path in self.config.fs_watch_paths:
            if os.path.exists(watch_path):
                self._scan_path(watch_path)
    
    def _scan_path(self, path: str):
        """Recursively scan a path"""
        try:
            if os.path.isfile(path):
                stat = os.stat(path)
                self.file_stats[path] = {
                    'size': stat.st_size,
                    'mtime': stat.st_mtime,
                    'permissions': oct(stat.st_mode)[-3:],
                    'owner': stat.st_uid
                }
            elif os.path.isdir(path) and self.config.fs_recursive:
                for root, dirs, files in os.walk(path):
                    for name in files + dirs:
                        full_path = os.path.join(root, name)
                        try:
                            stat = os.stat(full_path)
                            self.file_stats[full_path] = {
                                'size': stat.st_size,
                                'mtime': stat.st_mtime,
                                'permissions': oct(stat.st_mode)[-3:],
                                'owner': stat.st_uid
                            }
                        except:
                            pass
        except Exception as e:
            logging.error(f"Error scanning path {path}: {e}")
    
    def _detect_changes(self) -> List[Dict[str, Any]]:
        """Detect filesystem changes"""
        events = []
        timestamp = time.time()
        current_stats = {}
        
        # Rescan directories
        for watch_path in self.config.fs_watch_paths:
            if os.path.exists(watch_path):
                self._scan_current_path(watch_path, current_stats)
        
        # Compare with previous scan
        # New files
        for path in current_stats:
            if path not in self.file_stats:
                events.append({
                    'timestamp': timestamp,
                    'event_type': 'created',
                    'path': path,
                    'size': current_stats[path]['size'],
                    'permissions': current_stats[path]['permissions'],
                    'owner': str(current_stats[path]['owner'])
                })
        
        # Modified files
        for path in current_stats:
            if path in self.file_stats:
                old_stat = self.file_stats[path]
                new_stat = current_stats[path]
                
                if old_stat['mtime'] != new_stat['mtime']:
                    events.append({
                        'timestamp': timestamp,
                        'event_type': 'modified',
                        'path': path,
                        'size': new_stat['size'],
                        'permissions': new_stat['permissions'],
                        'owner': str(new_stat['owner'])
                    })
        
        # Deleted files
        for path in self.file_stats:
            if path not in current_stats:
                events.append({
                    'timestamp': timestamp,
                    'event_type': 'deleted',
                    'path': path,
                    'size': 0,
                    'permissions': '',
                    'owner': ''
                })
        
        # Update file stats
        self.file_stats = current_stats
        
        return events
    
    def _scan_current_path(self, path: str, current_stats: Dict[str, Dict]):
        """Scan path and update current stats"""
        try:
            if os.path.isfile(path):
                stat = os.stat(path)
                current_stats[path] = {
                    'size': stat.st_size,
                    'mtime': stat.st_mtime,
                    'permissions': oct(stat.st_mode)[-3:],
                    'owner': stat.st_uid
                }
            elif os.path.isdir(path) and self.config.fs_recursive:
                for root, dirs, files in os.walk(path):
                    for name in files + dirs:
                        full_path = os.path.join(root, name)
                        try:
                            stat = os.stat(full_path)
                            current_stats[full_path] = {
                                'size': stat.st_size,
                                'mtime': stat.st_mtime,
                                'permissions': oct(stat.st_mode)[-3:],
                                'owner': stat.st_uid
                            }
                        except:
                            pass
        except Exception as e:
            logging.error(f"Error scanning current path {path}: {e}")

class AppMonitor:
    """Monitors app activity and events"""
    
    def __init__(self, config: MonitorConfig, db: DatabaseManager):
        self.config = config
        self.db = db
        self.running = False
        self.thread = None
    
    def start(self):
        """Start app monitoring"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        logging.info("App monitor started")
    
    def stop(self):
        """Stop app monitoring"""
        self.running = False
        if self.thread:
            self.thread.join()
        logging.info("App monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        # Monitor through logcat with ActivityManager filter
        cmd = ['logcat', '-v', 'time', 'ActivityManager:I', '*:S']
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            batch = []
            last_flush = time.time()
            
            for line in iter(process.stdout.readline, ''):
                if not self.running:
                    break
                
                event = self._parse_app_event(line.strip())
                if event:
                    batch.append(event)
                    
                    # Flush to database periodically
                    if len(batch) >= 50 or time.time() - last_flush > 5:
                        self.db.insert_batch('app_events', batch)
                        batch = []
                        last_flush = time.time()
            
            # Final flush
            if batch:
                self.db.insert_batch('app_events', batch)
                
        except Exception as e:
            logging.error(f"App monitoring error: {e}")
        finally:
            if process:
                process.terminate()
    
    def _parse_app_event(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse app event from logcat line"""
        timestamp = time.time()
        
        # Common patterns
        patterns = {
            'start_activity': r'START.*cmp=([^/]+)/([^\s]+)',
            'displayed': r'Displayed ([^:]+): \+(\d+)ms',
            'force_stop': r'Force stopping ([^\s]+)',
            'crash': r'Process ([^\s]+).*has crashed',
            'anr': r'ANR in ([^\s]+)'
        }
        
        for event_type, pattern in patterns.items():
            match = re.search(pattern, line)
            if match:
                if event_type == 'start_activity':
                    return {
                        'timestamp': timestamp,
                        'package_name': match.group(1),
                        'event_type': 'start_activity',
                        'component': match.group(2),
                        'data': line
                    }
                elif event_type == 'displayed':
                    return {
                        'timestamp': timestamp,
                        'package_name': match.group(1).split('/')[0],
                        'event_type': 'activity_displayed',
                        'component': match.group(1),
                        'data': f"Launch time: {match.group(2)}ms"
                    }
                elif event_type in ['force_stop', 'crash', 'anr']:
                    return {
                        'timestamp': timestamp,
                        'package_name': match.group(1),
                        'event_type': event_type,
                        'component': '',
                        'data': line
                    }
        
        return None

class AndroidMonitor:
    """Main monitoring orchestrator"""
    
    def __init__(self, config_path: Optional[str] = None):
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Setup output directory
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize database
        db_path = os.path.join(self.config.output_dir, self.config.db_path)
        self.db = DatabaseManager(db_path)
        
        # Initialize monitors
        self.monitors = {}
        self._init_monitors()
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self, config_path: Optional[str]) -> MonitorConfig:
        """Load configuration from file or defaults"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    config_dict = yaml.safe_load(f)
                else:
                    config_dict = json.load(f)
                return MonitorConfig(**config_dict)
        return MonitorConfig()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.join(self.config.output_dir, 'monitor.log')
        
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _init_monitors(self):
        """Initialize monitoring modules"""
        if self.config.enable_logcat:
            self.monitors[MonitorModule.LOGCAT] = LogcatMonitor(self.config, self.db)
        
        if self.config.enable_network:
            self.monitors[MonitorModule.NETWORK] = NetworkMonitor(self.config, self.db)
        
        if self.config.enable_process:
            self.monitors[MonitorModule.PROCESS] = ProcessMonitor(self.config, self.db)
        
        if self.config.enable_memory:
            self.monitors[MonitorModule.MEMORY] = MemoryMonitor(self.config, self.db)
        
        if self.config.enable_battery:
            self.monitors[MonitorModule.BATTERY] = BatteryMonitor(self.config, self.db)
        
        if self.config.enable_filesystem:
            self.monitors[MonitorModule.FILESYSTEM] = FilesystemMonitor(self.config, self.db)
        
        if self.config.enable_apps:
            self.monitors[MonitorModule.APPS] = AppMonitor(self.config, self.db)
    
    def start(self):
        """Start all monitors"""
        logging.info("Starting Android Monitor...")
        
        for module, monitor in self.monitors.items():
            try:
                monitor.start()
                logging.info(f"Started {module.value} monitor")
            except Exception as e:
                logging.error(f"Failed to start {module.value} monitor: {e}")
    
    def stop(self):
        """Stop all monitors"""
        logging.info("Stopping Android Monitor...")
        
        for module, monitor in self.monitors.items():
            try:
                monitor.stop()
                logging.info(f"Stopped {module.value} monitor")
            except Exception as e:
                logging.error(f"Failed to stop {module.value} monitor: {e}")
        
        # Close database
        self.db.close()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logging.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def run(self):
        """Run the monitor"""
        self.start()
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Android Activity Monitor for Termux",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file (JSON or YAML)',
        default=None
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        help='Output directory for logs and database',
        default='/data/data/com.termux/files/home/android_monitor'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    # Module toggles
    parser.add_argument('--disable-logcat', action='store_true', help='Disable logcat monitoring')
    parser.add_argument('--disable-network', action='store_true', help='Disable network monitoring')
    parser.add_argument('--disable-process', action='store_true', help='Disable process monitoring')
    parser.add_argument('--disable-memory', action='store_true', help='Disable memory monitoring')
    parser.add_argument('--disable-battery', action='store_true', help='Disable battery monitoring')
    parser.add_argument('--disable-filesystem', action='store_true', help='Disable filesystem monitoring')
    parser.add_argument('--disable-apps', action='store_true', help='Disable app monitoring')
    
    # Quick presets
    parser.add_argument(
        '--preset',
        choices=['minimal', 'standard', 'full', 'performance', 'security'],
        help='Use a preset configuration'
    )
    
    args = parser.parse_args()
    
    # Create config
    config = MonitorConfig()
    
    # Apply command line overrides
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.log_level:
        config.log_level = args.log_level
    
    # Apply disable flags
    if args.disable_logcat:
        config.enable_logcat = False
    if args.disable_network:
        config.enable_network = False
    if args.disable_process:
        config.enable_process = False
    if args.disable_memory:
        config.enable_memory = False
    if args.disable_battery:
        config.enable_battery = False
    if args.disable_filesystem:
        config.enable_filesystem = False
    if args.disable_apps:
        config.enable_apps = False
    
    # Apply presets
    if args.preset == 'minimal':
        config.enable_logcat = False
        config.enable_sensors = False
        config.enable_filesystem = False
        config.process_interval = 30
        config.network_interval = 30
        config.memory_interval = 60
    elif args.preset == 'performance':
        config.enable_sensors = False
        config.enable_filesystem = False
        config.process_top_n = 50
        config.process_interval = 5
        config.memory_detailed = True
    elif args.preset == 'security':
        config.enable_sensors = False
        config.logcat_filters = ['AuthService:*', 'PackageManager:*', 'ActivityManager:*']
        config.network_capture_packets = True
        config.fs_recursive = True
    
    # Load config file if provided
    if args.config:
        config = AndroidMonitor(args.config).config
    
    # Create and run monitor
    monitor = AndroidMonitor()
    monitor.config = config
    monitor.run()

if __name__ == '__main__':
    main()
