"use strict";
/**
 * permit.js — EIP-2612 Permit signature generation
 *
 * Allows gasless approvals: instead of sending an approve() transaction,
 * the user signs a typed message off-chain and the contract verifies it
 * on-chain, combining approve + transfer into a single tx.
 *
 * SECURITY: domain name must exactly match the ERC20Permit constructor argument
 * to prevent signature replay across contracts. Here: 'Memory Protocol Token'
 */

const { ethers } = require("ethers");

/**
 * Generate an EIP-2612 permit signature.
 *
 * @param {ethers.Wallet}  wallet      Signer wallet (owner of tokens)
 * @param {string}         mmpAddress  MMPToken contract address
 * @param {string}         spender     Contract that will spend tokens (MemoryProtocol)
 * @param {bigint|string}  value       Amount to approve (in MMP wei)
 * @param {number}         deadline    Unix timestamp expiry
 * @returns {Promise<{v: number, r: string, s: string, deadline: number}>}
 */
async function generatePermitSignature(wallet, mmpAddress, spender, value, deadline) {
  // Fetch the current nonce for the owner from the ERC20Permit contract
  const mmpAbi = [
    "function nonces(address owner) view returns (uint256)",
    "function DOMAIN_SEPARATOR() view returns (bytes32)",
  ];
  const mmpContract = new ethers.Contract(mmpAddress, mmpAbi, wallet.provider);
  const nonce = await mmpContract.nonces(wallet.address);

  const chainId = (await wallet.provider.getNetwork()).chainId;

  // EIP-712 Domain — name MUST match ERC20Permit constructor: 'Memory Protocol Token'
  const domain = {
    name:              "Memory Protocol Token",
    version:           "1",
    chainId:           chainId,
    verifyingContract: mmpAddress,
  };

  // EIP-2612 Permit type
  const types = {
    Permit: [
      { name: "owner",    type: "address" },
      { name: "spender",  type: "address" },
      { name: "value",    type: "uint256" },
      { name: "nonce",    type: "uint256" },
      { name: "deadline", type: "uint256" },
    ],
  };

  const message = {
    owner:    wallet.address,
    spender:  spender,
    value:    BigInt(value),
    nonce:    nonce,
    deadline: BigInt(deadline),
  };

  // Sign using EIP-712 (signTypedData)
  const signature = await wallet.signTypedData(domain, types, message);
  const { v, r, s } = ethers.Signature.from(signature);

  return { v, r, s, deadline };
}

module.exports = { generatePermitSignature };
