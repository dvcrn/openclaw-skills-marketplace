#!/usr/bin/env python3
"""
LongTask Progress - 长任务强制进度报告系统

防止长任务执行过程中"失去专注"或"睡着"，通过定时强制报告保持任务连续性。
"""

import time
import threading
from datetime import datetime
from typing import Optional, Callable
import sys

class LongTaskProgress:
    """
    长任务进度报告器
    
    使用方式：
        1. 装饰器方式（推荐）
        2. 上下文管理器方式
        3. 手动调用方式
    """
    
    def __init__(
        self,
        task_name: str,
        total_steps: Optional[int] = None,
        interval: int = 300,
        callback: Optional[Callable] = None
    ):
        """
        初始化进度报告器
        
        Args:
            task_name: 任务名称（用于报告标识）
            total_steps: 总步骤数（可选，用于计算百分比）
            interval: 强制报告间隔（秒），默认300秒（5分钟）
            callback: 自定义回调函数，接收(report_data)参数
        """
        self.task_name = task_name
        self.total_steps = total_steps
        self.interval = interval
        self.callback = callback
        
        self.current_step = 0
        self.start_time = time.time()
        self.last_report_time = self.start_time
        self._stop_event = threading.Event()
        self._timer_thread = None
        self._is_running = False
        
    def start(self) -> 'LongTaskProgress':
        """启动进度报告"""
        if self._is_running:
            raise RuntimeError("进度报告器已在运行中")
            
        self._is_running = True
        self._schedule_next_report()
        
        report_msg = f"【强制报告】任务'{self.task_name}'开始，每{self.interval}秒强制报告一次"
        print(report_msg, file=sys.stderr)
        
        if self.callback:
            self.callback({
                'event': 'start',
                'task': self.task_name,
                'interval': self.interval,
                'total_steps': self.total_steps,
                'time': datetime.now().isoformat()
            })
            
        return self
        
    def _schedule_next_report(self):
        """调度下一次报告"""
        if not self._stop_event.is_set() and self._is_running:
            self._timer_thread = threading.Timer(self.interval, self._forced_report)
            self._timer_thread.daemon = True
            self._timer_thread.start()
            
    def _forced_report(self):
        """执行强制报告"""
        if not self._stop_event.is_set() and self._is_running:
            elapsed = time.time() - self.start_time
            since_last = time.time() - self.last_report_time
            
            report_data = {
                'event': 'progress',
                'task': self.task_name,
                'time': datetime.now().strftime('%H:%M:%S'),
                'elapsed_minutes': round(elapsed / 60, 1),
                'since_last_minutes': round(since_last / 60, 1),
                'current_step': self.current_step,
                'total_steps': self.total_steps,
            }
            
            if self.total_steps and self.total_steps > 0:
                report_data['progress_percent'] = round(
                    (self.current_step / self.total_steps) * 100, 1
                )
            
            # 输出到stderr确保即使stdout被重定向也能看到
            print(f"\n【强制报告 - {report_data['time']}】", file=sys.stderr)
            print(f"  任务: {self.task_name}", file=sys.stderr)
            print(f"  已用时间: {report_data['elapsed_minutes']}分钟", file=sys.stderr)
            print(f"  距离上次报告: {report_data['since_last_minutes']}分钟", file=sys.stderr)
            
            if self.total_steps:
                print(f"  进度: {self.current_step}/{self.total_steps} ({report_data['progress_percent']}%)", file=sys.stderr)
            else:
                print(f"  当前步骤: {self.current_step}", file=sys.stderr)
                
            print(f"  状态: 仍在执行中...\n", file=sys.stderr)
            
            if self.callback:
                self.callback(report_data)
                
            self._schedule_next_report()
            
    def step(self, message: str = "") -> None:
        """
        完成一个步骤并报告
        
        Args:
            message: 步骤描述信息
        """
        if not self._is_running:
            raise RuntimeError("进度报告器未启动，请先调用start()")
            
        self.current_step += 1
        self.last_report_time = time.time()
        
        progress_info = ""
        if self.total_steps:
            percent = round((self.current_step / self.total_steps) * 100)
            progress_info = f"  总进度: {percent}%"
        
        print(f"【步骤完成】{self.task_name} - 第{self.current_step}步完成", file=sys.stderr)
        if message:
            print(f"  详情: {message}", file=sys.stderr)
        if progress_info:
            print(progress_info, file=sys.stderr)
            
        if self.callback:
            self.callback({
                'event': 'step',
                'task': self.task_name,
                'step': self.current_step,
                'message': message,
                'time': datetime.now().isoformat()
            })
            
    def update(self, message: str) -> None:
        """
        更新当前步骤状态（不增加步骤计数）
        
        Args:
            message: 状态更新信息
        """
        print(f"【状态更新】{self.task_name}: {message}", file=sys.stderr)
        
        if self.callback:
            self.callback({
                'event': 'update',
                'task': self.task_name,
                'message': message,
                'time': datetime.now().isoformat()
            })
            
    def stop(self) -> None:
        """停止进度报告"""
        if not self._is_running:
            return
            
        self._stop_event.set()
        self._is_running = False
        
        if self._timer_thread:
            self._timer_thread.cancel()
            
        elapsed = time.time() - self.start_time
        minutes = round(elapsed / 60, 1)
        
        print(f"【任务完成】{self.task_name} - 总耗时{minutes}分钟", file=sys.stderr)
        
        if self.callback:
            self.callback({
                'event': 'stop',
                'task': self.task_name,
                'total_time_minutes': minutes,
                'total_steps': self.current_step,
                'time': datetime.now().isoformat()
            })
            
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()
        return False


# 装饰器工厂
def track_progress(
    task_name: Optional[str] = None,
    total_steps: Optional[int] = None,
    interval: int = 300
):
    """
    装饰器：自动追踪函数执行进度
    
    Args:
        task_name: 任务名称（默认使用函数名）
        total_steps: 总步骤数
        interval: 报告间隔（秒）
        
    使用示例：
        @track_progress(total_steps=5, interval=60)
        def my_long_task(reporter):
            for i in range(5):
                do_work()
                reporter.step(f"完成第{i}步")
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            name = task_name or func.__name__
            
            with LongTaskProgress(name, total_steps, interval) as reporter:
                # 将reporter作为参数传递给被装饰函数
                return func(*args, reporter=reporter, **kwargs)
                
        return wrapper
    return decorator


# 便捷函数
def quick_progress(task_name: str, message: str, interval: int = 300):
    """
    快速创建一个进度报告器并发送一条消息
    
    使用场景：简单任务，不需要精细步骤追踪
    
    Args:
        task_name: 任务名称
        message: 当前状态消息
        interval: 报告间隔
    """
    reporter = LongTaskProgress(task_name, interval=interval)
    reporter.start()
    reporter.update(message)
    return reporter


if __name__ == "__main__":
    # 使用示例1：上下文管理器
    print("=== 示例1：上下文管理器方式 ===")
    with LongTaskProgress("示例任务", total_steps=3, interval=10) as reporter:
        for i in range(3):
            time.sleep(2)
            reporter.step(f"处理第{i+1}个文件")
    
    # 使用示例2：装饰器
    print("\n=== 示例2：装饰器方式 ===")
    
    @track_progress(total_steps=3, interval=10)
    def download_files(reporter):
        for i in range(3):
            time.sleep(2)
            reporter.step(f"下载文件{i+1}")
    
    download_files()
    
    # 使用示例3：手动调用
    print("\n=== 示例3：手动调用方式 ===")
    reporter = LongTaskProgress("手动任务", total_steps=3, interval=10)
    reporter.start()
    
    for i in range(3):
        time.sleep(2)
        reporter.step(f"步骤{i+1}")
        
    reporter.stop()
    
    print("\n✅ 所有示例完成")
