#!/usr/bin/env node
/**
 * PolyClawster Swap — convert POL or native USDC to USDC.e for trading
 *
 * Usage:
 *   node swap.js                    # Auto-detect and swap all available
 *   node swap.js --pol 10           # Swap 10 POL → USDC.e
 *   node swap.js --usdc 15          # Swap 15 native USDC → USDC.e
 *   node swap.js --check            # Check balances only
 */
'use strict';
const { loadConfig } = require('./setup');

const POLYGON_RPC = 'https://polygon-bor-rpc.publicnode.com';
const USDC_NATIVE = '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359';
const USDC_E      = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174';
const WMATIC      = '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270';
const SWAP_ROUTER = '0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45'; // Uniswap SwapRouter02

const ERC20_ABI = [
  'function balanceOf(address) view returns (uint256)',
  'function approve(address,uint256) returns (bool)',
  'function allowance(address,address) view returns (uint256)',
];

async function run() {
  const config = loadConfig();
  if (!config?.privateKey) throw new Error('No config. Run: node scripts/setup.js --auto');

  const { ethers } = await import('ethers');
  const provider = new ethers.providers.JsonRpcProvider(POLYGON_RPC);
  const wallet = new ethers.Wallet(config.privateKey, provider);

  const polBal = await provider.getBalance(wallet.address);
  const usdcNative = new ethers.Contract(USDC_NATIVE, ERC20_ABI, wallet);
  const usdcE = new ethers.Contract(USDC_E, ERC20_ABI, wallet);

  const nativeBal = await usdcNative.balanceOf(wallet.address);
  const eBal = await usdcE.balanceOf(wallet.address);

  console.log('📊 Balances:');
  console.log('   POL:         ' + parseFloat(ethers.utils.formatEther(polBal)).toFixed(4));
  console.log('   USDC:        $' + ethers.utils.formatUnits(nativeBal, 6));
  console.log('   USDC.e:      $' + ethers.utils.formatUnits(eBal, 6) + ' (trading token)');
  console.log('');

  if (process.argv.includes('--check')) return;

  const gasPrice = await provider.getGasPrice();
  const opts = { gasLimit: 300000, gasPrice: gasPrice.mul(2), type: 0 };

  const router = new ethers.Contract(SWAP_ROUTER, [
    'function exactInputSingle((address tokenIn, address tokenOut, uint24 fee, address recipient, uint256 amountIn, uint256 amountOutMinimum, uint160 sqrtPriceLimitX96)) external payable returns (uint256)',
    'function multicall(uint256 deadline, bytes[] data) external payable returns (bytes[])',
  ], wallet);

  // Parse args
  const args = process.argv.slice(2);
  let swapPol = 0, swapUsdc = 0;

  const polIdx = args.indexOf('--pol');
  const usdcIdx = args.indexOf('--usdc');

  if (polIdx >= 0 && args[polIdx + 1]) {
    swapPol = parseFloat(args[polIdx + 1]);
  } else if (usdcIdx >= 0 && args[usdcIdx + 1]) {
    swapUsdc = parseFloat(args[usdcIdx + 1]);
  } else {
    // Auto: swap native USDC first, then POL if no USDC
    if (nativeBal.gt(0)) {
      swapUsdc = parseFloat(ethers.utils.formatUnits(nativeBal, 6));
    } else {
      // Keep 1 POL for gas, swap rest
      const polFloat = parseFloat(ethers.utils.formatEther(polBal));
      if (polFloat > 2) swapPol = polFloat - 1;
    }
  }

  // Swap native USDC → USDC.e (1:1 stablecoin pool)
  if (swapUsdc > 0) {
    const amountIn = ethers.utils.parseUnits(swapUsdc.toFixed(6), 6);
    if (amountIn.gt(nativeBal)) {
      console.log('❌ Insufficient USDC balance');
      return;
    }

    // Approve router
    const allowance = await usdcNative.allowance(wallet.address, SWAP_ROUTER);
    if (allowance.lt(amountIn)) {
      console.log('⏳ Approving USDC for swap...');
      const tx = await usdcNative.approve(SWAP_ROUTER, ethers.constants.MaxUint256, opts);
      await tx.wait();
    }

    console.log('🔄 Swapping $' + swapUsdc.toFixed(2) + ' USDC → USDC.e...');
    const tx = await router.exactInputSingle({
      tokenIn: USDC_NATIVE,
      tokenOut: USDC_E,
      fee: 100, // 0.01% stablecoin pool
      recipient: wallet.address,
      amountIn,
      amountOutMinimum: amountIn.mul(99).div(100),
      sqrtPriceLimitX96: 0,
    }, opts);
    console.log('   TX: ' + tx.hash);
    await tx.wait();
    const newBal = await usdcE.balanceOf(wallet.address);
    console.log('✅ Done! USDC.e balance: $' + ethers.utils.formatUnits(newBal, 6));
  }

  // Swap POL → USDC.e (POL → WMATIC → USDC.e)
  if (swapPol > 0) {
    const amountIn = ethers.utils.parseEther(swapPol.toFixed(4));
    if (amountIn.gt(polBal)) {
      console.log('❌ Insufficient POL balance');
      return;
    }

    console.log('🔄 Swapping ' + swapPol.toFixed(2) + ' POL → USDC.e...');

    // Wrap POL → WMATIC, then swap WMATIC → USDC.e
    // Use multicall: wrapETH + exactInputSingle
    const iface = new ethers.utils.Interface([
      'function exactInputSingle((address tokenIn, address tokenOut, uint24 fee, address recipient, uint256 amountIn, uint256 amountOutMinimum, uint160 sqrtPriceLimitX96)) returns (uint256)',
    ]);

    const swapData = iface.encodeFunctionData('exactInputSingle', [{
      tokenIn: WMATIC,
      tokenOut: USDC_E,
      fee: 500, // 0.05% fee tier for WMATIC/USDC.e
      recipient: wallet.address,
      amountIn: amountIn,
      amountOutMinimum: 0, // accept any (POL is volatile)
      sqrtPriceLimitX96: 0,
    }]);

    // Wrap + swap via multicall
    const wrapIface = new ethers.utils.Interface(['function wrapETH(uint256 value)']);
    const wrapData = wrapIface.encodeFunctionData('wrapETH', [amountIn]);

    const deadline = Math.floor(Date.now() / 1000) + 300;
    const tx = await router.multicall(deadline, [wrapData, swapData], {
      ...opts,
      value: amountIn,
    });
    console.log('   TX: ' + tx.hash);
    await tx.wait();
    const newBal = await usdcE.balanceOf(wallet.address);
    console.log('✅ Done! USDC.e balance: $' + ethers.utils.formatUnits(newBal, 6));
  }

  if (swapPol === 0 && swapUsdc === 0) {
    console.log('ℹ️  Nothing to swap. Send POL or USDC to: ' + wallet.address);
  }
}

run().catch(e => { console.error('❌ Error:', e.message); process.exit(1); });
