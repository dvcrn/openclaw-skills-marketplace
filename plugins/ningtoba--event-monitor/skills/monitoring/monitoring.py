#!/usr/bin/env python3
"""
Monitoring Skill for OpenClaw
Collects CPU and memory metrics, stores in SQLite, generates Excel reports.
"""

import sqlite3
import psutil
import datetime
import socket
import os
import argparse
from openpyxl import Workbook
from openpyxl.styles import Font

# Skill directory for database and reports
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SKILL_DIR, "monitoring.db")


class DatabaseManager:
    """SQLite database manager for monitoring metrics."""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Get SQLite connection."""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # CPU usage table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cpu_usage_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT,
                application_name TEXT,
                cpu_usage REAL,
                timestamp DATETIME,
                day INTEGER,
                week INTEGER,
                month INTEGER,
                working_day TEXT
            )
            """)
            
            # Memory usage table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_usage_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT,
                application_name TEXT,
                memory_usage REAL,
                timestamp DATETIME,
                day INTEGER,
                week INTEGER,
                month INTEGER,
                working_day TEXT
            )
            """)
            
            conn.commit()

    def insert_cpu_metrics(self, metrics):
        """Insert CPU metrics into database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO cpu_usage_table
                (device_name, application_name, cpu_usage, timestamp, day, week, month, working_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, metrics)
            conn.commit()

    def insert_memory_metrics(self, metrics):
        """Insert memory metrics into database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO memory_usage_table
                (device_name, application_name, memory_usage, timestamp, day, week, month, working_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, metrics)
            conn.commit()

    def get_recent_cpu(self, limit=10):
        """Get recent CPU metrics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM cpu_usage_table 
                ORDER BY timestamp DESC, id DESC 
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()

    def get_recent_memory(self, limit=10):
        """Get recent memory metrics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM memory_usage_table 
                ORDER BY timestamp DESC, id DESC 
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()


def collect_metrics():
    """Collect current system metrics."""
    device_name = socket.gethostname()
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    day = now.isoweekday()
    week = (now.day - 1) // 7 + 1
    month = now.month
    working_day = "Weekday" if day <= 5 else "Weekend"
    
    cpu_count = psutil.cpu_count(logical=True)
    psutil.cpu_percent(interval=0.1)  # Initial call to seed cpu_percent
    
    process_list = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['pid'] == 0 or proc.info['name'].lower() in ['system idle process', 'idle']:
                continue
            cpu = proc.cpu_percent(interval=None)
            normalized_cpu = min(round(cpu / cpu_count, 3), 100.0)
            mem = round(proc.memory_percent(), 3)
            app_name = proc.info['name']
            process_list.append({
                'device_name': device_name,
                'app_name': app_name,
                'cpu_usage': normalized_cpu,
                'mem_usage': mem,
                'timestamp': timestamp,
                'day': day,
                'week': week,
                'month': month,
                'working_day': working_day
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    top_cpu = sorted(process_list, key=lambda x: x['cpu_usage'], reverse=True)[:10]
    top_mem = sorted(process_list, key=lambda x: x['mem_usage'], reverse=True)[:10]
    
    return top_cpu, top_mem


def save_to_db(top_cpu, top_mem, db_manager):
    """Save metrics to SQLite database."""
    cpu_data = [
        (m['device_name'], m['app_name'], m['cpu_usage'], m['timestamp'], m['day'], m['week'], m['month'], m['working_day'])
        for m in top_cpu
    ]
    mem_data = [
        (m['device_name'], m['app_name'], m['mem_usage'], m['timestamp'], m['day'], m['week'], m['month'], m['working_day'])
        for m in top_mem
    ]
    
    db_manager.insert_cpu_metrics(cpu_data)
    db_manager.insert_memory_metrics(mem_data)
    print(f"[OK] Metrics saved to {db_manager.db_path}")


def generate_excel_report(db_manager, filename="system_report.xlsx"):
    """Generate Excel report from database."""
    top_cpu = db_manager.get_recent_cpu(10)
    top_mem = db_manager.get_recent_memory(10)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Resource Usage"
    
    headers = ["ID", "Device Name", "Application Name", "CPU Usage (%)", "Memory Usage (%)", "Timestamp", "Day", "Week", "Month", "Working Day"]
    ws.append(headers)
    
    header_font = Font(bold=True)
    for cell in ws[1]:
        cell.font = header_font
        
    # Add CPU data
    for row in top_cpu:
        ws.append([row[0], row[1], row[2], f"{row[3]:.3f}", f"{row[3]:.3f}", row[4], row[5], row[6], row[7], row[8]])
        
    for column_cells in ws.columns:
        max_length = 0
        column_letter = column_cells[0].column_letter
        for cell in column_cells:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[column_letter].width = max_length + 2
        
    output_path = os.path.join(SKILL_DIR, filename)
    wb.save(output_path)
    print(f"[OK] Report saved to {output_path}")


def show_metrics(db_manager, limit=10, metric_type="both"):
    """Display recent metrics from database."""
    if metric_type in ["cpu", "both"]:
        print("\n=== Recent CPU Metrics ===")
        cpu_data = db_manager.get_recent_cpu(limit)
        if cpu_data:
            for row in cpu_data[:5]:
                print(f"  {row[2]}: {row[3]:.3f}% @ {row[4]}")
        else:
            print("  No CPU data found")
    
    if metric_type in ["memory", "both"]:
        print("\n=== Recent Memory Metrics ===")
        mem_data = db_manager.get_recent_memory(limit)
        if mem_data:
            for row in mem_data[:5]:
                print(f"  {row[2]}: {row[3]:.3f}% @ {row[4]}")
        else:
            print("  No memory data found")


def run_skill():
    """Main skill execution."""
    db_manager = DatabaseManager()
    top_cpu, top_mem = collect_metrics()
    save_to_db(top_cpu, top_mem, db_manager)
    generate_excel_report(db_manager)


def main():
    parser = argparse.ArgumentParser(description="Monitoring Skill for OpenClaw")
    parser.add_argument("--collect", action="store_true", help="Collect and save metrics")
    parser.add_argument("--report", action="store_true", help="Generate Excel report")
    parser.add_argument("--show", action="store_true", help="Show recent metrics")
    parser.add_argument("--limit", type=int, default=10, help="Number of records to show")
    parser.add_argument("--type", choices=["cpu", "memory", "both"], default="both", help="Metric type")
    args = parser.parse_args()
    
    db_manager = DatabaseManager()
    
    if args.collect:
        top_cpu, top_mem = collect_metrics()
        save_to_db(top_cpu, top_mem, db_manager)
    elif args.report:
        generate_excel_report(db_manager)
    elif args.show:
        show_metrics(db_manager, args.limit, args.type)
    else:
        # Default: collect + report
        run_skill()


if __name__ == "__main__":
    main()
