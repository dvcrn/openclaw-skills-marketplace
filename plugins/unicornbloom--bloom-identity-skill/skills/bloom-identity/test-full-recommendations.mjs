#!/usr/bin/env nodeThe Connect X Account button doesn't work. Right now, LearnHowItWorks is on the same row as Connect X Account, so I think it's in the wrong position.c

/**
 * Test full recommendation flow including ClawHub + Claude Code + GitHub
 */

import { ClaudeCodeClient } from './src/integrations/claude-code-client.ts';

async function testFullFlow() {
  console.log('🧪 Testing Full Recommendation Flow\n');

  // Simulate "The Trailblazer" identity (AI Tools + Productivity)
  const testIdentity = {
    personalityType: 'The Trailblazer',
    mainCategories: ['AI Tools', 'Productivity'],
    subCategories: ['Wellness', 'Education'],
  };

  console.log('📋 Test Identity:', testIdentity);
  console.log('');

  // Test Claude Code Client
  console.log('🔷 Testing Claude Code Client...');
  const claudeCodeClient = new ClaudeCodeClient();

  try {
    const claudeCodeRecs = await claudeCodeClient.getRecommendations({
      mainCategories: testIdentity.mainCategories,
      subCategories: testIdentity.subCategories,
      limit: 10,
    });

    console.log(`✅ Claude Code: ${claudeCodeRecs.length} recommendations`);

    if (claudeCodeRecs.length > 0) {
      console.log('\n📦 Top 3 Claude Code recommendations:');
      claudeCodeRecs.slice(0, 3).forEach((rec, i) => {
        console.log(`\n${i + 1}. ${rec.skillName}`);
        console.log(`   Type: ${rec.type}`);
        console.log(`   Source: ${rec.source}`);
        console.log(`   Description: ${rec.description.substring(0, 80)}...`);
        console.log(`   URL: ${rec.url}`);
      });

      // Verify data structure matches what frontend expects
      console.log('\n✅ Data structure validation:');
      const firstRec = claudeCodeRecs[0];
      const hasRequiredFields =
        firstRec.skillName &&
        firstRec.description &&
        firstRec.url &&
        firstRec.source === 'ClaudeCode';

      console.log(`   - Has skillName: ${!!firstRec.skillName}`);
      console.log(`   - Has description: ${!!firstRec.description}`);
      console.log(`   - Has url: ${!!firstRec.url}`);
      console.log(`   - Source is 'ClaudeCode': ${firstRec.source === 'ClaudeCode'}`);
      console.log(`   - Structure valid: ${hasRequiredFields ? '✅' : '❌'}`);

      // Simulate what would be sent to backend
      console.log('\n📤 Sample recommendation object (what gets sent to backend):');
      console.log(JSON.stringify({
        skillName: firstRec.skillName,
        description: firstRec.description,
        url: firstRec.url,
        matchScore: 85,
        source: 'ClaudeCode',
        creator: firstRec.creator,
      }, null, 2));

    } else {
      console.log('⚠️  No Claude Code recommendations found!');
      console.log('   This might indicate:');
      console.log('   - GitHub API rate limiting');
      console.log('   - Network issues');
      console.log('   - Parsing errors');
    }

  } catch (error) {
    console.error('❌ Claude Code test failed:', error.message);
    throw error;
  }

  console.log('\n' + '='.repeat(60));
  console.log('✅ Test Complete!');
  console.log('='.repeat(60));
}

testFullFlow().catch(error => {
  console.error('\n❌ Test failed:', error);
  process.exit(1);
});
