// ========================
// 获取事件详情
// ========================
// 用法: bun run scripts/get-event.ts <event_id_or_slug>
// 先尝试按 ID 查询，失败则按 slug 查询

import { getPublicClobClient, jsonStringify } from "./config";

const USAGE = `用法: bun run scripts/get-event.ts <event_id_or_slug> [--json]

示例:
  bun run scripts/get-event.ts 12345
  bun run scripts/get-event.ts bitcoin-price-2025
  bun run scripts/get-event.ts some-slug --json`;

async function getEvent(idOrSlug: string, jsonMode: boolean) {
  const client = getPublicClobClient();
  let event: any = null;

  // 先尝试按 ID 查询
  try {
    event = await client.getEventById({ id: idOrSlug });
  } catch {
    // ID 查询失败，尝试 slug
  }

  if (!event) {
    try {
      event = await client.getEventBySlug({ slug: idOrSlug });
    } catch {
      console.error(`错误: 未找到事件 "${idOrSlug}" (按 ID 和 slug 均未找到)`);
      process.exit(1);
    }
  }

  if (!event) {
    console.error(`错误: 未找到事件 "${idOrSlug}"`);
    process.exit(1);
  }

  if (jsonMode) {
    console.log(jsonStringify(event));
    return;
  }

  // 格式化输出
  console.log(`事件详情\n${"=".repeat(50)}`);
  console.log(`  标题:   ${event.title ?? event.name ?? "N/A"}`);
  if (event.id) console.log(`  ID:     ${event.id}`);
  if (event.slug) console.log(`  Slug:   ${event.slug}`);
  if (event.status) console.log(`  状态:   ${event.status}`);
  if (event.description) console.log(`  描述:   ${event.description}`);
  if (event.volume !== undefined) console.log(`  成交量: ${event.volume}`);
  if (event.startDate) console.log(`  开始:   ${event.startDate}`);
  if (event.endDate) console.log(`  结束:   ${event.endDate}`);

  const markets = event.markets ?? [];
  if (markets.length) {
    console.log(`\n  市场 (${markets.length}):`);
    console.log(`  ${"-".repeat(46)}`);
    for (const m of markets) {
      console.log(`  问题: ${m.question ?? m.title ?? "N/A"}`);
      if (m.id) console.log(`    市场 ID: ${m.id}`);
      if (m.status) console.log(`    状态:    ${m.status}`);

      // 显示 token IDs
      const tokens = m.tokens ?? m.outcomes ?? [];
      if (tokens.length) {
        console.log(`    Tokens:`);
        for (const t of tokens) {
          const outcome = t.outcome ?? t.name ?? t.side ?? "N/A";
          const tokenId = t.tokenId ?? t.token_id ?? t.id ?? "N/A";
          console.log(`      ${outcome}: ${tokenId}`);
        }
      }
      console.log();
    }
  }
}

function main() {
  const args = process.argv.slice(2);

  if (args.includes("--help") || args.includes("-h")) {
    console.log(USAGE);
    return;
  }

  const jsonMode = args.includes("--json");
  const idOrSlug = args.find((a) => !a.startsWith("--"));

  if (!idOrSlug) {
    console.error("错误: 请提供事件 ID 或 slug");
    console.log(USAGE);
    process.exit(1);
  }

  return getEvent(idOrSlug, jsonMode);
}

main()?.catch(console.error);
