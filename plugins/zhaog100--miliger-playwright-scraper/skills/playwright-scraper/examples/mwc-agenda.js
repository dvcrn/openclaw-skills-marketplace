/**
 * MWC议程爬取示例
 * 演示如何使用Playwright爬取多Tab、懒加载的会议议程
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function scrapeMWCAgenda() {
  console.log('喏，官家！开始爬取MWC议程！');

  // 启动浏览器（持久化Profile）
  const browser = await chromium.launchPersistentContext('./chrome-profile', {
    headless: false, // 调试时可见
    viewport: { width: 1920, height: 1080 }
  });

  const page = browser.pages()[0] || await browser.newPage();

  try {
    // 访问MWC议程页面
    console.log('访问MWC议程页面...');
    await page.goto('https://mwcbarcelona.com/agenda', {
      waitUntil: 'networkidle'
    });

    // 等待页面加载
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000); // 额外等待3秒

    // 定义日期Tab
    const dateTabs = ['PRE', 'MON', 'TUE', 'WED', 'THU'];
    const allSessions = {};

    // 循环点击每个Tab
    for (const dateTab of dateTabs) {
      console.log(`\n处理 ${dateTab} Tab...`);

      try {
        // 定位并点击日期按钮
        const tabButton = await page.locator(`text="${dateTab}"`).first();
        await tabButton.click();

        // 等待内容加载
        await page.waitForTimeout(2000);

        // 滚动到底部（触发懒加载）
        await scrollToloadAll(page);

        // 提取所有session数据
        const sessions = await extractSessions(page);

        allSessions[dateTab] = sessions;
        console.log(`  提取了 ${sessions.length} 个session`);

      } catch (error) {
        console.error(`  ${dateTab} Tab处理失败: ${error.message}`);
        allSessions[dateTab] = [];
      }
    }

    // 保存数据
    await saveData(allSessions);

    console.log('\n✅ 爬取完成！数据已保存。');

  } catch (error) {
    console.error('爬取失败:', error);
  } finally {
    await browser.close();
  }
}

/**
 * 滚动页面直到所有内容加载
 */
async function scrollToloadAll(page) {
  let previousHeight = 0;
  let currentHeight = await page.evaluate(() => document.body.scrollHeight);

  while (previousHeight !== currentHeight) {
    previousHeight = currentHeight;

    // 滚动到底部
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });

    // 等待新内容加载
    await page.waitForTimeout(1000);

    // 检查新高度
    currentHeight = await page.evaluate(() => document.body.scrollHeight);
  }
}

/**
 * 提取所有session数据
 */
async function extractSessions(page) {
  return await page.evaluate(() => {
    const sessions = [];

    // 这里需要根据实际页面结构调整选择器
    // 示例：假设每个session是一个.session元素
    document.querySelectorAll('.session').forEach(sessionEl => {
      const title = sessionEl.querySelector('.session-title')?.textContent?.trim();
      const time = sessionEl.querySelector('.session-time')?.textContent?.trim();
      const location = sessionEl.querySelector('.session-location')?.textContent?.trim();
      const speakers = Array.from(sessionEl.querySelectorAll('.speaker-name'))
        .map(el => el.textContent?.trim())
        .filter(Boolean);

      if (title) {
        sessions.push({
          title,
          time: time || 'N/A',
          location: location || 'N/A',
          speakers: speakers.length > 0 ? speakers : ['N/A']
        });
      }
    });

    return sessions;
  });
}

/**
 * 保存数据到文件
 */
async function saveData(allSessions) {
  // 确保目录存在
  const outputDir = './mwc-agenda';
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // 按日期保存Markdown文件
  for (const [date, sessions] of Object.entries(allSessions)) {
    const filename = path.join(outputDir, `${date}.md`);

    let markdown = `# MWC ${date} 议程\n\n`;
    markdown += `> 抓取时间: ${new Date().toLocaleString('zh-CN')}\n\n`;
    markdown += `## Session列表 (${sessions.length}个)\n\n`;

    sessions.forEach((session, index) => {
      markdown += `### ${index + 1}. ${session.title}\n\n`;
      markdown += `- **时间**: ${session.time}\n`;
      markdown += `- **地点**: ${session.location}\n`;
      if (session.speakers[0] !== 'N/A') {
        markdown += `- **演讲者**: ${session.speakers.join(', ')}\n`;
      }
      markdown += `\n`;
    });

    fs.writeFileSync(filename, markdown);
    console.log(`  保存: ${filename}`);
  }

  // 保存汇总JSON
  const summaryPath = path.join(outputDir, 'all-sessions.json');
  fs.writeFileSync(summaryPath, JSON.stringify(allSessions, null, 2));
  console.log(`  保存汇总: ${summaryPath}`);
}

// 运行
scrapeMWCAgenda().catch(console.error);
