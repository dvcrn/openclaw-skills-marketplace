/**
 * Pattern Storage - Manage discovered patterns
 */

import * as fs from 'fs-extra';
import * as path from 'path';
import { Pattern, Insight, MinerConfig } from './types';

export class PatternStorage {
  private patternDir: string;
  private patternsFile: string;
  private insightsFile: string;
  private config: MinerConfig;

  constructor(patternDir: string, config: MinerConfig) {
    this.patternDir = patternDir;
    this.config = config;
    this.patternsFile = path.join(patternDir, 'patterns.json');
    this.insightsFile = path.join(patternDir, 'insights.json');
  }

  async initialize(): Promise<void> {
    await fs.ensureDir(this.patternDir);
    
    if (!await fs.pathExists(this.patternsFile)) {
      await fs.writeFile(this.patternsFile, JSON.stringify([], null, 2));
    }
    
    if (!await fs.pathExists(this.insightsFile)) {
      await fs.writeFile(this.insightsFile, JSON.stringify([], null, 2));
    }
  }

  async savePatterns(patterns: Pattern[]): Promise<void> {
    const existing = await this.loadPatterns();
    
    // Merge with existing, avoiding duplicates
    const patternMap = new Map<string, Pattern>();
    for (const p of existing) {
      patternMap.set(p.id, p);
    }
    
    for (const p of patterns) {
      if (!patternMap.has(p.id)) {
        patternMap.set(p.id, p);
      }
    }
    
    // Convert to array and sort by importance
    const allPatterns = Array.from(patternMap.values())
      .sort((a, b) => b.importance - a.importance);
    
    // Limit to maxPatterns
    const limited = allPatterns.slice(0, this.config.maxPatterns);
    
    await fs.writeFile(this.patternsFile, JSON.stringify(limited, null, 2));
  }

  async loadPatterns(): Promise<Pattern[]> {
    try {
      const content = await fs.readFile(this.patternsFile, 'utf-8');
      const data = JSON.parse(content);
      return data.map((p: any) => ({
        id: p.id,
        type: p.type,
        items: p.items,
        confidence: p.confidence,
        frequency: p.frequency,
        importance: p.importance,
        metadata: p.metadata,
        createdAt: new Date(p.createdAt),
        source: p.source
      }));
    } catch {
      return [];
    }
  }

  async saveInsights(insights: Insight[]): Promise<void> {
    const existing = await this.loadInsights();
    
    // Merge with existing
    const insightMap = new Map<string, Insight>();
    for (const i of existing) {
      insightMap.set(i.id, i);
    }
    
    for (const i of insights) {
      if (!insightMap.has(i.id)) {
        insightMap.set(i.id, i);
      }
    }
    
    const allInsights = Array.from(insightMap.values())
      .sort((a, b) => b.expectedImpact - a.expectedImpact);
    
    await fs.writeFile(this.insightsFile, JSON.stringify(allInsights, null, 2));
  }

  async loadInsights(): Promise<Insight[]> {
    try {
      const content = await fs.readFile(this.insightsFile, 'utf-8');
      const data = JSON.parse(content);
      return data.map((i: any) => ({
        id: i.id,
        patternId: i.patternId,
        title: i.title,
        description: i.description,
        action: i.action,
        priority: i.priority,
        expectedImpact: i.expectedImpact,
        category: i.category,
        applied: i.applied,
        appliedAt: i.appliedAt ? new Date(i.appliedAt) : undefined
      }));
    } catch {
      return [];
    }
  }

  async getPatternById(id: string): Promise<Pattern | undefined> {
    const patterns = await this.loadPatterns();
    return patterns.find(p => p.id === id);
  }

  async getInsightById(id: string): Promise<Insight | undefined> {
    const insights = await this.loadInsights();
    return insights.find(i => i.id === id);
  }

  async getInsightsByCategory(category: string): Promise<Insight[]> {
    const insights = await this.loadInsights();
    return insights.filter(i => i.category === category);
  }

  async markInsightApplied(id: string): Promise<void> {
    const insights = await this.loadInsights();
    const insight = insights.find(i => i.id === id);
    if (insight) {
      insight.applied = true;
      insight.appliedAt = new Date();
      await this.saveInsights(insights);
    }
  }

  async cleanupOldPatterns(): Promise<void> {
    const patterns = await this.loadPatterns();
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - this.config.retentionDays);
    
    const filtered = patterns.filter(p => p.createdAt > cutoff);
    
    if (filtered.length < patterns.length) {
      await fs.writeFile(this.patternsFile, JSON.stringify(filtered, null, 2));
    }
  }

  async exportPatterns(format: 'json' | 'csv' = 'json'): Promise<string> {
    const patterns = await this.loadPatterns();
    
    if (format === 'csv') {
      const headers = ['id', 'type', 'confidence', 'frequency', 'importance', 'source', 'createdAt'];
      const rows = patterns.map(p => [
        p.id,
        p.type,
        p.confidence,
        p.frequency,
        p.importance,
        p.source,
        p.createdAt.toISOString()
      ]);
      return [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    }
    
    return JSON.stringify(patterns, null, 2);
  }

  async getStats(): Promise<{
    totalPatterns: number;
    totalInsights: number;
    appliedInsights: number;
    byType: Record<string, number>;
    byCategory: Record<string, number>;
  }> {
    const patterns = await this.loadPatterns();
    const insights = await this.loadInsights();
    
    const byType: Record<string, number> = {};
    for (const p of patterns) {
      byType[p.type] = (byType[p.type] || 0) + 1;
    }
    
    const byCategory: Record<string, number> = {};
    for (const i of insights) {
      byCategory[i.category] = (byCategory[i.category] || 0) + 1;
    }
    
    return {
      totalPatterns: patterns.length,
      totalInsights: insights.length,
      appliedInsights: insights.filter(i => i.applied).length,
      byType,
      byCategory
    };
  }
}
