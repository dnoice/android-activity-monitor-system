#!/usr/bin/env python3
"""
Android Monitor Query Tool
Interactive tool for querying and analyzing collected monitoring data
"""

import os
import sys
import json
import sqlite3
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
import numpy as np
from collections import defaultdict

class MonitorQuery:
    """Query interface for monitor database"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def get_time_range(self) -> Tuple[datetime, datetime]:
        """Get the time range of data in database"""
        query = """
        SELECT 
            MIN(timestamp) as start_time,
            MAX(timestamp) as end_time
        FROM (
            SELECT MIN(timestamp) as timestamp FROM logcat_entries
            UNION ALL
            SELECT MIN(timestamp) FROM network_stats
            UNION ALL
            SELECT MIN(timestamp) FROM process_stats
            UNION ALL
            SELECT MIN(timestamp) FROM memory_stats
            UNION ALL
            SELECT MIN(timestamp) FROM battery_stats
            UNION ALL
            SELECT MIN(timestamp) FROM filesystem_events
            UNION ALL
            SELECT MIN(timestamp) FROM app_events
        )
        """
        
        result = self.conn.execute(query).fetchone()
        if result and result['start_time']:
            return (
                datetime.fromtimestamp(result['start_time']),
                datetime.fromtimestamp(result['end_time'])
            )
        return None, None
    
    def query_logcat(self, 
                     start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None,
                     level: Optional[str] = None,
                     tag: Optional[str] = None,
                     search: Optional[str] = None,
                     limit: int = 100) -> pd.DataFrame:
        """Query logcat entries"""
        conditions = []
        params = []
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.timestamp())
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.timestamp())
        
        if level:
            conditions.append("level = ?")
            params.append(level)
        
        if tag:
            conditions.append("tag LIKE ?")
            params.append(f"%{tag}%")
        
        if search:
            conditions.append("message LIKE ?")
            params.append(f"%{search}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT * FROM logcat_entries
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT {limit}
        """
        
        return pd.read_sql_query(query, self.conn, params=params)
    
    def query_network_stats(self,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           interface: Optional[str] = None) -> pd.DataFrame:
        """Query network statistics"""
        conditions = []
        params = []
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.timestamp())
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.timestamp())
        
        if interface:
            conditions.append("interface = ?")
            params.append(interface)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT * FROM network_stats
        WHERE {where_clause}
        ORDER BY timestamp
        """
        
        return pd.read_sql_query(query, self.conn, params=params)
    
    def query_process_stats(self,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           process_name: Optional[str] = None,
                           min_cpu: Optional[float] = None) -> pd.DataFrame:
        """Query process statistics"""
        conditions = []
        params = []
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.timestamp())
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.timestamp())
        
        if process_name:
            conditions.append("name LIKE ?")
            params.append(f"%{process_name}%")
        
        if min_cpu is not None:
            conditions.append("cpu_percent >= ?")
            params.append(min_cpu)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT * FROM process_stats
        WHERE {where_clause}
        ORDER BY timestamp
        """
        
        return pd.read_sql_query(query, self.conn, params=params)
    
    def query_memory_stats(self,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> pd.DataFrame:
        """Query memory statistics"""
        conditions = []
        params = []
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.timestamp())
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.timestamp())
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT * FROM memory_stats
        WHERE {where_clause}
        ORDER BY timestamp
        """
        
        return pd.read_sql_query(query, self.conn, params=params)
    
    def query_battery_stats(self,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> pd.DataFrame:
        """Query battery statistics"""
        conditions = []
        params = []
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.timestamp())
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.timestamp())
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT * FROM battery_stats
        WHERE {where_clause}
        ORDER BY timestamp
        """
        
        return pd.read_sql_query(query, self.conn, params=params)
    
    def query_filesystem_events(self,
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None,
                               event_type: Optional[str] = None,
                               path_pattern: Optional[str] = None) -> pd.DataFrame:
        """Query filesystem events"""
        conditions = []
        params = []
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.timestamp())
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.timestamp())
        
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
        
        if path_pattern:
            conditions.append("path LIKE ?")
            params.append(f"%{path_pattern}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT * FROM filesystem_events
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT 1000
        """
        
        return pd.read_sql_query(query, self.conn, params=params)
    
    def query_app_events(self,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        package_name: Optional[str] = None,
                        event_type: Optional[str] = None) -> pd.DataFrame:
        """Query app events"""
        conditions = []
        params = []
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.timestamp())
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.timestamp())
        
        if package_name:
            conditions.append("package_name LIKE ?")
            params.append(f"%{package_name}%")
        
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT * FROM app_events
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT 1000
        """
        
        return pd.read_sql_query(query, self.conn, params=params)
    
    def query_alerts(self,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None,
                    module: Optional[str] = None,
                    severity: Optional[str] = None) -> pd.DataFrame:
        """Query alerts"""
        conditions = []
        params = []
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time.timestamp())
        
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time.timestamp())
        
        if module:
            conditions.append("module = ?")
            params.append(module)
        
        if severity:
            conditions.append("severity = ?")
            params.append(severity)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT * FROM alerts
        WHERE {where_clause}
        ORDER BY timestamp DESC
        """
        
        return pd.read_sql_query(query, self.conn, params=params)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        stats = {}
        
        # Record counts
        tables = [
            'logcat_entries', 'network_stats', 'process_stats',
            'memory_stats', 'battery_stats', 'filesystem_events',
            'app_events', 'alerts'
        ]
        
        for table in tables:
            count = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            stats[f'{table}_count'] = count
        
        # Time range
        start_time, end_time = self.get_time_range()
        if start_time:
            stats['start_time'] = start_time.isoformat()
            stats['end_time'] = end_time.isoformat()
            stats['duration_hours'] = (end_time - start_time).total_seconds() / 3600
        
        # Top processes by CPU
        query = """
        SELECT name, AVG(cpu_percent) as avg_cpu, COUNT(*) as samples
        FROM process_stats
        GROUP BY name
        ORDER BY avg_cpu DESC
        LIMIT 10
        """
        stats['top_cpu_processes'] = [dict(row) for row in self.conn.execute(query)]
        
        # Top apps by events
        query = """
        SELECT package_name, COUNT(*) as event_count
        FROM app_events
        GROUP BY package_name
        ORDER BY event_count DESC
        LIMIT 10
        """
        stats['top_apps'] = [dict(row) for row in self.conn.execute(query)]
        
        # Alert summary
        query = """
        SELECT module, severity, COUNT(*) as count
        FROM alerts
        GROUP BY module, severity
        ORDER BY count DESC
        """
        stats['alert_summary'] = [dict(row) for row in self.conn.execute(query)]
        
        return stats

class DataAnalyzer:
    """Advanced data analysis functions"""
    
    def __init__(self, query: MonitorQuery):
        self.query = query
        
    def analyze_network_usage(self, start_time: Optional[datetime] = None,
                             end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze network usage patterns"""
        df = self.query.query_network_stats(start_time, end_time)
        
        if df.empty:
            return {}
        
        analysis = {}
        
        # Convert timestamps
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Calculate rates for each interface
        for interface in df['interface'].unique():
            iface_df = df[df['interface'] == interface].copy()
            iface_df = iface_df.sort_values('timestamp')
            
            # Calculate byte rates
            iface_df['bytes_sent_rate'] = iface_df['bytes_sent'].diff() / iface_df['timestamp'].diff()
            iface_df['bytes_recv_rate'] = iface_df['bytes_recv'].diff() / iface_df['timestamp'].diff()
            
            # Remove negative rates (counter resets)
            iface_df = iface_df[
                (iface_df['bytes_sent_rate'] >= 0) & 
                (iface_df['bytes_recv_rate'] >= 0)
            ]
            
            if not iface_df.empty:
                analysis[interface] = {
                    'total_sent_mb': iface_df['bytes_sent'].max() / (1024*1024),
                    'total_recv_mb': iface_df['bytes_recv'].max() / (1024*1024),
                    'avg_sent_rate_kbps': iface_df['bytes_sent_rate'].mean() * 8 / 1024,
                    'avg_recv_rate_kbps': iface_df['bytes_recv_rate'].mean() * 8 / 1024,
                    'max_sent_rate_kbps': iface_df['bytes_sent_rate'].max() * 8 / 1024,
                    'max_recv_rate_kbps': iface_df['bytes_recv_rate'].max() * 8 / 1024,
                    'total_errors': iface_df['errors_in'].max() + iface_df['errors_out'].max()
                }
        
        return analysis
    
    def analyze_process_behavior(self, process_name: str,
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze specific process behavior"""
        df = self.query.query_process_stats(start_time, end_time, process_name)
        
        if df.empty:
            return {}
        
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        analysis = {
            'process_name': process_name,
            'sample_count': len(df),
            'cpu_stats': {
                'mean': df['cpu_percent'].mean(),
                'std': df['cpu_percent'].std(),
                'min': df['cpu_percent'].min(),
                'max': df['cpu_percent'].max(),
                'percentile_95': df['cpu_percent'].quantile(0.95)
            },
            'memory_stats': {
                'mean_percent': df['memory_percent'].mean(),
                'max_percent': df['memory_percent'].max(),
                'mean_rss_mb': df['memory_rss'].mean() / (1024*1024),
                'max_rss_mb': df['memory_rss'].max() / (1024*1024)
            }
        }
        
        # Detect anomalies (values > 2 std from mean)
        cpu_mean = df['cpu_percent'].mean()
        cpu_std = df['cpu_percent'].std()
        anomalies = df[df['cpu_percent'] > cpu_mean + 2*cpu_std]
        
        if not anomalies.empty:
            analysis['anomalies'] = {
                'count': len(anomalies),
                'timestamps': anomalies['datetime'].tolist()
            }
        
        return analysis
    
    def analyze_memory_pressure(self, start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze memory pressure periods"""
        df = self.query.query_memory_stats(start_time, end_time)
        
        if df.empty:
            return {}
        
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Define pressure thresholds
        high_pressure = df[df['percent'] > 85]
        critical_pressure = df[df['percent'] > 95]
        
        analysis = {
            'average_usage_percent': df['percent'].mean(),
            'max_usage_percent': df['percent'].max(),
            'high_pressure_periods': len(high_pressure),
            'critical_pressure_periods': len(critical_pressure),
            'total_samples': len(df)
        }
        
        # Find continuous pressure periods
        if not high_pressure.empty:
            pressure_periods = []
            current_period = None
            
            for idx, row in high_pressure.iterrows():
                if current_period is None:
                    current_period = {
                        'start': row['datetime'],
                        'end': row['datetime'],
                        'max_percent': row['percent']
                    }
                elif (row['datetime'] - current_period['end']).seconds < 120:
                    current_period['end'] = row['datetime']
                    current_period['max_percent'] = max(current_period['max_percent'], row['percent'])
                else:
                    pressure_periods.append(current_period)
                    current_period = {
                        'start': row['datetime'],
                        'end': row['datetime'],
                        'max_percent': row['percent']
                    }
            
            if current_period:
                pressure_periods.append(current_period)
            
            analysis['pressure_periods'] = pressure_periods
        
        return analysis
    
    def analyze_battery_drain(self, start_time: Optional[datetime] = None,
                             end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze battery drain patterns"""
        df = self.query.query_battery_stats(start_time, end_time)
        
        if df.empty:
            return {}
        
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df.sort_values('timestamp')
        
        # Calculate drain rate
        df['drain_rate'] = -df['level'].diff() / (df['timestamp'].diff() / 3600)  # % per hour
        
        # Filter out charging periods and invalid rates
        drain_df = df[(df['status'] == 'Discharging') & (df['drain_rate'] > 0)]
        
        if drain_df.empty:
            return {'message': 'No discharge periods found'}
        
        analysis = {
            'average_drain_rate': drain_df['drain_rate'].mean(),
            'max_drain_rate': drain_df['drain_rate'].max(),
            'total_drain': df['level'].iloc[0] - df['level'].iloc[-1],
            'duration_hours': (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]) / 3600
        }
        
        # Identify high drain periods
        high_drain = drain_df[drain_df['drain_rate'] > drain_df['drain_rate'].mean() + drain_df['drain_rate'].std()]
        
        if not high_drain.empty:
            analysis['high_drain_periods'] = {
                'count': len(high_drain),
                'timestamps': high_drain['datetime'].tolist(),
                'rates': high_drain['drain_rate'].tolist()
            }
        
        return analysis
    
    def correlate_events(self, start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Correlate events across different monitors"""
        # Get alerts
        alerts = self.query.query_alerts(start_time, end_time)
        
        if alerts.empty:
            return {'message': 'No alerts found in the specified period'}
        
        correlations = []
        
        for _, alert in alerts.iterrows():
            alert_time = datetime.fromtimestamp(alert['timestamp'])
            window_start = alert_time - timedelta(minutes=5)
            window_end = alert_time + timedelta(minutes=5)
            
            correlation = {
                'alert': {
                    'time': alert_time,
                    'module': alert['module'],
                    'message': alert['message']
                },
                'related_events': {}
            }
            
            # Check for app events
            app_events = self.query.query_app_events(window_start, window_end)
            if not app_events.empty:
                correlation['related_events']['app_events'] = app_events.to_dict('records')
            
            # Check for filesystem events
            fs_events = self.query.query_filesystem_events(window_start, window_end)
            if not fs_events.empty:
                correlation['related_events']['filesystem_events'] = fs_events.to_dict('records')
            
            # Check for high CPU processes
            process_stats = self.query.query_process_stats(window_start, window_end, min_cpu=50)
            if not process_stats.empty:
                correlation['related_events']['high_cpu_processes'] = process_stats.to_dict('records')
            
            if correlation['related_events']:
                correlations.append(correlation)
        
        return {'correlations': correlations}

class Visualizer:
    """Data visualization functions"""
    
    def __init__(self, query: MonitorQuery):
        self.query = query
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def plot_network_usage(self, interface: Optional[str] = None,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None,
                          save_path: Optional[str] = None):
        """Plot network usage over time"""
        df = self.query.query_network_stats(start_time, end_time, interface)
        
        if df.empty:
            print("No network data to plot")
            return
        
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Calculate rates
        for iface in df['interface'].unique():
            mask = df['interface'] == iface
            df.loc[mask, 'bytes_sent_rate'] = df.loc[mask, 'bytes_sent'].diff() / df.loc[mask, 'timestamp'].diff()
            df.loc[mask, 'bytes_recv_rate'] = df.loc[mask, 'bytes_recv'].diff() / df.loc[mask, 'timestamp'].diff()
        
        # Convert to Mbps
        df['sent_mbps'] = df['bytes_sent_rate'] * 8 / (1024*1024)
        df['recv_mbps'] = df['bytes_recv_rate'] * 8 / (1024*1024)
        
        # Remove invalid values
        df = df[(df['sent_mbps'] >= 0) & (df['recv_mbps'] >= 0)]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        for iface in df['interface'].unique():
            iface_df = df[df['interface'] == iface]
            ax1.plot(iface_df['datetime'], iface_df['sent_mbps'], label=f'{iface} TX', alpha=0.7)
            ax2.plot(iface_df['datetime'], iface_df['recv_mbps'], label=f'{iface} RX', alpha=0.7)
        
        ax1.set_ylabel('Upload (Mbps)')
        ax1.legend()
        ax1.set_title('Network Upload Speed')
        
        ax2.set_ylabel('Download (Mbps)')
        ax2.set_xlabel('Time')
        ax2.legend()
        ax2.set_title('Network Download Speed')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_cpu_usage(self, top_n: int = 10,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None,
                      save_path: Optional[str] = None):
        """Plot CPU usage by top processes"""
        df = self.query.query_process_stats(start_time, end_time)
        
        if df.empty:
            print("No process data to plot")
            return
        
        # Get top N processes by average CPU
        top_processes = df.groupby('name')['cpu_percent'].mean().nlargest(top_n).index.tolist()
        
        df_filtered = df[df['name'].isin(top_processes)]
        df_filtered['datetime'] = pd.to_datetime(df_filtered['timestamp'], unit='s')
        
        plt.figure(figsize=(14, 8))
        
        for process in top_processes:
            process_df = df_filtered[df_filtered['name'] == process]
            plt.plot(process_df['datetime'], process_df['cpu_percent'], 
                    label=process[:30], alpha=0.7, linewidth=2)
        
        plt.xlabel('Time')
        plt.ylabel('CPU Usage (%)')
        plt.title(f'CPU Usage - Top {top_n} Processes')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_memory_usage(self, start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None,
                         save_path: Optional[str] = None):
        """Plot memory usage over time"""
        df = self.query.query_memory_stats(start_time, end_time)
        
        if df.empty:
            print("No memory data to plot")
            return
        
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # Memory percentage
        ax1.plot(df['datetime'], df['percent'], 'b-', linewidth=2)
        ax1.axhline(y=80, color='orange', linestyle='--', label='Warning (80%)')
        ax1.axhline(y=90, color='red', linestyle='--', label='Critical (90%)')
        ax1.set_ylabel('Memory Usage (%)')
        ax1.set_title('System Memory Usage')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Memory values in GB
        ax2.plot(df['datetime'], df['used']/(1024**3), label='Used', linewidth=2)
        ax2.plot(df['datetime'], df['available']/(1024**3), label='Available', linewidth=2)
        ax2.plot(df['datetime'], df['total']/(1024**3), label='Total', linewidth=1, linestyle='--')
        ax2.set_ylabel('Memory (GB)')
        ax2.set_xlabel('Time')
        ax2.set_title('Memory Distribution')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_battery_status(self, start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           save_path: Optional[str] = None):
        """Plot battery status over time"""
        df = self.query.query_battery_stats(start_time, end_time)
        
        if df.empty:
            print("No battery data to plot")
            return
        
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # Battery level
        ax1.plot(df['datetime'], df['level'], 'g-', linewidth=2)
        
        # Color by status
        charging = df[df['status'] == 'Charging']
        if not charging.empty:
            ax1.scatter(charging['datetime'], charging['level'], 
                       color='blue', s=30, alpha=0.5, label='Charging')
        
        ax1.axhline(y=20, color='red', linestyle='--', label='Low Battery (20%)')
        ax1.set_ylabel('Battery Level (%)')
        ax1.set_title('Battery Level')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 105)
        
        # Temperature
        if 'temperature' in df.columns:
            ax2.plot(df['datetime'], df['temperature'], 'r-', linewidth=2)
            ax2.axhline(y=40, color='orange', linestyle='--', label='Warning (40°C)')
            ax2.set_ylabel('Temperature (°C)')
            ax2.set_xlabel('Time')
            ax2.set_title('Battery Temperature')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_alert_timeline(self, start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           save_path: Optional[str] = None):
        """Plot timeline of alerts"""
        df = self.query.query_alerts(start_time, end_time)
        
        if df.empty:
            print("No alerts to plot")
            return
        
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Create a categorical y-axis for modules
        modules = df['module'].unique()
        module_positions = {module: i for i, module in enumerate(modules)}
        
        plt.figure(figsize=(14, 6))
        
        # Color map for severity
        severity_colors = {
            'INFO': 'blue',
            'WARNING': 'orange',
            'ERROR': 'red',
            'CRITICAL': 'darkred'
        }
        
        for _, alert in df.iterrows():
            y_pos = module_positions[alert['module']]
            color = severity_colors.get(alert['severity'], 'gray')
            plt.scatter(alert['datetime'], y_pos, c=color, s=100, alpha=0.7)
            
            # Add text annotation for important alerts
            if alert['severity'] in ['ERROR', 'CRITICAL']:
                plt.annotate(alert['message'][:50], 
                           (alert['datetime'], y_pos),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, alpha=0.7)
        
        plt.yticks(range(len(modules)), modules)
        plt.xlabel('Time')
        plt.ylabel('Module')
        plt.title('Alert Timeline')
        plt.grid(True, alpha=0.3, axis='x')
        
        # Add legend
        for severity, color in severity_colors.items():
            plt.scatter([], [], c=color, label=severity, s=100)
        plt.legend(title='Severity', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()

class InteractiveQuery:
    """Interactive query interface"""
    
    def __init__(self, db_path: str):
        self.query = MonitorQuery(db_path)
        self.analyzer = DataAnalyzer(self.query)
        self.visualizer = Visualizer(self.query)
    
    def run_interactive(self):
        """Run interactive query session"""
        print("\nAndroid Monitor Query Tool")
        print("=" * 50)
        
        # Show summary
        self.show_summary()
        
        while True:
            print("\nOptions:")
            print("1. Query logcat")
            print("2. Query network stats")
            print("3. Query process stats")
            print("4. Query memory stats")
            print("5. Query battery stats")
            print("6. Query filesystem events")
            print("7. Query app events")
            print("8. Query alerts")
            print("9. Analyze network usage")
            print("10. Analyze process behavior")
            print("11. Analyze memory pressure")
            print("12. Analyze battery drain")
            print("13. Correlate events")
            print("14. Visualize data")
            print("15. Export data")
            print("0. Exit")
            
            try:
                choice = input("\nSelect option: ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self.query_logcat_interactive()
                elif choice == '2':
                    self.query_network_interactive()
                elif choice == '3':
                    self.query_process_interactive()
                elif choice == '4':
                    self.query_memory_interactive()
                elif choice == '5':
                    self.query_battery_interactive()
                elif choice == '6':
                    self.query_filesystem_interactive()
                elif choice == '7':
                    self.query_app_interactive()
                elif choice == '8':
                    self.query_alerts_interactive()
                elif choice == '9':
                    self.analyze_network_interactive()
                elif choice == '10':
                    self.analyze_process_interactive()
                elif choice == '11':
                    self.analyze_memory_interactive()
                elif choice == '12':
                    self.analyze_battery_interactive()
                elif choice == '13':
                    self.correlate_events_interactive()
                elif choice == '14':
                    self.visualize_interactive()
                elif choice == '15':
                    self.export_interactive()
                else:
                    print("Invalid option")
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled")
            except Exception as e:
                print(f"Error: {e}")
    
    def show_summary(self):
        """Show database summary"""
        stats = self.query.get_summary_stats()
        
        print("\nDatabase Summary:")
        print("-" * 50)
        
        if 'start_time' in stats:
            print(f"Time range: {stats['start_time']} to {stats['end_time']}")
            print(f"Duration: {stats['duration_hours']:.2f} hours")
        
        print("\nRecord counts:")
        for key, value in stats.items():
            if key.endswith('_count'):
                table = key.replace('_count', '')
                print(f"  {table}: {value:,}")
        
        if 'top_cpu_processes' in stats and stats['top_cpu_processes']:
            print("\nTop CPU processes:")
            for proc in stats['top_cpu_processes'][:5]:
                print(f"  {proc['name']}: {proc['avg_cpu']:.1f}% avg")
        
        if 'alert_summary' in stats and stats['alert_summary']:
            print("\nAlert summary:")
            for alert in stats['alert_summary']:
                print(f"  {alert['module']} - {alert['severity']}: {alert['count']}")
    
    def query_logcat_interactive(self):
        """Interactive logcat query"""
        print("\nLogcat Query")
        print("-" * 30)
        
        level = input("Log level (V/D/I/W/E) [all]: ").strip().upper() or None
        tag = input("Tag filter [all]: ").strip() or None
        search = input("Search in message [all]: ").strip() or None
        limit = int(input("Limit [100]: ").strip() or 100)
        
        df = self.query.query_logcat(level=level, tag=tag, search=search, limit=limit)
        
        if df.empty:
            print("No results found")
        else:
            print(f"\nFound {len(df)} entries:")
            print(tabulate(df[['timestamp', 'level', 'tag', 'message']].head(20), 
                         headers='keys', tablefmt='grid'))
            
            if len(df) > 20:
                print(f"\n... and {len(df) - 20} more entries")
    
    def query_network_interactive(self):
        """Interactive network query"""
        print("\nNetwork Stats Query")
        print("-" * 30)
        
        interface = input("Interface [all]: ").strip() or None
        
        df = self.query.query_network_stats(interface=interface)
        
        if df.empty:
            print("No results found")
        else:
            # Show summary
            print(f"\nFound {len(df)} records")
            
            for iface in df['interface'].unique():
                iface_df = df[df['interface'] == iface]
                total_sent = iface_df['bytes_sent'].max() / (1024**3)
                total_recv = iface_df['bytes_recv'].max() / (1024**3)
                print(f"\n{iface}:")
                print(f"  Total sent: {total_sent:.2f} GB")
                print(f"  Total received: {total_recv:.2f} GB")
    
    def visualize_interactive(self):
        """Interactive visualization menu"""
        print("\nVisualization Options:")
        print("1. Network usage")
        print("2. CPU usage")
        print("3. Memory usage")
        print("4. Battery status")
        print("5. Alert timeline")
        
        choice = input("\nSelect visualization: ").strip()
        
        if choice == '1':
            interface = input("Interface [all]: ").strip() or None
            self.visualizer.plot_network_usage(interface=interface)
        elif choice == '2':
            top_n = int(input("Top N processes [10]: ").strip() or 10)
            self.visualizer.plot_cpu_usage(top_n=top_n)
        elif choice == '3':
            self.visualizer.plot_memory_usage()
        elif choice == '4':
            self.visualizer.plot_battery_status()
        elif choice == '5':
            self.visualizer.plot_alert_timeline()
    
    def export_interactive(self):
        """Interactive data export"""
        print("\nExport Options:")
        print("1. Export to CSV")
        print("2. Export to JSON")
        print("3. Generate HTML report")
        
        choice = input("\nSelect export format: ").strip()
        
        if choice == '1':
            self.export_csv()
        elif choice == '2':
            self.export_json()
        elif choice == '3':
            self.generate_html_report()
    
    def export_csv(self):
        """Export data to CSV files"""
        output_dir = input("Output directory [./export]: ").strip() or "./export"
        os.makedirs(output_dir, exist_ok=True)
        
        tables = [
            'logcat_entries', 'network_stats', 'process_stats',
            'memory_stats', 'battery_stats', 'filesystem_events',
            'app_events', 'alerts'
        ]
        
        for table in tables:
            df = pd.read_sql_query(f"SELECT * FROM {table}", self.query.conn)
            if not df.empty:
                output_file = os.path.join(output_dir, f"{table}.csv")
                df.to_csv(output_file, index=False)
                print(f"Exported {len(df)} records to {output_file}")
    
    def generate_html_report(self):
        """Generate comprehensive HTML report"""
        output_file = input("Output file [report.html]: ").strip() or "report.html"
        
        print("Generating report...")
        
        # Create temporary directory for plots
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate plots
            plots = []
            
            # Network usage
            plot_path = os.path.join(tmpdir, "network_usage.png")
            self.visualizer.plot_network_usage(save_path=plot_path)
            plots.append(("Network Usage", "network_usage.png"))
            
            # CPU usage
            plot_path = os.path.join(tmpdir, "cpu_usage.png")
            self.visualizer.plot_cpu_usage(save_path=plot_path)
            plots.append(("CPU Usage", "cpu_usage.png"))
            
            # Memory usage
            plot_path = os.path.join(tmpdir, "memory_usage.png")
            self.visualizer.plot_memory_usage(save_path=plot_path)
            plots.append(("Memory Usage", "memory_usage.png"))
            
            # Battery status
            plot_path = os.path.join(tmpdir, "battery_status.png")
            self.visualizer.plot_battery_status(save_path=plot_path)
            plots.append(("Battery Status", "battery_status.png"))
            
            # Alert timeline
            plot_path = os.path.join(tmpdir, "alert_timeline.png")
            self.visualizer.plot_alert_timeline(save_path=plot_path)
            plots.append(("Alert Timeline", "alert_timeline.png"))
            
            # Generate HTML
            self._generate_html_report(output_file, plots, tmpdir)
        
        print(f"Report generated: {output_file}")
    
    def _generate_html_report(self, output_file: str, plots: List[Tuple[str, str]], 
                             plot_dir: str):
        """Generate HTML report file"""
        import base64
        
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Android Monitor Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        h2 { color: #666; margin-top: 30px; }
        .summary { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .plot { margin: 20px 0; text-align: center; }
        .plot img { max-width: 100%; border: 1px solid #ddd; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .alert { background-color: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Android Monitor Report</h1>
"""
        
        # Add summary
        stats = self.query.get_summary_stats()
        
        html += '<div class="summary">'
        html += '<h2>Summary</h2>'
        
        if 'start_time' in stats:
            html += f"<p><strong>Monitoring Period:</strong> {stats['start_time']} to {stats['end_time']}</p>"
            html += f"<p><strong>Duration:</strong> {stats['duration_hours']:.2f} hours</p>"
        
        html += '<h3>Data Collection</h3>'
        html += '<table>'
        html += '<tr><th>Data Type</th><th>Record Count</th></tr>'
        
        for key, value in stats.items():
            if key.endswith('_count'):
                table = key.replace('_count', '').replace('_', ' ').title()
                html += f'<tr><td>{table}</td><td>{value:,}</td></tr>'
        
        html += '</table>'
        html += '</div>'
        
        # Add plots
        html += '<h2>Visualizations</h2>'
        
        for title, filename in plots:
            plot_path = os.path.join(plot_dir, filename)
            if os.path.exists(plot_path):
                with open(plot_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                
                html += f'<div class="plot">'
                html += f'<h3>{title}</h3>'
                html += f'<img src="data:image/png;base64,{img_data}" />'
                html += '</div>'
        
        # Add alerts
        alerts = self.query.query_alerts()
        if not alerts.empty:
            html += '<h2>Recent Alerts</h2>'
            
            for _, alert in alerts.head(20).iterrows():
                severity_class = 'alert' if alert['severity'] == 'WARNING' else 'alert error'
                html += f'<div class="{severity_class}">'
                html += f'<strong>{alert["module"]} - {alert["severity"]}</strong><br/>'
                html += f'{alert["message"]}<br/>'
                html += f'<small>{datetime.fromtimestamp(alert["timestamp"])}</small>'
                html += '</div>'
        
        html += """
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Android Monitor Query Tool")
    
    parser.add_argument(
        'db_path',
        nargs='?',
        default='/data/data/com.termux/files/home/android_monitor/monitor_data.db',
        help='Path to monitor database'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '-s', '--summary',
        action='store_true',
        help='Show database summary'
    )
    
    parser.add_argument(
        '-q', '--query',
        choices=['logcat', 'network', 'process', 'memory', 'battery', 'filesystem', 'apps', 'alerts'],
        help='Query specific data type'
    )
    
    parser.add_argument(
        '-a', '--analyze',
        choices=['network', 'process', 'memory', 'battery', 'correlate'],
        help='Run analysis'
    )
    
    parser.add_argument(
        '-v', '--visualize',
        choices=['network', 'cpu', 'memory', 'battery', 'alerts'],
        help='Generate visualization'
    )
    
    parser.add_argument(
        '-e', '--export',
        choices=['csv', 'json', 'html'],
        help='Export data'
    )
    
    parser.add_argument(
        '--start-time',
        help='Start time (YYYY-MM-DD HH:MM:SS)'
    )
    
    parser.add_argument(
        '--end-time',
        help='End time (YYYY-MM-DD HH:MM:SS)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file/directory'
    )
    
    args = parser.parse_args()
    
    # Parse time arguments
    start_time = None
    end_time = None
    
    if args.start_time:
        start_time = datetime.strptime(args.start_time, '%Y-%m-%d %H:%M:%S')
    if args.end_time:
        end_time = datetime.strptime(args.end_time, '%Y-%m-%d %H:%M:%S')
    
    # Create query interface
    if args.interactive:
        interface = InteractiveQuery(args.db_path)
        interface.run_interactive()
    else:
        query = MonitorQuery(args.db_path)
        analyzer = DataAnalyzer(query)
        visualizer = Visualizer(query)
        
        if args.summary:
            stats = query.get_summary_stats()
            print(json.dumps(stats, indent=2, default=str))
        
        elif args.query:
            if args.query == 'logcat':
                df = query.query_logcat(start_time, end_time)
            elif args.query == 'network':
                df = query.query_network_stats(start_time, end_time)
            elif args.query == 'process':
                df = query.query_process_stats(start_time, end_time)
            elif args.query == 'memory':
                df = query.query_memory_stats(start_time, end_time)
            elif args.query == 'battery':
                df = query.query_battery_stats(start_time, end_time)
            elif args.query == 'filesystem':
                df = query.query_filesystem_events(start_time, end_time)
            elif args.query == 'apps':
                df = query.query_app_events(start_time, end_time)
            elif args.query == 'alerts':
                df = query.query_alerts(start_time, end_time)
            
            print(df.to_string())
        
        elif args.analyze:
            if args.analyze == 'network':
                result = analyzer.analyze_network_usage(start_time, end_time)
            elif args.analyze == 'memory':
                result = analyzer.analyze_memory_pressure(start_time, end_time)
            elif args.analyze == 'battery':
                result = analyzer.analyze_battery_drain(start_time, end_time)
            elif args.analyze == 'correlate':
                result = analyzer.correlate_events(start_time, end_time)
            
            print(json.dumps(result, indent=2, default=str))
        
        elif args.visualize:
            if args.visualize == 'network':
                visualizer.plot_network_usage(start_time=start_time, 
                                            end_time=end_time,
                                            save_path=args.output)
            elif args.visualize == 'cpu':
                visualizer.plot_cpu_usage(start_time=start_time,
                                        end_time=end_time,
                                        save_path=args.output)
            elif args.visualize == 'memory':
                visualizer.plot_memory_usage(start_time=start_time,
                                           end_time=end_time,
                                           save_path=args.output)
            elif args.visualize == 'battery':
                visualizer.plot_battery_status(start_time=start_time,
                                             end_time=end_time,
                                             save_path=args.output)
            elif args.visualize == 'alerts':
                visualizer.plot_alert_timeline(start_time=start_time,
                                             end_time=end_time,
                                             save_path=args.output)

if __name__ == '__main__':
    main()
