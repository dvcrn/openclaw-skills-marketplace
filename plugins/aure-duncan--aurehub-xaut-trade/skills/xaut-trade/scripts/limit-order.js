#!/usr/bin/env node
// skills/xaut-trade/scripts/limit-order.js
//
// Usage:
//   node limit-order.js place  --token-in <addr> --token-out <addr> \
//                               --amount-in <uint> --min-amount-out <uint> \
//                               --expiry <seconds> --wallet <addr> \
//                               --chain-id <int> --api-url <url>
//   node limit-order.js status --order-hash <0x...> --api-url <url> --chain-id <int>
//   node limit-order.js list   --wallet <addr> --api-url <url> --chain-id <int> [--order-status open|filled|expired|cancelled]
//   node limit-order.js cancel --nonce <uint>
//
// Signing mode (same as SKILL.md):
//   FOUNDRY_ACCOUNT + KEYSTORE_PASSWORD_FILE only.
//   PRIVATE_KEY runtime signing is intentionally not supported.
'use strict';

const { computeNonceComponents, checkPrecision } = require('./helpers');
const { ethers } = require('ethers');
const { execSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

// ethers v5 BigNumber (SDK uses .gte() etc — native BigInt not compatible)
const BN = ethers.BigNumber;

const [,, subcommand, ...argv] = process.argv;

function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, '').replace(/-([a-z])/g, (_, c) => c.toUpperCase());
    result[key] = args[i + 1];
  }
  return result;
}

async function main() {
  const args = parseArgs(argv);
  switch (subcommand) {
    case 'place':  return await place(args);
    case 'status': return await status(args);
    case 'list':   return await list(args);
    case 'cancel': return await cancel(args);
    default:
      console.error('Usage: limit-order.js <place|status|list|cancel> [options]');
      process.exit(1);
  }
}

main().catch(err => { console.error(err.message); process.exit(1); });

async function place(args) {
  const {
    tokenIn, tokenOut, amountIn, minAmountOut,
    expiry, wallet, chainId, apiUrl,
  } = args;

  // 1. Validate required args
  const required = { tokenIn, tokenOut, amountIn, minAmountOut, wallet, chainId, apiUrl };
  for (const [k, v] of Object.entries(required)) {
    if (!v) { console.error(`Missing required argument: --${k.replace(/([A-Z])/g, '-$1').toLowerCase()}`); process.exit(1); }
  }

  // Precision check: XAUT has 6 decimals max
  if (!checkPrecision(amountIn, 6)) {
    console.error('ERROR: XAUT amount exceeds maximum precision (6 decimal places)');
    process.exit(1);
  }

  const chainIdNum = parseInt(chainId, 10);
  const deadline = Math.floor(Date.now() / 1000) + parseInt(expiry || '86400', 10);

  // 2. Fetch nonce from UniswapX API
  // UniswapX API requires Origin header matching app.uniswap.org; may break if Uniswap changes policy
  const apiKey = process.env.UNISWAPX_API_KEY || '';
  const uniswapHeaders = {
    'Origin': 'https://app.uniswap.org',
    'User-Agent': 'Mozilla/5.0',
    ...(apiKey ? { 'x-api-key': apiKey } : {}),
  };
  const nonceRes = await fetch(`${apiUrl}/nonce?address=${wallet}&chainId=${chainId}`, { headers: uniswapHeaders });
  if (!nonceRes.ok) throw new Error(`Nonce fetch failed: ${nonceRes.status} ${await nonceRes.text()}`);
  const nonceData = await nonceRes.json();
  // Allow --nonce override to skip a used nonce; otherwise use API-returned nonce
  const nonce = args.nonce || nonceData.nonce;

  // 3. Build order using DutchOrderBuilder (no LimitOrderBuilder in SDK v2)
  //    Set decayStartTime === decayEndTime === deadline → zero decay = limit order
  //    SDK uses ethers v5 BigNumber (not native BigInt) — .gte() etc required
  const { DutchOrderBuilder } = require('@uniswap/uniswapx-sdk');
  const amountInBN = BN.from(amountIn);
  const minAmountOutBN = BN.from(minAmountOut);

  const builder = new DutchOrderBuilder(chainIdNum);
  const order = builder
    .deadline(deadline)
    .decayStartTime(deadline)
    .decayEndTime(deadline)
    .nonce(BN.from(nonce))
    .swapper(wallet)
    // input: startAmount === endAmount (no decay on input side)
    .input({ token: tokenIn, startAmount: amountInBN, endAmount: amountInBN })
    // output: startAmount === endAmount (fixed price, zero decay)
    .output({
      token: tokenOut,
      startAmount: minAmountOutBN,
      endAmount: minAmountOutBN,
      recipient: wallet,
    })
    .build();

  // 4. Sign via EIP-712
  const { domain, types, values } = order.permitData();
  // Serialize BigNumber → hex string so cast wallet sign can parse it
  const bnReplacer = (_, v) => (v && v.type === 'BigNumber' && v.hex) ? v.hex : v;
  // cast wallet sign requires primaryType and EIP712Domain in types
  const eip712Domain = [
    { name: 'name', type: 'string' },
    ...(domain.version !== undefined ? [{ name: 'version', type: 'string' }] : []),
    ...(domain.chainId !== undefined ? [{ name: 'chainId', type: 'uint256' }] : []),
    ...(domain.verifyingContract !== undefined ? [{ name: 'verifyingContract', type: 'address' }] : []),
  ];
  const primaryType = 'PermitWitnessTransferFrom'; // Permit2 fixed primary type
  const typesWithDomain = { EIP712Domain: eip712Domain, ...types };
  const typedDataJson = JSON.stringify({ domain, types: typesWithDomain, primaryType, message: values }, bnReplacer);
  let signature;

  const foundryAccount = process.env.FOUNDRY_ACCOUNT;
  const passwordFile = process.env.KEYSTORE_PASSWORD_FILE;
  const privateKey = process.env.PRIVATE_KEY;

  if (privateKey) {
    console.error('ERROR: PRIVATE_KEY runtime mode is deprecated. Migrate to FOUNDRY_ACCOUNT + KEYSTORE_PASSWORD_FILE.');
    process.exit(1);
  }

  if (foundryAccount && passwordFile) {
    // Keystore signing via cast subprocess
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'limit-order-'));
    const tmpFile = path.join(tmpDir, 'typed-data.json');
    fs.writeFileSync(tmpFile, typedDataJson);
    try {
      signature = execSync(
        `cast wallet sign --account "${foundryAccount}" --password-file "${passwordFile}" --data --from-file "${tmpFile}"`,
        { encoding: 'utf8' }
      ).trim();
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  } else {
    console.error('ERROR: Missing signing config. Set FOUNDRY_ACCOUNT + KEYSTORE_PASSWORD_FILE.');
    process.exit(1);
  }

  // 5. Submit to UniswapX API
  const encodedOrder = order.serialize();
  const orderHash = order.hash();

  const submitRes = await fetch(`${apiUrl}/order`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...uniswapHeaders },
    body: JSON.stringify({ encodedOrder, signature, chainId: chainIdNum }),
  });

  if (!submitRes.ok) {
    const body = await submitRes.text();
    throw new Error(`Order submission failed: ${submitRes.status} ${body}`);
  }

  // 6. Output JSON for SKILL.md to parse
  console.log(JSON.stringify({
    orderHash,
    deadline: new Date(deadline * 1000).toISOString(),
    deadlineUnix: deadline,
    nonce,
  }));
}

async function status(args) {
  const { orderHash, apiUrl, chainId } = args;
  if (!orderHash || !apiUrl || !chainId) {
    console.error('Missing required: --order-hash, --api-url, --chain-id');
    process.exit(1);
  }

  const apiKey = process.env.UNISWAPX_API_KEY || '';
  const res = await fetch(
    `${apiUrl}/orders?orderHash=${orderHash}&chainId=${chainId}`,
    { headers: {
      'Origin': 'https://app.uniswap.org',
      'User-Agent': 'Mozilla/5.0',
      ...(apiKey ? { 'x-api-key': apiKey } : {}),
    }}
  );
  if (!res.ok) throw new Error(`Status fetch failed: ${res.status} ${await res.text()}`);

  const data = await res.json();
  const orders = data.orders || [];

  if (orders.length === 0) {
    console.log(JSON.stringify({ status: 'not_found', orderHash }));
    return;
  }

  const o = orders[0];
  console.log(JSON.stringify({
    status: o.orderStatus,
    orderHash: o.orderHash,
    deadline: o.deadline ? new Date(o.deadline * 1000).toISOString() : null,
    txHash: o.txHash || null,
    settledAmounts: o.settledAmounts || null,
  }));
}

async function list(args) {
  const { wallet, apiUrl, chainId, orderStatus } = args;
  if (!wallet || !apiUrl || !chainId) {
    console.error('Missing required: --wallet, --api-url, --chain-id');
    process.exit(1);
  }

  const apiKey = process.env.UNISWAPX_API_KEY || '';
  const headers = {
    'Origin': 'https://app.uniswap.org',
    'User-Agent': 'Mozilla/5.0',
    ...(apiKey ? { 'x-api-key': apiKey } : {}),
  };

  let url = `${apiUrl}/orders?offerer=${wallet}&chainId=${chainId}`;
  if (orderStatus) url += `&orderStatus=${orderStatus}`;

  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error(`List fetch failed: ${res.status} ${await res.text()}`);

  const data = await res.json();
  const orders = (data.orders || []).map(o => ({
    orderHash: o.orderHash,
    status: o.orderStatus,
    inputToken: o.input?.token,
    inputAmount: o.input?.startAmount,
    outputToken: (o.outputs?.[0])?.token,
    outputAmount: (o.outputs?.[0])?.startAmount,
    txHash: o.txHash || null,
    createdAt: o.createdAt ? new Date(o.createdAt * 1000).toISOString() : null,
  }));

  console.log(JSON.stringify({ total: orders.length, orders }));
}

async function cancel(args) {
  const { nonce } = args;
  if (!nonce) {
    console.error('Missing required: --nonce');
    process.exit(1);
  }

  const { wordPos, mask } = computeNonceComponents(BigInt(nonce));

  // Output JSON for SKILL.md to capture and pass to cast send
  console.log(JSON.stringify({
    wordPos: wordPos.toString(),
    mask: mask.toString(),
    permit2: '0x000000000022D473030F116dDEE9F6B43aC78BA3',
  }));
}
