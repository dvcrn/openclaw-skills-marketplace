// ========================
// 列出事件
// ========================
// 用法: bun run scripts/list-events.ts [--limit <n>] [--offset <n>] [--json]

import { getPublicClobClient, jsonStringify } from "./config";

const USAGE = `用法: bun run scripts/list-events.ts [--limit <n>] [--offset <n>] [--json]

示例:
  bun run scripts/list-events.ts
  bun run scripts/list-events.ts --limit 10
  bun run scripts/list-events.ts --limit 5 --offset 10 --json`;

function parseIntFlag(args: string[], flag: string, defaultVal: number): number {
  const idx = args.indexOf(flag);
  if (idx !== -1 && args[idx + 1]) return parseInt(args[idx + 1], 10);
  return defaultVal;
}

async function listEvents(limit: number, offset: number, jsonMode: boolean) {
  const client = getPublicClobClient();
  const result = await client.getEvents({ limit, offset });

  if (jsonMode) {
    console.log(jsonStringify(result));
    return;
  }

  const events = Array.isArray(result) ? result : (result as any)?.events ?? [];
  if (!events.length) {
    console.log("未找到事件");
    return;
  }

  console.log(`事件列表 (offset=${offset}, limit=${limit}, 返回 ${events.length} 条)\n`);

  for (let i = 0; i < events.length; i++) {
    const e = events[i];
    console.log(`  [${offset + i + 1}] ${e.title ?? e.name ?? "N/A"}`);
    if (e.slug) console.log(`      Slug:   ${e.slug}`);
    if (e.id) console.log(`      ID:     ${e.id}`);
    if (e.status) console.log(`      状态:   ${e.status}`);
    if (e.volume !== undefined) console.log(`      成交量: ${e.volume}`);
    const mkts = e.markets ?? [];
    console.log(`      市场数: ${mkts.length}`);
    console.log();
  }
}

function main() {
  const args = process.argv.slice(2);

  if (args.includes("--help") || args.includes("-h")) {
    console.log(USAGE);
    return;
  }

  const jsonMode = args.includes("--json");
  const limit = parseIntFlag(args, "--limit", 20);
  const offset = parseIntFlag(args, "--offset", 0);

  return listEvents(limit, offset, jsonMode);
}

main()?.catch(console.error);
