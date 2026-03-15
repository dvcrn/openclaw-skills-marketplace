#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音自动回复助手 - 主程序
功能：自动回复评论、发送引荐码、引导私信
"""

import json
import time
import random
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('douyin_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DouyinAutoReply:
    """抖音自动回复机器人"""
    
    def __init__(self, config_path='config.json'):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.stats = {
            'total_replies': 0,
            'today_replies': 0,
            'last_reset': datetime.now().strftime('%Y-%m-%d'),
            'keywords_triggered': {}
        }
        self.load_stats()
        
    def load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            logger.warning(f"配置文件不存在：{self.config_path}")
            return self.create_default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_default_config(self):
        """创建默认配置"""
        default_config = {
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
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已创建默认配置文件：{self.config_path}")
        return default_config
    
    def load_stats(self):
        """加载统计数据"""
        stats_path = Path('stats.json')
        if stats_path.exists():
            with open(stats_path, 'r', encoding='utf-8') as f:
                self.stats = json.load(f)
                
            # 检查是否需要重置每日计数
            today = datetime.now().strftime('%Y-%m-%d')
            if self.stats.get('last_reset') != today:
                self.stats['today_replies'] = 0
                self.stats['last_reset'] = today
                self.save_stats()
    
    def save_stats(self):
        """保存统计数据"""
        stats_path = Path('stats.json')
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def check_daily_limit(self):
        """检查是否达到每日限制"""
        if self.stats['today_replies'] >= self.config.get('daily_limit', 100):
            logger.warning("已达到每日回复上限")
            return False
        return True
    
    def match_keyword(self, comment_text):
        """匹配关键词并返回回复内容"""
        keywords = self.config.get('keywords', {})
        
        for keyword, reply in keywords.items():
            if keyword in comment_text:
                # 记录关键词触发统计
                self.stats['keywords_triggered'][keyword] = \
                    self.stats['keywords_triggered'].get(keyword, 0) + 1
                return reply
        
        return None
    
    def is_blacklisted(self, comment_text):
        """检查是否在黑名单中"""
        blacklist = self.config.get('blacklist_words', [])
        return any(word in comment_text for word in blacklist)
    
    def is_whitelisted(self, user_id):
        """检查是否在白名单中"""
        whitelist = self.config.get('whitelist_users', [])
        return user_id in whitelist
    
    def get_comments(self):
        """
        获取最新评论列表
        
        TODO: 实现抖音 API 调用获取评论
        返回格式：[{'comment_id': 'xxx', 'user_id': 'xxx', 'text': 'xxx', 'create_time': 'xxx'}]
        """
        # 这里需要实现抖音 API 调用
        # 目前返回空列表作为示例
        logger.debug("获取评论（需实现 API 调用）")
        return []
    
    def reply_comment(self, comment_id, reply_text):
        """
        回复评论
        
        TODO: 实现抖音 API 调用回复评论
        """
        logger.info(f"回复评论 {comment_id}: {reply_text}")
        # 这里需要实现抖音 API 调用
        return True
    
    def send_private_message(self, user_id, message):
        """
        发送私信
        
        TODO: 实现抖音 API 调用发送私信
        """
        logger.info(f"发送私信给用户 {user_id}: {message}")
        # 这里需要实现抖音 API 调用
        return True
    
    def process_comment(self, comment):
        """处理单条评论"""
        comment_id = comment.get('comment_id')
        user_id = comment.get('user_id')
        text = comment.get('text', '')
        
        # 检查黑名单
        if self.is_blacklisted(text) and not self.is_whitelisted(user_id):
            logger.debug(f"评论包含黑名单词汇，跳过：{text[:20]}...")
            return False
        
        # 匹配关键词
        reply = self.match_keyword(text)
        
        if reply:
            # 检查每日限制
            if not self.check_daily_limit():
                return False
            
            # 延迟回复
            delay = self.config.get('reply_delay', 30)
            logger.info(f"{delay}秒后回复评论...")
            time.sleep(delay)
            
            # 回复评论
            if self.reply_comment(comment_id, reply):
                self.stats['total_replies'] += 1
                self.stats['today_replies'] += 1
                self.save_stats()
                logger.info(f"回复成功！今日已回复：{self.stats['today_replies']}/{self.config.get('daily_limit', 100)}")
                
                # 可选：发送私信
                if '私信' in reply or '已发送' in reply:
                    pm_message = "您好！这是您需要的信息..."
                    self.send_private_message(user_id, pm_message)
                
                return True
        
        return False
    
    def run(self):
        """主运行循环"""
        logger.info("=" * 50)
        logger.info("抖音自动回复助手启动中...")
        logger.info(f"每日限制：{self.config.get('daily_limit', 100)} 条")
        logger.info(f"回复延迟：{self.config.get('reply_delay', 30)} 秒")
        logger.info("=" * 50)
        
        if not self.config.get('douyin_cookie'):
            logger.error("未配置抖音 cookie，请在 config.json 中配置")
            return
        
        while True:
            try:
                # 获取评论
                comments = self.get_comments()
                logger.debug(f"获取到 {len(comments)} 条评论")
                
                # 处理每条评论
                for comment in comments:
                    self.process_comment(comment)
                
                # 等待下一轮
                check_interval = 60  # 每分钟检查一次
                logger.debug(f"{check_interval}秒后再次检查...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("用户中断，退出程序")
                break
            except Exception as e:
                logger.error(f"发生错误：{e}", exc_info=True)
                time.sleep(60)
    
    def status(self):
        """显示状态信息"""
        print("\n" + "=" * 50)
        print("📊 抖音自动回复助手 - 状态统计")
        print("=" * 50)
        print(f"总回复数：{self.stats.get('total_replies', 0)}")
        print(f"今日回复：{self.stats.get('today_replies', 0)}/{self.config.get('daily_limit', 100)}")
        print(f"最后重置：{self.stats.get('last_reset', 'N/A')}")
        
        if self.stats.get('keywords_triggered'):
            print("\n🔑 关键词触发统计:")
            for keyword, count in sorted(
                self.stats['keywords_triggered'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]:
                print(f"  {keyword}: {count} 次")
        
        print("=" * 50 + "\n")


def main():
    import sys
    
    bot = DouyinAutoReply()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start':
            bot.run()
        elif command == 'status':
            bot.status()
        elif command == 'test':
            logger.info("测试模式 - 检查配置")
            print(f"配置文件：{bot.config_path.exists()}")
            print(f"Cookie 配置：{'✓' if bot.config.get('douyin_cookie') else '✗'}")
            print(f"关键词数量：{len(bot.config.get('keywords', {}))}")
        else:
            print("用法：python douyin_bot.py [start|status|test]")
    else:
        print("用法：python douyin_bot.py [start|status|test]")
        print("  start  - 启动自动回复")
        print("  status - 查看统计状态")
        print("  test   - 测试配置")


if __name__ == '__main__':
    main()
