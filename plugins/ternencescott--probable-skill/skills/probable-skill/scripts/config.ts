// ========================
// 共享配置模块
// ========================
//
// 0xProbable Markets CLOB SDK 配置
// 链: BSC 主网 (chainId: 56)
// SDK: @prob/clob (viem-based)
//
// 鉴权: 每次调用 getClobClient() 自动 generateApiKey()
// 公共 API: getPublicClobClient() 无需私钥

import { createWalletClient, createPublicClient, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { bsc } from "viem/chains";
import { createClobClient, type ClobClient } from "@prob/clob";
import { ethers } from "ethers";

const PRIVATE_KEY = process.env.PRIVATE_KEY;
const BSC_RPC = process.env.BSC_RPC || "https://bsc-dataseed.bnbchain.org";
const CHAIN_ID = 56;

// 合约地址
const USDT_ADDRESS = "0x55d398326f99059ff775485246999027b3197955";
const PROXY_WALLET = "0xE1e2380cDe7d1822ACbD097E85f72040AB106f42";
const EOA_ADDRESS = "0xDDDddDcF23631d075C48e4669a5c0C227d5DdddD";

// ethers v6 provider (无需私钥)
const provider = new ethers.JsonRpcProvider(BSC_RPC);

// 需要私钥时才初始化的对象 (延迟创建)
function requirePrivateKey(): string {
  if (!PRIVATE_KEY) {
    console.error("错误: 请在 .env 文件中设置 PRIVATE_KEY");
    process.exit(1);
  }
  return PRIVATE_KEY;
}

function getViemWallet() {
  const pk = requirePrivateKey();
  const account = privateKeyToAccount(pk as `0x${string}`);
  return createWalletClient({
    chain: bsc,
    transport: http(BSC_RPC),
    account,
  });
}

function getEthersWallet() {
  const pk = requirePrivateKey();
  return new ethers.Wallet(pk, provider);
}

function getAccount() {
  const pk = requirePrivateKey();
  return privateKeyToAccount(pk as `0x${string}`);
}

const publicClient = createPublicClient({
  chain: bsc,
  transport: http(BSC_RPC),
});

// 创建已认证的 ClobClient
async function getClobClient(): Promise<ClobClient> {
  const wallet = getViemWallet();
  const client = createClobClient({
    chainId: CHAIN_ID,
    wallet,
  });
  await client.generateApiKey();
  return client;
}

// 创建无需认证的 ClobClient (公共 API)
function getPublicClobClient(): ClobClient {
  return createClobClient({
    chainId: CHAIN_ID,
  });
}

// BigInt JSON 序列化辅助
function jsonStringify(obj: any): string {
  return JSON.stringify(obj, (_, v) => (typeof v === "bigint" ? v.toString() : v), 2);
}

export {
  getClobClient,
  getPublicClobClient,
  getViemWallet,
  getEthersWallet,
  getAccount,
  publicClient,
  provider,
  CHAIN_ID,
  BSC_RPC,
  USDT_ADDRESS,
  PROXY_WALLET,
  EOA_ADDRESS,
  jsonStringify,
};
