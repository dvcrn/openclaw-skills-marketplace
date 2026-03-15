// ========================
// 订单簿
// ========================
// 用法: bun run scripts/orderbook.ts <token_id> [--json]

import { getPublicClobClient, jsonStringify } from "./config";

const USAGE = `用法: bun run scripts/orderbook.ts <token_id> [--json]

示例:
  bun run scripts/orderbook.ts 103150900523810306978382658655395688745354463907404362535146989263389724506168`;

async function orderbook(tokenId: string, jsonMode: boolean) {
  const client = getPublicClobClient();

  let book: any;
  try {
    book = await client.getOrderBook({ tokenId });
  } catch (err: any) {
    console.error(`错误: 无法获取订单簿 — ${err.message ?? err}`);
    process.exit(1);
  }

  if (jsonMode) {
    console.log(jsonStringify(book));
    return;
  }

  const bids: Array<{ price: number; size: number }> = (book?.bids ?? []).map((b: any) => ({
    price: Number(b.price ?? b.p ?? b[0]),
    size: Number(b.size ?? b.s ?? b.quantity ?? b[1]),
  }));

  const asks: Array<{ price: number; size: number }> = (book?.asks ?? []).map((a: any) => ({
    price: Number(a.price ?? a.p ?? a[0]),
    size: Number(a.size ?? a.s ?? a.quantity ?? a[1]),
  }));

  // 排序: bids 从高到低, asks 从低到高
  bids.sort((a, b) => b.price - a.price);
  asks.sort((a, b) => a.price - b.price);

  const bestBid = bids[0]?.price;
  const bestAsk = asks[0]?.price;
  const spread = bestBid !== undefined && bestAsk !== undefined ? bestAsk - bestBid : undefined;
  const midpoint = bestBid !== undefined && bestAsk !== undefined ? (bestBid + bestAsk) / 2 : undefined;

  console.log(`订单簿\n${"=".repeat(55)}`);
  console.log(`  Token ID: ${tokenId}\n`);

  // 卖单 (asks) — 从高到低显示，最低价在底部靠近中间
  console.log(`  卖单 (Asks) — ${asks.length} 档`);
  console.log(`  ${"价格".padEnd(12)}${"数量".padEnd(12)}累计`);
  console.log(`  ${"-".repeat(36)}`);

  // 累计从最低价开始
  let askCumulative = 0;
  const askRows = asks.map((a) => {
    askCumulative += a.size;
    return { ...a, cumulative: askCumulative };
  });
  // 显示时从高到低
  for (const row of [...askRows].reverse()) {
    console.log(`  ${row.price.toFixed(4).padEnd(12)}${row.size.toFixed(2).padEnd(12)}${row.cumulative.toFixed(2)}`);
  }

  // 价差
  console.log();
  if (spread !== undefined) {
    console.log(`  --- 价差: ${spread.toFixed(4)} | 中间价: ${midpoint!.toFixed(4)} ---`);
  }
  console.log();

  // 买单 (bids) — 从高到低
  console.log(`  买单 (Bids) — ${bids.length} 档`);
  console.log(`  ${"价格".padEnd(12)}${"数量".padEnd(12)}累计`);
  console.log(`  ${"-".repeat(36)}`);

  let bidCumulative = 0;
  for (const b of bids) {
    bidCumulative += b.size;
    console.log(`  ${b.price.toFixed(4).padEnd(12)}${b.size.toFixed(2).padEnd(12)}${bidCumulative.toFixed(2)}`);
  }

  // 汇总
  console.log(`\n  汇总:`);
  console.log(`    最佳买价: ${bestBid?.toFixed(4) ?? "N/A"}`);
  console.log(`    最佳卖价: ${bestAsk?.toFixed(4) ?? "N/A"}`);
  if (spread !== undefined) console.log(`    价差:     ${spread.toFixed(4)}`);
  if (midpoint !== undefined) console.log(`    中间价:   ${midpoint.toFixed(4)}`);
  console.log(`    买单总量: ${bids.reduce((s, b) => s + b.size, 0).toFixed(2)}`);
  console.log(`    卖单总量: ${asks.reduce((s, a) => s + a.size, 0).toFixed(2)}`);
  console.log();
}

function main() {
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

  return orderbook(tokenId, jsonMode);
}

main()?.catch(console.error);
