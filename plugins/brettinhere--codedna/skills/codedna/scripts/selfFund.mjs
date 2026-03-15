/**
 * selfFund.mjs — AgentSelfFund Skill 模块
 * 
 * 集成到 CodeDNA Skill (runner.mjs) 的自主 Gas 补充逻辑。
 * 每轮行动前调用 checkAndSelfFund()，BNB 不足时自动卖出锁定 DNAGOLD。
 *
 * 使用方式：
 *   import { checkAndSelfFund } from './selfFund.mjs'
 *   await checkAndSelfFund(provider, wallet, agentId, config)
 */

import { ethers } from 'ethers'

// ─── 合约地址（部署后填写）──────────────────────────────────
const CONTRACTS = {
  agentSelfFund: '0xEae472459BE2aea42FD4E805723E48ADb6bAd275',
  dnagold:       '0xE43c4e25666F2e181ecd7b4A96930b8F1EB6b855',
  rovexRouter:   '0x79f88e976Aa2a8cdB9D49b5C0F72a0EDdFD00353',
}

// ─── ABI 片段 ──────────────────────────────────────────────
const ASF_ABI = [
  'function selfFund(uint256 agentId, uint256 sellAmount, uint256 orderId, address recipient) external',
  'function canSelfFund(uint256 agentId) view returns (bool ready, uint256 blocksRemaining, uint256 maxGold)',
  'function nextSellBlock(uint256 agentId) view returns (uint256)',
  'function maxSellAmount(uint256 agentId) view returns (uint256)',
  'function SELL_COOLDOWN_BLOCKS() view returns (uint256)',
  'function MIN_SELL_AMOUNT() view returns (uint256)',
]

const ROVEX_ABI = [
  `function buyOrders(uint256 orderId) view returns (
    uint256 orderId,
    address buyer,
    address token,
    address paymentToken,
    uint256 tokenAmount,
    uint256 totalPayment,
    uint256 price,
    uint256 filledAmount,
    uint8 status,
    uint256 createdAt
  )`,
  'function nextOrderId() view returns (uint256)',
]

// ─── 触发门槛 ──────────────────────────────────────────────
const BNB_THRESHOLD = ethers.parseEther('0.005')  // 低于 0.005 BNB 触发补充
const SELL_RATIO    = 80n                           // 使用最大出售量的 80%

/**
 * 主入口：检查是否需要 Gas 补充，需要则自动执行
 *
 * @param {ethers.Provider}  provider  BSC RPC provider
 * @param {ethers.Signer}    wallet    生命体 owner 钱包（签名用）
 * @param {number|bigint}    agentId   生命体 tokenId
 * @returns {object|null} 执行结果，null 表示未触发
 */
export async function checkAndSelfFund(provider, wallet, agentId) {
  if (!CONTRACTS.agentSelfFund) {
    console.log('[SelfFund] AgentSelfFund 合约地址未配置，跳过')
    return null
  }

  const ownerAddr = await wallet.getAddress()
  const agentIdBn = BigInt(agentId)

  // ── 1. 检查 BNB 余额 ──────────────────────────────────────
  const bnbBalance = await provider.getBalance(ownerAddr)
  if (bnbBalance > BNB_THRESHOLD) {
    // BNB 充足，无需补充
    return null
  }

  console.log(`[SelfFund] BNB 余额不足: ${ethers.formatEther(bnbBalance)} BNB，触发自主补充`)

  // ── 2. 检查合约前置条件 ────────────────────────────────────
  const asf = new ethers.Contract(CONTRACTS.agentSelfFund, ASF_ABI, wallet)
  const [ready, blocksRemaining, maxGold] = await asf.canSelfFund(agentIdBn)

  if (!ready) {
    const secRemaining = Number(blocksRemaining) * 0.75
    const hoursRemaining = (secRemaining / 3600).toFixed(1)
    console.log(`[SelfFund] 冷却中，还需 ${blocksRemaining} 个区块（约 ${hoursRemaining} 小时）`)
    return { status: 'cooldown', blocksRemaining, hoursRemaining }
  }

  const minSell = await asf.MIN_SELL_AMOUNT()
  if (maxGold < minSell) {
    console.log(`[SelfFund] 锁定余额不足 ${ethers.formatEther(minSell)} DNAGOLD，无法出售`)
    return { status: 'insufficient_locked', maxGold: ethers.formatEther(maxGold) }
  }

  // ── 3. 计算出售量（最大允许量的 80%）────────────────────────
  const sellAmount = maxGold * SELL_RATIO / 100n

  console.log(`[SelfFund] 准备出售 ${ethers.formatEther(sellAmount)} DNAGOLD（最大可售 ${ethers.formatEther(maxGold)}）`)

  // ── 4. 查找最优 prelist.cz 买单 ───────────────────────────
  const orderId = await findBestOrder(provider, sellAmount)
  if (orderId === null) {
    console.log('[SelfFund] prelist.cz 上当前没有可用的 DNAGOLD 买单，稍后重试')
    return { status: 'no_orders' }
  }

  console.log(`[SelfFund] 找到买单 #${orderId}，执行 selfFund...`)

  // ── 5. 执行 selfFund ──────────────────────────────────────
  try {
    // recipient = address(0)，合约自动将 BNB 打给 msg.sender（小号钱包自己）
    const tx = await asf.selfFund(agentIdBn, sellAmount, BigInt(orderId), ethers.ZeroAddress, {
      gasLimit: 300_000n,
    })
    console.log(`[SelfFund] TX 已提交: ${tx.hash}`)
    const receipt = await tx.wait()

    // 解析 AgentSelfFunded 事件
    const iface = new ethers.Interface(ASF_ABI)
    let bnbReceived = 0n
    for (const log of receipt.logs) {
      try {
        const parsed = iface.parseLog(log)
        if (parsed?.name === 'AgentSelfFunded') {
          bnbReceived = parsed.args.bnbReceived
        }
      } catch { /* skip */ }
    }

    console.log(`[SelfFund] ✅ 成功！获得 ${ethers.formatEther(bnbReceived)} BNB → ${ownerAddr}`)
    return {
      status:      'success',
      txHash:      receipt.hash,
      sellAmount:  ethers.formatEther(sellAmount),
      bnbReceived: ethers.formatEther(bnbReceived),
      orderId,
    }
  } catch (err) {
    // 解析 revert 原因
    const reason = parseRevertReason(err)
    console.error(`[SelfFund] ❌ 失败: ${reason}`)
    return { status: 'failed', reason }
  }
}

// ─── 查找最优买单 ──────────────────────────────────────────
/**
 * 扫描 prelist.cz RovexRouter，找出价格最高的 DNAGOLD 买单
 *
 * @param {ethers.Provider} provider
 * @param {bigint} sellAmount 需要至少这么多剩余量的买单
 * @returns {number|null} orderId，null 表示没有可用买单
 */
async function findBestOrder(provider, sellAmount) {
  const rovex     = new ethers.Contract(CONTRACTS.rovexRouter, ROVEX_ABI, provider)
  const nextId    = await rovex.nextOrderId()
  const scanLimit = 500n  // 最多扫最近 500 个订单
  const scanFrom  = nextId > scanLimit ? nextId - scanLimit : 0n

  let bestOrderId = null
  let bestPrice   = 0n

  const promises = []
  for (let i = scanFrom; i < nextId; i++) {
    promises.push(rovex.buyOrders(i).then(order => ({ i, order })).catch(() => null))
  }

  const results = await Promise.all(promises)

  for (const res of results) {
    if (!res) continue
    const { i, order } = res
    if (
      order.status === 0n &&                                          // OPEN
      order.token.toLowerCase() === CONTRACTS.dnagold.toLowerCase() && // DNAGOLD
      order.paymentToken === ethers.ZeroAddress &&                    // BNB 支付
      (order.tokenAmount - order.filledAmount) >= sellAmount          // 剩余量足够
    ) {
      if (order.price > bestPrice) {
        bestPrice   = order.price
        bestOrderId = Number(i)
      }
    }
  }

  if (bestOrderId !== null) {
    console.log(`[SelfFund] 最优买单 #${bestOrderId}，价格 ${ethers.formatEther(bestPrice)} BNB/DNAGOLD`)
  }
  return bestOrderId
}

// ─── 错误解析 ──────────────────────────────────────────────
function parseRevertReason(err) {
  // 尝试从 error.data 或 error.message 解析 revert reason
  const msg = err?.shortMessage || err?.message || String(err)
  
  // 常见 custom error 匹配
  const customErrors = {
    'NotAgentOwner':               '调用者不是生命体 owner',
    'CooldownActive':              '冷却期未结束',
    'SellAmountTooSmall':          '出售量低于最小门槛',
    'SellAmountExceedsLimit':      '出售量超过5%上限',
    'InsufficientLockedBalance':   '锁定余额不足',
    'OrderNotOpen':                '买单非 OPEN 状态（可能已被抢先成交）',
    'OrderTokenMismatch':          '买单目标代币不是 DNAGOLD',
    'OrderInsufficientRemaining':  '买单剩余量不足（可能已被部分成交）',
    'SwapProducedNoBnb':           'Swap 未返回 BNB',
    'BnbTransferFailed':           'BNB 转给 owner 失败',
  }

  for (const [errorName, desc] of Object.entries(customErrors)) {
    if (msg.includes(errorName)) return `${errorName}: ${desc}`
  }
  return msg
}
