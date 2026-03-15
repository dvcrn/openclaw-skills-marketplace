#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理工具 - 用于管理抖音自动回复助手的配置
"""

import json
import sys
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path='config.json'):
        self.config_path = Path(config_path)
        self.config = self.load_or_create()
    
    def load_or_create(self):
        """加载或创建配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self.create_default()
    
    def create_default(self):
        """创建默认配置"""
        config = {
            "douyin_cookie": "",
            "keywords": {
                "怎么买": "亲，已私信您购买链接啦~ 😊",
                "价格": "价格已私信发送，请注意查收哦~ 💰",
                "多少钱": "优惠价格私信发您了，快去看看吧~ 🎁",
                "链接": "链接已私信，注意查看消息哦~ 📩",
                "购买": "购买方式已私信发送~ 😊",
                "微信": "已发送联系方式，请注意查收~ 📱",
                "优惠": "专属优惠券已私信发送~ 🎉",
                "课程": "课程详情已私信发您~ 📚"
            },
            "auto_reply_enabled": True,
            "reply_delay": 30,
            "daily_limit": 100,
            "blacklist_words": ["广告", "举报", "投诉"],
            "whitelist_users": []
        }
        
        self.save(config)
        return config
    
    def load(self):
        """加载配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save(self, config=None):
        """保存配置"""
        if config is None:
            config = self.config
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def add_keyword(self, keyword, reply):
        """添加关键词回复"""
        if 'keywords' not in self.config:
            self.config['keywords'] = {}
        
        self.config['keywords'][keyword] = reply
        self.save()
        print(f"✓ 已添加关键词：{keyword}")
    
    def remove_keyword(self, keyword):
        """删除关键词回复"""
        if keyword in self.config.get('keywords', {}):
            del self.config['keywords'][keyword]
            self.save()
            print(f"✓ 已删除关键词：{keyword}")
        else:
            print(f"✗ 关键词不存在：{keyword}")
    
    def list_keywords(self):
        """列出所有关键词"""
        keywords = self.config.get('keywords', {})
        print(f"\n共有 {len(keywords)} 个关键词回复规则:\n")
        
        for i, (keyword, reply) in enumerate(keywords.items(), 1):
            print(f"{i}. {keyword}")
            print(f"   → {reply[:50]}{'...' if len(reply) > 50 else ''}")
            print()
    
    def set_cookie(self, cookie):
        """设置抖音 cookie"""
        self.config['douyin_cookie'] = cookie
        self.save()
        print("✓ Cookie 已更新")
    
    def set_delay(self, seconds):
        """设置回复延迟"""
        self.config['reply_delay'] = int(seconds)
        self.save()
        print(f"✓ 回复延迟已设置为 {seconds} 秒")
    
    def set_daily_limit(self, limit):
        """设置每日限制"""
        self.config['daily_limit'] = int(limit)
        self.save()
        print(f"✓ 每日回复限制已设置为 {limit} 条")
    
    def show_config(self):
        """显示当前配置"""
        print("\n" + "=" * 50)
        print("⚙️  当前配置")
        print("=" * 50)
        print(f"Cookie 配置：{'✓ 已配置' if self.config.get('douyin_cookie') else '✗ 未配置'}")
        print(f"自动回复：{'开启' if self.config.get('auto_reply_enabled') else '关闭'}")
        print(f"回复延迟：{self.config.get('reply_delay', 30)} 秒")
        print(f"每日限制：{self.config.get('daily_limit', 100)} 条")
        print(f"关键词数：{len(self.config.get('keywords', {}))} 个")
        print(f"黑名单词：{len(self.config.get('blacklist_words', []))} 个")
        print(f"白名单用户：{len(self.config.get('whitelist_users', []))} 个")
        print("=" * 50 + "\n")


def main():
    manager = ConfigManager()
    
    if len(sys.argv) < 2:
        print("用法：python config_manager.py <command> [args]")
        print("\n命令:")
        print("  show                    - 显示配置")
        print("  list                    - 列出关键词")
        print("  add <关键词> <回复>     - 添加关键词")
        print("  remove <关键词>         - 删除关键词")
        print("  cookie <cookie>         - 设置抖音 cookie")
        print("  delay <秒数>            - 设置回复延迟")
        print("  limit <数量>            - 设置每日限制")
        return
    
    command = sys.argv[1]
    
    if command == 'show':
        manager.show_config()
    
    elif command == 'list':
        manager.list_keywords()
    
    elif command == 'add':
        if len(sys.argv) < 4:
            print("用法：python config_manager.py add <关键词> <回复>")
            return
        keyword = sys.argv[2]
        reply = ' '.join(sys.argv[3:])
        manager.add_keyword(keyword, reply)
    
    elif command == 'remove':
        if len(sys.argv) < 3:
            print("用法：python config_manager.py remove <关键词>")
            return
        manager.remove_keyword(sys.argv[2])
    
    elif command == 'cookie':
        if len(sys.argv) < 3:
            print("用法：python config_manager.py cookie <your_cookie>")
            return
        manager.set_cookie(sys.argv[2])
    
    elif command == 'delay':
        if len(sys.argv) < 3:
            print("用法：python config_manager.py delay <秒数>")
            return
        manager.set_delay(sys.argv[2])
    
    elif command == 'limit':
        if len(sys.argv) < 3:
            print("用法：python config_manager.py limit <数量>")
            return
        manager.set_daily_limit(sys.argv[2])
    
    else:
        print(f"未知命令：{command}")


if __name__ == '__main__':
    main()
