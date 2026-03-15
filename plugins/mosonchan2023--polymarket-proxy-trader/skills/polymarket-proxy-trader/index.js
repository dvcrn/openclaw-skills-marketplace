/**
 * Polymarket Proxy Wallet Trader + Balance Fix
 * 
 * 专治 Polymarket proxy_wallet read balance 问题
 * 支持 reading balance 和 execute trade
 * 每次调用自动通过 SkillPay.me 收取 0.001 USDT
 * 
 * 使用方法:
 * - 设置环境变量: SKILLPAY_API_KEY, PRIVATE_KEY, PROXY_ADDRESS
 * - 调用: handler(input, context)
 */

const { ClobClient, AssetType, Side, OrderType } = require('@polymarket/clob-client');
const { Wallet } = require('ethers');

// ============================================
// 配置 - 从环境变量读取
// ============================================
const SKILLPAY_API_KEY = process.env.SKILLPAY_API_KEY;
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const PROXY_ADDRESS = process.env.PROXY_ADDRESS;

// Polymarket 配置
const CLOB_HOST = 'https://clob.polymarket.com';
const CHAIN_ID = 137; // Polygon mainnet

// ============================================
// SkillPay 集成 - 3 行代码
// ============================================
async function chargeUser(userId, skillSlug = 'polymarket-proxy-trader') {
  try {
    // SkillPay API 端点 (基于 skillpay.me 文档)
    const response = await fetch('https://api.skillpay.me/v1/billing/charge', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SKILLPAY_API_KEY}`
      },
      body: JSON.stringify({
        user_id: userId,
        amount: 0.001,
        currency: 'USDT',
        skill_slug: skillSlug
      })
    });

    const result = await response.json();
    
    if (result.success) {
      return { paid: true, transaction_id: result.transaction_id };
    } else {
      return { 
        paid: false, 
        payment_url: result.payment_url || `https://skillpay.me/pay/${skillSlug}?user=${userId}&amount=0.001`,
        error: result.error
      };
    }
  } catch (error) {
    // 如果 SkillPay 服务不可用，跳过收费（开发测试用）
    console.error('SkillPay charge error:', error.message);
    return { paid: true, debug: true }; // 开发模式跳过收费
  }
}

// ============================================
// Polymarket 客户端初始化
// ============================================
function getClient() {
  if (!PRIVATE_KEY) {
    throw new Error('PRIVATE_KEY not configured');
  }

  const signer = new Wallet(PRIVATE_KEY);
  
  // 创建临时客户端来派生 API credentials
  const tempClient = new ClobClient(CLOB_HOST, CHAIN_ID, signer);
  
  // 派生 API credentials
  let apiCreds;
  try {
    apiCreds = tempClient.createOrDeriveApiKey();
  } catch (e) {
    console.log('Using existing API credentials');
    apiCreds = null;
  }

  // 创建完整客户端
  // signature_type: 0=EOA, 1=POLY_PROXY, 2=GNOSIS_SAFE (proxy wallet)
  const client = new ClobClient(
    CLOB_HOST,
    CHAIN_ID,
    signer,
    apiCreds,
    PROXY_ADDRESS ? 2 : 0, // 如果有 proxy address 用 2，否则用 0
    PROXY_ADDRESS || signer.address
  );

  return client;
}

// ============================================
// 核心功能: 读取余额 (修复 proxy wallet bug)
// ============================================
async function readBalance(client, proxyAddress) {
  // 关键修复: 强制使用 proxyAddress 作为 funder
  const funder = proxyAddress || PROXY_ADDRESS || client.address;
  
  try {
    // 获取 USDC (Collateral) 余额
    const usdcBalance = await client.getBalanceAllowance({
      asset_type: AssetType.COLLATERAL,
      funder: funder
    });

    // 格式化余额 (USDC 是 6 位小数)
    const balance = usdcBalance.balance || '0';
    const allowance = usdcBalance.allowance || '0';
    
    const balanceFormatted = (parseInt(balance) / 1e6).toFixed(6);
    const allowanceFormatted = (parseInt(allowance) / 1e6).toFixed(6);

    return {
      success: true,
      type: 'USDC',
      balance: balanceFormatted,
      allowance: allowanceFormatted,
      funder: funder,
      raw: usdcBalance
    };
  } catch (error) {
    // 如果官方 API 失败，尝试使用 data API
    console.error('Balance check error:', error.message);
    return {
      success: false,
      error: error.message,
      suggestion: '尝试使用 data-api.polymarket.com'
    };
  }
}

// ============================================
// 核心功能: 执行交易
// ============================================
async function executeTrade(client, orderParams) {
  const { tokenId, side, size, price, orderType = 'GTC' } = orderParams;
  
  if (!tokenId || !side || !size) {
    throw new Error('Missing required params: tokenId, side, size');
  }

  // 转换 side 为大写
  const orderSide = side.toUpperCase() === 'BUY' ? Side.BUY : Side.SELL;
  
  // 转换 order type
  let orderTypeEnum;
  switch (orderType.toUpperCase()) {
    case 'FOK':
      orderTypeEnum = OrderType.FOK;
      break;
    case 'GTD':
      orderTypeEnum = OrderType.GTD;
      break;
    default:
      orderTypeEnum = OrderType.GTC; // 默认 GTC
  }

  try {
    // 创建并提交订单
    const result = await client.createAndPostOrder(
      {
        tokenID: tokenId,
        price: price || 0.5,
        size: parseFloat(size),
        side: orderSide
      },
      {
        tickSize: '0.01',
        negRisk: false
      },
      orderTypeEnum
    );

    return {
      success: true,
      orderId: result.orderID,
      status: result.status,
      transactions: result.transactionsHashes,
      message: `订单已提交! ${orderSide === Side.BUY ? '买入' : '卖出'} ${size} @ $${price || 0.5}`
    };
  } catch (error) {
    console.error('Trade execution error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// ============================================
// 主处理函数 - Skill 入口点
// ============================================
async function handler(input, context) {
  // 获取 userId (从 context 或使用默认值)
  const userId = context?.userId || context?.user?.id || 'anonymous';
  
  // ========================================
  // Step 1: SkillPay 收费 (0.001 USDT)
  // ========================================
  console.log(`[Polymarket-Proxy-Trader] Charging user: ${userId}`);
  
  const chargeResult = await chargeUser(userId);
  
  if (!chargeResult.paid) {
    return {
      error: 'PAYMENT_REQUIRED',
      message: '请先支付 0.001 USDT',
      paymentUrl: chargeResult.payment_url,
      amount: '0.001 USDT',
      skill: 'polymarket-proxy-trader'
    };
  }

  console.log(`[Polymarket-Proxy-Trader] Payment confirmed, proceeding...`);

  // ========================================
  // Step 2: 解析用户输入
  // ========================================
  const { action, ...params } = input;
  
  // 支持的 action 类型
  const actionType = (action || '').toLowerCase();
  
  let result;

  try {
    // ========================================
    // Step 3: 执行对应功能
    // ========================================
    if (actionType === 'balance' || actionType === 'read_balance' || actionType === 'get_balance') {
      // 读取余额
      const client = getClient();
      const proxyAddress = params.proxyAddress || PROXY_ADDRESS;
      result = await readBalance(client, proxyAddress);
      
      if (result.success) {
        return {
          success: true,
          type: 'BALANCE',
          data: {
            balance: `${result.balance} USDC`,
            allowance: `${result.allowance} USDC`,
            wallet: result.funder
          },
          message: `✅ Proxy Wallet 余额: ${result.balance} USDC\n可用额度: ${result.allowance} USDC\n地址: ${result.funder}`
        };
      } else {
        return {
          success: false,
          error: result.error,
          message: `❌ 读取余额失败: ${result.error}`
        };
      }
      
    } else if (actionType === 'trade' || actionType === 'execute' || actionType === 'order') {
      // 执行交易
      const client = getClient();
      
      result = await executeTrade(client, {
        tokenId: params.tokenId || params.market,
        side: params.side,
        size: params.size || params.amount,
        price: params.price,
        orderType: params.orderType || 'GTC'
      });
      
      if (result.success) {
        return {
          success: true,
          type: 'TRADE',
          data: {
            orderId: result.orderId,
            status: result.status
          },
          message: `✅ ${result.message}\n订单ID: ${result.orderId}`
        };
      } else {
        return {
          success: false,
          error: result.error,
          message: `❌ 交易失败: ${result.error}`
        };
      }
      
    } else if (actionType === 'cancel') {
      // 取消订单
      const client = getClient();
      const orderId = params.orderId;
      
      if (!orderId) {
        return {
          success: false,
          error: 'Missing orderId',
          message: '请提供要取消的订单ID'
        };
      }
      
      try {
        const cancelResult = await client.cancelOrder(orderId);
        return {
          success: true,
          type: 'CANCEL',
          message: `✅ 订单已取消: ${orderId}`
        };
      } catch (e) {
        return {
          success: false,
          error: e.message,
          message: `❌ 取消失败: ${e.message}`
        };
      }
      
    } else {
      // 未知 action，返回帮助信息
      return {
        success: false,
        error: 'UNKNOWN_ACTION',
        message: `未知操作: ${action}\n\n支持的操作:\n- balance: 读取余额\n- trade: 执行交易\n- cancel: 取消订单\n\n示例:\n{ action: 'balance' }\n{ action: 'trade', tokenId: '...', side: 'BUY', size: 100, price: 0.5 }`,
        supportedActions: ['balance', 'trade', 'cancel']
      };
    }
    
  } catch (error) {
    console.error('[Polymarket-Proxy-Trader] Error:', error);
    return {
      success: false,
      error: error.message,
      message: `❌ 执行失败: ${error.message}`
    };
  }
}

// ============================================
// 导出
// ============================================
module.exports = { handler, chargeUser, readBalance, executeTrade };
