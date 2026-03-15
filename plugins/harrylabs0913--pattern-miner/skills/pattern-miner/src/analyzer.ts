/**
 * Pattern Analyzer - Interface with Python ML engine
 */

import * as fs from 'fs-extra';
import * as path from 'path';
import { spawn } from 'child_process';
import { promisify } from 'util';
import { RawDataItem, Pattern, Insight, AnalysisResult, ScanOptions } from './types';

const execFile = promisify(require('child_process').execFile);

export class PatternAnalyzer {
  private pythonScriptPath: string;
  private tempDir: string;

  constructor(skillDir: string) {
    this.pythonScriptPath = path.join(skillDir, 'python', 'pattern_analyzer.py');
    this.tempDir = path.join(skillDir, '.temp');
  }

  async analyze(data: RawDataItem[], options?: ScanOptions): Promise<AnalysisResult> {
    // Prepare data for Python analysis
    const preparedData = this.prepareDataForPython(data);
    
    // Write to temp file
    await fs.ensureDir(this.tempDir);
    const inputFile = path.join(this.tempDir, `input_${Date.now()}.json`);
    const outputFile = path.join(this.tempDir, `output_${Date.now()}.json`);
    
    await fs.writeFile(inputFile, JSON.stringify(preparedData, null, 2));
    
    try {
      // Run Python analyzer
      await execFile('python3', [
        this.pythonScriptPath,
        inputFile,
        outputFile
      ]);
      
      // Read results
      const results = await fs.readFile(outputFile, 'utf-8');
      const parsed = JSON.parse(results);
      
      // Transform to TypeScript types
      return this.transformResults(parsed);
    } catch (error) {
      console.error('Python analysis failed:', error);
      // Fallback to basic analysis
      return this.fallbackAnalysis(data);
    } finally {
      // Cleanup temp files
      await fs.remove(inputFile).catch(() => {});
      await fs.remove(outputFile).catch(() => {});
    }
  }

  private prepareDataForPython(data: RawDataItem[]): any[] {
    return data.map(item => ({
      id: item.id,
      content: item.content,
      timestamp: item.timestamp.toISOString(),
      source: item.source,
      type: item.type,
      metadata: item.metadata,
      tags: item.tags || [],
      keywords: item.keywords || [],
      priority: item.priority,
      resolved: item.resolved
    }));
  }

  private transformResults(parsed: any): AnalysisResult {
    return {
      patterns: (parsed.patterns || []).map((p: any) => ({
        id: p.id,
        type: p.type,
        items: p.items,
        confidence: p.confidence,
        frequency: p.frequency,
        importance: p.importance,
        metadata: p.metadata,
        createdAt: new Date(p.created_at),
        source: p.source
      })),
      insights: (parsed.insights || []).map((i: any) => ({
        id: i.id,
        patternId: i.pattern_id,
        title: i.title,
        description: i.description,
        action: i.action,
        priority: i.priority,
        expectedImpact: i.expected_impact,
        category: i.category
      })),
      summary: {
        totalPatterns: parsed.summary?.total_patterns || 0,
        totalInsights: parsed.summary?.total_insights || 0,
        byType: {
          cluster: parsed.summary?.by_type?.cluster || 0,
          association: parsed.summary?.by_type?.association || 0,
          anomaly: parsed.summary?.by_type?.anomaly || 0
        }
      }
    };
  }

  private fallbackAnalysis(data: RawDataItem[]): AnalysisResult {
    // Basic pattern detection when Python is unavailable
    const patterns: Pattern[] = [];
    const insights: Insight[] = [];
    
    // Group by source
    const bySource = new Map<string, RawDataItem[]>();
    for (const item of data) {
      const list = bySource.get(item.source) || [];
      list.push(item);
      bySource.set(item.source, list);
    }
    
    // Detect frequency patterns
    for (const [source, items] of bySource) {
      if (items.length >= 3) {
        const pattern: Pattern = {
          id: `freq_${source}_${Date.now()}`,
          type: 'cluster',
          items: items.slice(0, 10).map(i => i.content.slice(0, 200)),
          confidence: Math.min(items.length / 10, 1.0),
          frequency: items.length,
          importance: 0.5,
          metadata: { source, method: 'fallback' },
          createdAt: new Date(),
          source: 'fallback'
        };
        patterns.push(pattern);
        
        const insight: Insight = {
          id: `insight_${pattern.id}`,
          patternId: pattern.id,
          title: `High activity in ${source}`,
          description: `Found ${items.length} items from ${source}`,
          action: 'Review and optimize this data source',
          priority: 'medium',
          expectedImpact: 0.5,
          category: 'optimization'
        };
        insights.push(insight);
      }
    }
    
    return {
      patterns,
      insights,
      summary: {
        totalPatterns: patterns.length,
        totalInsights: insights.length,
        byType: {
          cluster: patterns.filter(p => p.type === 'cluster').length,
          association: patterns.filter(p => p.type === 'association').length,
          anomaly: patterns.filter(p => p.type === 'anomaly').length
        }
      }
    };
  }
}
