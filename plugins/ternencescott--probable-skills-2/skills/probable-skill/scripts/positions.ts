// ========================
// 查看持仓
// ========================
// 用法:
//   bun run scripts/positions.ts [--event <EVENT_ID>] [--token <TOKEN_ID>] [--market <MARKET_ID>]
//   bun run scripts/positions.ts --event 752 --pnl
//   bun run scripts/positions.ts --token <TOKEN_ID> --trades

import "dotenv/config";
import { getClobClient, getAccount, jsonStringify } from "./config";

const USAGE = `用法: bun run scripts/positions.ts [--event <EVENT_ID>] [--token <TOKEN_ID>] [--market <MARKET_ID>] [--pnl] [--trades] [--json]

示例:
  bun run scripts/positions.ts                          # 查看所有当前持仓
  bun run scripts/positions.ts --event 752              # 按事件查看持仓
  bun run scripts/positions.ts --event 752 --pnl        # 含盈亏信息
  bun run scripts/positions.ts --token <id> --trades    # 按 token 查看交易记录
  bun run scripts/positions.ts --market <id>            # 按市场查看待处理持仓
  bun run scripts/positions.ts --json                   # JSON 输出`;

async function main() {
  const args = process.argv.slice(2);

  if (args.includes("--help") || args.includes("-h")) {
    console.log(USAGE);
    return;
  }

  // 解析参数
  const eventIdx = args.indexOf("--event");
  const eventId = eventIdx !== -1 && args[eventIdx + 1] ? args[eventIdx + 1] : undefined;

  const tokenIdx = args.indexOf("--token");
  const tokenId = tokenIdx !== -1 && args[tokenIdx + 1] ? args[tokenIdx + 1] : undefined;

  const marketIdx = args.indexOf("--market");
  const marketId = marketIdx !== -1 && args[marketIdx + 1] ? args[marketIdx + 1] : undefined;

  const showPnl = args.includes("--pnl");
  const showTrades = args.includes("--trades");
  const jsonMode = args.includes("--json");

  const client = await getClobClient();
  const userAddress = getAccount().address;

  console.log(`=== 持仓信息 (用户: ${userAddress}) ===\n`);

  // 获取当前持仓 — requires user, optional eventId
  const currentPositions = await client.getCurrentPositions({ user: userAddress, ...(eventId ? { eventId } : {}) });

  // 获取已关闭持仓 — optional user, optional eventId
  const closedPositions = await client.getClosedPositions({ user: userAddress, ...(eventId ? { eventId } : {}) });

  // 获取待处理持仓 — requires marketId and user
  let pendingPositions: any = null;
  if (marketId) {
    pendingPositions = await client.getPendingPositions({ marketId, user: userAddress });
  }

  if (jsonMode) {
    const result: any = { currentPositions, closedPositions, pendingPositions };
    if (showPnl) {
      const [positionValue, pnl] = await Promise.all([
        client.getPositionValue({ user: userAddress }),
        client.getPnL({ userAddress }),
      ]);
      result.positionValue = positionValue;
      result.pnl = pnl;
    }
    if (showTrades && tokenId) {
      const [trades, activity] = await Promise.all([
        client.getTrades({ tokenId }),
        client.getActivity({ user: userAddress }),
      ]);
      result.trades = trades;
      result.activity = activity;
    }
    console.log(jsonStringify(result));
    return;
  }

  // 当前持仓
  console.log("--- 当前持仓 ---");
  const current = Array.isArray(currentPositions) ? currentPositions : (currentPositions as any)?.positions ?? [];
  if (current.length === 0) {
    console.log("  无当前持仓");
  } else {
    for (const p of current) {
      console.log(`  方向: ${p.side ?? p.outcome ?? "N/A"}`);
      console.log(`    数量: ${p.size ?? p.amount ?? "N/A"}`);
      console.log(`    均价: ${p.avgPrice ?? p.averagePrice ?? "N/A"}`);
      if (p.tokenId) console.log(`    TokenID: ${p.tokenId}`);
      console.log();
    }
  }

  // 待处理持仓
  if (marketId) {
    console.log("--- 待处理持仓 ---");
    const pending = Array.isArray(pendingPositions) ? pendingPositions : (pendingPositions as any)?.positions ?? [];
    if (pending.length === 0) {
      console.log("  无待处理持仓");
    } else {
      for (const p of pending) {
        console.log(`  方向: ${p.side ?? p.outcome ?? "N/A"}, 数量: ${p.size ?? p.amount ?? "N/A"}`);
      }
    }
  } else {
    console.log("--- 待处理持仓 ---");
    console.log("  (需要 --market <MARKET_ID> 参数来查询待处理持仓)");
  }

  // 已关闭持仓
  console.log("\n--- 已关闭持仓 ---");
  const closed = Array.isArray(closedPositions) ? closedPositions : (closedPositions as any)?.positions ?? [];
  if (closed.length === 0) {
    console.log("  无已关闭持仓");
  } else {
    for (const p of closed) {
      console.log(`  方向: ${p.side ?? p.outcome ?? "N/A"}, 数量: ${p.size ?? p.amount ?? "N/A"}, 结果: ${p.result ?? "N/A"}`);
    }
  }

  // PnL
  if (showPnl) {
    console.log("\n--- 盈亏 (PnL) ---");
    const [positionValue, pnl] = await Promise.all([
      client.getPositionValue({ user: userAddress }),
      client.getPnL({ userAddress }),
    ]);
    console.log(`  持仓价值: ${jsonStringify(positionValue)}`);
    console.log(`  PnL:      ${jsonStringify(pnl)}`);
  }

  // 交易记录
  if (showTrades) {
    console.log("\n--- 交易记录 ---");
    if (!tokenId) {
      console.log("  (需要 --token <TOKEN_ID> 参数来查询交易记录)");
    } else {
      const trades = await client.getTrades({ tokenId });
      const tradeList = Array.isArray(trades) ? trades : (trades as any)?.trades ?? [];
      if (tradeList.length === 0) {
        console.log("  无交易记录");
      } else {
        for (const t of tradeList) {
          console.log(`  ${t.side ?? "N/A"} | 价格: ${t.price ?? "N/A"} | 数量: ${t.size ?? t.amount ?? "N/A"} | 时间: ${t.createdAt ?? t.timestamp ?? "N/A"}`);
        }
      }
    }

    console.log("\n--- 活动记录 ---");
    const activity = await client.getActivity({ user: userAddress });
    const actList = Array.isArray(activity) ? activity : (activity as any)?.activities ?? [];
    if (actList.length === 0) {
      console.log("  无活动记录");
    } else {
      for (const a of actList) {
        console.log(`  类型: ${a.type ?? "N/A"} | ${a.side ?? ""} | 数量: ${a.size ?? a.amount ?? "N/A"} | 时间: ${a.createdAt ?? a.timestamp ?? "N/A"}`);
      }
    }
  }
}

main().catch(console.error);
