#!/usr/bin/env node

/**
 * MoreLogin Local API connection test
 */

const { requestApi, unwrapApiResult } = require('./common');

async function testRequest(title, endpoint, method, body) {
  try {
    const response = await requestApi(endpoint, { method, body });
    const result = unwrapApiResult(response);
    if (result.success) {
      console.log(`✅ ${title}`);
      if (result.data !== undefined) {
        console.log(JSON.stringify(result.data, null, 2));
      }
      return true;
    }
    console.log(`❌ ${title} - ${result.message || 'API error'}`);
    return false;
  } catch (error) {
    console.log(`❌ ${title} - ${error.message}`);
    return false;
  }
}

async function main() {
  console.log('🔍 MoreLogin Local API test\n');

  const checks = [
    ['Browser profile list', '/api/env/page', 'POST', { page: 1, pageSize: 5 }],
    ['Cloud phone list', '/api/cloudphone/page', 'POST', { page: 1, pageSize: 5 }],
    ['Tag list', '/api/envtag/all', 'GET', undefined],
  ];

  let passed = 0;
  for (const [title, endpoint, method, body] of checks) {
    console.log(`\n📍 ${title} (${method} ${endpoint})`);
    const ok = await testRequest(title, endpoint, method, body);
    if (ok) passed += 1;
  }

  console.log(`\nDone: ${passed}/${checks.length} checks passed`);
  if (passed !== checks.length) {
    console.log('💡 Please ensure the MoreLogin desktop app is running and logged in.');
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error(`❌ ${error.message}`);
  process.exit(1);
});
