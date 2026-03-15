#!/usr/bin/env node
/**
 * Xiaohongshu (小红书) Auto-Publish Script
 * 
 * Automates image+text post publishing on xiaohongshu.com creator platform.
 * Uses Playwright CDP to connect to an already-running browser instance.
 * 
 * Usage:
 *   node publish.js --title "标题" --body "正文内容" --images img1.png,img2.png [--cdp-url http://127.0.0.1:9222] [--publish]
 * 
 * Requirements:
 *   - playwright-core (npm install playwright-core)
 *   - A Chromium browser running with remote debugging (CDP)
 *   - Already logged in to creator.xiaohongshu.com
 * 
 * The script will NOT click publish unless --publish flag is set.
 * By default it fills everything and takes a screenshot for review.
 */

const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');

// --- Argument Parsing ---
function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    title: '',
    body: '',
    images: [],
    cdpUrl: process.env.XHS_CDP_URL || 'http://127.0.0.1:9222',
    publish: true,
    screenshot: '',
    hashtags: [],
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--title':
        opts.title = args[++i] || '';
        break;
      case '--body':
        opts.body = args[++i] || '';
        break;
      case '--body-file':
        opts.body = fs.readFileSync(args[++i], 'utf-8').trim();
        break;
      case '--images':
        opts.images = (args[++i] || '').split(',').map(s => s.trim()).filter(Boolean);
        break;
      case '--cdp-url':
        opts.cdpUrl = args[++i] || opts.cdpUrl;
        break;
      case '--dry-run':
        opts.publish = false;
        break;
      case '--screenshot':
        opts.screenshot = args[++i] || '';
        break;
      case '--hashtags':
        opts.hashtags = (args[++i] || '').split(',').map(s => s.trim()).filter(Boolean);
        break;
      case '--help':
        console.log(`
Xiaohongshu Auto-Publish

Usage:
  node publish.js --title "标题" --body "正文" --images img1.png,img2.png [options]

Options:
  --title <text>        Post title (max 20 chars)
  --body <text>         Post body text (max 1000 chars)
  --body-file <path>    Read body from a text file instead
  --images <paths>      Comma-separated image paths (1-18 images)
  --hashtags <tags>     Comma-separated hashtags (e.g. "AI绘画,塔罗牌")
  --cdp-url <url>       Chrome CDP endpoint (default: http://127.0.0.1:9222)
                        Can also set XHS_CDP_URL env var
  --dry-run             Preview only, don't click publish (default: auto-publish)
  --screenshot <path>   Save preview screenshot to this path
  --help                Show this help
        `);
        process.exit(0);
    }
  }

  return opts;
}

// --- Validation ---
function validate(opts) {
  const errors = [];
  if (!opts.title) errors.push('--title is required');
  if (opts.title.length > 20) errors.push(`Title too long: ${opts.title.length}/20 chars`);
  if (!opts.body && !opts.hashtags.length) errors.push('--body or --hashtags is required');
  if (opts.body.length > 1000) errors.push(`Body too long: ${opts.body.length}/1000 chars`);
  if (opts.images.length === 0) errors.push('--images is required (at least 1 image)');
  if (opts.images.length > 18) errors.push(`Too many images: ${opts.images.length}/18`);
  
  for (const img of opts.images) {
    if (!fs.existsSync(img)) errors.push(`Image not found: ${img}`);
  }

  if (errors.length) {
    console.error('Validation errors:');
    errors.forEach(e => console.error(`  ✖ ${e}`));
    process.exit(1);
  }
}

// --- Main ---
async function main() {
  const opts = parseArgs();
  validate(opts);

  // Append hashtags to body
  let fullBody = opts.body;
  if (opts.hashtags.length) {
    const tags = opts.hashtags.map(t => t.startsWith('#') ? t : `#${t}`).join(' ');
    fullBody = fullBody ? `${fullBody}\n\n${tags}` : tags;
  }

  console.log('🔗 Connecting to browser at', opts.cdpUrl);
  let browser;
  try {
    browser = await chromium.connectOverCDP(opts.cdpUrl);
  } catch (e) {
    console.error(`✖ Cannot connect to CDP at ${opts.cdpUrl}`);
    console.error('  Make sure a Chromium browser is running with remote debugging enabled.');
    console.error('  For OpenClaw users: the managed browser (profile "openclaw") exposes CDP automatically.');
    process.exit(1);
  }

  const ctx = browser.contexts()[0];
  if (!ctx) {
    console.error('✖ No browser context found');
    process.exit(1);
  }

  const page = await ctx.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });

  try {
    // Step 1: Navigate to publish page
    console.log('📄 Opening publish page...');
    await page.goto('https://creator.xiaohongshu.com/publish/publish?source=official', {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    });
    await page.waitForTimeout(3000);

    // Check if redirected (not logged in)
    if (!page.url().includes('/publish')) {
      console.error('✖ Redirected to', page.url());
      console.error('  You may not be logged in. Please log in to creator.xiaohongshu.com first.');
      process.exit(1);
    }
    console.log('✔ Publish page loaded');

    // Step 2: Click "上传图文" tab
    console.log('📸 Switching to image post mode...');
    const tabClicked = await page.evaluate(() => {
      const els = document.querySelectorAll('*');
      for (const el of els) {
        if (el.childElementCount === 0 && el.textContent.trim() === '上传图文') {
          el.click();
          return true;
        }
      }
      return false;
    });
    if (!tabClicked) {
      console.error('✖ Cannot find "上传图文" tab');
      process.exit(1);
    }
    await page.waitForTimeout(2000);
    console.log('✔ Image post mode selected');

    // Step 3: Upload images
    console.log(`🖼️  Uploading ${opts.images.length} image(s)...`);
    const fi = await page.$('input[type="file"]');
    if (!fi) {
      console.error('✖ Cannot find file upload input');
      process.exit(1);
    }
    
    // Force accept images and multiple
    await fi.evaluate(el => { el.accept = 'image/*'; el.multiple = true; });
    
    // Resolve absolute paths
    const absPaths = opts.images.map(p => path.resolve(p));
    
    if (absPaths.length === 1) {
      await fi.setInputFiles(absPaths[0]);
    } else {
      await fi.setInputFiles(absPaths);
    }
    
    // Wait for upload processing
    await page.waitForTimeout(Math.min(absPaths.length * 2000, 15000));
    console.log('✔ Images uploaded');

    // Step 4: Set title
    console.log('✏️  Setting title...');
    const titleSet = await page.evaluate((title) => {
      const el = document.querySelector('input[placeholder*="标题"]') || document.querySelector('input.d-text');
      if (!el) return false;
      const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      setter.call(el, title);
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    }, opts.title);
    
    if (!titleSet) {
      console.error('✖ Cannot find title input (page may not have loaded fully)');
      process.exit(1);
    }
    console.log('✔ Title set');

    // Step 5: Set body
    console.log('📝 Setting body...');
    const bodyHtml = fullBody.split('\n').map(line => `<p>${line || ''}</p>`).join('');
    const bodySet = await page.evaluate((html) => {
      const el = document.querySelector('[contenteditable="true"]');
      if (!el) return false;
      el.innerHTML = html;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      return true;
    }, bodyHtml);

    if (!bodySet) {
      console.error('✖ Cannot find content editor');
      process.exit(1);
    }
    console.log('✔ Body set');

    await page.waitForTimeout(2000);

    // Step 6: Screenshot preview
    const screenshotPath = opts.screenshot || `/tmp/xhs-preview-${Date.now()}.png`;
    await page.screenshot({ path: screenshotPath });
    console.log(`📸 Preview saved: ${screenshotPath}`);

    // Step 7: Publish (if flag set)
    if (opts.publish) {
      console.log('🚀 Publishing...');
      const published = await page.evaluate(() => {
        const btns = document.querySelectorAll('button');
        for (const btn of btns) {
          if (btn.textContent.trim() === '发布' && !btn.disabled) {
            btn.click();
            return true;
          }
        }
        return false;
      });
      if (published) {
        await page.waitForTimeout(3000);
        console.log('✔ Publish button clicked!');
      } else {
        console.error('✖ Could not find or click publish button');
      }
    } else {
      console.log('ℹ️  Dry-run mode — remove --dry-run to auto-publish');
    }

    console.log('\n✅ Done!');

  } catch (e) {
    console.error('Error:', e.message);
    const errShot = `/tmp/xhs-error-${Date.now()}.png`;
    await page.screenshot({ path: errShot }).catch(() => {});
    console.error(`Error screenshot: ${errShot}`);
    process.exit(1);
  }
}

main();
