#!/usr/bin/env python3
"""
Android Monitor Real-time Dashboard
Terminal-based dashboard for live monitoring
"""

import os
import sys
import time
import sqlite3
import curses
import threading
import argparse
from datetime import datetime, timedelta
from collections import deque, defaultdict
import psutil
import subprocess
from typing import Dict, List, Tuple, Optional, Any

class DashboardData:
    """Container for dashboard data"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Data buffers
        self.cpu_history = deque(maxlen=60)
        self.memory_history = deque(maxlen=60)
        self.network_history = deque(maxlen=60)
        self.battery_history = deque(maxlen=30)
        self.recent_alerts = deque(maxlen=10)
        self.recent_logs = deque(maxlen=20)
        self.recent_apps = deque(maxlen=10)
        self.top_processes = []
        
        # Current stats
        self.current_cpu = 0.0
        self.current_memory = 0.0
        self.current_battery = 0
        self.current_network_rate = 0.0
        self.network_interfaces = {}
        
        # Update lock
        self.lock = threading.Lock()
    
    def update_realtime_stats(self):
        """Update real-time statistics"""
        try:
            # CPU usage
            self.current_cpu = psutil.cpu_percent(interval=1)
            self.cpu_history.append(self.current_cpu)
            
            # Memory usage
            mem = psutil.virtual_memory()
            self.current_memory = mem.percent
            self.memory_history.append(self.current_memory)
            
            # Network stats
            net_io = psutil.net_io_counters(pernic=True)
            total_rate = 0
            
            for iface, counters in net_io.items():
                if iface in self.network_interfaces:
                    old_counters = self.network_interfaces[iface]
                    bytes_diff = (
                        (counters.bytes_sent - old_counters.bytes_sent) +
                        (counters.bytes_recv - old_counters.bytes_recv)
                    )
                    total_rate += bytes_diff
                
                self.network_interfaces[iface] = counters
            
            self.current_network_rate = total_rate / (1024 * 1024)  # MB/s
            self.network_history.append(self.current_network_rate)
            
            # Top processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] > 0:
                        processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            self.top_processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
            
        except Exception as e:
            pass
    
    def update_from_database(self):
        """Update data from database"""
        try:
            # Recent alerts
            query = """
            SELECT * FROM alerts 
            ORDER BY timestamp DESC 
            LIMIT 10
            """
            alerts = self.conn.execute(query).fetchall()
            with self.lock:
                self.recent_alerts.clear()
                self.recent_alerts.extend([dict(a) for a in alerts])
            
            # Recent logs
            query = """
            SELECT * FROM logcat_entries 
            WHERE level IN ('W', 'E') 
            ORDER BY timestamp DESC 
            LIMIT 20
            """
            logs = self.conn.execute(query).fetchall()
            with self.lock:
                self.recent_logs.clear()
                self.recent_logs.extend([dict(l) for l in logs])
            
            # Recent app events
            query = """
            SELECT * FROM app_events 
            ORDER BY timestamp DESC 
            LIMIT 10
            """
            apps = self.conn.execute(query).fetchall()
            with self.lock:
                self.recent_apps.clear()
                self.recent_apps.extend([dict(a) for a in apps])
            
            # Battery status
            query = """
            SELECT * FROM battery_stats 
            ORDER BY timestamp DESC 
            LIMIT 1
            """
            battery = self.conn.execute(query).fetchone()
            if battery:
                self.current_battery = battery['level']
                
                # Get battery history
                query = """
                SELECT level, timestamp FROM battery_stats 
                ORDER BY timestamp DESC 
                LIMIT 30
                """
                history = self.conn.execute(query).fetchall()
                with self.lock:
                    self.battery_history.clear()
                    self.battery_history.extend([h['level'] for h in reversed(history)])
            
        except Exception as e:
            pass

class Dashboard:
    """Terminal dashboard UI"""
    
    def __init__(self, data: DashboardData):
        self.data = data
        self.stdscr = None
        self.running = True
        self.update_interval = 1.0
        self.view_mode = 'overview'  # overview, processes, network, logs, alerts
        
        # Window sections
        self.header_height = 3
        self.footer_height = 2
        
    def run(self):
        """Run the dashboard"""
        curses.wrapper(self._run)
    
    def _run(self, stdscr):
        """Main dashboard loop"""
        self.stdscr = stdscr
        
        # Setup
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Non-blocking input
        stdscr.timeout(100) # 100ms timeout for getch
        
        # Setup colors
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Normal
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Warning
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    # Critical
            curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Info
            curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Header
        
        # Start update thread
        update_thread = threading.Thread(target=self._update_loop)
        update_thread.daemon = True
        update_thread.start()
        
        # Main loop
        while self.running:
            try:
                # Handle input
                key = stdscr.getch()
                if key == ord('q'):
                    self.running = False
                elif key == ord('1'):
                    self.view_mode = 'overview'
                elif key == ord('2'):
                    self.view_mode = 'processes'
                elif key == ord('3'):
                    self.view_mode = 'network'
                elif key == ord('4'):
                    self.view_mode = 'logs'
                elif key == ord('5'):
                    self.view_mode = 'alerts'
                
                # Clear and redraw
                stdscr.clear()
                self._draw()
                stdscr.refresh()
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                pass
    
    def _update_loop(self):
        """Background update loop"""
        while self.running:
            self.data.update_realtime_stats()
            self.data.update_from_database()
            time.sleep(self.update_interval)
    
    def _draw(self):
        """Draw the dashboard"""
        height, width = self.stdscr.getmaxyx()
        
        # Draw header
        self._draw_header(width)
        
        # Draw content based on view mode
        content_start = self.header_height
        content_height = height - self.header_height - self.footer_height
        
        if self.view_mode == 'overview':
            self._draw_overview(content_start, content_height, width)
        elif self.view_mode == 'processes':
            self._draw_processes(content_start, content_height, width)
        elif self.view_mode == 'network':
            self._draw_network(content_start, content_height, width)
        elif self.view_mode == 'logs':
            self._draw_logs(content_start, content_height, width)
        elif self.view_mode == 'alerts':
            self._draw_alerts(content_start, content_height, width)
        
        # Draw footer
        self._draw_footer(height - self.footer_height, width)
    
    def _draw_header(self, width):
        """Draw header section"""
        # Title bar
        title = "Android Activity Monitor - Real-time Dashboard"
        self.stdscr.attron(curses.color_pair(5))
        self.stdscr.addstr(0, 0, " " * width)
        self.stdscr.addstr(0, (width - len(title)) // 2, title)
        self.stdscr.attroff(curses.color_pair(5))
        
        # Status line
        status_items = [
            f"CPU: {self.data.current_cpu:.1f}%",
            f"Mem: {self.data.current_memory:.1f}%",
            f"Net: {self.data.current_network_rate:.2f} MB/s",
            f"Bat: {self.data.current_battery}%"
        ]
        
        status_line = " | ".join(status_items)
        self.stdscr.addstr(1, (width - len(status_line)) // 2, status_line)
        
        # Separator
        self.stdscr.addstr(2, 0, "─" * width)
    
    def _draw_footer(self, y, width):
        """Draw footer section"""
        # Separator
        self.stdscr.addstr(y, 0, "─" * width)
        
        # Navigation
        nav_items = [
            "[1] Overview",
            "[2] Processes",
            "[3] Network",
            "[4] Logs",
            "[5] Alerts",
            "[q] Quit"
        ]
        
        nav_line = "  ".join(nav_items)
        self.stdscr.addstr(y + 1, (width - len(nav_line)) // 2, nav_line)
    
    def _draw_overview(self, y_start, height, width):
        """Draw overview screen"""
        y = y_start
        
        # Section: System Resources
        self._draw_section_header(y, "System Resources", width)
        y += 2
        
        # CPU graph
        self._draw_mini_graph(y, 2, "CPU", self.data.cpu_history, width // 2 - 2, 5)
        
        # Memory graph
        self._draw_mini_graph(y, width // 2 + 2, "Memory", self.data.memory_history, width // 2 - 2, 5)
        y += 6
        
        # Section: Top Processes
        self._draw_section_header(y, "Top Processes (by CPU)", width)
        y += 2
        
        for i, proc in enumerate(self.data.top_processes[:5]):
            if y >= y_start + height - 2:
                break
            
            line = f"{proc['name'][:30]:<30} CPU: {proc['cpu_percent']:>5.1f}% MEM: {proc['memory_percent']:>5.1f}%"
            color = curses.color_pair(1)
            if proc['cpu_percent'] > 50:
                color = curses.color_pair(2)
            if proc['cpu_percent'] > 80:
                color = curses.color_pair(3)
            
            self.stdscr.addstr(y, 2, line, color)
            y += 1
        
        y += 1
        
        # Section: Recent Alerts
        if y < y_start + height - 2:
            self._draw_section_header(y, "Recent Alerts", width)
            y += 2
            
            with self.data.lock:
                alerts = list(self.data.recent_alerts)[:3]
            
            for alert in alerts:
                if y >= y_start + height - 2:
                    break
                
                timestamp = datetime.fromtimestamp(alert['timestamp']).strftime('%H:%M:%S')
                line = f"{timestamp} [{alert['module']}] {alert['message'][:width-20]}"
                
                color = curses.color_pair(2) if alert['severity'] == 'WARNING' else curses.color_pair(3)
                self.stdscr.addstr(y, 2, line[:width-4], color)
                y += 1
    
    def _draw_processes(self, y_start, height, width):
        """Draw processes screen"""
        y = y_start
        
        # Header
        header = f"{'Process':<30} {'PID':>8} {'CPU %':>8} {'MEM %':>8} {'Status':<10}"
        self.stdscr.addstr(y, 2, header, curses.A_BOLD)
        y += 1
        self.stdscr.addstr(y, 2, "-" * (width - 4))
        y += 1
        
        # Process list
        for proc in self.data.top_processes:
            if y >= y_start + height - 1:
                break
            
            try:
                p = psutil.Process(proc['pid'])
                status = p.status()
            except:
                status = "unknown"
            
            line = f"{proc['name'][:30]:<30} {proc['pid']:>8} {proc['cpu_percent']:>8.1f} {proc['memory_percent']:>8.1f} {status:<10}"
            
            color = curses.color_pair(1)
            if proc['cpu_percent'] > 50:
                color = curses.color_pair(2)
            if proc['cpu_percent'] > 80:
                color = curses.color_pair(3)
            
            self.stdscr.addstr(y, 2, line[:width-4], color)
            y += 1
    
    def _draw_network(self, y_start, height, width):
        """Draw network screen"""
        y = y_start
        
        # Network graph
        self._draw_section_header(y, "Network Activity", width)
        y += 2
        
        self._draw_mini_graph(y, 2, "Network Rate (MB/s)", self.data.network_history, width - 4, 8)
        y += 10
        
        # Interface stats
        if y < y_start + height - 2:
            self._draw_section_header(y, "Interface Statistics", width)
            y += 2
            
            header = f"{'Interface':<15} {'Sent (MB)':>12} {'Recv (MB)':>12} {'Packets':>12}"
            self.stdscr.addstr(y, 2, header, curses.A_BOLD)
            y += 1
            
            for iface, counters in self.data.network_interfaces.items():
                if y >= y_start + height - 1:
                    break
                
                sent_mb = counters.bytes_sent / (1024 * 1024)
                recv_mb = counters.bytes_recv / (1024 * 1024)
                packets = counters.packets_sent + counters.packets_recv
                
                line = f"{iface[:15]:<15} {sent_mb:>12.2f} {recv_mb:>12.2f} {packets:>12,}"
                self.stdscr.addstr(y, 2, line[:width-4])
                y += 1
    
    def _draw_logs(self, y_start, height, width):
        """Draw logs screen"""
        y = y_start
        
        self._draw_section_header(y, "Recent Warning/Error Logs", width)
        y += 2
        
        with self.data.lock:
            logs = list(self.data.recent_logs)
        
        for log in logs:
            if y >= y_start + height - 1:
                break
            
            timestamp = datetime.fromtimestamp(log['timestamp']).strftime('%H:%M:%S')
            line = f"{timestamp} [{log['level']}] {log['tag']}: {log['message']}"
            
            color = curses.color_pair(2) if log['level'] == 'W' else curses.color_pair(3)
            self.stdscr.addstr(y, 2, line[:width-4], color)
            y += 1
    
    def _draw_alerts(self, y_start, height, width):
        """Draw alerts screen"""
        y = y_start
        
        self._draw_section_header(y, "System Alerts", width)
        y += 2
        
        with self.data.lock:
            alerts = list(self.data.recent_alerts)
        
        for alert in alerts:
            if y >= y_start + height - 2:
                break
            
            timestamp = datetime.fromtimestamp(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            
            # Alert header
            header = f"{timestamp} - {alert['module']} - {alert['severity']}"
            color = curses.color_pair(2) if alert['severity'] == 'WARNING' else curses.color_pair(3)
            self.stdscr.addstr(y, 2, header, color | curses.A_BOLD)
            y += 1
            
            # Alert message
            message = alert['message']
            # Word wrap if needed
            words = message.split()
            line = ""
            for word in words:
                if len(line) + len(word) + 1 > width - 6:
                    self.stdscr.addstr(y, 4, line[:width-6])
                    y += 1
                    line = word + " "
                    if y >= y_start + height - 2:
                        break
                else:
                    line += word + " "
            
            if line and y < y_start + height - 2:
                self.stdscr.addstr(y, 4, line[:width-6])
                y += 1
            
            y += 1  # Empty line between alerts
    
    def _draw_section_header(self, y, title, width):
        """Draw a section header"""
        self.stdscr.addstr(y, 2, f"[{title}]", curses.A_BOLD | curses.color_pair(4))
    
    def _draw_mini_graph(self, y, x, title, data, width, height):
        """Draw a mini ASCII graph"""
        # Title
        self.stdscr.addstr(y, x, title, curses.A_BOLD)
        
        if not data:
            self.stdscr.addstr(y + 1, x, "No data")
            return
        
        # Scale data to fit height
        data_list = list(data)
        if data_list:
            max_val = max(data_list) or 1
            min_val = min(data_list) or 0
            range_val = max_val - min_val or 1
            
            # Create graph
            for row in range(height):
                graph_y = y + height - row
                threshold = min_val + (range_val * (row + 1) / height)
                
                line = ""
                for i in range(min(len(data_list), width)):
                    val = data_list[-(width-i)]
                    if val >= threshold:
                        line += "█"
                    else:
                        line += " "
                
                # Add scale on the right
                if row == 0:
                    scale = f" {min_val:.0f}"
                elif row == height - 1:
                    scale = f" {max_val:.0f}"
                else:
                    scale = ""
                
                self.stdscr.addstr(graph_y, x, line + scale)
            
            # Current value
            if data_list:
                current = data_list[-1]
                color = curses.color_pair(1)
                if title.startswith("CPU") and current > 80:
                    color = curses.color_pair(3)
                elif title.startswith("Memory") and current > 85:
                    color = curses.color_pair(3)
                
                self.stdscr.addstr(y + height + 1, x, f"Current: {current:.1f}", color)

class LiveMonitor:
    """Live monitoring without database"""
    
    def __init__(self):
        self.running = True
        self.stdscr = None
        
    def run(self):
        """Run live monitor"""
        curses.wrapper(self._run)
    
    def _run(self, stdscr):
        """Main loop for live monitoring"""
        self.stdscr = stdscr
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(1000)
        
        # Setup colors
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        
        while self.running:
            try:
                key = stdscr.getch()
                if key == ord('q'):
                    self.running = False
                
                stdscr.clear()
                self._draw_live_stats()
                stdscr.refresh()
                
            except KeyboardInterrupt:
                self.running = False
    
    def _draw_live_stats(self):
        """Draw live statistics"""
        height, width = self.stdscr.getmaxyx()
        
        # Title
        title = "Android Live Monitor"
        self.stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
        self.stdscr.addstr(1, 0, "─" * width)
        
        y = 3
        
        # System stats
        self.stdscr.addstr(y, 2, "System Statistics:", curses.A_BOLD)
        y += 2
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_color = curses.color_pair(1)
        if cpu_percent > 50:
            cpu_color = curses.color_pair(2)
        if cpu_percent > 80:
            cpu_color = curses.color_pair(3)
        
        self.stdscr.addstr(y, 4, f"CPU Usage: {cpu_percent:.1f}%", cpu_color)
        self._draw_bar(y, 25, cpu_percent, 30, cpu_color)
        y += 2
        
        # Memory
        mem = psutil.virtual_memory()
        mem_color = curses.color_pair(1)
        if mem.percent > 70:
            mem_color = curses.color_pair(2)
        if mem.percent > 85:
            mem_color = curses.color_pair(3)
        
        self.stdscr.addstr(y, 4, f"Memory: {mem.percent:.1f}% ({mem.used/(1024**3):.1f}/{mem.total/(1024**3):.1f} GB)", mem_color)
        self._draw_bar(y, 25, mem.percent, 30, mem_color)
        y += 2
        
        # Battery
        try:
            result = subprocess.run(['dumpsys', 'battery'], capture_output=True, text=True, timeout=1)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'level:' in line:
                        battery_level = int(line.split(':')[1].strip())
                        bat_color = curses.color_pair(1)
                        if battery_level < 30:
                            bat_color = curses.color_pair(2)
                        if battery_level < 15:
                            bat_color = curses.color_pair(3)
                        
                        self.stdscr.addstr(y, 4, f"Battery: {battery_level}%", bat_color)
                        self._draw_bar(y, 25, battery_level, 30, bat_color)
                        y += 2
                        break
        except:
            pass
        
        y += 1
        
        # Network
        self.stdscr.addstr(y, 2, "Network Interfaces:", curses.A_BOLD)
        y += 2
        
        net_io = psutil.net_io_counters(pernic=True)
        for iface, counters in list(net_io.items())[:5]:
            sent_mb = counters.bytes_sent / (1024**2)
            recv_mb = counters.bytes_recv / (1024**2)
            self.stdscr.addstr(y, 4, f"{iface}: ↑ {sent_mb:.1f} MB  ↓ {recv_mb:.1f} MB")
            y += 1
        
        y += 2
        
        # Top processes
        self.stdscr.addstr(y, 2, "Top Processes:", curses.A_BOLD)
        y += 2
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] > 0:
                    processes.append(pinfo)
            except:
                pass
        
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        for proc in processes[:min(10, height - y - 3)]:
            line = f"{proc['name'][:30]:<30} CPU: {proc['cpu_percent']:>5.1f}%"
            color = curses.color_pair(1)
            if proc['cpu_percent'] > 20:
                color = curses.color_pair(2)
            if proc['cpu_percent'] > 50:
                color = curses.color_pair(3)
            
            self.stdscr.addstr(y, 4, line[:width-6], color)
            y += 1
        
        # Footer
        self.stdscr.addstr(height - 1, (width - 20) // 2, "[q] Quit")
    
    def _draw_bar(self, y, x, percent, width, color):
        """Draw a percentage bar"""
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        self.stdscr.addstr(y, x, bar, color)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Android Monitor Dashboard")
    
    parser.add_argument(
        '-d', '--database',
        default='/data/data/com.termux/files/home/android_monitor/monitor_data.db',
        help='Path to monitor database'
    )
    
    parser.add_argument(
        '-l', '--live',
        action='store_true',
        help='Live monitoring mode (no database required)'
    )
    
    parser.add_argument(
        '-u', '--update-interval',
        type=float,
        default=1.0,
        help='Update interval in seconds'
    )
    
    args = parser.parse_args()
    
    try:
        if args.live:
            # Run live monitor
            monitor = LiveMonitor()
            monitor.run()
        else:
            # Check database exists
            if not os.path.exists(args.database):
                print(f"Error: Database not found: {args.database}")
                print("Run the main monitor script first or use --live mode")
                sys.exit(1)
            
            # Run dashboard with database
            data = DashboardData(args.database)
            dashboard = Dashboard(data)
            dashboard.update_interval = args.update_interval
            dashboard.run()
            
    except KeyboardInterrupt:
        print("\nDashboard stopped")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
