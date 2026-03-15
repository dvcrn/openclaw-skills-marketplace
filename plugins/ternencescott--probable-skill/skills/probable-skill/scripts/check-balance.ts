// ========================
// 检查余额
// ========================
// 用法: bun run scripts/check-balance.ts

import "dotenv/config";
import { ethers } from "ethers";
import { provider, USDT_ADDRESS, PROXY_WALLET, EOA_ADDRESS } from "./config";

const ERC20_ABI = [
  "function balanceOf(address account) view returns (uint256)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
];

async function main() {
  const usdt = new ethers.Contract(USDT_ADDRESS, ERC20_ABI, provider);

  console.log("=== 账户余额查询 ===\n");
  console.log(`EOA 地址:          ${EOA_ADDRESS}`);
  console.log(`Proxy Wallet 地址: ${PROXY_WALLET}\n`);

  // 并行查询所有余额
  const [proxyUsdtBalance, eoaUsdtBalance, eoaBnbBalance] = await Promise.all([
    usdt.balanceOf(PROXY_WALLET) as Promise<bigint>,
    usdt.balanceOf(EOA_ADDRESS) as Promise<bigint>,
    provider.getBalance(EOA_ADDRESS),
  ]);

  console.log("--- USDT 余额 (BSC, 18 decimals) ---");
  console.log(`  Proxy Wallet: ${ethers.formatEther(proxyUsdtBalance)} USDT`);
  console.log(`  EOA:          ${ethers.formatEther(eoaUsdtBalance)} USDT`);
  console.log(`  合计:         ${ethers.formatEther(proxyUsdtBalance + eoaUsdtBalance)} USDT`);

  console.log("\n--- BNB 余额 (Gas) ---");
  console.log(`  EOA:          ${ethers.formatEther(eoaBnbBalance)} BNB`);
}

main().catch(console.error);
