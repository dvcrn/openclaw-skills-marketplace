#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNY Rate Calculator - Prairie Grasslands Formula
Auto-fetch Bank of Taiwan CNY rates and calculate tiered pricing
Supports: Telegram, Discord, Signal, WhatsApp, Slack, iMessage, IRC, Google Chat
"""

import requests
import re
import sys
import json
import os
import subprocess
from datetime import datetime
from typing import Optional, Tuple, List


class CNYRateCalculator:
    """Bank of Taiwan CNY Exchange Rate Calculator"""
    
    # Default formula constants
    PRICE_DELTAS = [0.05, 0.03, 0.015]
    PRICE_LABELS = ["基礎成本", "滿萬優惠", "五萬優惠"]
    BOT_URL = "https://rate.bot.com.tw/xrt"
    
    # Supported channels
    SUPPORTED_CHANNELS = [
        'telegram', 'discord', 'signal', 'whatsapp', 'slack',
        'imessage', 'irc', 'googlechat', 'webhook', 'console'
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with optional config file"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        })
        
        self.config = {}
        self.channel_config = {}
        
        # Load config if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                formula = self.config.get('formula', {})
                self.PRICE_DELTAS = formula.get('deltas', self.PRICE_DELTAS)
                self.PRICE_LABELS = formula.get('labels', self.PRICE_LABELS)
                self.BOT_URL = self.config.get('sources', {}).get('bot_rate', self.BOT_URL)
                self.channel_config = self.config.get('channel', {})
        
        # Auto-detect channel if not configured
        if not self.validate_channel():
            self.channel_config = self.auto_detect_channel()
    
    def auto_detect_channel(self) -> dict:
        """Auto-detect channel from environment and OpenClaw config"""
        # Try to read OpenClaw config
        openclaw_config = self._load_openclaw_config()
        
        # Priority 1: Check if Telegram bot token exists (most common)
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            # Try to get chat_id from OpenClaw config
            chat_id = self._get_telegram_chat_id(openclaw_config)
            if chat_id:
                print(f"✅ Auto-detected Telegram channel: {chat_id}")
                return {'type': 'telegram', 'target': chat_id}
        
        # Priority 2: Check OpenClaw Gateway for supported channels
        if os.getenv('OPENCLAW_GATEWAY_TOKEN'):
            gateway_config = self._get_gateway_channel(openclaw_config)
            if gateway_config:
                print(f"✅ Auto-detected {gateway_config['type']} channel via OpenClaw Gateway")
                return gateway_config
        
        # Priority 3: Check Discord webhook from environment
        if os.getenv('DISCORD_WEBHOOK_URL'):
            print(f"✅ Auto-detected Discord webhook from environment")
            return {'type': 'discord', 'target': os.getenv('DISCORD_WEBHOOK_URL')}
        
        # Priority 4: Check Slack webhook from environment
        if os.getenv('SLACK_WEBHOOK_URL'):
            print(f"✅ Auto-detected Slack webhook from environment")
            return {'type': 'slack', 'target': os.getenv('SLACK_WEBHOOK_URL')}
        
        return {}
    
    def _load_openclaw_config(self) -> dict:
        """Load OpenClaw configuration file"""
        config_paths = [
            os.path.expanduser('~/.openclaw/config.json'),
            os.path.expanduser('~/.openclaw/openclaw.json'),
            os.path.join(os.getenv('LOCALAPPDATA', ''), 'openclaw', 'config.json'),
            os.path.join(os.getenv('APPDATA', ''), 'openclaw', 'config.json'),
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    pass
        
        return {}
    
    def _get_telegram_chat_id(self, openclaw_config: dict) -> Optional[str]:
        """Extract Telegram chat ID from OpenClaw config"""
        # Try to get from config
        channels = openclaw_config.get('channels', {})
        telegram_config = channels.get('telegram', {})
        
        # Check default chat_id
        chat_id = telegram_config.get('chat_id') or telegram_config.get('default_chat_id')
        if chat_id:
            return chat_id
        
        # Try to get from first available account
        accounts = telegram_config.get('accounts', [])
        if accounts:
            return accounts[0].get('chat_id') or accounts[0].get('target')
        
        # Try legacy format
        if 'telegram' in channels:
            tg = channels['telegram']
            if isinstance(tg, dict):
                return tg.get('chat_id') or tg.get('target') or tg.get('default')
        
        return None
    
    def _get_gateway_channel(self, openclaw_config: dict) -> Optional[dict]:
        """Get first available gateway channel"""
        channels = openclaw_config.get('channels', {})
        
        # Priority order for gateway channels
        gateway_channels = ['signal', 'whatsapp', 'imessage', 'irc']
        
        for ch_type in gateway_channels:
            if ch_type in channels:
                ch_config = channels[ch_type]
                if isinstance(ch_config, dict):
                    target = ch_config.get('target') or ch_config.get('default') or ch_config.get('chat_id')
                    if target:
                        return {'type': ch_type, 'target': target}
                elif isinstance(ch_config, list) and ch_config:
                    target = ch_config[0].get('target') or ch_config[0].get('chat_id')
                    if target:
                        return {'type': ch_type, 'target': target}
        
        return None
    
    def validate_channel(self) -> bool:
        """Validate channel configuration"""
        if not self.channel_config:
            return False
        
        channel_type = self.channel_config.get('type')
        target = self.channel_config.get('target')
        
        if not channel_type:
            return False
        if channel_type in ['YOUR_CHANNEL_TYPE', '']:
            return False
        if channel_type not in self.SUPPORTED_CHANNELS:
            return False
        if channel_type != 'console' and (not target or target in ['YOUR_TARGET_HERE', 'YOUR_CHAT_ID_HERE', '']):
            return False
        
        return True
    
    def fetch_rate(self) -> Optional[Tuple[float, float, str]]:
        """Fetch CNY exchange rate from Bank of Taiwan"""
        try:
            response = self.session.get(self.BOT_URL, timeout=30)
            response.encoding = 'utf-8'
            html = response.text
            
            # Extract update time
            time_match = re.search(r'牌價最新掛牌時間：(\d{4}/\d{2}/\d{2} \d{2}:\d{2})', html)
            update_time = time_match.group(1) if time_match else datetime.now().strftime("%Y/%m/%d %H:%M")
            
            # Extract CNY spot rate
            cny_pattern = r'人民幣 \(CNY\)[\s\S]*?(\d+\.\d{3})[\s\S]*?(\d+\.\d{3})[\s\S]*?(\d+\.\d{3})[\s\S]*?(\d+\.\d{3})'
            match = re.search(cny_pattern, html)
            
            if match:
                buy_rate = float(match.group(3))
                sell_rate = float(match.group(4))
                return buy_rate, sell_rate, update_time
            
            print("Error: Cannot parse CNY rate", file=sys.stderr)
            return None
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return None
    
    @staticmethod
    def round3(value: float) -> float:
        """Round to 3 decimal places"""
        return round(value * 1000) / 1000
    
    def calculate(self, buy_rate: float, sell_rate: float) -> dict:
        """Calculate tiered pricing"""
        mid = self.round3((buy_rate + sell_rate) / 2)
        
        results = {
            'buy_rate': buy_rate,
            'sell_rate': sell_rate,
            'mid': mid,
            'prices': []
        }
        
        for delta, label in zip(self.PRICE_DELTAS, self.PRICE_LABELS):
            price = self.round3(mid + delta)
            results['prices'].append({
                'label': label,
                'price': price,
                'delta': delta
            })
        
        return results
    
    def format_output(self, results: dict, update_time: str) -> List[str]:
        """Format output into 3 messages"""
        date_match = re.search(r'(\d{4})/(\d{2})/(\d{2})', update_time)
        date_str = f"{date_match.group(2)}.{date_match.group(3)}" if date_match else datetime.now().strftime("%m.%d")
        
        msg1 = f"{date_str}即期匯率\n台銀買入：{results['buy_rate']}\n台銀賣出：{results['sell_rate']}"
        
        price_lines = [f"{p['label']}：{p['price']:.3f}" for p in results['prices']]
        msg2 = '\n'.join(price_lines)
        
        msg3 = """台銀匯率：
https://rate.bot.com.tw/xrt

Line官方帳號：
https://manager.line.biz/account/@687spxpu/richmenu/edit/11648965"""
        
        return [msg1, msg2, msg3]
    
    def send_to_channel(self, messages: List[str]) -> bool:
        """Send messages to configured channel"""
        channel_type = self.channel_config.get('type')
        target = self.channel_config.get('target')
        
        try:
            if channel_type == 'telegram':
                return self._send_telegram(messages, target)
            elif channel_type == 'discord':
                return self._send_discord(messages, target)
            elif channel_type == 'slack':
                return self._send_slack(messages, target)
            elif channel_type == 'signal':
                return self._send_signal(messages, target)
            elif channel_type == 'whatsapp':
                return self._send_whatsapp(messages, target)
            elif channel_type == 'imessage':
                return self._send_imessage(messages, target)
            elif channel_type == 'irc':
                return self._send_irc(messages, target)
            elif channel_type == 'googlechat':
                return self._send_googlechat(messages, target)
            elif channel_type == 'webhook':
                return self._send_webhook(messages, target)
            elif channel_type == 'console':
                for msg in messages:
                    print(msg)
                    print("---")
                return True
            else:
                print(f"Error: Unsupported channel type '{channel_type}'", file=sys.stderr)
                return False
        except Exception as e:
            print(f"Error sending to channel: {e}", file=sys.stderr)
            return False
    
    def _send_telegram(self, messages: List[str], chat_id: str) -> bool:
        """Send messages via Telegram bot"""
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("Error: TELEGRAM_BOT_TOKEN environment variable not set", file=sys.stderr)
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        for msg in messages:
            payload = {
                'chat_id': chat_id,
                'text': msg,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=30)
            if not response.ok:
                print(f"Error sending to Telegram: {response.text}", file=sys.stderr)
                return False
        
        return True
    
    def _send_discord(self, messages: List[str], webhook_url: str) -> bool:
        """Send messages via Discord webhook"""
        for msg in messages:
            payload = {'content': msg}
            response = requests.post(webhook_url, json=payload, timeout=30)
            if not response.ok:
                print(f"Error sending to Discord: {response.text}", file=sys.stderr)
                return False
        
        return True
    
    def _send_slack(self, messages: List[str], webhook_url: str) -> bool:
        """Send messages via Slack webhook"""
        for msg in messages:
            payload = {'text': msg}
            response = requests.post(webhook_url, json=payload, timeout=30)
            if not response.ok:
                print(f"Error sending to Slack: {response.text}", file=sys.stderr)
                return False
        
        return True
    
    def _send_signal(self, messages: List[str], target: str) -> bool:
        """Send messages via Signal (requires signal-cli or OpenClaw gateway)"""
        # Try OpenClaw gateway first
        gateway_url = os.getenv('OPENCLAW_GATEWAY_URL', 'http://127.0.0.1:18790')
        gateway_token = os.getenv('OPENCLAW_GATEWAY_TOKEN')
        
        if gateway_token:
            for msg in messages:
                payload = {
                    'action': 'send',
                    'channel': 'signal',
                    'target': target,
                    'message': msg
                }
                headers = {'Authorization': f'Bearer {gateway_token}'}
                response = requests.post(f"{gateway_url}/api/v1/message", 
                                       json=payload, headers=headers, timeout=30)
                if not response.ok:
                    print(f"Error sending to Signal via gateway: {response.text}", file=sys.stderr)
                    return False
            return True
        
        # Fallback to signal-cli
        print("Note: Using signal-cli. Ensure signal-cli is installed and configured.", file=sys.stderr)
        for msg in messages:
            try:
                result = subprocess.run(
                    ['signal-cli', 'send', '-m', msg, target],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    print(f"Error sending to Signal: {result.stderr}", file=sys.stderr)
                    return False
            except FileNotFoundError:
                print("Error: signal-cli not found. Please install signal-cli or configure OpenClaw gateway.", file=sys.stderr)
                return False
        
        return True
    
    def _send_whatsapp(self, messages: List[str], target: str) -> bool:
        """Send messages via WhatsApp (requires OpenClaw gateway)"""
        gateway_url = os.getenv('OPENCLAW_GATEWAY_URL', 'http://127.0.0.1:18790')
        gateway_token = os.getenv('OPENCLAW_GATEWAY_TOKEN')
        
        if not gateway_token:
            print("Error: WhatsApp requires OPENCLAW_GATEWAY_TOKEN environment variable", file=sys.stderr)
            return False
        
        for msg in messages:
            payload = {
                'action': 'send',
                'channel': 'whatsapp',
                'target': target,
                'message': msg
            }
            headers = {'Authorization': f'Bearer {gateway_token}'}
            response = requests.post(f"{gateway_url}/api/v1/message", 
                                   json=payload, headers=headers, timeout=30)
            if not response.ok:
                print(f"Error sending to WhatsApp: {response.text}", file=sys.stderr)
                return False
        
        return True
    
    def _send_imessage(self, messages: List[str], target: str) -> bool:
        """Send messages via iMessage (macOS only, requires OpenClaw gateway or osascript)"""
        import platform
        if platform.system() != 'Darwin':
            print("Error: iMessage is only available on macOS", file=sys.stderr)
            return False
        
        # Try OpenClaw gateway first
        gateway_url = os.getenv('OPENCLAW_GATEWAY_URL', 'http://127.0.0.1:18790')
        gateway_token = os.getenv('OPENCLAW_GATEWAY_TOKEN')
        
        if gateway_token:
            for msg in messages:
                payload = {
                    'action': 'send',
                    'channel': 'imessage',
                    'target': target,
                    'message': msg
                }
                headers = {'Authorization': f'Bearer {gateway_token}'}
                response = requests.post(f"{gateway_url}/api/v1/message", 
                                       json=payload, headers=headers, timeout=30)
                if not response.ok:
                    print(f"Error sending to iMessage via gateway: {response.text}", file=sys.stderr)
                    return False
            return True
        
        # Fallback to osascript
        for msg in messages:
            try:
                script = f'tell application "Messages" to send "{msg}" to buddy "{target}"'
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    print(f"Error sending to iMessage: {result.stderr}", file=sys.stderr)
                    return False
            except Exception as e:
                print(f"Error sending to iMessage: {e}", file=sys.stderr)
                return False
        
        return True
    
    def _send_irc(self, messages: List[str], target: str) -> bool:
        """Send messages via IRC (requires OpenClaw gateway)"""
        gateway_url = os.getenv('OPENCLAW_GATEWAY_URL', 'http://127.0.0.1:18790')
        gateway_token = os.getenv('OPENCLAW_GATEWAY_TOKEN')
        
        if not gateway_token:
            print("Error: IRC requires OPENCLAW_GATEWAY_TOKEN environment variable", file=sys.stderr)
            return False
        
        for msg in messages:
            payload = {
                'action': 'send',
                'channel': 'irc',
                'target': target,
                'message': msg
            }
            headers = {'Authorization': f'Bearer {gateway_token}'}
            response = requests.post(f"{gateway_url}/api/v1/message", 
                                   json=payload, headers=headers, timeout=30)
            if not response.ok:
                print(f"Error sending to IRC: {response.text}", file=sys.stderr)
                return False
        
        return True
    
    def _send_googlechat(self, messages: List[str], webhook_url: str) -> bool:
        """Send messages via Google Chat webhook"""
        for msg in messages:
            payload = {'text': msg}
            response = requests.post(webhook_url, json=payload, timeout=30)
            if not response.ok:
                print(f"Error sending to Google Chat: {response.text}", file=sys.stderr)
                return False
        
        return True
    
    def _send_webhook(self, messages: List[str], webhook_url: str) -> bool:
        """Send messages to generic webhook"""
        for msg in messages:
            payload = {
                'message': msg,
                'timestamp': datetime.now().isoformat(),
                'source': 'cny-rate-calculator'
            }
            response = requests.post(webhook_url, json=payload, timeout=30)
            if not response.ok:
                print(f"Error sending to webhook: {response.text}", file=sys.stderr)
                return False
        
        return True
    
    def run(self) -> Optional[List[str]]:
        """Execute full workflow"""
        rate_data = self.fetch_rate()
        if not rate_data:
            return None
        
        buy_rate, sell_rate, update_time = rate_data
        results = self.calculate(buy_rate, sell_rate)
        messages = self.format_output(results, update_time)
        
        return messages


def print_setup_guide():
    """Print setup guide for all supported channels"""
    print("=" * 60)
    print("🔧 首次使用設定")
    print("=" * 60)
    print("\n請先設定訊息發送通道，才能使用此 Skill。\n")
    print("請編輯 config.json，加入以下其中一種設定：\n")
    
    channels = [
        ("Telegram", "telegram", '"你的_CHAT_ID"', "TELEGRAM_BOT_TOKEN"),
        ("Discord", "discord", '"你的_WEBHOOK_URL"', None),
        ("Slack", "slack", '"你的_WEBHOOK_URL"', None),
        ("Google Chat", "googlechat", '"你的_WEBHOOK_URL"', None),
        ("Signal", "signal", '"+886123456789" 或 "群組ID"', "OPENCLAW_GATEWAY_TOKEN (建議)"),
        ("WhatsApp", "whatsapp", '"+886123456789"', "OPENCLAW_GATEWAY_TOKEN (必需)"),
        ("iMessage", "imessage", '"聯絡人名稱或電話"', "OPENCLAW_GATEWAY_TOKEN (建議) 或 macOS"),
        ("IRC", "irc", '"#頻道名"', "OPENCLAW_GATEWAY_TOKEN (必需)"),
        ("通用 Webhook", "webhook", '"你的_WEBHOOK_URL"', None),
        ("僅終端輸出", "console", "null (不需要 target)", None),
    ]
    
    for name, type_, target, env_var in channels:
        print(f"{name}：")
        print(f'  "channel": {{')
        print(f'    "type": "{type_}",')
        if type_ != 'console':
            print(f'    "target": {target}')
        else:
            print(f'    "target": null')
        print(f'  }}')
        if env_var:
            print(f'  環境變數: {env_var}')
        print()
    
    print("=" * 60)
    print("設定完成後再次執行即可。")
    print("=" * 60)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='CNY Rate Calculator')
    parser.add_argument('--config', '-c', help='Path to config.json')
    parser.add_argument('--setup', action='store_true', help='Show setup guide')
    args = parser.parse_args()

    if args.setup:
        print_setup_guide()
        return 0

    # Find config file
    config_path = args.config
    if not config_path:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        skill_dir = os.path.dirname(script_dir)
        default_config = os.path.join(skill_dir, 'config.json')
        if os.path.exists(default_config):
            config_path = default_config

    calc = CNYRateCalculator(config_path=config_path)

    # Validate channel configuration
    if not calc.validate_channel():
        print_setup_guide()
        return 0

    messages = calc.run()

    if not messages:
        print("Failed to fetch rates", file=sys.stderr)
        return 1

    # Send to configured channel
    if not calc.send_to_channel(messages):
        return 1

    print(f"Successfully sent {len(messages)} messages to {calc.channel_config['type']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
