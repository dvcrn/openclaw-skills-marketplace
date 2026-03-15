// 取消订单
// 用法:
//   bun run scripts/cancel-orders.ts --order <ORDER_ID> --token <TOKEN_ID>   # 取消单个订单
//   bun run scripts/cancel-orders.ts --event <EVENT_ID>                      # 取消 event 下全部订单
//
// 注意: cancelOrder 需要 orderId + tokenId
//       cancelAllOrders 需要 tokenId (取消该 token 全部订单)

import "dotenv/config";
import { getClobClient, jsonStringify } from "./config";

async function cancelSingleOrder(orderId: string, tokenId: string): Promise<void> {
    const client = await getClobClient();

    console.log(`取消订单: ${orderId} (token: ${tokenId}) ...`);
    const result = await client.cancelOrder({ orderId, tokenId });
    console.log("取消结果:");
    console.log(jsonStringify(result));
}

async function cancelAllForEvent(eventId: string): Promise<void> {
    const client = await getClobClient();

    // 先获取 event 下所有订单
    console.log(`查询 event ${eventId} 的活跃订单...`);
    const orders = await client.getOpenOrders({ eventId });

    if (!orders || orders.length === 0) {
        console.log("该 event 下没有活跃订单");
        return;
    }

    console.log(`找到 ${orders.length} 个订单，开始取消...\n`);

    // 按 tokenId 分组取消
    const tokenIds = [...new Set(orders.map((o) => o.tokenId))];
    for (const tokenId of tokenIds) {
        const tokenOrders = orders.filter((o) => o.tokenId === tokenId);
        console.log(`取消 token ${tokenId} 下的 ${tokenOrders.length} 个订单...`);
        const result = await client.cancelAllOrders({ tokenId });
        console.log("结果:", jsonStringify(result));
        console.log("");
    }

    console.log("全部取消完成");
}

// CLI 参数解析
const args = process.argv.slice(2);
let orderId: string | undefined;
let tokenId: string | undefined;
let eventId: string | undefined;

for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
        case "--order": orderId = args[++i]; break;
        case "--token": tokenId = args[++i]; break;
        case "--event": eventId = args[++i]; break;
    }
}

if (orderId && tokenId) {
    // 取消单个订单
    cancelSingleOrder(orderId, tokenId).catch(console.error);
} else if (eventId) {
    // 取消 event 下全部订单
    cancelAllForEvent(eventId).catch(console.error);
} else {
    console.error("用法:");
    console.error("  bun run scripts/cancel-orders.ts --order <ORDER_ID> --token <TOKEN_ID>  # 取消单个订单");
    console.error("  bun run scripts/cancel-orders.ts --event <EVENT_ID>                     # 取消 event 下全部订单");
    process.exit(1);
}
