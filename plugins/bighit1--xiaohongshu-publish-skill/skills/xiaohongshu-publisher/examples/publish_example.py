"""
示例：使用 XHSPublisher 类直接发布图文笔记
运行方式：.\venv\Scripts\python.exe examples\publish_example.py
"""
from pathlib import Path
import sys

# 将 scripts 目录加入模块搜索路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from publish_xhs import XHSPublisher

def main():
    # 初始化（自动从 .env 中读取 XHS_COOKIE）
    publisher = XHSPublisher()
    
    # 验证 Cookie 是否有效
    print("=== 验证登录状态 ===")
    publisher.get_self_info()

    # 发布一条私密笔记用于测试
    print("\n=== 发布测试笔记 ===")
    result = publisher.publish_image_note(
        title="测试笔记（请忽略）",
        desc="这是一条用于测试的私密笔记，不会展示给其他用户。\n\n#测试",
        images=["test.jpg"],   # 替换为真实图片路径
        is_private=True        # 仅自己可见
    )
    
    print("\n=== 发布完成 ===")
    print(f"返回结果: {result}")

if __name__ == "__main__":
    main()
