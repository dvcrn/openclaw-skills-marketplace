import asyncio
import os
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Page, BrowserContext

# Skill 根目录（scripts/ 的上一级）
_SKILL_ROOT = Path(__file__).parent.parent

class XHSInteractor:
    """基于 Playwright 的小红书网页互动器"""
    
    def __init__(self, user_data_dir: Optional[str] = None):
        # 默认将浏览器数据存在 skill 根目录下，保证路径与调用位置无关
        if user_data_dir is None:
            user_data_dir = str(_SKILL_ROOT / 'xhs_browser_data')
        self.user_data_dir = os.path.abspath(user_data_dir)
        self.playwright = None
        self.context: BrowserContext = None
        self.page: Page = None
        
    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def start(self, headless: bool = False):
        """启动浏览器"""
        print(f"🚀 启动 Playwright 浏览器以加载配置: {self.user_data_dir}")
        self.playwright = await async_playwright().start()
        
        # 使用 persistent context 保留登录状态
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=headless,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 获取现有的页面，或者新建
        pages = self.context.pages
        self.page = pages[0] if pages else await self.context.new_page()

        # 隐藏 webdriver 特征
        await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    async def close(self):
        """关闭浏览器"""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        print("🛑 浏览器已关闭。")

    async def check_login(self) -> bool:
        """检查是否已登录"""
        await self.page.goto("https://www.xiaohongshu.com/")
        await self.page.wait_for_load_state("networkidle")
        
        # 通过检查页面是否包含明确的未登录特征（比如登录弹窗或者导航栏缺少头像）
        # 此处简化为等待包含用户信息或登录按钮的元素
        
        try:
            # 尝试找头像或对应的已登录元素
            # .user-avatar 或者类似的容器
            await self.page.wait_for_selector(".login-btn", timeout=3000)
            print("⚠️ 未登录小红书。请手动扫描二维码登录。")
            return False
        except:
            print("✅ 似乎已处于登录状态。")
            return True

    async def manual_login_wait(self):
        """等待用户手动进行扫码等操作"""
        print("⏳ 请在打开的浏览器中手动登录...完成后按任意键.")
        await self.page.goto("https://www.xiaohongshu.com/")
        # 在脚本中暂停等待用户终端输入
        await asyncio.to_thread(input, "等待登录完成中，完成后请回车继续...")


    async def search_and_browse(self, keyword: str):
        """搜索关键词并进入第一个结果（示例）"""
        print(f"🔍 搜索关键词: {keyword}")
        await self.page.goto(f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes")
        await self.page.wait_for_load_state("networkidle")
        
        # 等待笔记卡片出现
        try:
            await self.page.wait_for_selector("section.note-item", timeout=10000)
            print("✅ 搜索结果已加载。")
            
            # 找到第一个笔记的详情链接并点击
            first_note = self.page.locator("section.note-item a.cover").first
            href = await first_note.get_attribute("href")
            print(f"📂 尝试进入第一个笔记: {href}")
            
            await first_note.click()
            await asyncio.sleep(2) # 简单等待动画
            
            # 等待弹出的详情页模态框加载
            await self.page.wait_for_selector(".note-detail-mask", timeout=5000)
            print("📄 详情已打开。")
            
        except Exception as e:
            print(f"❌ 搜索或点击失败: {e}")

    async def add_comment(self, text: str):
        """在当前打开的笔记详情页新增评论"""
        print(f"💬 尝试评论: {text}")
        try:
            # 检查评论输入框
            input_locator = self.page.locator("p.content-input") # XHS 常用富文本评论框
            if await input_locator.count() > 0:
                await input_locator.click()
                await input_locator.fill(text)
                await asyncio.sleep(0.5)
                
                # 发送按钮
                submit_btn = self.page.locator(".submit-btn")
                await submit_btn.click()
                print("✅ 评论已发送。")
            else:
                print("⚠️ 没找到评论输入框，可能该笔记禁评或改版。")
        except Exception as e:
            print(f"❌ 评论失败: {e}")


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="小红书网页互动工具")
    parser.add_argument("--login", action="store_true", help="启动有头浏览器进行初始登录")
    args = parser.parse_args()

    async with XHSInteractor() as interactor:
        if args.login:
            # 强制用有头模式开浏览器，人工登录
            await interactor.close() # 先关掉默认启动的
            await interactor.start(headless=False)
            is_logged_in = await interactor.check_login()
            if not is_logged_in:
                await interactor.manual_login_wait()
            else:
                print("🎉 您已登录！可以退出此步骤。")
        else:
            # 比如做个搜索样例
            await interactor.start(headless=False) # 调试建议开有头
            if await interactor.check_login():
                await interactor.search_and_browse("自动化编程")
            await asyncio.sleep(5) # 看看结果


if __name__ == "__main__":
    asyncio.run(main())
