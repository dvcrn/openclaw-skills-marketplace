// ========================
// 价格历史
// ========================
// 用法: bun run scripts/price-history.ts <token_id> [--hours <n>] [--json]

import { getPublicClobClient, jsonStringify } from "./config";

const USAGE = `用法: bun run scripts/price-history.ts <token_id> [--hours <n>] [--json]

参数:
  --hours <n>   查询最近 n 小时的数据 (默认 24)
  --json        输出原始 JSON

示例:
  bun run scripts/price-history.ts <token_id>
  bun run scripts/price-history.ts <token_id> --hours 72
  bun run scripts/price-history.ts <token_id> --json`;

// 简单 ASCII 折线图
function asciiChart(values: number[], width = 60, height = 15): string {
  if (values.length === 0) return "  (无数据)";

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  // 采样到 width 个点
  const sampled: number[] = [];
  for (let i = 0; i < width; i++) {
    const idx = Math.floor((i / width) * values.length);
    sampled.push(values[idx]);
  }

  const lines: string[] = [];
  for (let row = height - 1; row >= 0; row--) {
    const threshold = min + (range * row) / (height - 1);
    const label = threshold.toFixed(3).padStart(7);
    let line = `${label} |`;
    for (let col = 0; col < width; col++) {
      const val = sampled[col];
      const valRow = Math.round(((val - min) / range) * (height - 1));
      line += valRow === row ? "*" : " ";
    }
    lines.push(line);
  }
  lines.push(`${"".padStart(7)} +${"─".repeat(width)}`);
  lines.push(`${"".padStart(8)} 旧${"".padStart(width - 4)}新`);

  return lines.join("\n");
}

async function priceHistory(tokenId: string, hours: number, jsonMode: boolean) {
  const client = getPublicClobClient();

  const endTime = Math.floor(Date.now() / 1000);
  const startTime = endTime - hours * 3600;

  const result = await client.getPricesHistory({
    market: tokenId,
    startTs: startTime,
    endTs: endTime,
  });

  if (jsonMode) {
    console.log(jsonStringify(result));
    return;
  }

  const history = Array.isArray(result) ? result : (result as any)?.prices ?? (result as any)?.history ?? [];

  if (!history.length) {
    console.log(`未找到 token 最近 ${hours} 小时的价格数据`);
    return;
  }

  // 提取价格值
  const prices = history.map((p: any) => Number(p.price ?? p.p ?? p.value ?? p));
  const times = history.map((p: any) => {
    const t = p.timestamp ?? p.time ?? p.t;
    return t ? new Date(typeof t === "number" && t < 1e12 ? t * 1000 : Number(t)) : null;
  });

  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const first = prices[0];
  const last = prices[prices.length - 1];
  const change = last - first;
  const changePct = first !== 0 ? ((change / first) * 100).toFixed(2) : "N/A";

  console.log(`价格历史 (最近 ${hours} 小时)\n${"=".repeat(50)}`);
  console.log(`  Token ID:  ${tokenId}`);
  console.log(`  数据点数:  ${history.length}`);
  console.log(`  时间范围:  ${times[0]?.toISOString() ?? "N/A"} ~ ${times[times.length - 1]?.toISOString() ?? "N/A"}`);
  console.log();
  console.log(`  摘要:`);
  console.log(`    起始价: ${first.toFixed(4)}`);
  console.log(`    最新价: ${last.toFixed(4)}`);
  console.log(`    最高价: ${maxPrice.toFixed(4)}`);
  console.log(`    最低价: ${minPrice.toFixed(4)}`);
  console.log(`    变化:   ${change >= 0 ? "+" : ""}${change.toFixed(4)} (${changePct}%)`);
  console.log();
  console.log(`  价格走势:`);
  console.log(asciiChart(prices));
  console.log();
}

function main() {
  const args = process.argv.slice(2);

  if (args.includes("--help") || args.includes("-h")) {
    console.log(USAGE);
    return;
  }

  const jsonMode = args.includes("--json");
  let hours = 24;
  const hoursIdx = args.indexOf("--hours");
  if (hoursIdx !== -1 && args[hoursIdx + 1]) {
    hours = parseInt(args[hoursIdx + 1], 10);
  }

  // 提取 token ID（第一个非 flag 参数）
  const skipSet = new Set<number>();
  if (jsonMode) skipSet.add(args.indexOf("--json"));
  if (hoursIdx !== -1) {
    skipSet.add(hoursIdx);
    skipSet.add(hoursIdx + 1);
  }
  const tokenId = args.find((_, i) => !skipSet.has(i) && !args[i].startsWith("--"));

  if (!tokenId) {
    console.error("错误: 请提供 token ID");
    console.log(USAGE);
    process.exit(1);
  }

  return priceHistory(tokenId, hours, jsonMode);
}

main()?.catch(console.error);
