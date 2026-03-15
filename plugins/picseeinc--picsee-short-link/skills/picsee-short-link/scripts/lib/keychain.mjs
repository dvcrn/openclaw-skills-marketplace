#!/usr/bin/env node
// Cross-platform secure token storage using AES-256 encryption

import { readFileSync, writeFileSync, unlinkSync, existsSync, mkdirSync } from 'fs';
import { createCipheriv, createDecipheriv, randomBytes, createHash } from 'crypto';
import { homedir } from 'os';
import { join, dirname } from 'path';
import os from 'os';

const TOKEN_FILE = join(homedir(), '.openclaw', '.picsee_token');

/**
 * Generate machine-specific encryption key
 * Based on hostname + username (unique per machine/user)
 */
function getMachineKey() {
  const identifier = `${os.hostname()}-${os.userInfo().username}`;
  return createHash('sha256').update(identifier).digest();
}

/**
 * Encrypt token with AES-256-CBC
 */
function encryptToken(token) {
  const key = getMachineKey();
  const iv = randomBytes(16);
  const cipher = createCipheriv('aes-256-cbc', key, iv);
  
  let encrypted = cipher.update(token, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  
  // Format: iv:encrypted (both in hex)
  return iv.toString('hex') + ':' + encrypted;
}

/**
 * Decrypt token from AES-256-CBC
 */
function decryptToken(encrypted) {
  const key = getMachineKey();
  const parts = encrypted.split(':');
  
  if (parts.length !== 2) {
    throw new Error('Invalid encrypted token format');
  }
  
  const iv = Buffer.from(parts[0], 'hex');
  const encryptedText = parts[1];
  
  const decipher = createDecipheriv('aes-256-cbc', key, iv);
  let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  
  return decrypted;
}

/**
 * Store token securely (encrypted file)
 * @param {string} token - PicSee API token
 */
export function setToken(token) {
  if (!token || typeof token !== 'string') {
    throw new Error('Invalid token');
  }
  
  try {
    // Ensure directory exists
    const dir = dirname(TOKEN_FILE);
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }
    
    // Encrypt and write
    const encrypted = encryptToken(token);
    writeFileSync(TOKEN_FILE, encrypted, { mode: 0o600 });
    
    return true;
  } catch (err) {
    throw new Error(`Failed to store token: ${err.message}`);
  }
}

/**
 * Retrieve token from encrypted file
 * @returns {string|null} Token or null if not found
 */
export function getToken() {
  try {
    if (!existsSync(TOKEN_FILE)) {
      return null;
    }
    
    const encrypted = readFileSync(TOKEN_FILE, 'utf8').trim();
    const token = decryptToken(encrypted);
    
    return token || null;
  } catch (err) {
    // Token file corrupted or decryption failed
    return null;
  }
}

/**
 * Delete token file
 */
export function deleteToken() {
  try {
    if (existsSync(TOKEN_FILE)) {
      unlinkSync(TOKEN_FILE);
    }
    return true;
  } catch {
    return false;
  }
}
