// 买入下单
// 用法: bun run scripts/buy.ts --token <TOKEN_ID> --price <PRICE> --size <SIZE> [--type market|limit]
//
// --type 默认: limit
// LIMIT 订单: createLimitOrder + GTC, feeRateBps=175n
// MARKET 订单: createMarketOrder

import "dotenv/config";
import { getClobClient, jsonStringify } from "./config";
import { getPriceInfo } from "./price-info";
import { OrderSide, LimitTimeInForce } from "@prob/clob";

async function buyOrder(
    tokenId: string,
    price: number,
    size: number,
    orderType: string = "limit",
): Promise<void> {
    const client = await getClobClient();

    // 获取价格参考
    const priceInfo = await getPriceInfo(tokenId);
    console.log();

    if (orderType === "market") {
        // 市价买入
        console.log(`市价买入: ${size} shares ...`);
        const order = await client.createMarketOrder({
            tokenId,
            size,
            side: OrderSide.Buy,
        });
        const result = await client.postOrder(order);
        console.log("订单已提交:");
        console.log(jsonStringify(result));
    } else {
        // 限价买入
        console.log(`限价买入: ${size} shares @ $${price} (总计 ~$${(price * size).toFixed(2)}) ...`);
        const order = await client.createLimitOrder({
            tokenId,
            price,
            size,
            side: OrderSide.Buy,
            timeInForce: LimitTimeInForce.GTC,
        });
        // 设置最低手续费
        order.feeRateBps = 175n;
        const result = await client.postOrder(order);
        console.log("订单已提交:");
        console.log(jsonStringify(result));
    }
}

// CLI 参数解析
const args = process.argv.slice(2);
let tokenId = "";
let price = 0;
let size = 0;
let orderType = "limit";

for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
        case "--token": tokenId = args[++i]; break;
        case "--price": price = parseFloat(args[++i]); break;
        case "--size": size = parseFloat(args[++i]); break;
        case "--type": orderType = args[++i]; break;
    }
}

if (!tokenId || !size) {
    console.error("用法: bun run scripts/buy.ts --token <TOKEN_ID> --price <PRICE> --size <SIZE> [--type market|limit]");
    console.error("\n参数说明:");
    console.error("  --token   Token ID (必须)");
    console.error("  --price   价格 0-1 (limit 订单必须)");
    console.error("  --size    share 数量 (必须)");
    console.error("  --type    订单类型: market | limit (默认 limit)");
    process.exit(1);
}

if (orderType === "limit" && !price) {
    console.error("错误: limit 订单必须指定 --price");
    process.exit(1);
}

buyOrder(tokenId, price, size, orderType).catch(console.error);
