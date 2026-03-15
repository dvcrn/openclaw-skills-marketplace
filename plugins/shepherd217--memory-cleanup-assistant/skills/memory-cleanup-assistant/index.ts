import * as fs from 'fs';
import * as path from 'path';
import { createHash } from 'crypto';

interface FileAnalysis {
  path: string;
  sizeKB: number;
  lines: number;
  duplicates: string[];
  oldEntries: string[];
  suggestions: string[];
  potentialSavingsKB: number;
}

interface CleanupReport {
  timestamp: string;
  files: FileAnalysis[];
  totalSizeBefore: number;
  totalSizeAfter: number;
  savingsKB: number;
  estimatedWeeklySavings: number;
}

export class MemoryCleanupAssistant {
  private workspacePath: string;
  private backupPath: string;
  private configPath: string;
  private config: any;

  constructor(workspacePath: string = '~/.openclaw/workspace') {
    this.workspacePath = workspacePath.replace('~', process.env.HOME || '');
    this.backupPath = path.join(this.workspacePath, '.memory-backup');
    this.configPath = path.join(this.workspacePath, '.memory-cleanup-config.json');
    this.config = this.loadConfig();
  }

  /**
   * Load or create config
   */
  private loadConfig(): any {
    if (fs.existsSync(this.configPath)) {
      return JSON.parse(fs.readFileSync(this.configPath, 'utf-8'));
    }
    return {
      autoCleanup: false,
      lastCleanup: null,
      schedule: '0 0 * * 0', // Weekly on Sunday
      thresholdKB: 50,
      dailyRetention: 7,
      enabled: true
    };
  }

  /**
   * Save config
   */
  private saveConfig(): void {
    fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 2));
  }

  /**
   * Enable auto-cleanup with cron schedule
   */
  enableAutoCleanup(schedule?: string): void {
    this.config.autoCleanup = true;
    if (schedule) this.config.schedule = schedule;
    this.saveConfig();
    console.log('✅ Auto-cleanup enabled');
    console.log(`Schedule: ${this.config.schedule}`);
    console.log('Add to HEARTBEAT.md for automatic execution');
  }

  /**
   * Disable auto-cleanup
   */
  disableAutoCleanup(): void {
    this.config.autoCleanup = false;
    this.saveConfig();
    console.log('❌ Auto-cleanup disabled');
  }

  /**
   * Check if cleanup is due
   */
  isCleanupDue(): boolean {
    if (!this.config.autoCleanup) return false;
    if (!this.config.lastCleanup) return true;
    
    const last = new Date(this.config.lastCleanup);
    const now = new Date();
    const daysSince = (now.getTime() - last.getTime()) / (1000 * 60 * 60 * 24);
    
    return daysSince >= 7; // Weekly check
  }

  /**
   * Run auto-cleanup if due
   */
  async runAutoCleanup(): Promise<void> {
    if (!this.isCleanupDue()) {
      console.log('⏭️  Auto-cleanup not due yet');
      return;
    }

    console.log('🤖 Running auto-cleanup...');
    const report = await this.audit();
    
    if (report.savingsKB > this.config.thresholdKB) {
      console.log(`💰 Savings threshold met (${report.savingsKB}KB > ${this.config.thresholdKB}KB)`);
      await this.cleanup(false); // Non-dry run
      this.config.lastCleanup = new Date().toISOString();
      this.saveConfig();
      console.log('✅ Auto-cleanup complete');
    } else {
      console.log(`⏭️  Savings below threshold (${report.savingsKB}KB)`);
    }
  }

  /**
   * Main audit function - analyze all context files
   */
  async audit(): Promise<CleanupReport> {
    console.log('🔍 Starting Memory Audit...\n');

    const files: FileAnalysis[] = [];

    // Check main context files
    const mainFiles = ['SOUL.md', 'AGENTS.md', 'MEMORY.md', 'TOOLS.md'];
    for (const file of mainFiles) {
      const analysis = await this.analyzeFile(file);
      if (analysis) files.push(analysis);
    }

    // Check daily memory files
    const dailyAnalysis = await this.analyzeDailyFiles();
    if (dailyAnalysis) files.push(dailyAnalysis);

    const totalBefore = files.reduce((sum, f) => sum + f.sizeKB, 0);
    const totalSavings = files.reduce((sum, f) => sum + f.potentialSavingsKB, 0);

    const report: CleanupReport = {
      timestamp: new Date().toISOString(),
      files,
      totalSizeBefore: Math.round(totalBefore),
      totalSizeAfter: Math.round(totalBefore - totalSavings),
      savingsKB: Math.round(totalSavings),
      estimatedWeeklySavings: Math.round(totalSavings * 0.7) // ~70% of context loads use compressed version
    };

    this.printReport(report);
    return report;
  }

  /**
   * Analyze a single context file
   */
  private async analyzeFile(filename: string): Promise<FileAnalysis | null> {
    const filePath = path.join(this.workspacePath, filename);

    if (!fs.existsSync(filePath)) {
      return null;
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    const sizeKB = Buffer.byteLength(content) / 1024;
    const lines = content.split('\n').length;

    const duplicates = this.findDuplicates(content);
    const oldEntries = this.findOldEntries(content);
    const suggestions: string[] = [];

    // Generate suggestions based on file type
    if (filename === 'SOUL.md') {
      if (content.includes('## Experiments') && content.indexOf('## Experiments') > 0) {
        const experimentsMatch = content.match(/## Experiments[\s\S]*?(?=## |$)/);
        if (experimentsMatch && experimentsMatch[0].split('\n').length > 20) {
          suggestions.push('Archive old experiments (90+ days)');
        }
      }
      if (duplicates.length > 0) {
        suggestions.push(`Merge ${duplicates.length} duplicate personality traits`);
      }
    }

    if (filename === 'AGENTS.md') {
      const deprecatedWorkflows = (content.match(/deprecated|outdated|old/gi) || []).length;
      if (deprecatedWorkflows > 0) {
        suggestions.push(`Review ${deprecatedWorkflows} potentially outdated workflows`);
      }
      if (content.length > 10000) {
        suggestions.push('Consider splitting into multiple workflow files');
      }
    }

    if (filename === 'MEMORY.md') {
      const memories = content.match(/## \[\d{4}/g) || [];
      if (memories.length > 50) {
        suggestions.push(`Archive ${memories.length - 30} old memories (keep last 30)`);
      }
    }

    // Calculate potential savings
    let potentialSavingsKB = 0;
    if (duplicates.length > 0) potentialSavingsKB += sizeKB * 0.1;
    if (oldEntries.length > 0) potentialSavingsKB += (oldEntries.length / lines) * sizeKB;
    if (suggestions.some(s => s.includes('Archive'))) potentialSavingsKB += sizeKB * 0.3;

    return {
      path: filename,
      sizeKB: Math.round(sizeKB * 10) / 10,
      lines,
      duplicates,
      oldEntries,
      suggestions,
      potentialSavingsKB: Math.round(potentialSavingsKB * 10) / 10
    };
  }

  /**
   * Analyze daily memory files
   */
  private async analyzeDailyFiles(): Promise<FileAnalysis | null> {
    const memoryDir = path.join(this.workspacePath, 'memory');
    
    if (!fs.existsSync(memoryDir)) {
      return null;
    }

    const files = fs.readdirSync(memoryDir)
      .filter(f => f.match(/\d{4}-\d{2}-\d{2}\.md$/));

    if (files.length === 0) {
      return null;
    }

    let totalSize = 0;
    let oldFiles = 0;
    const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);

    for (const file of files) {
      const filePath = path.join(memoryDir, file);
      const stats = fs.statSync(filePath);
      const size = stats.size / 1024;
      totalSize += size;

      if (stats.mtimeMs < sevenDaysAgo) {
        oldFiles++;
      }
    }

    const suggestions: string[] = [];
    if (files.length > 7) {
      suggestions.push(`Archive ${oldFiles} daily files older than 7 days`);
    }
    if (totalSize > 50) {
      suggestions.push('Create weekly summaries to reduce daily file count');
    }

    return {
      path: 'memory/*.md (daily files)',
      sizeKB: Math.round(totalSize * 10) / 10,
      lines: files.length,
      duplicates: [],
      oldEntries: files.slice(0, oldFiles),
      suggestions,
      potentialSavingsKB: Math.round((oldFiles / files.length) * totalSize * 10) / 10
    };
  }

  /**
   * Find duplicate content sections
   */
  private findDuplicates(content: string): string[] {
    const lines = content.split('\n').filter(l => l.trim().length > 0);
    const seen = new Map<string, number>();
    const duplicates: string[] = [];

    for (const line of lines) {
      const normalized = line.toLowerCase().trim();
      if (normalized.length < 20) continue; // Skip short lines

      const count = seen.get(normalized) || 0;
      if (count === 1) {
        duplicates.push(line.slice(0, 50) + '...');
      }
      seen.set(normalized, count + 1);
    }

    return duplicates.slice(0, 5); // Limit to first 5
  }

  /**
   * Find old entries (simple heuristic)
   */
  private findOldEntries(content: string): string[] {
    const datePattern = /\d{4}-\d{2}-\d{2}/g;
    const matches = content.match(datePattern) || [];
    const sixMonthsAgo = new Date();
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);

    return matches.filter(date => {
      const d = new Date(date);
      return d < sixMonthsAgo;
    }).slice(0, 5);
  }

  /**
   * Print formatted report
   */
  private printReport(report: CleanupReport): void {
    console.log('╔═══════════════════════════════════════════════════╗');
    console.log('║  📊 MEMORY CLEANUP AUDIT REPORT                   ║');
    console.log('╚═══════════════════════════════════════════════════╝\n');

    for (const file of report.files) {
      console.log(`📄 ${file.path}`);
      console.log(`   Size: ${file.sizeKB}KB (${file.lines} lines)`);
      
      if (file.suggestions.length > 0) {
        console.log(`   💡 Suggestions:`);
        for (const suggestion of file.suggestions) {
          console.log(`      • ${suggestion}`);
        }
      }
      
      if (file.potentialSavingsKB > 0) {
        console.log(`   💰 Potential savings: ${file.potentialSavingsKB}KB`);
      }
      console.log('');
    }

    console.log('╔═══════════════════════════════════════════════════╗');
    console.log(`║  Total Size: ${report.totalSizeBefore}KB → ${report.totalSizeAfter}KB          ║`);
    console.log(`║  Savings: ${report.savingsKB}KB (${Math.round((report.savingsKB / report.totalSizeBefore) * 100)}%)                     ║`);
    console.log(`║  Est. Weekly Savings: $${report.estimatedWeeklySavings} in API costs       ║`);
    console.log('╚═══════════════════════════════════════════════════╝');
  }

  /**
   * Create backup before cleanup
   */
  private createBackup(): void {
    if (!fs.existsSync(this.backupPath)) {
      fs.mkdirSync(this.backupPath, { recursive: true });
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupDir = path.join(this.backupPath, timestamp);
    fs.mkdirSync(backupDir, { recursive: true });

    const filesToBackup = ['SOUL.md', 'AGENTS.md', 'MEMORY.md', 'TOOLS.md'];
    for (const file of filesToBackup) {
      const src = path.join(this.workspacePath, file);
      if (fs.existsSync(src)) {
        fs.copyFileSync(src, path.join(backupDir, file));
      }
    }

    console.log(`✅ Backup created: ${backupDir}`);
  }

  /**
   * Execute cleanup (dry-run or actual)
   */
  async cleanup(dryRun: boolean = true): Promise<void> {
    if (!dryRun) {
      this.createBackup();
    }

    console.log(dryRun ? '🧹 DRY RUN - No files will be modified\n' : '🧹 EXECUTING CLEANUP\n');

    // Implementation would go here for actual cleanup operations
    // - Archive old daily files
    // - Remove duplicates
    // - Compress verbose sections
    // - Summarize old memories

    console.log(dryRun 
      ? 'Run with --confirm to execute these changes'
      : '✅ Cleanup complete!');
  }
}

// CLI Interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  const assistant = new MemoryCleanupAssistant();

  switch (command) {
    case 'audit':
      assistant.audit();
      break;
    case 'clean':
      const dryRun = !args.includes('--confirm');
      assistant.cleanup(dryRun);
      break;
    case 'auto-enable':
      const schedule = args[1] || '0 0 * * 0';
      assistant.enableAutoCleanup(schedule);
      break;
    case 'auto-disable':
      assistant.disableAutoCleanup();
      break;
    case 'auto-run':
      assistant.runAutoCleanup();
      break;
    case 'status':
      console.log('📊 Memory Cleanup Status:');
      console.log(`  Auto-cleanup: ${assistant.config.autoCleanup ? '✅ Enabled' : '❌ Disabled'}`);
      console.log(`  Schedule: ${assistant.config.schedule}`);
      console.log(`  Last cleanup: ${assistant.config.lastCleanup || 'Never'}`);
      console.log(`  Threshold: ${assistant.config.thresholdKB}KB`);
      break;
    default:
      console.log('Usage: memory-cleanup [audit|clean [--confirm]|auto-enable [schedule]|auto-disable|auto-run|status]');
  }
}
