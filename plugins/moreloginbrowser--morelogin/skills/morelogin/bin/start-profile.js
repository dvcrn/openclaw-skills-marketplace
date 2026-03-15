#!/usr/bin/env node

/**
 * Start and check MoreLogin profile status
 */

const { requestApi, unwrapApiResult } = require('./common');

async function startProfile(envId) {
  console.log(`🚀 Starting profile: ${envId}`);
  const response = await requestApi('/api/env/start', {
    method: 'POST',
    body: { envId },
  });
  const result = unwrapApiResult(response);
  if (!result.success) {
    throw new Error(result.message || 'Start failed');
  }
  return result.data;
}

async function statusProfile(envId) {
  const response = await requestApi('/api/env/status', {
    method: 'POST',
    body: { envId },
  });
  const result = unwrapApiResult(response);
  if (!result.success) {
    throw new Error(result.message || 'Status query failed');
  }
  return result.data;
}

async function main() {
  const args = process.argv.slice(2);
  const envId = args[0];

  if (!envId) {
    console.error('❌ Usage: node bin/start-profile.js <envId>');
    process.exit(1);
  }

  const startData = await startProfile(envId);
  console.log('✅ Started successfully');
  console.log(JSON.stringify(startData, null, 2));

  const statusData = await statusProfile(envId);
  console.log('\n📊 Current status');
  console.log(JSON.stringify(statusData, null, 2));
}

main().catch((error) => {
  console.error(`❌ ${error.message}`);
  process.exit(1);
});
