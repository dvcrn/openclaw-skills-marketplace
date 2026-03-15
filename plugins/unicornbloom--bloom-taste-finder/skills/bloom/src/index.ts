/**
 * Bloom Identity Card Generator - CLI Entry Point
 *
 * OpenClaw skill wrapper for bloom-identity-skill-v2
 */

import 'dotenv/config';
import { Command } from 'commander';
import { BloomIdentitySkillV2, ExecutionMode } from './bloom-identity-skill-v2';

const program = new Command();

program
  .name('bloom-identity')
  .description('Generate Bloom Identity Card from Twitter/X and on-chain data')
  .version('2.0.0')
  .requiredOption('--user-id <userId>', 'OpenClaw user ID')
  .option('--mode <mode>', 'Execution mode: auto, manual, or hybrid', 'auto')
  .option('--skip-share', 'Skip Twitter share link generation', false)
  .option('--mint-to-base', 'Mint identity card as SBT on Base', false)
  .parse(process.argv);

const options = program.opts();

async function main() {
  try {
    console.log('🌸 Bloom Identity Card Generator');
    console.log('================================\n');

    const skill = new BloomIdentitySkillV2();

    const result = await skill.execute(options.userId, {
      mode: options.mode as ExecutionMode,
      skipShare: options.skipShare,
      mintToBase: options.mintToBase,
    });

    if (!result.success) {
      if (result.needsManualInput) {
        console.error('\n❌ Insufficient data. Manual Q&A required.');
        console.error('Questions:', result.manualQuestions);
        process.exit(1);
      }

      console.error(`\n❌ Failed: ${result.error}`);
      process.exit(1);
    }

    // Format and output the result
    formatResult(result);

  } catch (error) {
    console.error('\n❌ Error:', error instanceof Error ? error.message : 'Unknown error');
    process.exit(1);
  }
}

function formatResult(result: any): void {
  const { identityData, agentWallet, recommendations, mode, dimensions, dashboardUrl, actions } = result;

  const modeEmoji = mode === 'manual' ? '📝' : '🤖';

  // Top border
  console.log('\n═══════════════════════════════════════════════════════');
  console.log(`🎉 Your Bloom Identity Card is ready! ${modeEmoji}`);
  console.log('═══════════════════════════════════════════════════════\n');

  // Dashboard URL first (most important)
  if (dashboardUrl) {
    console.log('🔗 VIEW YOUR IDENTITY CARD (Click below):\n');
    console.log(`   ${dashboardUrl}\n`);
  }

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  // Personality (real data from analysis)
  console.log(`${getPersonalityEmoji(identityData.personalityType)} ${identityData.personalityType}`);
  console.log(`💬 "${identityData.customTagline}"\n`);
  console.log(`📝 ${identityData.customDescription}\n`);

  // Categories (real data)
  console.log(`🏷️  Categories: ${identityData.mainCategories.join(', ')}`);
  if (identityData.subCategories && identityData.subCategories.length > 0) {
    console.log(`   Interests: ${identityData.subCategories.join(', ')}`);
  }
  console.log('');

  // 2x2 Metrics (real data if available)
  if (dimensions) {
    const isCultivator = identityData.personalityType === 'The Cultivator';

    console.log('📊 2x2 Metrics:');
    console.log(`   Conviction ${dimensions.conviction} ← → Curiosity ${100 - dimensions.conviction}`);
    console.log(`   Intuition ${dimensions.intuition} ← → Analysis ${100 - dimensions.intuition}`);

    // Only show contribution for The Cultivator
    if (isCultivator) {
      console.log(`   Contribution: ${dimensions.contribution}/100`);
    }
    console.log('');
  }

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  // Skills (real recommendations from ClawHub)
  console.log(`🎯 Recommended OpenClaw Skills (${recommendations.length}):\n`);
  recommendations.slice(0, 5).forEach((skill: any, i: number) => {
    const creatorInfo = skill.creator ? ` • ${skill.creator}` : '';
    console.log(`${i + 1}. ${skill.skillName} (${skill.matchScore}% match)${creatorInfo}`);
    console.log(`   ${skill.description}`);
    console.log(`   💡 Tip creators with your Agent wallet!`);
    console.log(`   → ${skill.url}\n`);
  });

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  // Wallet info with marketing message
  console.log('🤖 Your Agent Wallet Created\n');
  console.log(`   Network: ${agentWallet?.network || 'Base'}`);
  console.log('   Status: ✅ Wallet generated and registered\n');
  console.log('   💡 Use your agent wallet to tip skill creators!');
  console.log('   ⚠️  Tipping, payments, and management features coming soon');
  console.log('   🔒 Do not deposit funds - withdrawals not ready yet\n');

  if (actions?.mint) {
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    console.log('🪪 SBT Minted on Base:\n');
    console.log(`   Contract: ${actions.mint.contractAddress}`);
    console.log(`   Tx: ${actions.mint.txHash}`);
    console.log(`   Network: ${actions.mint.network}`);
    console.log('');
  }

  console.log('═══════════════════════════════════════════════════════\n');
  console.log(`${mode === 'manual' ? '📝 Q&A' : '🤖 On-chain'} • @openclaw @coinbase @base 🦞\n`);
}

function getPersonalityEmoji(type: string): string {
  const emojiMap: Record<string, string> = {
    'The Visionary': '💜',
    'The Explorer': '💚',
    'The Cultivator': '🩷',
    'The Optimizer': '🧡',
    'The Innovator': '💙',
  };
  return emojiMap[type] || '🌸';
}

// Run the CLI
main();
