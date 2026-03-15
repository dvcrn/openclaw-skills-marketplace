#!/usr/bin/env node

/**
 * import-tasks.js
 *
 * 批量导入 Linso Task 导出的 openclaw cron add 命令。
 *
 * 用法:
 *   echo "命令文本" | node import-tasks.js
 *   node import-tasks.js < exported-commands.txt
 *   node import-tasks.js exported-commands.txt
 */

const { execSync } = require("child_process");
const { readFileSync } = require("fs");
const { createInterface } = require("readline");

async function readInput() {
  const args = process.argv.slice(2);

  // 从文件读取
  if (args.length > 0) {
    try {
      return readFileSync(args[0], "utf-8");
    } catch (err) {
      console.error(`无法读取文件: ${args[0]}`);
      console.error(err.message);
      process.exit(1);
    }
  }

  // 从 stdin 读取
  if (!process.stdin.isTTY) {
    return readFileSync("/dev/stdin", "utf-8");
  }

  // 交互模式
  console.log("请粘贴 Linso Task 导出的命令（输入空行结束）：\n");

  return new Promise((resolve) => {
    const rl = createInterface({ input: process.stdin, output: process.stdout });
    const lines = [];
    let emptyCount = 0;

    rl.on("line", (line) => {
      if (line.trim() === "") {
        emptyCount++;
        if (emptyCount >= 2) {
          rl.close();
          return;
        }
      } else {
        emptyCount = 0;
      }
      lines.push(line);
    });

    rl.on("close", () => resolve(lines.join("\n")));
  });
}

function parseCommands(text) {
  const commands = [];
  let current = "";

  for (const line of text.split("\n")) {
    const trimmed = line.trim();

    // 跳过空行和注释
    if (!trimmed || trimmed.startsWith("#")) {
      if (current) {
        commands.push(current);
        current = "";
      }
      continue;
    }

    // 处理续行符
    if (trimmed.endsWith("\\")) {
      current += (current ? " " : "") + trimmed.slice(0, -1).trim();
    } else {
      current += (current ? " " : "") + trimmed;
      commands.push(current);
      current = "";
    }
  }

  if (current) {
    commands.push(current);
  }

  // 只保留 openclaw cron add 命令
  return commands.filter((cmd) => cmd.includes("openclaw cron add"));
}

function extractName(cmd) {
  const match = cmd.match(/--name\s+["']([^"']+)["']/);
  return match ? match[1] : cmd.slice(0, 50) + "...";
}

async function main() {
  const input = await readInput();

  if (!input || !input.trim()) {
    console.error("未收到任何输入。");
    console.error("");
    console.error("用法:");
    console.error("  echo '命令' | node import-tasks.js");
    console.error("  node import-tasks.js exported-commands.txt");
    console.error("  node import-tasks.js  (交互模式)");
    process.exit(1);
  }

  const commands = parseCommands(input);

  if (commands.length === 0) {
    console.error("未找到有效的 openclaw cron add 命令。");
    process.exit(1);
  }

  console.log(`\n找到 ${commands.length} 条任务命令，开始导入...\n`);

  let success = 0;
  let failed = 0;
  const errors = [];

  for (let i = 0; i < commands.length; i++) {
    const cmd = commands[i];
    const name = extractName(cmd);
    const index = `[${i + 1}/${commands.length}]`;

    process.stdout.write(`${index} ${name} ... `);

    try {
      execSync(cmd, {
        stdio: ["pipe", "pipe", "pipe"],
        timeout: 30000,
        encoding: "utf-8",
      });
      console.log("OK");
      success++;
    } catch (err) {
      const errMsg = err.stderr || err.message || "未知错误";
      console.log("FAILED");
      errors.push({ index: i + 1, name, error: errMsg.trim() });
      failed++;
    }
  }

  // 输出报告
  console.log("\n" + "=".repeat(50));
  console.log("导入完成");
  console.log("=".repeat(50));
  console.log(`  成功: ${success}`);
  console.log(`  失败: ${failed}`);
  console.log(`  总计: ${commands.length}`);

  if (errors.length > 0) {
    console.log("\n失败详情:");
    for (const e of errors) {
      console.log(`  #${e.index} ${e.name}`);
      console.log(`     ${e.error}`);
    }
  }

  console.log("\n提示: 运行 `openclaw cron list` 查看已导入的任务");

  process.exit(failed > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error("导入脚本出错:", err.message);
  process.exit(1);
});
