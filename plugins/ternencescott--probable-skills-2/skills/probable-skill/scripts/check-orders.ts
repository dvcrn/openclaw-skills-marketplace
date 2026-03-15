// 查看活跃订单
// 用法:
//   bun run scripts/check-orders.ts                        # 查看所有订单
//   bun run scripts/check-orders.ts --event <EVENT_ID>     # 按 event 过滤
//   bun run scripts/check-orders.ts --token <TOKEN_ID>     # 按 token 过滤

import "dotenv/config";
import { getClobClient, jsonStringify } from "./config";
import type { OrderResponse } from "@prob/clob";

function printOrders(orders: OrderResponse[]): void {
    if (!orders || orders.length === 0) {
        console.log("没有活跃订单");
        return;
    }

    console.log(`找到 ${orders.length} 个活跃订单\n`);

    for (let i = 0; i < orders.length; i++) {
        const o = orders[i];
        console.log(`${i + 1}. Order ID: ${o.orderId}`);
        console.log(`   Side:     ${o.side}`);
        console.log(`   Type:     ${o.type} / ${o.timeInForce}`);
        console.log(`   Price:    ${o.price} (${(parseFloat(o.price) * 100).toFixed(1)}c)`);
        console.log(`   Size:     ${o.origQty} shares`);
        console.log(`   Filled:   ${o.executedQty} shares`);
        console.log(`   Status:   ${o.status}`);
        console.log(`   Token:    ${o.tokenId}`);
        if (o.time) {
            console.log(`   Created:  ${new Date(o.time).toLocaleString()}`);
        }
        if (o.updateTime) {
            console.log(`   Updated:  ${new Date(o.updateTime).toLocaleString()}`);
        }
        console.log("");
    }

    const buys = orders.filter((o) => o.side === "BUY").length;
    const sells = orders.filter((o) => o.side === "SELL").length;
    console.log(`Buy: ${buys}, Sell: ${sells}, 合计: ${orders.length}`);
}

async function checkOrders(opts: {
    eventId?: string;
    tokenId?: string;
}): Promise<void> {
    const client = await getClobClient();

    let orders: OrderResponse[];

    if (opts.eventId) {
        // 按 event 查询
        console.log(`查询 event ${opts.eventId} 的订单...\n`);
        orders = await client.getOpenOrders({ eventId: opts.eventId });
    } else if (opts.tokenId) {
        // 按 token 查询
        console.log(`查询 token ${opts.tokenId} 的订单...\n`);
        orders = await client.getOpenOrders({ tokenIds: [opts.tokenId] });
    } else {
        // 查询所有
        console.log("查询所有活跃订单...\n");
        orders = await client.getOpenOrders();
    }

    printOrders(orders);
}

// CLI 参数解析
const args = process.argv.slice(2);
let eventId: string | undefined;
let tokenId: string | undefined;

for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
        case "--event": eventId = args[++i]; break;
        case "--token": tokenId = args[++i]; break;
    }
}

checkOrders({ eventId, tokenId }).catch(console.error);
