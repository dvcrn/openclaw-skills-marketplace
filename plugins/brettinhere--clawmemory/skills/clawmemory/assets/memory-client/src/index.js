"use strict";
/**
 * index.js — @omp/memory-client public API
 *
 * Re-exports all modules for use as a programmatic SDK.
 */

const { deriveKey, encrypt, decrypt }       = require("./crypto");
const { buildTree, getProof, verifyProof, CHUNK_SIZE } = require("./merkle");
const { generatePermitSignature }            = require("./permit");
const { writeAndConfirm }                    = require("./hypercore");
const { createChainClient }                  = require("./chain");
const { buildIndexFile, parseIndexFile }     = require("./index-file");
const { loadWallet, createWallet }           = require("./wallet");

module.exports = {
  // Crypto
  deriveKey,
  encrypt,
  decrypt,
  // Merkle
  buildTree,
  getProof,
  verifyProof,
  CHUNK_SIZE,
  // Permit
  generatePermitSignature,
  // P2P
  writeAndConfirm,
  // Chain
  createChainClient,
  // Index
  buildIndexFile,
  parseIndexFile,
  // Wallet
  loadWallet,
  createWallet,
};
