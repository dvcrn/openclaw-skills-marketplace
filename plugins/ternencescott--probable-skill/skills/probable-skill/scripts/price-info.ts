// ========================
// 获取价格信息
// ========================
// 用法: bun run scripts/price-info.ts <token_id> [--json]
// 导出 getPriceInfo 函数供其他脚本复用

import { getPublicClobClient, jsonStringify } from "./config";

const USAGE = `用法: bun run scripts/price-info.ts <token_id> [--json]

示例:
  bun run scripts/price-info.ts <token_id>`;

export interface PriceInfo {
  tokenId: string;
  bid: number | null;
  ask: number | null;
  mid: number | null;
  spread: number | null;
}

// 获取价格信息（可复用）
export async function getPriceInfo(tokenId: string): Promise<PriceInfo> {
  const client = getPublicClobClient();

  // getPrice(side=BUY) → 即时买入价 (ask), getPrice(side=SELL) → 即时卖出价 (bid)
  // getMidpoint SDK 有 bug (发送 type_id 而非 token_id), 改用 bid/ask 计算
  const [askRes, bidRes] = await Promise.all([
    client.getPrice({ tokenId, side: "BUY" as any }).catch(() => null),
    client.getPrice({ tokenId, side: "SELL" as any }).catch(() => null),
  ]);

  const bid = bidRes != null ? Number((bidRes as any)?.price ?? bidRes) : null;
  const ask = askRes != null ? Number((askRes as any)?.price ?? askRes) : null;
  const mid = bid != null && ask != null ? (bid + ask) / 2 : null;
  const spread = bid != null && ask != null ? ask - bid : null;

  return { tokenId, bid, ask, mid, spread };
}

async function main() {
  const args = process.argv.slice(2);

  if (args.includes("--help") || args.includes("-h")) {
    console.log(USAGE);
    return;
  }

  const jsonMode = args.includes("--json");
  const tokenId = args.find((a) => !a.startsWith("--"));

  if (!tokenId) {
    console.error("错误: 请提供 token ID");
    console.log(USAGE);
    process.exit(1);
  }

  const info = await getPriceInfo(tokenId);

  if (jsonMode) {
    console.log(jsonStringify(info));
    return;
  }

  console.log(`价格信息\n${"=".repeat(50)}`);
  console.log(`  Token ID: ${tokenId}\n`);
  console.log(`  买价 (Bid):  ${info.bid != null ? `$${info.bid.toFixed(4)} (${(info.bid * 100).toFixed(1)}%)` : "N/A"}`);
  console.log(`  卖价 (Ask):  ${info.ask != null ? `$${info.ask.toFixed(4)} (${(info.ask * 100).toFixed(1)}%)` : "N/A"}`);
  console.log(`  中间价:      ${info.mid != null ? `$${info.mid.toFixed(4)} (${(info.mid * 100).toFixed(1)}%)` : "N/A"}`);
  console.log(`  价差:        ${info.spread != null ? `$${info.spread.toFixed(4)}` : "N/A"}`);
}

if (import.meta.main) {
  main().catch(console.error);
}
