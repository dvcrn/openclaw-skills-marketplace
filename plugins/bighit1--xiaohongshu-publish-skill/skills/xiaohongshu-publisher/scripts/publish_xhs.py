import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from xhs import XhsClient
from xhs.help import sign as local_sign

class XHSPublisher:
    """基于 xhs 库的小红书发布器"""
    
    def __init__(self, cookie: Optional[str] = None):
        if cookie is None:
            # 从脚本文件位置向上找到 skill 根目录的 .env
            _skill_root = Path(__file__).parent.parent
            load_dotenv(_skill_root / '.env')
            self.cookie = os.getenv('XHS_COOKIE')
            if not self.cookie:
                raise ValueError("未提供Cookie且环境变量XHS_COOKIE为空。请在.env中配置XHS_COOKIE。")
        else:
            self.cookie = cookie
        
        self.client = None
        self._init_client()

    def _parse_cookie(self) -> Dict[str, str]:
        cookies = {}
        for item in self.cookie.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                cookies[key.strip()] = value.strip()
        return cookies

    def _init_client(self):
        cookies = self._parse_cookie()
        a1 = cookies.get('a1', '')
        if not a1:
            print("⚠️ 警告：Cookie 中没有解析到 a1 字段，签名可能会失败。")

        def sign_func(uri, data=None, a1_param="", web_session=""):
            return local_sign(uri, data, a1=a1 or a1_param)
        
        self.client = XhsClient(cookie=self.cookie, sign=sign_func)

    def get_self_info(self) -> Dict[str, Any]:
        """测试 Cookie 是否有效"""
        try:
            info = self.client.get_self_info()
            print(f"✅ 成功连接。当前用户：{info.get('nickname', '未知')}")
            return info
        except Exception as e:
            print(f"❌ 获取用户信息失败: {e}")
            raise

    def publish_image_note(self, title: str, desc: str, images: List[str], is_private: bool = True) -> Dict[str, Any]:
        """发布图文笔记"""
        # 预检查图片
        valid_images = [os.path.abspath(img) for img in images if os.path.exists(img)]
        if not valid_images:
            raise FileNotFoundError("未提供有效的图片路径。")
        
        if len(title) > 20:
            print(f"⚠️ 警告: 标题超过20字，将被截断")
            title = title[:20]

        print(f"🚀 准备发布笔记...")
        print(f"  📌 标题: {title}")
        print(f"  📝 描述: {desc[:30]}...")
        print(f"  🖼️ 图片数: {len(valid_images)}")

        try:
            result = self.client.create_image_note(
                title=title,
                desc=desc,
                files=valid_images,
                is_private=is_private
            )
            print("\n✨ 笔记发布成功！")
            note_id = result.get('note_id') or result.get('id')
            if note_id:
                print(f"  🔗 链接: https://www.xiaohongshu.com/explore/{note_id}")
            return result
        except Exception as e:
            print(f"\n❌ 发布失败: {e}")
            raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="小红书发布 CLI 工具")
    parser.add_argument("--title", required=True, help="笔记标题")
    parser.add_argument("--desc", default="", help="笔记正文内容")
    parser.add_argument("--images", nargs="+", required=True, help="图片路径列表")
    parser.add_argument("--public", action="store_true", help="是否公开（默认私密）")
    parser.add_argument("--dry-run", action="store_true", help="仅测试Cookie连接，不发送")
    
    args = parser.parse_args()
    
    try:
        publisher = XHSPublisher()
        publisher.get_self_info()
        if not args.dry_run:
            publisher.publish_image_note(args.title, args.desc, args.images, is_private=not args.public)
    except Exception as e:
        import sys
        sys.exit(1)
