#!/usr/bin/env bun

import { chromium } from "playwright";
import { parseArgs } from "util";
import * as path from "path";

const { values, positionals } = parseArgs({
  args: Bun.argv,
  options: {
    image: {
      type: "string",
      multiple: true,
    },
    submit: {
      type: "boolean",
      default: false,
    },
    profile: {
      type: "string",
    },
  },
  strict: true,
  allowPositionals: true,
});

const text = positionals.slice(2).join(" ");
const images = values.image || [];

if (!text && images.length === 0) {
  console.log("用法: bun weibo-publisher.ts <文字内容> [--image 图片路径] [--submit]");
  console.log("");
  console.log("示例:");
  console.log("  bun weibo-publisher.ts \"你好，微博！\"");
  console.log("  bun weibo-publisher.ts \"看这张图！\" --image photo.png");
  console.log("  bun weibo-publisher.ts \"发布微博！\" --image photo.png --submit");
  process.exit(1);
}

console.log("🚀 启动微博发布器...");
console.log(`📝 内容: ${text || "(无文字)"}`);
console.log(`🖼️  图片: ${images.length > 0 ? images.join(", ") : "(无图片)"}`);
console.log(`✅ 实际发布: ${values.submit ? "是" : "否 (预览模式)"}`);
console.log("");

// 获取 skill 目录
const SKILL_DIR = path.dirname(path.dirname(path.dirname(Bun.argv[1] || "")));
const userDataDir = values.profile || path.join(SKILL_DIR, "weibo-profile");

// 自动检测 Chrome 路径
let executablePath: string | undefined;
if (process.platform === "darwin") {
  executablePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
} else if (process.platform === "linux") {
  executablePath = "/usr/bin/google-chrome";
} else if (process.platform === "win32") {
  executablePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
}

const browser = await chromium.launchPersistentContext(userDataDir, {
  headless: false,
  executablePath,
  channel: !executablePath ? "chrome" : undefined,
  viewport: { width: 1280, height: 800 },
});

const page = browser.pages()[0] || (await browser.newPage());

try {
  console.log("🌐 访问微博...");
  await page.goto("https://weibo.com", { waitUntil: "networkidle", timeout: 60000 });

  // 检查是否需要登录
  const loginRequired = await page.locator("text=登录").isVisible({ timeout: 5000 }).catch(() => true);
  
  if (loginRequired) {
    console.log("🔐 请在浏览器中登录微博...");
    console.log("   登录完成后按回车键继续...");
    await new Promise(resolve => process.stdin.once("data", resolve));
  }

  console.log("✍️  准备发布...");

  // 点击发布框
  await page.waitForSelector("textarea[placeholder*='有什么新鲜事'], div[contenteditable='true']", { timeout: 10000 });
  
  const editBox = page.locator("textarea[placeholder*='有什么新鲜事'], div[contenteditable='true']").first();
  await editBox.click();
  
  // 输入文字
  if (text) {
    await editBox.fill(text);
  }

  // 上传图片
  if (images.length > 0) {
    console.log(`📤 上传 ${images.length} 张图片...`);
    const fileInput = page.locator('input[type="file"]').first();
    await fileInput.setInputFiles(images);
    await page.waitForTimeout(2000);
  }

  if (values.submit) {
    console.log("🚀 发布中...");
    // 尝试多种选择器
    const publishBtn = page.locator("button:has-text('发送'), button:has-text('发布'), a:has-text('发送'), a:has-text('发布'), [node-type='submit'], .W_btn_a").first();
    await publishBtn.waitFor({ state: "visible", timeout: 10000 });
    await publishBtn.click();
    await page.waitForTimeout(3000);
    console.log("✅ 发布成功！");
  } else {
    console.log("👀 预览模式 - 请在浏览器中查看，按 Ctrl+C 退出");
    await new Promise(() => {});
  }

} catch (error) {
  console.error("❌ 出错:", error);
} finally {
  if (values.submit) {
    await browser.close();
  }
}
