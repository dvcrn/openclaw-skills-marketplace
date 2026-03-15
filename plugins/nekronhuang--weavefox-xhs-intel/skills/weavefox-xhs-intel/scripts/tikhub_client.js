#!/usr/bin/env node

/**
 * TikHub API 共享客户端（小红书数据源）
 *
 * API Key 来源优先级：
 * 1. 脚本参数 --api-key
 * 2. 内置默认 Key（测试用）
 *
 */

const BASE_URL = 'https://api.tikhub.io';

// 保守请求间隔：1s
const DEFAULT_REQUEST_INTERVAL_MS = 1000;

// 测试 token
const DEFAULT_API_KEY = 'h88oLcQJzUazwWOsPbqYnRb7JymhZYZk5kmEqX2aDfGYu22geVOifmmxDQ==';

/**
 * 获取 API Key
 * 优先级：CLI 参数 > 内置默认
 */
function getApiKey(cliApiKey) {
  return cliApiKey || DEFAULT_API_KEY;
}

/**
 * 获取监控关键词列表（默认列表）
 */
function getMonitorKeywords() {
  return [];
}

/**
 * 获取监控用户 ID 列表
 */
function getMonitorUserIds() {
  return [];
}

/**
 * 延时
 */
function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

/**
 * 调用 TikHub API（GET 请求）
 */
async function callTikHubAPI(endpoint, params = {}, apiKey) {
  const key = getApiKey(apiKey);
  if (!key) {
    throw new Error(
      'No TikHub API key found. 请通过 --api-key 参数配置'
    );
  }

  const qs = new URLSearchParams(params).toString();
  const url = `${BASE_URL}${endpoint}${qs ? '?' + qs : ''}`;

  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${key}` },
    signal: AbortSignal.timeout(15000),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(`TikHub API ${response.status}: ${data.detail?.message || data.message || JSON.stringify(data)}`);
  }

  return data;
}

/**
 * 调用 TikHub API（POST 请求）
 */
async function callTikHubAPIPost(endpoint, body = {}, apiKey) {
  const key = getApiKey(apiKey);
  if (!key) {
    throw new Error(
      'No TikHub API key found. 请通过 --api-key 参数配置'
    );
  }

  const url = `${BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(15000),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(`TikHub API ${response.status}: ${data.detail?.message || data.message || JSON.stringify(data)}`);
  }

  return data;
}

/**
 * 批量调用，自动处理限流
 */
async function callTikHubAPIBatch(calls, apiKey) {
  const results = [];
  for (let i = 0; i < calls.length; i++) {
    const { endpoint, params, label } = calls[i];
    try {
      const data = await callTikHubAPI(endpoint, params, apiKey);
      results.push({ label, success: true, data });
    } catch (e) {
      results.push({ label, success: false, error: e.message });
    }
    if (i < calls.length - 1) {
      await sleep(DEFAULT_REQUEST_INTERVAL_MS);
    }
  }
  return results;
}

module.exports = {
  callTikHubAPI,
  callTikHubAPIPost,
  callTikHubAPIBatch,
  getApiKey,
  getMonitorKeywords,
  getMonitorUserIds,
  sleep,
  BASE_URL,
  DEFAULT_REQUEST_INTERVAL_MS,
};
