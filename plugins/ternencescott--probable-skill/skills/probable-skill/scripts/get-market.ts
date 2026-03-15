// ========================
// 获取市场详情
// ========================
// 用法: bun run scripts/get-market.ts <market_id> [--json]

import { getPublicClobClient, jsonStringify } from "./config";

const USAGE = `用法: bun run scripts/get-market.ts <market_id> [--json]

示例:
  bun run scripts/get-market.ts 12345
  bun run scripts/get-market.ts 12345 --json`;

async function getMarket(marketId: string, jsonMode: boolean) {
  const client = getPublicClobClient();

  let market: any;
  try {
    market = await client.getMarketById({ id: marketId });
  } catch (err: any) {
    console.error(`错误: 无法获取市场 "${marketId}" — ${err.message ?? err}`);
    process.exit(1);
  }

  if (!market) {
    console.error(`错误: 未找到市场 "${marketId}"`);
    process.exit(1);
  }

  if (jsonMode) {
    console.log(jsonStringify(market));
    return;
  }

  console.log(`市场详情\n${"=".repeat(50)}`);
  console.log(`  问题:   ${market.question ?? market.title ?? "N/A"}`);
  if (market.id) console.log(`  ID:     ${market.id}`);
  if (market.status) console.log(`  状态:   ${market.status}`);
  if (market.eventId) console.log(`  事件ID: ${market.eventId}`);
  if (market.volume !== undefined) console.log(`  成交量: ${market.volume}`);
  if (market.liquidity !== undefined) console.log(`  流动性: ${market.liquidity}`);
  if (market.description) console.log(`  描述:   ${market.description}`);

  // Token 信息
  const tokens = market.tokens ?? market.outcomes ?? [];
  if (tokens.length) {
    console.log(`\n  Tokens:`);
    console.log(`  ${"-".repeat(46)}`);
    for (const t of tokens) {
      const outcome = t.outcome ?? t.name ?? t.side ?? "N/A";
      const tokenId = t.tokenId ?? t.token_id ?? t.id ?? "N/A";
      const price = t.price ?? "N/A";
      console.log(`    ${outcome}:`);
      console.log(`      Token ID: ${tokenId}`);
      console.log(`      价格:     ${price}`);
    }
  }

  // 价格信息
  if (market.bestBid !== undefined || market.bestAsk !== undefined) {
    console.log(`\n  价格信息:`);
    if (market.bestBid !== undefined) console.log(`    最佳买价: ${market.bestBid}`);
    if (market.bestAsk !== undefined) console.log(`    最佳卖价: ${market.bestAsk}`);
  }
  console.log();
}

function main() {
  const args = process.argv.slice(2);

  if (args.includes("--help") || args.includes("-h")) {
    console.log(USAGE);
    return;
  }

  const jsonMode = args.includes("--json");
  const marketId = args.find((a) => !a.startsWith("--"));

  if (!marketId) {
    console.error("错误: 请提供市场 ID");
    console.log(USAGE);
    process.exit(1);
  }

  return getMarket(marketId, jsonMode);
}

main()?.catch(console.error);
