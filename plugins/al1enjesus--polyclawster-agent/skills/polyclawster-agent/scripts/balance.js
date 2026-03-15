#!/usr/bin/env node
/**
 * PolyClawster Balance — check all balances
 */
'use strict';
const { loadConfig } = require('./setup');

async function run() {
  const config = loadConfig();
  if (!config?.privateKey) throw new Error('Not configured. Run: node scripts/setup.js --auto');

  const { ethers } = await import('ethers');
  const provider = new ethers.providers.JsonRpcProvider('https://polygon-bor-rpc.publicnode.com');
  const wallet = new ethers.Wallet(config.privateKey, provider);

  const USDC_E = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174';
  const USDC_NATIVE = '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359';

  const usdce = new ethers.Contract(USDC_E, ['function balanceOf(address) view returns (uint256)'], provider);
  const usdc = new ethers.Contract(USDC_NATIVE, ['function balanceOf(address) view returns (uint256)'], provider);

  const polBal = await provider.getBalance(wallet.address);
  const usdceBal = await usdce.balanceOf(wallet.address);
  const usdcBal = await usdc.balanceOf(wallet.address);

  console.log('💰 ' + wallet.address);
  console.log('');
  console.log('   POL:        ' + parseFloat(ethers.utils.formatEther(polBal)).toFixed(4));
  console.log('   USDC.e:     $' + ethers.utils.formatUnits(usdceBal, 6) + '  ← trading token');
  if (usdcBal.gt(0)) {
    console.log('   USDC:       $' + ethers.utils.formatUnits(usdcBal, 6) + '  ← run swap.js to convert');
  }

  // CLOB balance
  if (config.clobApiKey && config.clobApiSecret) {
    try {
      const { ClobClient, SignatureType } = await import('@polymarket/clob-client');
      const signer = new ethers.Wallet(config.privateKey);
      const creds = { key: config.clobApiKey, secret: config.clobApiSecret, passphrase: config.clobApiPassphrase };
      const client = new ClobClient('https://clob.polymarket.com', 137, signer, creds, SignatureType.EOA, signer.address);
      await client.updateBalanceAllowance({ asset_type: 'COLLATERAL' });
      const bal = await client.getBalanceAllowance({ asset_type: 'COLLATERAL' });
      console.log('   CLOB:       $' + (parseInt(bal.balance) / 1e6).toFixed(2) + '  ← available for orders');
    } catch {}
  }

  console.log('');
  console.log('📋 Polygonscan: https://polygonscan.com/address/' + wallet.address);
  console.log('');
  console.log('To fund: send POL (Polygon) to ' + wallet.address);
  console.log('Then run: node scripts/swap.js');
}

run().catch(e => { console.error('❌', e.message); process.exit(1); });
