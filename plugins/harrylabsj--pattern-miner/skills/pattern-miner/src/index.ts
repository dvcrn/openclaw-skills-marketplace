/**
 * Pattern Miner - Main Module
 * 
 * Intelligent pattern recognition and actionable insights
 * from multi-source data (conversations, decisions, tasks)
 */

export { DataCollector } from './collector';
export { PatternAnalyzer } from './analyzer';
export { PatternStorage } from './storage';
export * from './types';

import { DataCollector } from './collector';
import { PatternAnalyzer } from './analyzer';
import { PatternStorage } from './storage';
import { MinerConfig, ScanOptions, AnalysisResult } from './types';
import * as path from 'path';
import * as fs from 'fs-extra';

const DEFAULT_PATTERN_DIR = path.join(process.env.HOME || '~', '.pattern-miner');

/**
 * Main PatternMiner class - High-level API
 */
export class PatternMiner {
  private config: MinerConfig;
  private collector: DataCollector;
  private analyzer: PatternAnalyzer;
  private storage: PatternStorage;

  constructor(config?: Partial<MinerConfig>) {
    this.config = {
      dataDir: path.join(process.env.HOME || '~', '.openclaw', 'workspace'),
      patternDir: DEFAULT_PATTERN_DIR,
      minConfidence: 0.6,
      minFrequency: 3,
      analysisTypes: ['cluster', 'association', 'anomaly'],
      sources: [],
      autoScan: false,
      scanInterval: 60,
      maxPatterns: 1000,
      retentionDays: 30,
      ...config
    };

    this.collector = new DataCollector();
    this.analyzer = new PatternAnalyzer(__dirname);
    this.storage = new PatternStorage(this.config.patternDir, this.config);
  }

  /**
   * Initialize the pattern miner
   */
  async initialize(): Promise<void> {
    await this.storage.initialize();
    
    // Add default sources if none configured
    if (this.config.sources.length === 0) {
      this.addDefaultSources();
    }
  }

  /**
   * Add a data source for collection
   */
  addSource(source: import('./types').DataSource): void {
    this.collector.addSource(source);
  }

  /**
   * Run pattern mining
   */
  async mine(options?: ScanOptions): Promise<AnalysisResult> {
    await this.initialize();
    
    // Collect data
    const data = await this.collector.collectAll(options);
    
    // Analyze patterns
    const results = await this.analyzer.analyze(data, options);
    
    // Store results
    await this.storage.savePatterns(results.patterns);
    await this.storage.saveInsights(results.insights);
    
    return results;
  }

  /**
   * List discovered patterns
   */
  async listPatterns(type?: string, limit?: number): Promise<import('./types').Pattern[]> {
    let patterns = await this.storage.loadPatterns();
    
    if (type) {
      patterns = patterns.filter(p => p.type === type);
    }
    
    if (limit) {
      patterns = patterns.slice(0, limit);
    }
    
    return patterns;
  }

  /**
   * List insights
   */
  async listInsights(category?: string, pendingOnly?: boolean): Promise<import('./types').Insight[]> {
    let insights = await this.storage.loadInsights();
    
    if (category) {
      insights = insights.filter(i => i.category === category);
    }
    
    if (pendingOnly) {
      insights = insights.filter(i => !i.applied);
    }
    
    return insights;
  }

  /**
   * Get statistics
   */
  async getStats(): Promise<{
    totalPatterns: number;
    totalInsights: number;
    appliedInsights: number;
    byType: Record<string, number>;
    byCategory: Record<string, number>;
  }> {
    return this.storage.getStats();
  }

  /**
   * Apply an insight
   */
  async applyInsight(insightId: string): Promise<void> {
    await this.storage.markInsightApplied(insightId);
  }

  /**
   * Export patterns
   */
  async exportPatterns(format: 'json' | 'csv' = 'json'): Promise<string> {
    return this.storage.exportPatterns(format);
  }

  private addDefaultSources(): void {
    const defaultSources = [
      {
        type: 'conversation' as const,
        name: 'conversations',
        path: path.join(process.env.HOME || '~', '.openclaw', 'sessions'),
        pattern: '**/*.json'
      },
      {
        type: 'decision' as const,
        name: 'decisions',
        path: path.join(process.env.HOME || '~', '.openclaw', 'decisions'),
        pattern: '**/*.json'
      },
      {
        type: 'task' as const,
        name: 'tasks',
        path: path.join(process.env.HOME || '~', '.openclaw', 'workspace'),
        pattern: '**/*.{json,md}'
      }
    ];
    
    for (const source of defaultSources) {
      this.collector.addSource(source);
    }
  }
}

/**
 * Create a new PatternMiner instance
 */
export function createPatternMiner(config?: Partial<MinerConfig>): PatternMiner {
  return new PatternMiner(config);
}

export default PatternMiner;
