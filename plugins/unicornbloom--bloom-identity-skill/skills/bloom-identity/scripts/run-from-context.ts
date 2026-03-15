/**
 * Run Bloom Identity Analysis from Conversation Context
 *
 * This script is designed to be called by OpenClaw bot with conversation text piped to stdin.
 * It analyzes the conversation directly without reading session files.
 *
 * Usage:
 *   echo "conversation text here" | npx tsx scripts/run-from-context.ts --user-id telegram:123
 */

import 'dotenv/config';
import { Command } from 'commander';
import { BloomIdentitySkillV2, ExecutionMode } from '../src/bloom-identity-skill-v2';
import * as readline from 'readline';

const program = new Command();

program
  .name('bloom-identity-from-context')
  .description('Generate Bloom Identity Card from provided conversation context')
  .version('2.0.0')
  .requiredOption('--user-id <userId>', 'User ID (e.g., telegram:123, discord:456)')
  .option('--mode <mode>', 'Execution mode: auto, manual, or data_only', 'auto')
  .option('--skip-share', 'Skip Twitter share link generation', false)
  .parse(process.argv);

const options = program.opts();

async function readConversationFromStdin(): Promise<string> {
  return new Promise((resolve, reject) => {
    const lines: string[] = [];
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      terminal: false,
    });

    rl.on('line', (line) => {
      lines.push(line);
    });

    rl.on('close', () => {
      const conversationText = lines.join('\n');
      if (conversationText.trim().length === 0) {
        reject(new Error('No conversation text provided via stdin'));
      } else {
        resolve(conversationText);
      }
    });

    rl.on('error', (error) => {
      reject(error);
    });
  });
}

async function main() {
  try {
    console.log('🌸 Bloom Identity Card Generator (from context)');
    console.log('============================================\n');

    // Read conversation text from stdin
    console.log('📖 Reading conversation from stdin...');
    const conversationText = await readConversationFromStdin();
    console.log(`✅ Received ${conversationText.length} characters of conversation text\n`);

    // Run Bloom analysis with provided conversation
    const skill = new BloomIdentitySkillV2();

    const result = await skill.execute(options.userId, {
      mode: options.mode as ExecutionMode,
      skipShare: options.skipShare,
      conversationText, // ⭐ Provide conversation directly
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
    if (error instanceof Error && error.stack) {
      console.error('\nStack trace:', error.stack);
    }
    process.exit(1);
  }
}

function formatResult(result: any): void {
  const { identityData, agentWallet, recommendations, mode, dimensions, dashboardUrl } = result;

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

  // Skills (diverse recommendations from all sources)
  console.log(`🎯 Recommended for You (${recommendations.length}):\n`);
  recommendations.slice(0, 7).forEach((skill: any, i: number) => {
    const creatorInfo = skill.creator ? ` • ${skill.creator}` : '';
    console.log(`${i + 1}. ${skill.skillName}${creatorInfo}`);
    console.log(`   ${skill.description}`);
    if (skill.reason) {
      console.log(`   💡 ${skill.reason}`);
    }
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

  console.log('═══════════════════════════════════════════════════════\n');
  console.log(`${mode === 'manual' ? '📝 Q&A' : '🤖 Conversation'} • @openclaw @coinbase @base 🦞\n`);
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
