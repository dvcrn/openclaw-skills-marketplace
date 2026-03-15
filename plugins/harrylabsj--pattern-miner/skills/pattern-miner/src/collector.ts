/**
 * Data Collector - Multi-source data ingestion
 */

import * as fs from 'fs-extra';
import * as path from 'path';
import { glob } from 'glob';
import { DataSource, RawDataItem } from './types';

export class DataCollector {
  private sources: DataSource[] = [];

  addSource(source: DataSource): void {
    this.sources.push(source);
  }

  async collectAll(options?: { since?: Date; sources?: string[] }): Promise<RawDataItem[]> {
    const allData: RawDataItem[] = [];
    
    const sourcesToProcess = options?.sources 
      ? this.sources.filter(s => options.sources?.includes(s.name))
      : this.sources;

    for (const source of sourcesToProcess) {
      try {
        const data = await this.collectFromSource(source, options?.since);
        allData.push(...data);
      } catch (error) {
        console.error(`Error collecting from ${source.name}:`, error);
      }
    }

    // Sort by timestamp
    return allData.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }

  private async collectFromSource(source: DataSource, since?: Date): Promise<RawDataItem[]> {
    switch (source.type) {
      case 'conversation':
        return this.collectConversations(source, since);
      case 'decision':
        return this.collectDecisions(source, since);
      case 'task':
        return this.collectTasks(source, since);
      case 'file':
        return this.collectFromFiles(source, since);
      case 'api':
        return this.collectFromAPI(source, since);
      default:
        return [];
    }
  }

  private async collectConversations(source: DataSource, since?: Date): Promise<RawDataItem[]> {
    const items: RawDataItem[] = [];
    
    if (!source.path) return items;

    // Look for conversation logs in context-preserver format
    const pattern = source.pattern || '**/*.json';
    const files = await glob(pattern, { cwd: source.path, absolute: true });

    for (const file of files) {
      try {
        const content = await fs.readFile(file, 'utf-8');
        const data = JSON.parse(content);
        
        if (Array.isArray(data.conversations || data.messages)) {
          const conversations = data.conversations || data.messages;
          for (const conv of conversations) {
            const timestamp = new Date(conv.timestamp || conv.created_at || Date.now());
            if (since && timestamp < since) continue;

            items.push({
              id: conv.id || `${file}_${items.length}`,
              content: conv.content || conv.message || JSON.stringify(conv),
              timestamp,
              source: source.name,
              type: 'conversation',
              metadata: conv.metadata || {},
              tags: conv.tags || [],
              keywords: conv.keywords || this.extractKeywords(conv.content || '')
            });
          }
        }
      } catch (error) {
        console.error(`Error reading ${file}:`, error);
      }
    }

    return items;
  }

  private async collectDecisions(source: DataSource, since?: Date): Promise<RawDataItem[]> {
    const items: RawDataItem[] = [];
    
    if (!source.path) return items;

    // Look for decision logs in decision-recorder format
    const pattern = source.pattern || '**/*.json';
    const files = await glob(pattern, { cwd: source.path, absolute: true });

    for (const file of files) {
      try {
        const content = await fs.readFile(file, 'utf-8');
        const data = JSON.parse(content);
        
        if (Array.isArray(data.decisions)) {
          for (const decision of data.decisions) {
            const timestamp = new Date(decision.timestamp || decision.created_at || Date.now());
            if (since && timestamp < since) continue;

            items.push({
              id: decision.id || `${file}_${items.length}`,
              content: decision.description || decision.context || JSON.stringify(decision),
              timestamp,
              source: source.name,
              type: 'decision',
              metadata: decision.metadata || {},
              tags: decision.tags || [],
              keywords: decision.keywords || this.extractKeywords(decision.description || ''),
              priority: decision.priority || 'medium'
            });
          }
        }
      } catch (error) {
        console.error(`Error reading ${file}:`, error);
      }
    }

    return items;
  }

  private async collectTasks(source: DataSource, since?: Date): Promise<RawDataItem[]> {
    const items: RawDataItem[] = [];
    
    if (!source.path) return items;

    const pattern = source.pattern || '**/*.{json,md,yaml,yml}';
    const files = await glob(pattern, { cwd: source.path, absolute: true });

    for (const file of files) {
      try {
        const content = await fs.readFile(file, 'utf-8');
        const ext = path.extname(file).toLowerCase();
        
        let data: any;
        if (ext === '.json') {
          data = JSON.parse(content);
        } else if (ext === '.md') {
          data = this.parseMarkdownTasks(content);
        } else {
          continue;
        }

        const tasks = Array.isArray(data) ? data : (data.tasks || []);
        
        for (const task of tasks) {
          const timestamp = new Date(task.timestamp || task.created_at || Date.now());
          if (since && timestamp < since) continue;

          items.push({
            id: task.id || `${file}_${items.length}`,
            content: task.title || task.description || task.name || JSON.stringify(task),
            timestamp,
            source: source.name,
            type: 'task',
            metadata: task.metadata || {},
            tags: task.tags || [],
            keywords: task.keywords || this.extractKeywords(task.title || ''),
            priority: task.priority || 'medium',
            resolved: task.completed || task.done || task.resolved || false
          });
        }
      } catch (error) {
        console.error(`Error reading ${file}:`, error);
      }
    }

    return items;
  }

  private async collectFromFiles(source: DataSource, since?: Date): Promise<RawDataItem[]> {
    const items: RawDataItem[] = [];
    
    if (!source.path) return items;

    const pattern = source.pattern || '**/*';
    const files = await glob(pattern, { cwd: source.path, absolute: true, nodir: true });

    for (const file of files) {
      try {
        const stat = await fs.stat(file);
        if (since && stat.mtime < since) continue;

        const content = await fs.readFile(file, 'utf-8');
        
        items.push({
          id: file,
          content: content.slice(0, 10000), // Limit content size
          timestamp: stat.mtime,
          source: source.name,
          type: 'file',
          metadata: { path: file, size: stat.size }
        });
      } catch (error) {
        // Skip files that can't be read
      }
    }

    return items;
  }

  private async collectFromAPI(source: DataSource, _since?: Date): Promise<RawDataItem[]> {
    // Placeholder for API collection
    // Would implement actual API calls based on source.config
    console.log(`API collection not yet implemented for ${source.name}`);
    return [];
  }

  private parseMarkdownTasks(content: string): any[] {
    const tasks: any[] = [];
    const lines = content.split('\n');
    
    for (const line of lines) {
      const match = line.match(/^\s*[-*]\s*\[([ x])\]\s*(.+)$/);
      if (match) {
        tasks.push({
          title: match[2].trim(),
          completed: match[1] === 'x',
          type: 'markdown_task'
        });
      }
    }
    
    return tasks;
  }

  private extractKeywords(text: string): string[] {
    // Simple keyword extraction
    const words = text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length > 3 && !this.isStopWord(w));
    
    return [...new Set(words)].slice(0, 10);
  }

  private isStopWord(word: string): boolean {
    const stopWords = new Set([
      'this', 'that', 'with', 'from', 'they', 'have', 'been', 'were', 'said',
      'each', 'which', 'their', 'would', 'there', 'could', 'should'
    ]);
    return stopWords.has(word);
  }
}
