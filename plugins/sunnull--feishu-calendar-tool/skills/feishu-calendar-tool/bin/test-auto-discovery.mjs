#!/usr/bin/env node
/**
 * Test script for auto-discovery feature
 */

import { getConfig, clearCache } from '../lib/config.mjs';
import { getCalendarId, resetCalendarIdCache } from '../lib/calendar.mjs';
import { getUserId } from '../lib/config.mjs';

async function test() {
  console.log('\n🧪 Testing Auto-Discovery Feature\n');

  // Clear cache to test fresh discovery
  console.log('1️⃣ Clearing cache...');
  await clearCache();
  resetCalendarIdCache();
  console.log('✅ Cache cleared\n');

  // Test user_id discovery
  console.log('2️⃣ Testing user_id discovery...');
  try {
    const userId = await getUserId();
    console.log(`✅ Discovered user_id: ${userId}`);
  } catch (error) {
    console.log(`❌ Failed to discover user_id: ${error.message}`);
  }

  // Test calendar_id discovery
  console.log('\n3️⃣ Testing calendar_id discovery...');
  try {
    const calendarId = await getCalendarId();
    console.log(`✅ Discovered calendar_id: ${calendarId}`);
  } catch (error) {
    console.log(`❌ Failed to discover calendar_id: ${error.message}`);
  }

  // Test combined config
  console.log('\n4️⃣ Testing combined config...');
  try {
    const config = await getConfig();
    console.log(`✅ User ID: ${config.userId || '(not set)'}`);
    console.log(`✅ Calendar ID: ${config.calendarId || '(not set)'}`);
  } catch (error) {
    console.log(`❌ Failed to get config: ${error.message}`);
  }

  console.log('\n✨ Test complete!\n');
}

test().catch(console.error);
