#!/usr/bin/env bun

import { chromium, type BrowserContext, type Page } from "playwright";
import { parseArgs } from "util";
import * as path from "path";

const { values, positionals } = parseArgs({
  args: Bun.argv,
  options: {
    weibo: {
      type: "string",
    },
    xhs: {
      type: "string",
    },
    image: {
      type: "string",
      multiple: true,
    },
    topic: {
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

const weiboText = values.weibo;
const xhsText = values.xhs;
const images = values.image || [];
const topics = values.topic || [];

if (!weiboText && !xhsText) {
  console.log("用法: bun social-publisher.ts [--weibo 微博内容] [--xhs 小红书内容] [--image 图片路径] [--submit]");
  console.log("");
  console.log("示例:");
  console.log("  # 只发微博");
  console.log("  bun social-publisher.ts --weibo \"你好，微博！\"");
  console.log("  # 只发小红书");
  console.log("  bun social-publisher.ts --xhs \"你好，小红书！\" --image photo.png");
  console.log("  # 同时发布");
  console.log("  bun social-publisher.ts --weibo \"你好！\" --xhs \"你好！\" --image photo.png --submit");
  process.exit(1);
}

if (xhsText && images.length === 0) {
  console.log("⚠️  小红书推荐使用图片，但也支持纯文字发布");
}

console.log("🚀 启动社交平台发布器...");
if (weiboText) console.log(`📝 微博内容: ${weiboText}`);
if (xhsText) console.log(`📝 小红书内容: ${xhsText}`);
console.log(`🖼️  图片: ${images.length > 0 ? images.join(", ") : "(无图片)"}`);
console.log(`✅ 实际发布: ${values.submit ? "是" : "否 (预览模式)"}`);
console.log("");

// 获取 skill 目录
const SKILL_DIR = path.dirname(path.dirname(path.dirname(Bun.argv[1] || "")));
const userDataDir = values.profile || path.join(SKILL_DIR, "social-profile");

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

async function publishWeibo(page: Page, text: string, images: string[], submit: boolean) {
  console.log("🌐 [微博] 访问微博...");
  await page.goto("https://weibo.com", { waitUntil: "networkidle", timeout: 60000 });

  // 检查是否需要登录
  const loginRequired = await page.locator("text=登录").isVisible({ timeout: 5000 }).catch(() => true);
  
  if (loginRequired) {
    console.log("🔐 [微博] 请在浏览器中登录微博...");
    console.log("   登录完成后按回车键继续...");
    await new Promise(resolve => process.stdin.once("data", resolve));
  }

  console.log("✍️  [微博] 准备发布...");

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
    console.log(`📤 [微博] 上传 ${images.length} 张图片...`);
    const fileInput = page.locator('input[type="file"]').first();
    await fileInput.setInputFiles(images);
    await page.waitForTimeout(2000);
  }

  if (submit) {
    console.log("🚀 [微博] 发布中...");
    const publishBtn = page.locator("button:has-text('发送'), button:has-text('发布'), a:has-text('发送'), a:has-text('发布'), [node-type='submit'], .W_btn_a").first();
    await publishBtn.waitFor({ state: "visible", timeout: 10000 });
    await publishBtn.click();
    await page.waitForTimeout(3000);
    console.log("✅ [微博] 发布成功！");
  }
}

async function publishXiaohongshu(page: Page, text: string, images: string[], submit: boolean) {
  console.log("🌐 [小红书] 访问小红书发布页面...");
  await page.goto("https://creator.xiaohongshu.com/publish/publish?from=menu&target=article", { waitUntil: "networkidle", timeout: 60000 });

  // 检查是否需要登录
  const loginRequired = await page.locator("text=登录, text=扫码登录").isVisible({ timeout: 5000 }).catch(() => true);
  
  if (loginRequired) {
    console.log("🔐 [小红书] 请在浏览器中登录小红书...");
    console.log("   登录完成后按回车键继续...");
    await new Promise(resolve => process.stdin.once("data", resolve));
  }

  console.log("✍️  [小红书] 准备发布...");

  // 点击"新的创作"
  const newCreateBtn = page.locator(".new-btn").first();
  if (await newCreateBtn.isVisible({ timeout: 5000 })) {
    await newCreateBtn.click();
    await page.waitForTimeout(2000);
  }

  // 输入标题
  if (text) {
    console.log("📝 [小红书] 输入标题...");
    const titleBox = page.locator("textarea[placeholder*='输入标题'], input[placeholder*='输入标题']").first();
    await titleBox.waitFor({ state: "visible", timeout: 10000 });
    await titleBox.click();
    await titleBox.fill(text.substring(0, 20));
  }

  // 输入正文（带话题）
  if (text) {
    console.log("📝 [小红书] 输入正文...");
    const contentBox = page.locator("div[contenteditable='true'], textarea[placeholder*='粘贴到这里或输入文字']").first();
    await contentBox.waitFor({ state: "visible", timeout: 10000 });
    await contentBox.click();
    
    let fullText = text;
    if (topics.length > 0) {
      fullText += " " + topics.map(t => `#${t}`).join(" ");
    }
    await contentBox.fill(fullText);
  }

  // 点击一键排版
  console.log("🎨 [小红书] 点击一键排版...");
  const formatBtn = page.locator(".next-btn").first();
  if (await formatBtn.isVisible({ timeout: 5000 })) {
    await formatBtn.click();
    await page.waitForTimeout(2000);
  }

  // 选择模板（简约基础、绿色或黄色）
  console.log("🎨 [小红书] 选择模板...");
  const templateBtn = page.locator(".color-item[style*='--item-color: #FFFEEA']").first();
  if (await templateBtn.isVisible({ timeout: 5000 })) {
    await templateBtn.click();
    await page.waitForTimeout(1000);
  }

  // 点击下一步
  console.log("➡️  [小红书] 点击下一步...");
  const nextBtn = page.locator(".submit").first();
  if (await nextBtn.isVisible({ timeout: 5000 })) {
    await nextBtn.click();
    await page.waitForTimeout(2000);
  }

  // 在最后页面输入正文描述（带话题）
  if (text) {
    console.log("📝 [小红书] 输入正文描述...");
    const finalContentBox = page.locator("div[contenteditable='true'], textarea[placeholder*='正文描述'], textarea[placeholder*='真诚有价值的分享予人温暖']").first();
    await finalContentBox.waitFor({ state: "visible", timeout: 10000 });
    await finalContentBox.click();
    
    let fullText = text;
    if (topics.length > 0) {
      fullText += " " + topics.map(t => `#${t}`).join(" ");
    }
    await finalContentBox.fill(fullText);
  }

  if (submit) {
    console.log("🚀 [小红书] 发布中...");
    const submitBtn = page.locator(".bg-red").last();
    await submitBtn.waitFor({ state: "visible", timeout: 10000 });
    await submitBtn.click();
    await page.waitForTimeout(3000);
    console.log("✅ [小红书] 发布成功！");
  }
}

try {
  if (weiboText) {
    const weiboPage = browser.pages()[0] || (await browser.newPage());
    await publishWeibo(weiboPage, weiboText, images, values.submit);
    if (!values.submit) {
      console.log("👀 [微博] 预览模式 - 请在浏览器中查看");
    }
  }

  if (xhsText) {
    const xhsPage = await browser.newPage();
    await publishXiaohongshu(xhsPage, xhsText, images, values.submit);
    if (!values.submit) {
      console.log("👀 [小红书] 预览模式 - 请在浏览器中查看");
    }
  }

  if (!values.submit) {
    console.log("");
    console.log("按 Ctrl+C 退出");
    await new Promise(() => {});
  }

} catch (error) {
  console.error("❌ 出错:", error);
} finally {
  if (values.submit) {
    await browser.close();
  }
}
