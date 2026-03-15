#!/usr/bin/env node
/**
 * PolyClawster Approve — one-time on-chain USDC approval for live trading
 *
 * Approves the Polymarket CTF Exchange contract to spend your USDC.
 * Required ONCE before your first live trade.
 * Requires a small amount of POL for gas (~0.01 POL).
 *
 * Usage:
 *   node approve.js           # Check status and approve if needed
 *   node approve.js --check   # Check approval status only (no tx)
 */
'use strict';
const { loadConfig } = require('./setup');

// Polygon mainnet contract addresses
const USDC_CONTRACT     = '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359'; // native USDC (Polygon)
const USDC_E_CONTRACT   = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'; // USDC.e
const CTF_EXCHANGE      = '0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E'; // Polymarket CTF Exchange
const NEG_RISK_EXCHANGE = '0xC5d563A36AE78145C45a50134d48A1215220f80a'; // Neg Risk CTF Exchange
const POLYGON_RPC       = 'https://polygon-bor-rpc.publicnode.com';

// Minimal ERC20 ABI for approve + allowance
const ERC20_ABI = [
  'function approve(address spender, uint256 amount) external returns (bool)',
  'function allowance(address owner, address spender) external view returns (uint256)',
  'function balanceOf(address account) external view returns (uint256)',
];

async function run(checkOnly = false) {
  const config = loadConfig();
  if (!config?.privateKey) {
    throw new Error('No config. Run: node scripts/setup.js --auto');
  }

  const { ethers } = await import('ethers');

  const provider = new ethers.providers.JsonRpcProvider(POLYGON_RPC);
  const wallet   = new ethers.Wallet(config.privateKey, provider);

  console.log(`📋 Wallet: ${wallet.address}`);
  console.log('');

  // Check POL balance for gas
  const polBalance = await provider.getBalance(wallet.address);
  const polFormatted = parseFloat(ethers.utils.formatEther(polBalance)).toFixed(4);
  console.log(`⛽ POL balance: ${polFormatted} (needed: ~0.01 for gas)`);

  if (parseFloat(polFormatted) < 0.005) {
    console.log('');
    console.log('⚠️  Insufficient POL for gas. Send at least 0.01 POL to:');
    console.log(`   ${wallet.address}`);
    console.log('   (POL is Polygon\'s native token, available on any CEX)');
    if (!checkOnly) process.exit(1);
    return;
  }

  const INFINITY = ethers.constants.MaxUint256;
  const contracts = [
    { label: 'USDC (native)', address: USDC_CONTRACT },
    { label: 'USDC.e',        address: USDC_E_CONTRACT },
  ];
  const spenders = [
    { label: 'CTF Exchange',      address: CTF_EXCHANGE },
    { label: 'Neg Risk Exchange', address: NEG_RISK_EXCHANGE },
  ];

  console.log('');
  console.log('🔍 Checking USDC approvals...');
  console.log('');

  for (const token of contracts) {
    const erc20 = new ethers.Contract(token.address, ERC20_ABI, wallet);

    // Check USDC balance
    let balance = 0;
    try {
      const rawBal = await erc20.balanceOf(wallet.address);
      balance = parseFloat(ethers.utils.formatUnits(rawBal, 6));
    } catch {}
    console.log(`💵 ${token.label} balance: $${balance.toFixed(2)}`);

    for (const spender of spenders) {
      let allowance = BigInt(0);
      try {
        allowance = BigInt((await erc20.allowance(wallet.address, spender.address)).toString());
      } catch {}

      const approved = allowance > BigInt('1000000000000'); // > $1M = effectively infinite
      const status   = approved ? '✅ approved' : '❌ not approved';
      console.log(`   ${spender.label}: ${status}`);

      if (!approved && !checkOnly) {
        console.log(`   → Approving ${token.label} for ${spender.label}...`);
        try {
          const gasPrice = await provider.getGasPrice();
          const tx = await erc20.approve(spender.address, INFINITY, { gasLimit: 100000, gasPrice: gasPrice.mul(2), type: 0 });
          console.log(`   → TX: ${tx.hash}`);
          await tx.wait();
          console.log(`   ✅ Done!`);
        } catch (e) {
          console.warn(`   ⚠️  Approval failed: ${e.message}`);
        }
      }
    }
    console.log('');
  }

  // CTF Conditional Tokens approvals (setApprovalForAll)
  const CTF_CONTRACT = '0x4D97DCd97eC945f40cF65F87097ACe5EA0476045';
  const ctf = new ethers.Contract(CTF_CONTRACT, [
    'function isApprovedForAll(address owner, address operator) view returns (bool)',
    'function setApprovalForAll(address operator, bool approved) external',
  ], wallet);

  const ctfSpenders = [
    { label: 'CTF Exchange',      address: CTF_EXCHANGE },
    { label: 'Neg Risk Exchange', address: NEG_RISK_EXCHANGE },
    { label: 'Neg Risk Adapter',  address: '0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296' },
  ];

  console.log('🔍 Checking CTF (Conditional Tokens) approvals...');
  console.log('');
  for (const spender of ctfSpenders) {
    const approved = await ctf.isApprovedForAll(wallet.address, spender.address);
    console.log('   ' + spender.label + ': ' + (approved ? '✅ approved' : '❌ not approved'));
    if (!approved && !checkOnly) {
      console.log('   → Setting approval...');
      try {
        const gasPrice = await provider.getGasPrice();
        const tx = await ctf.setApprovalForAll(spender.address, true, { gasLimit: 100000, gasPrice: gasPrice.mul(2), type: 0 });
        console.log('   → TX: ' + tx.hash);
        await tx.wait();
        console.log('   ✅ Done!');
      } catch (e) {
        console.warn('   ⚠️  Approval failed: ' + e.message);
      }
    }
  }
  console.log('');

  if (!checkOnly) {
    console.log('✅ All approvals complete! You can now live-trade on Polymarket.');
    console.log('   node scripts/trade.js --market "bitcoin-100k" --side YES --amount 5');
  }
}

if (require.main === module) {
  const checkOnly = process.argv.includes('--check');
  if (checkOnly) console.log('🔍 Checking approvals (read-only)...\n');
  else console.log('⚡ Setting up USDC approvals for live trading...\n');

  run(checkOnly).catch(e => {
    console.error('❌ Error:', e.message);
    process.exit(1);
  });
}
