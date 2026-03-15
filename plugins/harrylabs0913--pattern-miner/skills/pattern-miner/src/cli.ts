#!/usr/bin/env node
/**
 * Pattern Miner CLI
 * Commands: mine, list, analyze, apply, stats, export, config
 */

import { Command } from 'commander';
import * as path from 'path';
import * as fs from 'fs-extra';
import chalk from 'chalk';
import { DataCollector } from './collector';
import { PatternAnalyzer } from './analyzer';
import { PatternStorage } from './storage';
import { MinerConfig, ScanOptions, ApplyOptions } from './types';

const program = new Command();
const SKILL_DIR = path.resolve(__dirname, '..');
const DEFAULT_PATTERN_DIR = path.join(process.env.HOME || '~', '.pattern-miner');

// Default configuration
const defaultConfig: MinerConfig = {
  dataDir: path.join(process.env.HOME || '~', '.openclaw', 'workspace'),
  patternDir: DEFAULT_PATTERN_DIR,
  minConfidence: 0.6,
  minFrequency: 3,
  analysisTypes: ['cluster', 'association', 'anomaly'],
  sources: [
    {
      type: 'conversation',
      name: 'conversations',
      path: path.join(process.env.HOME || '~', '.openclaw', 'sessions'),
      pattern: '**/*.json'
    },
    {
      type: 'decision',
      name: 'decisions',
      path: path.join(process.env.HOME || '~', '.openclaw', 'decisions'),
      pattern: '**/*.json'
    },
    {
      type: 'task',
      name: 'tasks',
      path: path.join(process.env.HOME || '~', '.openclaw', 'workspace'),
      pattern: '**/*.{json,md}'
    }
  ],
  autoScan: false,
  scanInterval: 60,
  maxPatterns: 1000,
  retentionDays: 30
};

program
  .name('pattern-miner')
  .description('Intelligent pattern recognition and actionable insights')
  .version('1.0.0');

program
  .command('mine')
  .description('Run pattern mining on collected data')
  .option('-i, --incremental', 'Only scan new data since last run')
  .option('-s, --sources <sources>', 'Comma-separated list of sources to scan')
  .option('-t, --types <types>', 'Analysis types (cluster,association,anomaly)')
  .option('-o, --output <file>', 'Output results to file')
  .action(async (options) => {
    console.log(chalk.blue('🔍 Starting pattern mining...\n'));
    
    const config = await loadConfig();
    const storage = new PatternStorage(config.patternDir, config);
    await storage.initialize();
    
    const collector = new DataCollector();
    for (const source of config.sources) {
      collector.addSource(source);
    }
    
    const scanOptions: ScanOptions = {
      incremental: options.incremental,
      sources: options.sources?.split(','),
      analysisTypes: options.types?.split(',') as any[]
    };
    
    console.log(chalk.gray('Collecting data from sources...'));
    const data = await collector.collectAll(scanOptions);
    console.log(chalk.green(`✓ Collected ${data.length} items\n`));
    
    if (data.length === 0) {
      console.log(chalk.yellow('No data to analyze. Configure sources or add data.'));
      return;
    }
    
    console.log(chalk.gray('Running pattern analysis...'));
    const analyzer = new PatternAnalyzer(SKILL_DIR);
    const results = await analyzer.analyze(data, scanOptions);
    
    console.log(chalk.green(`✓ Found ${results.summary.totalPatterns} patterns`));
    console.log(chalk.green(`✓ Generated ${results.summary.totalInsights} insights\n`));
    
    await storage.savePatterns(results.patterns);
    await storage.saveInsights(results.insights);
    
    if (options.output) {
      await fs.writeFile(options.output, JSON.stringify(results, null, 2));
      console.log(chalk.green(`✓ Results saved to ${options.output}\n`));
    }
    
    // Display top insights
    if (results.insights.length > 0) {
      console.log(chalk.bold('\n📊 Top Insights:\n'));
      results.insights.slice(0, 5).forEach((insight, i) => {
        console.log(chalk.cyan(`${i + 1}. ${insight.title}`));
        console.log(chalk.gray(`   ${insight.description}`));
        console.log(chalk.yellow(`   → Action: ${insight.action}`));
        console.log();
      });
    }
  });

program
  .command('list')
  .description('List discovered patterns')
  .option('-t, --type <type>', 'Filter by pattern type')
  .option('-l, --limit <n>', 'Limit results', '10')
  .option('-v, --verbose', 'Show full details')
  .action(async (options) => {
    const config = await loadConfig();
    const storage = new PatternStorage(config.patternDir, config);
    
    let patterns = await storage.loadPatterns();
    
    if (options.type) {
      patterns = patterns.filter(p => p.type === options.type);
    }
    
    const limit = parseInt(options.limit, 10);
    patterns = patterns.slice(0, limit);
    
    if (patterns.length === 0) {
      console.log(chalk.yellow('No patterns found. Run "pattern-miner mine" first.'));
      return;
    }
    
    console.log(chalk.bold(`\n📋 Discovered Patterns (${patterns.length}):\n`));
    
    patterns.forEach((pattern, i) => {
      const icon = pattern.type === 'cluster' ? '🔷' : 
                   pattern.type === 'association' ? '🔗' : 
                   pattern.type === 'anomaly' ? '⚠️' : '📌';
      
      console.log(chalk.cyan(`${icon} ${i + 1}. [${pattern.type}] ${pattern.id}`));
      
      if (options.verbose) {
        console.log(chalk.gray(`   Confidence: ${(pattern.confidence * 100).toFixed(1)}%`));
        console.log(chalk.gray(`   Frequency: ${pattern.frequency}`));
        console.log(chalk.gray(`   Importance: ${(pattern.importance * 100).toFixed(1)}%`));
        console.log(chalk.gray(`   Source: ${pattern.source}`));
        console.log(chalk.gray(`   Created: ${pattern.createdAt.toISOString()}`));
      } else {
        console.log(chalk.gray(`   Items: ${pattern.items.length} | Confidence: ${(pattern.confidence * 100).toFixed(0)}%`));
      }
      console.log();
    });
  });

program
  .command('analyze')
  .description('Analyze specific patterns or insights')
  .option('-p, --pattern <id>', 'Analyze specific pattern')
  .option('-i, --insight <id>', 'Analyze specific insight')
  .option('-c, --category <category>', 'Filter insights by category')
  .action(async (options) => {
    const config = await loadConfig();
    const storage = new PatternStorage(config.patternDir, config);
    
    if (options.pattern) {
      const pattern = await storage.getPatternById(options.pattern);
      if (!pattern) {
        console.log(chalk.red(`Pattern ${options.pattern} not found`));
        return;
      }
      
      console.log(chalk.bold(`\n🔷 Pattern Analysis: ${pattern.id}\n`));
      console.log(chalk.cyan('Type:'), pattern.type);
      console.log(chalk.cyan('Confidence:'), `${(pattern.confidence * 100).toFixed(1)}%`);
      console.log(chalk.cyan('Frequency:'), pattern.frequency);
      console.log(chalk.cyan('Importance:'), `${(pattern.importance * 100).toFixed(1)}%`);
      console.log(chalk.cyan('Source:'), pattern.source);
      console.log(chalk.cyan('Created:'), pattern.createdAt.toISOString());
      console.log(chalk.cyan('\nItems:'));
      pattern.items.slice(0, 5).forEach((item, i) => {
        console.log(chalk.gray(`  ${i + 1}. ${item.slice(0, 200)}...`));
      });
      return;
    }
    
    if (options.insight) {
      const insight = await storage.getInsightById(options.insight);
      if (!insight) {
        console.log(chalk.red(`Insight ${options.insight} not found`));
        return;
      }
      
      console.log(chalk.bold(`\n💡 Insight Analysis: ${insight.id}\n`));
      console.log(chalk.cyan('Title:'), insight.title);
      console.log(chalk.cyan('Description:'), insight.description);
      console.log(chalk.cyan('Action:'), insight.action);
      console.log(chalk.cyan('Priority:'), insight.priority);
      console.log(chalk.cyan('Expected Impact:'), `${(insight.expectedImpact * 100).toFixed(1)}%`);
      console.log(chalk.cyan('Category:'), insight.category);
      console.log(chalk.cyan('Applied:'), insight.applied ? 'Yes' : 'No');
      return;
    }
    
    if (options.category) {
      const insights = await storage.getInsightsByCategory(options.category);
      console.log(chalk.bold(`\n📊 Insights in category "${options.category}" (${insights.length}):\n`));
      insights.forEach((i, idx) => {
        console.log(chalk.cyan(`${idx + 1}. ${i.title}`));
        console.log(chalk.gray(`   Priority: ${i.priority} | Impact: ${(i.expectedImpact * 100).toFixed(0)}%`));
        console.log();
      });
      return;
    }
    
    // Default: show summary
    const stats = await storage.getStats();
    console.log(chalk.bold('\n📊 Pattern Mining Summary:\n'));
    console.log(chalk.cyan('Total Patterns:'), stats.totalPatterns);
    console.log(chalk.cyan('Total Insights:'), stats.totalInsights);
    console.log(chalk.cyan('Applied Insights:'), stats.appliedInsights);
    console.log(chalk.cyan('\nBy Type:'));
    Object.entries(stats.byType).forEach(([type, count]) => {
      console.log(chalk.gray(`  ${type}: ${count}`));
    });
    console.log(chalk.cyan('\nBy Category:'));
    Object.entries(stats.byCategory).forEach(([cat, count]) => {
      console.log(chalk.gray(`  ${cat}: ${count}`));
    });
  });

program
  .command('apply')
  .description('Apply insights to generate improvements')
  .option('-i, --insight <id>', 'Apply specific insight')
  .option('-c, --category <category>', 'Apply all insights in category')
  .option('--dry-run', 'Show what would be applied without making changes')
  .option('--confirm', 'Skip confirmation prompts')
  .action(async (options) => {
    const config = await loadConfig();
    const storage = new PatternStorage(config.patternDir, config);
    
    const applyOptions: ApplyOptions = {
      dryRun: options.dryRun,
      confirm: options.confirm,
      categories: options.category ? [options.category] : undefined
    };
    
    let insights = await storage.loadInsights();
    insights = insights.filter(i => !i.applied);
    
    if (options.insight) {
      insights = insights.filter(i => i.id === options.insight);
    }
    
    if (options.category) {
      insights = insights.filter(i => i.category === options.category);
    }
    
    if (insights.length === 0) {
      console.log(chalk.yellow('No insights to apply.'));
      return;
    }
    
    console.log(chalk.bold(`\n🎯 Insights to Apply (${insights.length}):\n`));
    
    insights.forEach((insight, i) => {
      console.log(chalk.cyan(`${i + 1}. ${insight.title}`));
      console.log(chalk.gray(`   Action: ${insight.action}`));
      console.log(chalk.gray(`   Priority: ${insight.priority}`));
      console.log();
    });
    
    if (applyOptions.dryRun) {
      console.log(chalk.yellow('\n⚠️  Dry run - no changes made\n'));
      return;
    }
    
    if (!applyOptions.confirm) {
      console.log(chalk.yellow('Run with --confirm to apply insights'));
      return;
    }
    
    // Apply insights
    for (const insight of insights) {
      console.log(chalk.gray(`Applying: ${insight.title}...`));
      await storage.markInsightApplied(insight.id);
      console.log(chalk.green(`✓ Applied: ${insight.id}\n`));
    }
    
    console.log(chalk.green(`✓ Applied ${insights.length} insights`));
  });

program
  .command('stats')
  .description('Show mining statistics')
  .action(async () => {
    const config = await loadConfig();
    const storage = new PatternStorage(config.patternDir, config);
    const stats = await storage.getStats();
    
    console.log(chalk.bold('\n📊 Pattern Mining Statistics:\n'));
    console.log(chalk.cyan('Total Patterns:'), stats.totalPatterns);
    console.log(chalk.cyan('Total Insights:'), stats.totalInsights);
    console.log(chalk.cyan('Applied Insights:'), stats.appliedInsights);
    console.log(chalk.cyan('Pending Insights:'), stats.totalInsights - stats.appliedInsights);
    
    console.log(chalk.cyan('\nPatterns by Type:'));
    Object.entries(stats.byType).forEach(([type, count]) => {
      const bar = '█'.repeat(Math.ceil(count / 10));
      console.log(chalk.gray(`  ${type.padEnd(15)} ${count.toString().padStart(4)} ${bar}`));
    });
    
    console.log(chalk.cyan('\nInsights by Category:'));
    Object.entries(stats.byCategory).forEach(([cat, count]) => {
      const bar = '█'.repeat(Math.ceil(count / 5));
      console.log(chalk.gray(`  ${cat.padEnd(15)} ${count.toString().padStart(4)} ${bar}`));
    });
  });

program
  .command('export')
  .description('Export patterns to file')
  .option('-f, --format <format>', 'Output format (json|csv)', 'json')
  .option('-o, --output <file>', 'Output file path')
  .action(async (options) => {
    const config = await loadConfig();
    const storage = new PatternStorage(config.patternDir, config);
    
    const content = await storage.exportPatterns(options.format as 'json' | 'csv');
    
    if (options.output) {
      await fs.writeFile(options.output, content);
      console.log(chalk.green(`✓ Exported to ${options.output}`));
    } else {
      console.log(content);
    }
  });

program
  .command('config')
  .description('Show or edit configuration')
  .option('--init', 'Initialize default configuration')
  .option('--show', 'Show current configuration')
  .action(async (options) => {
    const configPath = path.join(DEFAULT_PATTERN_DIR, 'config.json');
    
    if (options.init) {
      await fs.ensureDir(DEFAULT_PATTERN_DIR);
      await fs.writeFile(configPath, JSON.stringify(defaultConfig, null, 2));
      console.log(chalk.green(`✓ Configuration initialized at ${configPath}`));
      return;
    }
    
    if (options.show) {
      const config = await loadConfig();
      console.log(chalk.bold('\n⚙️  Current Configuration:\n'));
      console.log(JSON.stringify(config, null, 2));
      return;
    }
    
    // Default: show config location
    console.log(chalk.gray(`Config file: ${configPath}`));
    console.log(chalk.gray(`Pattern dir: ${DEFAULT_PATTERN_DIR}`));
  });

async function loadConfig(): Promise<MinerConfig> {
  const configPath = path.join(DEFAULT_PATTERN_DIR, 'config.json');
  
  try {
    const content = await fs.readFile(configPath, 'utf-8');
    return { ...defaultConfig, ...JSON.parse(content) };
  } catch {
    return defaultConfig;
  }
}

program.parse();
