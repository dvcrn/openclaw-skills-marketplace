#!/usr/bin/env node

/**
 * Research Report Download Script
 *
 * **Get API Key** from [https://pc.yanbaoke.cn/openclaw](https://pc.yanbaoke.cn/openclaw) (required for download) / 前往 https://pc.yanbaoke.cn/openclaw 获取 API Key（下载必需）
 * Usage:
 *   node download.mjs <uuid> [api_key] [options]
 *
 * Environment variables:
 *   YANBAOKE_API_KEY - Default API key (can be overridden by argument)
 *   YANBAOKE_DOWNLOAD_DIR - Default download directory (default: ./downloads)
 *
 * Examples:
 *   node download.mjs "abc123-def456"
 *   node download.mjs "abc123-def456" "sk-your-api-key"
 *   node download.mjs "abc123-def456" -d              # Auto download to ./downloads
 *   node download.mjs "abc123-def456" -d -o ./reports # Download to ./reports
 */

function usage() {
  console.error(`Usage: download.mjs <uuid> [api_key] [options]

Arguments:
  uuid              Report UUID (required)
  api_key           API key for authentication (optional, uses YANBAOKE_API_KEY env var)

Options:
  -d, --download    Auto download the file to local disk
  -o, --output <dir> Output directory for downloaded files (default: ./downloads)
  -h, --help        Show this help message

Environment Variables:
  YANBAOKE_API_KEY      Default API key for authentication
  YANBAOKE_DOWNLOAD_DIR Default download directory (default: ./downloads)

Examples:
  node {baseDir}/scripts/download.mjs "abc123-def456"
  node {baseDir}/scripts/download.mjs "abc123-def456" "sk-your-api-key"
  node {baseDir}/scripts/download.mjs "abc123-def456" -d
  node {baseDir}/scripts/download.mjs "abc123-def456" -d -o ./reports

Note: You can get your API key from https://pc.yanbaoke.cn/openclaw`);
  process.exit(2);
}

const args = process.argv.slice(2);

if (args.length === 0 || args.includes("-h") || args.includes("--help")) usage();

const uuid = args[0];
let apiKey = "";
let autoDownload = false;
let outputDir = process.env.YANBAOKE_DOWNLOAD_DIR ?? "./downloads";

// Parse arguments
for (let i = 1; i < args.length; i++) {
  const arg = args[i];
  if (arg === "-d" || arg === "--download") {
    autoDownload = true;
  } else if (arg === "-o" || arg === "--output") {
    outputDir = args[++i];
  } else if (!arg.startsWith("-")) {
    apiKey = arg;
  }
}

apiKey = apiKey || process.env.YANBAOKE_API_KEY || "";

if (!uuid) {
  console.error("Error: UUID is required");
  usage();
}

if (!apiKey) {
  console.error("Error: API key is required. Provide it as an argument or set YANBAOKE_API_KEY environment variable.");
  console.error("\nGet your API key from: https://pc.yanbaoke.cn/openclaw");
  process.exit(1);
}

try {
  const resp = await fetch(`https://api.yanbaoke.cn/skills/report_download/${uuid}`, {
    headers: {
      "Authorization": `Bearer ${apiKey}`
    }
  });

  const body = await resp.json().catch(() => null);

  if (!resp.ok) {
    const errorMsg = body?.error?.message ?? body?.message ?? `HTTP ${resp.status}`;
    console.error(`Error: ${errorMsg}`);
    process.exit(1);
  }

  let report;
  // 检查是否是 OpenAI 格式响应
  if (body?.choices && body.choices[0]?.report) {
    report = body.choices[0].report;
  } else if (body?.download_url) {
    report = body;
  } else {
    console.error("Unexpected response format");
    console.error(JSON.stringify(body, null, 2));
    process.exit(1);
  }

  const { download_url, title, filename } = report;

  if (autoDownload) {
    // 自动下载到本地
    import('path').then(({ join, resolve }) => {
      import('fs').then(({ mkdirSync, writeFileSync }) => {
        // 创建下载目录
        const absoluteOutputDir = resolve(outputDir);
        mkdirSync(absoluteOutputDir, { recursive: true });

        // 下载文件
        console.log(`## Downloading report...\n`);
        console.log(`**Title**: ${title}`);
        console.log(`**Filename**: ${filename}`);
        console.log(`**Save to**: ${absoluteOutputDir}\n`);

        fetch(download_url)
          .then(fileResp => {
            if (!fileResp.ok) {
              throw new Error(`Failed to download file (HTTP ${fileResp.status})`);
            }
            return fileResp.arrayBuffer();
          })
          .then(buffer => {
            const filepath = join(absoluteOutputDir, filename);
            writeFileSync(filepath, Buffer.from(buffer));

            console.log(`## Download Complete!\n`);
            console.log(`**File saved**: ${filepath}`);
            console.log(`**File size**: ${(buffer.length / 1024).toFixed(2)} KB`);
            console.log(`\nYou can open the file with:`);
            console.log(`  open "${filepath}"`);
          })
          .catch(err => {
            console.error(`Error: ${err.message}`);
            process.exit(1);
          });
      });
    });
  } else {
    // 默认行为：显示下载链接
    console.log(`## Report Download Link\n`);
    console.log(`**Title**: ${title}`);
    console.log(`**Filename**: ${filename}`);
    console.log(`**Expires in**: ${report.expires_in ?? 60} seconds\n`);
    console.log(`**Download URL** (click to download):`);
    console.log(`${download_url}\n`);
    console.log(`---\n`);
    console.log(`*Note: This download link expires in 60 seconds.*`);
    console.log(`*Tip: Use -d flag to auto-download to local disk*`);
  }

} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
