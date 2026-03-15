#!/usr/bin/env python3
"""
WebSocket Receiver Skill v2.0
稳定、可靠的 WebSocket 数据接收框架
"""

import asyncio
import atexit
import json
import logging
import os
import signal
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable, List, Dict, Any, Optional

try:
    import websockets
    from websockets.exceptions import ConnectionClosed, InvalidStatusCode
except ImportError:
    print("请安装 websockets: pip install websockets")
    sys.exit(1)

# ============ 默认配置 ============
DEFAULT_CONFIG = {
    "ws_url": "",  # 必须配置，否则无法启动
    "batch_size": 10,
    "auto_analyze": True,
    "data_dir": "~/clawd/data/websocket",
    # 重连配置
    "reconnect_delay": 2,           # 初始重连延迟（秒）
    "reconnect_max_delay": 60,      # 最大重连延迟（秒）
    "reconnect_max_attempts": 0,    # 最大重连次数，0=无限
    # 连接配置
    "connect_timeout": 30,          # 连接超时（秒）
    "ping_interval": 30,            # 心跳间隔（秒）
    "ping_timeout": 10,             # 心跳超时（秒）
    # 日志配置
    "log_max_bytes": 10 * 1024 * 1024,  # 10MB
    "log_backup_count": 3,
}
# ==================================


class WebSocketReceiver:
    """WebSocket 接收器主类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.shutting_down = False
        self.reconnect_count = 0
        self.processed_count = 0
        self.analysis_count = 0
        self.batch_buffer: List[Dict] = []
        self.current_delay = self.config["reconnect_delay"]
        
        # 数据目录
        self.data_dir = Path(self.config["data_dir"]).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # PID 文件
        self.pid_file = self.data_dir / "receiver.pid"
        
        # 设置日志
        self._setup_logging()
        
        # 自定义处理器
        self.on_message: Callable = self._default_on_message
        self.on_batch: Callable = self._default_on_batch

    def _setup_logging(self):
        """配置带轮转的日志"""
        log_file = self.data_dir / "receiver.log"
        
        # 创建 logger
        self.logger = logging.getLogger("websocket-receiver")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        
        # 文件处理器（带轮转）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.config["log_max_bytes"],
            backupCount=self.config["log_backup_count"],
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _write_pid(self):
        """写入 PID 文件"""
        try:
            self.pid_file.write_text(str(os.getpid()))
            self.logger.info(f"PID {os.getpid()} written to {self.pid_file}")
        except Exception as e:
            self.logger.error(f"Failed to write PID file: {e}")

    def _remove_pid(self):
        """删除 PID 文件"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                self.logger.info("PID file removed")
        except Exception as e:
            self.logger.error(f"Failed to remove PID file: {e}")

    def _default_on_message(self, data: Dict) -> bool:
        """默认消息处理：保存到 JSONL 文件"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H')
            data_file = self.data_dir / f"data_{timestamp}.jsonl"
            
            with open(data_file, 'a', encoding='utf-8') as f:
                record = {
                    "received_at": datetime.now().isoformat(),
                    "data": data
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            return True
        except Exception as e:
            self.logger.error(f"Failed to save message: {e}")
            return False

    async def _default_on_batch(self, batch: List[Dict]) -> Optional[str]:
        """默认批量处理：异步 AI 分析"""
        if not self.config.get("auto_analyze"):
            return None
            
        try:
            # 构建分析提示
            news_list = []
            for i, news in enumerate(batch, 1):
                title = news.get('title', 'N/A')
                content = news.get('content', 'N/A')[:300]
                news_list.append(f"【{i}】{title}: {content}...")
            
            all_news = "\n".join(news_list)
            prompt = f"""请分析以下 {len(batch)} 条新闻，提供批量总结：

{all_news}

请用中文回复，格式：
## 批量总结（{len(batch)}条）
### 📌 核心趋势
### 🔥 热点话题  
### 💡 关键洞察
"""
            
            self.logger.info(f"🤖 Analyzing batch of {len(batch)} items...")
            
            # 异步调用 OpenClaw
            proc = await asyncio.create_subprocess_exec(
                'openclaw', 'agent', '--agent', 'main', '--message', prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), 
                    timeout=120
                )
                if proc.returncode == 0:
                    return stdout.decode('utf-8').strip()
                else:
                    self.logger.error(f"OpenClaw error: {stderr.decode('utf-8')}")
                    return None
            except asyncio.TimeoutError:
                proc.kill()
                self.logger.error("OpenClaw timeout")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to analyze batch: {e}")
            return None

    def _save_analysis(self, batch: List[Dict], analysis: str):
        """保存分析报告"""
        try:
            analysis_file = self.data_dir / f"analysis_{datetime.now().strftime('%Y%m%d')}.md"
            with open(analysis_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"## 批量分析 #{self.analysis_count} ({len(batch)}条)\n")
                f.write(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(analysis)
                f.write(f"\n{'='*60}\n")
        except Exception as e:
            self.logger.error(f"Failed to save analysis: {e}")

    async def _notify(self, message: str):
        """异步发送通知"""
        try:
            proc = await asyncio.create_subprocess_exec(
                'openclaw', 'notify', message,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await asyncio.wait_for(proc.wait(), timeout=10)
        except Exception as e:
            self.logger.error(f"Failed to notify: {e}")

    async def _process_batch(self):
        """处理批量数据"""
        if not self.batch_buffer:
            return
        
        batch = self.batch_buffer.copy()
        self.batch_buffer.clear()
        
        # 调用批量处理器（支持同步和异步）
        if asyncio.iscoroutinefunction(self.on_batch):
            analysis = await self.on_batch(batch)
        else:
            analysis = self.on_batch(batch)
        
        if analysis:
            self.analysis_count += 1
            self._save_analysis(batch, analysis)
            
            report = f"📊 已处理 {self.processed_count} 条，完成第 {self.analysis_count} 次批量分析（{len(batch)}条）"
            self.logger.info(f"\n{'='*60}\n{report}\n{'='*60}")
            await self._notify(report)

    async def _handle_message(self, message: str):
        """处理收到的消息"""
        try:
            data = json.loads(message)
            title = data.get('title', 'N/A')[:40]
            
            batch_size = self.config["batch_size"]
            self.logger.info(f"📩 [{len(self.batch_buffer)+1}/{batch_size}] {title}...")
            
            # 调用消息处理器
            if self.on_message(data):
                self.processed_count += 1
                self.batch_buffer.append(data)
            
            # 达到批量阈值，触发处理
            if len(self.batch_buffer) >= batch_size:
                await self._process_batch()
                
        except json.JSONDecodeError:
            self.logger.warning(f"Non-JSON message: {message[:200]}")
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")

    def _calculate_backoff(self) -> float:
        """计算指数退避延迟"""
        delay = min(
            self.config["reconnect_delay"] * (2 ** self.reconnect_count),
            self.config["reconnect_max_delay"]
        )
        return delay

    async def _connect_loop(self):
        """主连接循环（带指数退避重连）"""
        ws_url = self.config["ws_url"]
        max_attempts = self.config["reconnect_max_attempts"]
        
        while self.running and not self.shutting_down:
            # 检查最大重连次数
            if max_attempts > 0 and self.reconnect_count >= max_attempts:
                self.logger.error(f"❌ Max reconnect attempts ({max_attempts}) reached. Giving up.")
                break
            
            try:
                self.logger.info(f"🔌 Connecting to {ws_url}...")
                
                # 带超时的连接
                self.ws = await asyncio.wait_for(
                    websockets.connect(
                        ws_url,
                        ping_interval=self.config["ping_interval"],
                        ping_timeout=self.config["ping_timeout"],
                        close_timeout=10
                    ),
                    timeout=self.config["connect_timeout"]
                )
                
                # 连接成功，重置计数器
                self.reconnect_count = 0
                self.logger.info("✅ Connected!")
                
                try:
                    async for message in self.ws:
                        if self.shutting_down:
                            break
                        await self._handle_message(message)
                except ConnectionClosed as e:
                    self.logger.warning(f"⚠️ Connection closed: code={e.code}, reason={e.reason}")
                finally:
                    self.ws = None
                        
            except asyncio.TimeoutError:
                self.logger.error(f"❌ Connection timeout ({self.config['connect_timeout']}s)")
            except ConnectionRefusedError:
                self.logger.error("❌ Connection refused")
            except InvalidStatusCode as e:
                self.logger.error(f"❌ Invalid status code: {e.status_code}")
            except OSError as e:
                self.logger.error(f"❌ Network error: {e}")
            except Exception as e:
                self.logger.error(f"❌ Unexpected error: {type(e).__name__}: {e}")
            
            # 重连逻辑
            if self.running and not self.shutting_down:
                self.reconnect_count += 1
                delay = self._calculate_backoff()
                self.logger.info(f"🔄 Reconnecting in {delay:.1f}s... (attempt #{self.reconnect_count})")
                
                # 可中断的等待
                try:
                    await asyncio.sleep(delay)
                except asyncio.CancelledError:
                    break

    async def _shutdown(self):
        """优雅关闭"""
        if self.shutting_down:
            return
        
        self.shutting_down = True
        self.logger.info("\n🛑 Shutting down gracefully...")
        
        # 处理剩余缓冲区
        if self.batch_buffer:
            self.logger.info(f"Processing remaining {len(self.batch_buffer)} items...")
            await self._process_batch()
        
        # 关闭 WebSocket 连接
        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass
        
        # 最终报告
        final_report = f"📊 本次共处理 {self.processed_count} 条，完成 {self.analysis_count} 次批量分析"
        self.logger.info(final_report)
        await self._notify(final_report)
        
        self.running = False

    def _setup_signal_handlers(self, loop: asyncio.AbstractEventLoop):
        """设置信号处理器"""
        def handle_signal(sig):
            self.logger.info(f"Received signal {sig.name}")
            if not self.shutting_down:
                asyncio.create_task(self._shutdown())
        
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
            except NotImplementedError:
                # Windows 不支持 add_signal_handler
                signal.signal(sig, lambda s, f, sig=sig: handle_signal(sig))

    async def _run_async(self):
        """异步主入口"""
        loop = asyncio.get_running_loop()
        self._setup_signal_handlers(loop)
        
        self.running = True
        self._write_pid()
        atexit.register(self._remove_pid)
        
        self.logger.info("=" * 60)
        self.logger.info("🚀 WebSocket Receiver v2.0 Started")
        self.logger.info(f"📁 Data: {self.data_dir}")
        self.logger.info(f"🔗 URL: {self.config['ws_url']}")
        self.logger.info(f"📦 Batch: {self.config['batch_size']}")
        self.logger.info(f"🔄 Reconnect: delay={self.config['reconnect_delay']}s, max={self.config['reconnect_max_delay']}s")
        self.logger.info("=" * 60)
        
        try:
            await self._connect_loop()
        finally:
            if not self.shutting_down:
                await self._shutdown()
            self._remove_pid()

    def run(self):
        """启动接收器（同步入口）"""
        # 检查必须配置
        if not self.config.get("ws_url"):
            print("❌ 错误: 未配置 WebSocket 地址")
            print("")
            print("请通过以下方式配置:")
            print("  1. 环境变量: WEBSOCKET_URL=ws://your-server:port/ws")
            print("  2. 配置文件: ~/.openclaw/websocket-config.json")
            print("  3. 命令行:   --url ws://your-server:port/ws")
            print("")
            print("联系作者获取测试服务器地址，或自行搭建 WebSocket 服务。")
            sys.exit(1)
        
        try:
            asyncio.run(self._run_async())
        except KeyboardInterrupt:
            pass  # 已在信号处理器中处理


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WebSocket Receiver Skill v2.0')
    parser.add_argument('--config', '-c', help='Config JSON file')
    parser.add_argument('--url', '-u', help='WebSocket URL')
    parser.add_argument('--batch-size', '-b', type=int, help='Batch size')
    parser.add_argument('--data-dir', '-d', help='Data directory')
    parser.add_argument('--no-analyze', action='store_true', help='Disable auto analysis')
    
    args = parser.parse_args()
    
    # 加载配置
    config = DEFAULT_CONFIG.copy()
    
    if args.config:
        config_path = Path(args.config).expanduser()
        if config_path.exists():
            with open(config_path) as f:
                config.update(json.load(f))
    
    # 命令行参数覆盖
    if args.url:
        config['ws_url'] = args.url
    if args.batch_size:
        config['batch_size'] = args.batch_size
    if args.data_dir:
        config['data_dir'] = args.data_dir
    if args.no_analyze:
        config['auto_analyze'] = False
    
    # 启动
    receiver = WebSocketReceiver(config)
    receiver.run()


if __name__ == "__main__":
    main()
