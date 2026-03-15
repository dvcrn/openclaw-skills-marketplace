/**
 * Type definitions for Pattern Miner
 */

export interface DataSource {
  type: 'conversation' | 'decision' | 'task' | 'file' | 'api';
  path?: string;
  pattern?: string;
  name: string;
  config?: Record<string, any>;
}

export interface RawDataItem {
  id: string;
  content: string;
  timestamp: Date;
  source: string;
  type: string;
  metadata?: Record<string, any>;
  tags?: string[];
  keywords?: string[];
  priority?: 'low' | 'medium' | 'high';
  resolved?: boolean;
}

export interface Pattern {
  id: string;
  type: 'cluster' | 'association' | 'sequential' | 'anomaly';
  items: string[];
  confidence: number;
  frequency: number;
  importance: number;
  metadata: Record<string, any>;
  createdAt: Date;
  source: string;
}

export interface Insight {
  id: string;
  patternId: string;
  title: string;
  description: string;
  action: string;
  priority: 'high' | 'medium' | 'low';
  expectedImpact: number;
  category: string;
  applied?: boolean;
  appliedAt?: Date;
}

export interface AnalysisResult {
  patterns: Pattern[];
  insights: Insight[];
  summary: {
    totalPatterns: number;
    totalInsights: number;
    byType: {
      cluster: number;
      association: number;
      anomaly: number;
    };
  };
}

export interface MinerConfig {
  dataDir: string;
  patternDir: string;
  minConfidence: number;
  minFrequency: number;
  analysisTypes: ('cluster' | 'association' | 'anomaly')[];
  sources: DataSource[];
  autoScan: boolean;
  scanInterval: number; // minutes
  maxPatterns: number;
  retentionDays: number;
}

export interface ScanOptions {
  incremental?: boolean;
  sources?: string[];
  since?: Date;
  analysisTypes?: ('cluster' | 'association' | 'anomaly')[];
}

export interface ApplyOptions {
  dryRun?: boolean;
  confirm?: boolean;
  categories?: string[];
}
