// ========================
// 从 Proxy Wallet 提取 USDT
// ========================
// 用法:
//   bun run scripts/withdraw.ts              # 提取全部 USDT
//   bun run scripts/withdraw.ts --amount 100 # 提取 100 USDT

import "dotenv/config";
import { ethers } from "ethers";
import { provider, getEthersWallet, USDT_ADDRESS, PROXY_WALLET, EOA_ADDRESS } from "./config";

const USAGE = `用法: bun run scripts/withdraw.ts [--amount <USDT>]

示例:
  bun run scripts/withdraw.ts              # 提取全部 USDT
  bun run scripts/withdraw.ts --amount 100 # 提取 100 USDT`;

const ERC20_ABI = [
  "function transfer(address to, uint256 amount) returns (bool)",
  "function balanceOf(address account) view returns (uint256)",
];

const GNOSIS_SAFE_ABI = [
  "function execTransaction(address to, uint256 value, bytes calldata data, uint8 operation, uint256 safeTxGas, uint256 baseGas, uint256 gasPrice, address gasToken, address refundReceiver, bytes memory signatures) payable returns (bool)",
  "function getTransactionHash(address to, uint256 value, bytes calldata data, uint8 operation, uint256 safeTxGas, uint256 baseGas, uint256 gasPrice, address gasToken, address refundReceiver, uint256 _nonce) view returns (bytes32)",
  "function nonce() view returns (uint256)",
  "function getThreshold() view returns (uint256)",
  "function getOwners() view returns (address[])",
];

async function main() {
  const args = process.argv.slice(2);

  if (args.includes("--help") || args.includes("-h")) {
    console.log(USAGE);
    return;
  }

  // 解析 --amount
  let specifiedAmount: bigint | null = null;
  const amountIdx = args.indexOf("--amount");
  if (amountIdx !== -1 && args[amountIdx + 1]) {
    const amountStr = args[amountIdx + 1];
    // BSC USDT 使用 18 decimals
    specifiedAmount = ethers.parseEther(amountStr);
  }

  const wallet = getEthersWallet();
  const usdt = new ethers.Contract(USDT_ADDRESS, ERC20_ABI, provider);
  const safe = new ethers.Contract(PROXY_WALLET, GNOSIS_SAFE_ABI, wallet);

  console.log("=== 从 Proxy Wallet 提取 USDT ===\n");
  console.log(`Proxy Wallet: ${PROXY_WALLET}`);
  console.log(`EOA 地址:     ${EOA_ADDRESS}\n`);

  // 检查 Safe 配置
  const [threshold, owners, nonce] = await Promise.all([
    safe.getThreshold(),
    safe.getOwners(),
    safe.nonce(),
  ]);

  if (!owners.map((o: string) => o.toLowerCase()).includes(wallet.address.toLowerCase())) {
    throw new Error(`${wallet.address} 不是 proxy wallet 的 owner`);
  }
  console.log(`Safe threshold: ${threshold}, nonce: ${nonce}`);

  // 查询余额（提取前）
  const [proxyBalance, eoaBalanceBefore] = await Promise.all([
    usdt.balanceOf(PROXY_WALLET) as Promise<bigint>,
    usdt.balanceOf(EOA_ADDRESS) as Promise<bigint>,
  ]);

  console.log(`\n--- 提取前余额 ---`);
  console.log(`  Proxy Wallet: ${ethers.formatEther(proxyBalance)} USDT`);
  console.log(`  EOA:          ${ethers.formatEther(eoaBalanceBefore)} USDT`);

  if (proxyBalance === 0n) {
    console.log("\nProxy Wallet 余额为 0，无需提取");
    return;
  }

  // 确定提取金额
  const withdrawAmount = specifiedAmount ?? proxyBalance;
  if (withdrawAmount > proxyBalance) {
    throw new Error(`提取金额 ${ethers.formatEther(withdrawAmount)} 超过余额 ${ethers.formatEther(proxyBalance)}`);
  }

  console.log(`\n提取金额: ${ethers.formatEther(withdrawAmount)} USDT`);

  // 构建 transfer calldata
  const transferData = usdt.interface.encodeFunctionData("transfer", [EOA_ADDRESS, withdrawAmount]);

  const txParams = {
    to: USDT_ADDRESS,
    value: 0,
    data: transferData,
    operation: 0,
    safeTxGas: 0,
    baseGas: 0,
    gasPrice: 0,
    gasToken: ethers.ZeroAddress,
    refundReceiver: ethers.ZeroAddress,
    nonce,
  };

  // 获取交易哈希并签名
  const txHash = await safe.getTransactionHash(
    txParams.to, txParams.value, txParams.data, txParams.operation,
    txParams.safeTxGas, txParams.baseGas, txParams.gasPrice,
    txParams.gasToken, txParams.refundReceiver, txParams.nonce,
  );

  let signature = await wallet.signMessage(ethers.getBytes(txHash));
  let v = parseInt(signature.slice(-2), 16);
  if (v < 27) v += 27;
  v += 4; // eth_sign v-value offset
  signature = signature.slice(0, -2) + v.toString(16).padStart(2, "0");

  // 执行交易
  console.log(`\n转账 ${ethers.formatEther(withdrawAmount)} USDT → ${EOA_ADDRESS}`);
  const tx = await safe.execTransaction(
    txParams.to, txParams.value, txParams.data, txParams.operation,
    txParams.safeTxGas, txParams.baseGas, txParams.gasPrice,
    txParams.gasToken, txParams.refundReceiver, signature,
  );
  console.log(`Tx hash: ${tx.hash}`);

  const receipt = await tx.wait();
  console.log(`确认! Block: ${receipt.blockNumber}, Gas: ${receipt.gasUsed.toString()}`);

  // 查询余额（提取后）
  const [proxyAfter, eoaAfter] = await Promise.all([
    usdt.balanceOf(PROXY_WALLET) as Promise<bigint>,
    usdt.balanceOf(EOA_ADDRESS) as Promise<bigint>,
  ]);

  console.log(`\n--- 提取后余额 ---`);
  console.log(`  Proxy Wallet: ${ethers.formatEther(proxyAfter)} USDT`);
  console.log(`  EOA:          ${ethers.formatEther(eoaAfter)} USDT`);
}

main().catch(console.error);
