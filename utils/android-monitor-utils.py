#!/usr/bin/env python3
"""
Android Monitor Utilities
Additional tools for monitoring system maintenance and advanced features
"""

import os
import sys
import json
import yaml
import sqlite3
import argparse
import subprocess
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from pathlib import Path
import hashlib
import zipfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class DatabaseOptimizer:
    """Database maintenance and optimization"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    def analyze_database(self) -> Dict[str, Any]:
        """Analyze database health and statistics"""
        stats = {}
        
        # Get database size
        stats['size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
        
        # Get table statistics
        tables = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        
        stats['tables'] = {}
        for table in tables:
            table_name = table[0]
            count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            
            # Get table size estimate
            page_count = self.conn.execute(
                f"SELECT COUNT(*) FROM dbstat WHERE name='{table_name}'"
            ).fetchone()[0] if 'dbstat' in [t[0] for t in tables] else 0
            
            stats['tables'][table_name] = {
                'row_count': count,
                'page_count': page_count
            }
        
        # Check fragmentation
        stats['fragmentation'] = self._check_fragmentation()
        
        # Get index statistics
        stats['indexes'] = self._get_index_stats()
        
        return stats
    
    def optimize(self, vacuum: bool = True, reindex: bool = True) -> Dict[str, Any]:
        """Optimize database performance"""
        results = {}
        
        initial_size = os.path.getsize(self.db_path) / (1024 * 1024)
        
        if reindex:
            print("Reindexing database...")
            self.conn.execute("REINDEX")
            results['reindex'] = 'completed'
        
        if vacuum:
            print("Vacuuming database...")
            self.conn.execute("VACUUM")
            results['vacuum'] = 'completed'
        
        # Analyze tables for query optimization
        print("Analyzing tables...")
        self.conn.execute("ANALYZE")
        results['analyze'] = 'completed'
        
        final_size = os.path.getsize(self.db_path) / (1024 * 1024)
        results['size_reduction_mb'] = initial_size - final_size
        results['size_reduction_percent'] = (
            (initial_size - final_size) / initial_size * 100 
            if initial_size > 0 else 0
        )
        
        return results
    
    def _check_fragmentation(self) -> float:
        """Check database fragmentation level"""
        try:
            page_count = self.conn.execute("PRAGMA page_count").fetchone()[0]
            freelist_count = self.conn.execute("PRAGMA freelist_count").fetchone()[0]
            
            if page_count > 0:
                return (freelist_count / page_count) * 100
            return 0.0
        except:
            return 0.0
    
    def _get_index_stats(self) -> List[Dict[str, Any]]:
        """Get index statistics"""
        indexes = []
        
        cursor = self.conn.execute(
            "SELECT name, tbl_name FROM sqlite_master WHERE type='index'"
        )
        
        for idx in cursor:
            indexes.append({
                'name': idx[0],
                'table': idx[1]
            })
        
        return indexes
    
    def archive_old_data(self, days_to_keep: int = 30, 
                        archive_path: Optional[str] = None) -> str:
        """Archive old data to separate database"""
        if not archive_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_path = f"{self.db_path}.archive_{timestamp}"
        
        # Create archive database
        archive_conn = sqlite3.connect(archive_path)
        
        # Copy schema
        schema = self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table'"
        ).fetchall()
        
        for table_sql in schema:
            if table_sql[0]:
                archive_conn.execute(table_sql[0])
        
        # Calculate cutoff timestamp
        cutoff = datetime.now() - timedelta(days=days_to_keep)
        cutoff_timestamp = cutoff.timestamp()
        
        # Archive data from each table
        tables = [
            'logcat_entries', 'network_stats', 'process_stats',
            'memory_stats', 'battery_stats', 'filesystem_events',
            'app_events', 'alerts'
        ]
        
        for table in tables:
            print(f"Archiving {table}...")
            
            # Copy old data to archive
            old_data = self.conn.execute(
                f"SELECT * FROM {table} WHERE timestamp < ?",
                (cutoff_timestamp,)
            ).fetchall()
            
            if old_data:
                columns = [desc[0] for desc in self.conn.execute(
                    f"SELECT * FROM {table} LIMIT 1"
                ).description]
                
                placeholders = ','.join(['?' for _ in columns])
                archive_conn.executemany(
                    f"INSERT INTO {table} VALUES ({placeholders})",
                    old_data
                )
                
                # Delete from main database
                self.conn.execute(
                    f"DELETE FROM {table} WHERE timestamp < ?",
                    (cutoff_timestamp,)
                )
        
        archive_conn.commit()
        archive_conn.close()
        
        self.conn.commit()
        
        # Compress archive
        zip_path = archive_path + '.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(archive_path, os.path.basename(archive_path))
        
        os.remove(archive_path)
        
        return zip_path

class AlertManager:
    """Advanced alert management and notifications"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.alert_history = []
    
    def setup_email_alerts(self, smtp_server: str, smtp_port: int,
                          email: str, password: str, recipients: List[str]):
        """Configure email alerts"""
        self.email_config = {
            'server': smtp_server,
            'port': smtp_port,
            'email': email,
            'password': password,
            'recipients': recipients
        }
    
    def send_alert(self, alert_type: str, message: str, 
                  data: Optional[Dict[str, Any]] = None):
        """Send alert via configured channels"""
        alert = {
            'timestamp': datetime.now(),
            'type': alert_type,
            'message': message,
            'data': data
        }
        
        self.alert_history.append(alert)
        
        # Console output
        print(f"[ALERT] {alert_type}: {message}")
        
        # Email notification
        if hasattr(self, 'email_config'):
            self._send_email_alert(alert)
        
        # Termux notification
        self._send_termux_notification(alert)
        
        # Custom webhook
        if 'webhook_url' in self.config:
            self._send_webhook(alert)
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = ', '.join(self.email_config['recipients'])
            msg['Subject'] = f"Android Monitor Alert: {alert['type']}"
            
            body = f"""
Android Monitor Alert

Type: {alert['type']}
Time: {alert['timestamp']}
Message: {alert['message']}

Data:
{json.dumps(alert['data'], indent=2) if alert['data'] else 'No additional data'}

---
This is an automated alert from Android Monitor
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(
                self.email_config['server'], 
                self.email_config['port']
            )
            server.starttls()
            server.login(
                self.email_config['email'], 
                self.email_config['password']
            )
            
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    def _send_termux_notification(self, alert: Dict[str, Any]):
        """Send Termux notification"""
        try:
            subprocess.run([
                'termux-notification',
                '-t', f"Monitor Alert: {alert['type']}",
                '-c', alert['message'],
                '--priority', 'high',
                '--vibrate', '500,500,500'
            ])
        except:
            pass
    
    def _send_webhook(self, alert: Dict[str, Any]):
        """Send webhook notification"""
        try:
            import requests
            
            payload = {
                'type': alert['type'],
                'message': alert['message'],
                'timestamp': alert['timestamp'].isoformat(),
                'data': alert['data']
            }
            
            requests.post(
                self.config['webhook_url'],
                json=payload,
                timeout=5
            )
        except:
            pass

class ReportGenerator:
    """Advanced report generation"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    def generate_executive_summary(self, 
                                  start_date: datetime,
                                  end_date: datetime) -> Dict[str, Any]:
        """Generate executive summary report"""
        summary = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'duration_hours': (end_date - start_date).total_seconds() / 3600
            }
        }
        
        # System health score
        summary['health_score'] = self._calculate_health_score(start_date, end_date)
        
        # Key metrics
        summary['metrics'] = self._get_key_metrics(start_date, end_date)
        
        # Top issues
        summary['top_issues'] = self._get_top_issues(start_date, end_date)
        
        # Recommendations
        summary['recommendations'] = self._generate_recommendations(summary)
        
        return summary
    
    def _calculate_health_score(self, start_date: datetime, 
                               end_date: datetime) -> float:
        """Calculate overall system health score (0-100)"""
        scores = []
        
        # CPU health
        cpu_data = pd.read_sql_query(
            """
            SELECT AVG(cpu_percent) as avg_cpu
            FROM (
                SELECT SUM(cpu_percent) as cpu_percent
                FROM process_stats
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY timestamp
            )
            """,
            self.conn,
            params=(start_date.timestamp(), end_date.timestamp())
        )
        
        if not cpu_data.empty:
            avg_cpu = cpu_data['avg_cpu'].iloc[0] or 0
            cpu_score = max(0, 100 - avg_cpu)
            scores.append(cpu_score)
        
        # Memory health
        mem_data = pd.read_sql_query(
            """
            SELECT AVG(percent) as avg_mem
            FROM memory_stats
            WHERE timestamp BETWEEN ? AND ?
            """,
            self.conn,
            params=(start_date.timestamp(), end_date.timestamp())
        )
        
        if not mem_data.empty:
            avg_mem = mem_data['avg_mem'].iloc[0] or 0
            mem_score = max(0, 100 - avg_mem)
            scores.append(mem_score)
        
        # Alert frequency (lower is better)
        alert_count = self.conn.execute(
            """
            SELECT COUNT(*) FROM alerts
            WHERE timestamp BETWEEN ? AND ?
            AND severity IN ('WARNING', 'ERROR', 'CRITICAL')
            """,
            (start_date.timestamp(), end_date.timestamp())
        ).fetchone()[0]
        
        hours = (end_date - start_date).total_seconds() / 3600
        alerts_per_hour = alert_count / hours if hours > 0 else 0
        alert_score = max(0, 100 - (alerts_per_hour * 10))
        scores.append(alert_score)
        
        # Calculate overall score
        return sum(scores) / len(scores) if scores else 50.0
    
    def _get_key_metrics(self, start_date: datetime, 
                        end_date: datetime) -> Dict[str, Any]:
        """Get key performance metrics"""
        metrics = {}
        
        # Average resource usage
        metrics['avg_cpu'] = self.conn.execute(
            """
            SELECT AVG(cpu_percent) FROM process_stats
            WHERE timestamp BETWEEN ? AND ?
            """,
            (start_date.timestamp(), end_date.timestamp())
        ).fetchone()[0] or 0
        
        metrics['avg_memory'] = self.conn.execute(
            """
            SELECT AVG(percent) FROM memory_stats
            WHERE timestamp BETWEEN ? AND ?
            """,
            (start_date.timestamp(), end_date.timestamp())
        ).fetchone()[0] or 0
        
        # Network usage
        net_data = pd.read_sql_query(
            """
            SELECT 
                MAX(bytes_sent) - MIN(bytes_sent) as total_sent,
                MAX(bytes_recv) - MIN(bytes_recv) as total_recv
            FROM network_stats
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY interface
            """,
            self.conn,
            params=(start_date.timestamp(), end_date.timestamp())
        )
        
        if not net_data.empty:
            metrics['total_network_gb'] = (
                net_data['total_sent'].sum() + net_data['total_recv'].sum()
            ) / (1024**3)
        else:
            metrics['total_network_gb'] = 0
        
        # Battery drain
        battery_data = pd.read_sql_query(
            """
            SELECT MIN(level) as min_level, MAX(level) as max_level
            FROM battery_stats
            WHERE timestamp BETWEEN ? AND ?
            AND status = 'Discharging'
            """,
            self.conn,
            params=(start_date.timestamp(), end_date.timestamp())
        )
        
        if not battery_data.empty and battery_data['max_level'].iloc[0]:
            metrics['battery_drain'] = (
                battery_data['max_level'].iloc[0] - 
                battery_data['min_level'].iloc[0]
            )
        else:
            metrics['battery_drain'] = 0
        
        return metrics
    
    def _get_top_issues(self, start_date: datetime, 
                       end_date: datetime) -> List[Dict[str, Any]]:
        """Get top system issues"""
        issues = []
        
        # High CPU processes
        cpu_issues = pd.read_sql_query(
            """
            SELECT name, COUNT(*) as occurrences, AVG(cpu_percent) as avg_cpu
            FROM process_stats
            WHERE timestamp BETWEEN ? AND ?
            AND cpu_percent > 50
            GROUP BY name
            ORDER BY occurrences DESC
            LIMIT 5
            """,
            self.conn,
            params=(start_date.timestamp(), end_date.timestamp())
        )
        
        for _, proc in cpu_issues.iterrows():
            issues.append({
                'type': 'high_cpu',
                'process': proc['name'],
                'severity': 'high' if proc['avg_cpu'] > 80 else 'medium',
                'occurrences': proc['occurrences'],
                'avg_cpu': proc['avg_cpu']
            })
        
        # Memory pressure events
        mem_pressure = self.conn.execute(
            """
            SELECT COUNT(*) FROM memory_stats
            WHERE timestamp BETWEEN ? AND ?
            AND percent > 85
            """,
            (start_date.timestamp(), end_date.timestamp())
        ).fetchone()[0]
        
        if mem_pressure > 0:
            issues.append({
                'type': 'memory_pressure',
                'severity': 'high',
                'occurrences': mem_pressure
            })
        
        # Critical alerts
        alerts = pd.read_sql_query(
            """
            SELECT module, message, COUNT(*) as count
            FROM alerts
            WHERE timestamp BETWEEN ? AND ?
            AND severity IN ('ERROR', 'CRITICAL')
            GROUP BY module, message
            ORDER BY count DESC
            LIMIT 5
            """,
            self.conn,
            params=(start_date.timestamp(), end_date.timestamp())
        )
        
        for _, alert in alerts.iterrows():
            issues.append({
                'type': 'alert',
                'module': alert['module'],
                'message': alert['message'],
                'severity': 'high',
                'occurrences': alert['count']
            })
        
        return issues
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Based on health score
        if summary['health_score'] < 50:
            recommendations.append(
                "System health is poor. Consider investigating resource usage and optimizing applications."
            )
        elif summary['health_score'] < 70:
            recommendations.append(
                "System health could be improved. Monitor resource-intensive applications."
            )
        
        # Based on metrics
        metrics = summary['metrics']
        
        if metrics['avg_cpu'] > 70:
            recommendations.append(
                f"High average CPU usage ({metrics['avg_cpu']:.1f}%). "
                "Consider closing unnecessary applications or upgrading hardware."
            )
        
        if metrics['avg_memory'] > 80:
            recommendations.append(
                f"High memory usage ({metrics['avg_memory']:.1f}%). "
                "Clear cache, close apps, or increase available RAM."
            )
        
        if metrics['battery_drain'] > 30:
            recommendations.append(
                f"Significant battery drain ({metrics['battery_drain']}%). "
                "Check for power-hungry apps and optimize battery settings."
            )
        
        # Based on issues
        for issue in summary['top_issues']:
            if issue['type'] == 'high_cpu' and issue['severity'] == 'high':
                recommendations.append(
                    f"Process '{issue['process']}' frequently uses high CPU. "
                    "Consider limiting its usage or finding alternatives."
                )
        
        return recommendations

class ConfigValidator:
    """Configuration validation and management"""
    
    @staticmethod
    def validate_config(config_path: str) -> Dict[str, Any]:
        """Validate configuration file"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Failed to load config: {e}")
            return results
        
        # Required fields
        required_fields = [
            'output_dir', 'db_path', 'log_level'
        ]
        
        for field in required_fields:
            if field not in config:
                results['valid'] = False
                results['errors'].append(f"Missing required field: {field}")
        
        # Validate paths
        if 'output_dir' in config:
            output_dir = config['output_dir']
            if not os.path.isabs(output_dir):
                results['warnings'].append(
                    f"output_dir is relative path: {output_dir}"
                )
        
        # Validate intervals
        interval_fields = [
            'network_interval', 'process_interval', 
            'memory_interval', 'battery_interval'
        ]
        
        for field in interval_fields:
            if field in config:
                value = config[field]
                if not isinstance(value, (int, float)) or value <= 0:
                    results['errors'].append(
                        f"{field} must be positive number, got: {value}"
                    )
                elif value < 1:
                    results['warnings'].append(
                        f"{field} is very small ({value}s), may impact performance"
                    )
        
        # Validate thresholds
        threshold_fields = [
            'alert_cpu_threshold', 'alert_memory_threshold',
            'alert_battery_threshold', 'alert_network_threshold'
        ]
        
        for field in threshold_fields:
            if field in config:
                value = config[field]
                if not isinstance(value, (int, float)):
                    results['errors'].append(
                        f"{field} must be numeric, got: {value}"
                    )
                elif field != 'alert_network_threshold' and (value < 0 or value > 100):
                    results['errors'].append(
                        f"{field} must be between 0-100, got: {value}"
                    )
        
        # Module dependencies
        if config.get('enable_apps') and not config.get('enable_logcat'):
            results['warnings'].append(
                "App monitoring works better with logcat enabled"
            )
        
        return results
    
    @staticmethod
    def merge_configs(base_config: str, override_config: str) -> Dict[str, Any]:
        """Merge two configuration files"""
        with open(base_config, 'r') as f:
            base = yaml.safe_load(f)
        
        with open(override_config, 'r') as f:
            override = yaml.safe_load(f)
        
        # Deep merge
        def deep_merge(base_dict, override_dict):
            for key, value in override_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_merge(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        merged = base.copy()
        deep_merge(merged, override)
        
        return merged

class SystemDiagnostics:
    """System diagnostics and troubleshooting"""
    
    @staticmethod
    def run_diagnostics() -> Dict[str, Any]:
        """Run comprehensive system diagnostics"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'environment': {},
            'permissions': {},
            'resources': {},
            'connectivity': {}
        }
        
        # Environment checks
        results['environment']['termux'] = os.path.exists('/data/data/com.termux')
        results['environment']['python_version'] = sys.version
        results['environment']['platform'] = sys.platform
        
        # Check required commands
        commands = ['logcat', 'dumpsys', 'sqlite3']
        for cmd in commands:
            results['environment'][f'cmd_{cmd}'] = shutil.which(cmd) is not None
        
        # Permission checks
        test_paths = [
            '/data/data/com.termux/files/home',
            '/sdcard',
            '/proc/stat',
            '/proc/meminfo'
        ]
        
        for path in test_paths:
            results['permissions'][path] = {
                'exists': os.path.exists(path),
                'readable': os.access(path, os.R_OK) if os.path.exists(path) else False,
                'writable': os.access(path, os.W_OK) if os.path.exists(path) else False
            }
        
        # Resource availability
        import psutil
        
        results['resources']['cpu_count'] = psutil.cpu_count()
        results['resources']['memory_total_gb'] = psutil.virtual_memory().total / (1024**3)
        results['resources']['disk_usage_percent'] = psutil.disk_usage('/').percent
        
        # Test database creation
        try:
            test_db = '/tmp/test_monitor.db'
            conn = sqlite3.connect(test_db)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.close()
            os.remove(test_db)
            results['resources']['sqlite_ok'] = True
        except:
            results['resources']['sqlite_ok'] = False
        
        # Network connectivity
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            results['connectivity']['internet'] = True
        except:
            results['connectivity']['internet'] = False
        
        return results
    
    @staticmethod
    def check_dependencies() -> Dict[str, bool]:
        """Check all required dependencies"""
        dependencies = {
            'python_modules': [
                'psutil', 'pandas', 'numpy', 'matplotlib',
                'seaborn', 'yaml', 'requests', 'tabulate'
            ],
            'system_commands': [
                'logcat', 'dumpsys', 'sqlite3', 'ps', 'top'
            ],
            'optional_commands': [
                'termux-notification', 'termux-vibrate'
            ]
        }
        
        results = {}
        
        # Check Python modules
        for module in dependencies['python_modules']:
            try:
                __import__(module)
                results[f'python_{module}'] = True
            except ImportError:
                results[f'python_{module}'] = False
        
        # Check system commands
        for cmd in dependencies['system_commands']:
            results[f'cmd_{cmd}'] = shutil.which(cmd) is not None
        
        # Check optional commands
        for cmd in dependencies['optional_commands']:
            results[f'opt_{cmd}'] = shutil.which(cmd) is not None
        
        return results

def main():
    """Main utility entry point"""
    parser = argparse.ArgumentParser(
        description="Android Monitor Utilities",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Database optimization
    db_parser = subparsers.add_parser('optimize', help='Optimize database')
    db_parser.add_argument('database', help='Database path')
    db_parser.add_argument('--analyze', action='store_true', help='Analyze only')
    db_parser.add_argument('--archive', type=int, help='Archive data older than N days')
    
    # Configuration validation
    config_parser = subparsers.add_parser('validate', help='Validate configuration')
    config_parser.add_argument('config', help='Configuration file path')
    
    # Diagnostics
    diag_parser = subparsers.add_parser('diagnose', help='Run system diagnostics')
    diag_parser.add_argument('--check-deps', action='store_true', 
                           help='Check dependencies only')
    
    # Report generation
    report_parser = subparsers.add_parser('report', help='Generate executive report')
    report_parser.add_argument('database', help='Database path')
    report_parser.add_argument('--days', type=int, default=7, 
                             help='Number of days to analyze')
    report_parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    if args.command == 'optimize':
        optimizer = DatabaseOptimizer(args.database)
        
        if args.analyze:
            stats = optimizer.analyze_database()
            print(json.dumps(stats, indent=2))
        elif args.archive:
            archive_path = optimizer.archive_old_data(args.archive)
            print(f"Data archived to: {archive_path}")
            
            # Optimize after archiving
            results = optimizer.optimize()
            print(f"Optimization complete:")
            print(f"  Size reduction: {results['size_reduction_mb']:.2f} MB "
                  f"({results['size_reduction_percent']:.1f}%)")
        else:
            results = optimizer.optimize()
            print(f"Optimization complete:")
            print(f"  Size reduction: {results['size_reduction_mb']:.2f} MB "
                  f"({results['size_reduction_percent']:.1f}%)")
    
    elif args.command == 'validate':
        results = ConfigValidator.validate_config(args.config)
        
        print(f"Configuration {'valid' if results['valid'] else 'INVALID'}")
        
        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  ✗ {error}")
        
        if results['warnings']:
            print("\nWarnings:")
            for warning in results['warnings']:
                print(f"  ⚠ {warning}")
        
        if results['valid'] and not results['warnings']:
            print("\n✓ Configuration is valid with no issues")
        
        sys.exit(0 if results['valid'] else 1)
    
    elif args.command == 'diagnose':
        if args.check_deps:
            deps = SystemDiagnostics.check_dependencies()
            
            print("Dependency Check:")
            print("-" * 40)
            
            for dep, available in sorted(deps.items()):
                status = "✓" if available else "✗"
                print(f"{status} {dep}")
            
            missing = [d for d, v in deps.items() if not v and not d.startswith('opt_')]
            if missing:
                print(f"\nMissing required dependencies: {len(missing)}")
                sys.exit(1)
            else:
                print("\n✓ All required dependencies are available")
        else:
            results = SystemDiagnostics.run_diagnostics()
            print(json.dumps(results, indent=2))
    
    elif args.command == 'report':
        generator = ReportGenerator(args.database)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
        
        report = generator.generate_executive_summary(start_date, end_date)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"Report saved to: {args.output}")
        else:
            print(json.dumps(report, indent=2, default=str))
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
