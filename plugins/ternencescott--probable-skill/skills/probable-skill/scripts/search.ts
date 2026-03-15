// ========================
// 搜索市场
// ========================
// 用法: bun run scripts/search.ts <关键词> [--limit <n>] [--json]

import { getPublicClobClient, jsonStringify } from "./config";

const USAGE = `用法: bun run scripts/search.ts <关键词> [--limit <n>] [--json]

示例:
  bun run scripts/search.ts bitcoin
  bun run scripts/search.ts "US election" --limit 5
  bun run scripts/search.ts trump --json`;

async function search(query: string, limit: number, jsonMode: boolean) {
  const client = getPublicClobClient();
  const result = await client.search({ q: query });

  if (jsonMode) {
    console.log(jsonStringify(result));
    return;
  }

  const events = (result as any)?.events ?? (Array.isArray(result) ? result : []);
  if (!events.length) {
    console.log(`未找到与 "${query}" 相关的市场`);
    return;
  }

  const display = limit > 0 ? events.slice(0, limit) : events;
  console.log(`🔍 搜索 "${query}" — 共 ${events.length} 个结果${limit > 0 && limit < events.length ? ` (显示前 ${limit} 个)` : ""}\n`);

  for (const event of display) {
    console.log(`  标题: ${event.title ?? event.name ?? "N/A"}`);
    if (event.slug) console.log(`  Slug: ${event.slug}`);
    if (event.id) console.log(`  ID:   ${event.id}`);
    const markets = event.markets ?? [];
    if (markets.length) {
      console.log(`  市场 (${markets.length}):`);
      for (const m of markets) {
        const q = m.question ?? m.title ?? "N/A";
        console.log(`    - ${q}${m.id ? ` [${m.id}]` : ""}`);
      }
    }
    console.log();
  }
}

// 解析参数
function main() {
  const args = process.argv.slice(2);

  if (args.includes("--help") || args.includes("-h")) {
    console.log(USAGE);
    return;
  }

  const jsonMode = args.includes("--json");
  let limit = 0;
  const limitIdx = args.indexOf("--limit");
  if (limitIdx !== -1 && args[limitIdx + 1]) {
    limit = parseInt(args[limitIdx + 1], 10);
  }

  // 提取关键词（跳过 flags）
  const skipSet = new Set<number>();
  if (jsonMode) skipSet.add(args.indexOf("--json"));
  if (limitIdx !== -1) {
    skipSet.add(limitIdx);
    skipSet.add(limitIdx + 1);
  }
  const keywords = args.filter((_, i) => !skipSet.has(i));
  const query = keywords.join(" ");

  if (!query) {
    console.error("错误: 请提供搜索关键词");
    console.log(USAGE);
    process.exit(1);
  }

  return search(query, limit, jsonMode);
}

main()?.catch(console.error);
