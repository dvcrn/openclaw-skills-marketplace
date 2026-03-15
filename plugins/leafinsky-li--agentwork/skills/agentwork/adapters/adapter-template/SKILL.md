---
name: agentwork-adapter-template
description: "Template for creating AgentWork browser automation adapters. Clone this template and customize for any Web-only AI platform."
---

# AgentWork Adapter Template

## Quick Guide: How to create an adapter for a new platform

To add support for a new Web-only AI platform (e.g., a new AI video tool, 
a new code generator, etc.), follow this template.

## Directory Structure

```
agentwork-<platform>/
├── SKILL.md                    # Agent instructions (natural language)
├── scripts/
│   ├── config.js               # UI selectors and timing config
│   ├── health_check.js         # Verify session is valid
│   ├── check_credits.js        # Check remaining credits/quota
│   ├── execute_task.js          # Main automation script
│   └── download_result.js      # Extract and save output
├── references/
│   └── platform-notes.md       # Platform quirks and tips
└── package.json
```

## config.js Template

```javascript
module.exports = {
  // Platform identity
  platform: {
    name: "<platform>",
    url: "https://<platform>.com",
    dashboardUrl: "https://<platform>.com/dashboard",
  },

  // Browser session storage
  session: {
    dir: process.env.SESSION_DIR || "~/.openclaw/adapters/<platform>",
    file: "session.json",
  },

  // UI selectors — CUSTOMIZE THESE for your platform
  // Use multiple selectors (comma-separated) for resilience
  selectors: {
    // Login state detection
    loggedInIndicator: '[data-testid="user-menu"], .avatar, .user-profile',
    loginPage: 'form[action*="login"], .login-form',

    // Task creation
    newTaskButton: 'button:has-text("New"), button:has-text("Create")',
    taskInput: 'textarea, [contenteditable="true"]',
    submitButton: 'button:has-text("Run"), button:has-text("Generate"), button:has-text("Submit")',

    // Execution monitoring
    loadingIndicator: '.loading, .spinner, [data-status="running"]',
    completedIndicator: ':text("Done"), :text("Complete"), [data-status="complete"]',
    errorIndicator: ':text("Error"), :text("Failed"), [data-status="error"]',

    // Results extraction
    resultContainer: '.result, .output, [data-testid="result"]',
    downloadButton: 'button:has-text("Download"), a[download]',
    copyButton: 'button:has-text("Copy")',

    // Credits/quota display
    creditDisplay: '.credits, .quota, .balance',
  },

  // Timing configuration
  timing: {
    pollIntervalMs: 15000,       // How often to check task status
    maxWaitMs: 600000,           // Maximum wait for task completion (10 min)
    pageLoadTimeoutMs: 30000,    // Page load timeout
    actionDelayMs: 1000,         // Delay between UI actions (avoid detection)
    typingDelayMs: 50,           // Per-character typing delay (human-like)
  },

  // Credit management
  credits: {
    reserveMinimum: 100,         // Never go below this many credits
    estimatePerTask: {
      simple: 100,
      medium: 500,
      complex: 1000,
    },
  },
};
```

## health_check.js Template

```javascript
const { chromium } = require('playwright');
const config = require('./config');
const path = require('path');

async function healthCheck() {
  const sessionPath = path.resolve(
    config.session.dir.replace('~', process.env.HOME),
    config.session.file
  );

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ storageState: sessionPath });
  const page = await context.newPage();

  try {
    await page.goto(config.platform.dashboardUrl, {
      timeout: config.timing.pageLoadTimeoutMs,
    });

    // Check if we're logged in
    const loggedIn = await page.locator(config.selectors.loggedInIndicator)
      .first()
      .isVisible({ timeout: 5000 })
      .catch(() => false);

    if (!loggedIn) {
      console.error('✗ Session expired. Please re-login.');
      process.exit(1);
    }

    // Check credits if possible
    const creditEl = await page.locator(config.selectors.creditDisplay)
      .first()
      .textContent({ timeout: 3000 })
      .catch(() => null);

    const credits = creditEl ? creditEl.replace(/[^0-9.]/g, '') : 'unknown';

    console.log(`✓ ${config.platform.name} session valid. Credits: ${credits}`);

    // Output structured result for programmatic use
    console.log(JSON.stringify({
      status: 'healthy',
      provider: config.platform.name,
      credits_remaining: credits !== 'unknown' ? parseFloat(credits) : null,
      checked_at: new Date().toISOString(),
    }));

  } catch (err) {
    console.error(`✗ Health check failed: ${err.message}`);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

healthCheck();
```

## execute_task.js Template

```javascript
const { chromium } = require('playwright');
const config = require('./config');
const fs = require('fs');
const path = require('path');

async function executeTask(options) {
  const { taskTitle, taskDescription, inputFile, outputDir, timeout } = options;

  // Ensure output directory exists
  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(path.join(outputDir, 'artifacts'), { recursive: true });

  const sessionPath = path.resolve(
    config.session.dir.replace('~', process.env.HOME),
    config.session.file
  );

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ storageState: sessionPath });
  const page = await context.newPage();

  const executionLog = [];
  const log = (msg) => {
    const entry = `[${new Date().toISOString()}] ${msg}`;
    executionLog.push(entry);
    console.log(entry);
  };

  try {
    // 1. Navigate to dashboard
    log('Navigating to platform dashboard...');
    await page.goto(config.platform.dashboardUrl, {
      timeout: config.timing.pageLoadTimeoutMs,
    });

    // 2. Click "New Task"
    log('Creating new task...');
    await page.locator(config.selectors.newTaskButton).first().click();
    await page.waitForTimeout(config.timing.actionDelayMs);

    // 3. Input task description
    log('Entering task description...');
    const input = page.locator(config.selectors.taskInput).first();
    await input.click();

    // Build the full prompt from task details
    const fullPrompt = [
      taskTitle,
      '',
      taskDescription,
      inputFile ? `\nInput data:\n${fs.readFileSync(inputFile, 'utf-8')}` : '',
    ].join('\n');

    await input.fill(fullPrompt);
    await page.waitForTimeout(config.timing.actionDelayMs);

    // 4. Submit / Run
    log('Submitting task...');
    await page.locator(config.selectors.submitButton).first().click();

    // 5. Wait for completion
    log('Waiting for task completion...');
    const maxWait = timeout || config.timing.maxWaitMs;
    const startTime = Date.now();

    while (Date.now() - startTime < maxWait) {
      // Check for completion
      const completed = await page.locator(config.selectors.completedIndicator)
        .first()
        .isVisible({ timeout: 1000 })
        .catch(() => false);

      if (completed) {
        log('Task completed!');
        break;
      }

      // Check for errors
      const errored = await page.locator(config.selectors.errorIndicator)
        .first()
        .isVisible({ timeout: 1000 })
        .catch(() => false);

      if (errored) {
        const errorText = await page.locator(config.selectors.errorIndicator)
          .first().textContent().catch(() => 'Unknown error');
        throw new Error(`Platform execution failed: ${errorText}`);
      }

      log(`Still running... (${Math.round((Date.now() - startTime) / 1000)}s elapsed)`);
      await page.waitForTimeout(config.timing.pollIntervalMs);
    }

    if (Date.now() - startTime >= maxWait) {
      throw new Error(`Task timed out after ${maxWait / 1000} seconds`);
    }

    // 6. Extract results
    log('Extracting results...');

    // Try to get text content
    const resultText = await page.locator(config.selectors.resultContainer)
      .first()
      .textContent({ timeout: 5000 })
      .catch(() => null);

    // Try to download files
    const downloadButtons = await page.locator(config.selectors.downloadButton).all();
    const downloadedFiles = [];

    for (const btn of downloadButtons) {
      try {
        const [download] = await Promise.all([
          page.waitForEvent('download', { timeout: 10000 }),
          btn.click(),
        ]);
        const filePath = path.join(outputDir, 'artifacts', download.suggestedFilename());
        await download.saveAs(filePath);
        downloadedFiles.push(filePath);
        log(`Downloaded: ${download.suggestedFilename()}`);
      } catch (e) {
        log(`Download attempt failed: ${e.message}`);
      }
    }

    // 7. Take proof screenshot
    const screenshotPath = path.join(outputDir, 'screenshot.png');
    await page.screenshot({ path: screenshotPath, fullPage: false });
    log('Proof screenshot saved.');

    // 8. Build result
    const result = {
      status: 'success',
      provider: config.platform.name,
      output_text: resultText,
      output_files: downloadedFiles,
      screenshot: screenshotPath,
      execution_time_seconds: Math.round((Date.now() - startTime) / 1000),
      completed_at: new Date().toISOString(),
    };

    fs.writeFileSync(
      path.join(outputDir, 'result.json'),
      JSON.stringify(result, null, 2)
    );

    // Save execution log
    fs.writeFileSync(
      path.join(outputDir, 'execution_log.txt'),
      executionLog.join('\n')
    );

    log('Task execution complete.');
    console.log(JSON.stringify(result));

  } catch (err) {
    log(`ERROR: ${err.message}`);

    // Save error screenshot
    await page.screenshot({
      path: path.join(outputDir, 'error_screenshot.png'),
      fullPage: false,
    }).catch(() => {});

    const errorResult = {
      status: 'error',
      provider: config.platform.name,
      error: err.message,
      execution_time_seconds: Math.round((Date.now() - Date.now()) / 1000),
    };

    fs.writeFileSync(
      path.join(outputDir, 'result.json'),
      JSON.stringify(errorResult, null, 2)
    );
    fs.writeFileSync(
      path.join(outputDir, 'execution_log.txt'),
      executionLog.join('\n')
    );

    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Parse CLI args
const args = process.argv.slice(2);
const getArg = (name) => {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 ? args[idx + 1] : undefined;
};

executeTask({
  taskTitle: getArg('task-title') || 'Untitled Task',
  taskDescription: getArg('task-description') || '',
  inputFile: getArg('task-input-file'),
  outputDir: getArg('output-dir') || '/tmp/agentwork/output',
  timeout: getArg('timeout') ? parseInt(getArg('timeout')) * 1000 : undefined,
});
```

## Creating a New Adapter: Checklist

1. [ ] Clone this template: `cp -r agentwork-adapter-template agentwork-<platform>`
2. [ ] Update `config.js`:
   - [ ] Set platform name and URLs
   - [ ] Map all UI selectors by inspecting the platform's DOM
   - [ ] Adjust timing for the platform's typical execution speed
   - [ ] Set credit estimation per task type
3. [ ] Test `health_check.js`:
   - [ ] Manually log in and save session
   - [ ] Verify the script detects logged-in state
   - [ ] Verify credit reading works
4. [ ] Test `execute_task.js`:
   - [ ] Run a simple test task end-to-end
   - [ ] Verify output extraction works (text + file downloads)
   - [ ] Verify screenshot capture
5. [ ] Write the `SKILL.md`:
   - [ ] Describe setup instructions for the operator
   - [ ] Document the automation flow
   - [ ] Add credit estimation guidelines
   - [ ] List known quirks and troubleshooting steps
6. [ ] Test the full loop:
   - [ ] AgentWork task → Adapter → Platform → Result → Submit → Oracle
7. [ ] Publish to ClawHub: `clawhub publish agentwork-<platform>`
