import { ParsedInsight, NoteSearchResult } from '../types';
import * as fs from 'fs/promises';
import * as path from 'path';
import { glob } from 'glob';
import lunr from 'lunr';

export class NoteSearcher {
  private index: lunr.Index | null = null;
  private documents: Map<string, any> = new Map();
  private lastIndexTime: number = 0;
  private indexUpdateInterval: number = 3600; // 1 hour

  constructor(
    private notePaths: string[],
    private maxResults: number = 5,
    private minRelevanceScore: number = 0.3
  ) {}

  async search(parsed: ParsedInsight): Promise<NoteSearchResult[]> {
    // 1. 确保索引是最新的
    await this.ensureIndexUpdated();
    
    // 2. 构建搜索查询
    const query = this.buildSearchQuery(parsed);
    
    // 3. 执行搜索
    const results = this.executeSearch(query);
    
    // 4. 过滤和排序
    const filtered = this.filterResults(results);
    
    // 5. 返回格式化结果
    return this.formatResults(filtered);
  }

  private async ensureIndexUpdated(): Promise<void> {
    const now = Date.now();
    const shouldUpdate = !this.index || 
      (now - this.lastIndexTime) > this.indexUpdateInterval * 1000;

    if (shouldUpdate) {
      await this.buildIndex();
      this.lastIndexTime = now;
    }
  }

  private async buildIndex(): Promise<void> {
    console.log('正在构建笔记索引...');
    
    const documents: Array<{
      id: string;
      filePath: string;
      title: string;
      content: string;
      metadata: any;
    }> = [];

    // 收集所有笔记文件
    const noteFiles = await this.collectNoteFiles();
    
    for (const filePath of noteFiles) {
      try {
        const document = await this.processNoteFile(filePath);
        if (document) {
          documents.push(document);
        }
      } catch (error) {
        console.warn(`处理笔记文件失败: ${filePath}`, error);
      }
    }

    console.log(`索引构建完成，共 ${documents.length} 个文档`);

    // 构建 Lunr 索引
    this.index = lunr(function() {
      this.ref('id');
      this.field('title', { boost: 2 });
      this.field('content');
      this.field('tags', { boost: 1.5 });

      documents.forEach(doc => {
        this.add(doc);
      });
    });

    // 保存文档映射
    this.documents.clear();
    documents.forEach(doc => {
      this.documents.set(doc.id, doc);
    });
  }

  private async collectNoteFiles(): Promise<string[]> {
    const patterns = [
      '**/*.md',
      '**/*.txt',
      '**/*.markdown'
    ];

    const files: string[] = [];

    for (const notePath of this.notePaths) {
      const resolvedPath = this.resolvePath(notePath);
      
      for (const pattern of patterns) {
        const fullPattern = path.join(resolvedPath, pattern);
        const matches = await glob(fullPattern, { nodir: true });
        files.push(...matches);
      }
    }

    return [...new Set(files)]; // 去重
  }

  private async processNoteFile(filePath: string): Promise<any | null> {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      const title = this.extractTitle(filePath, content);
      const metadata = this.extractMetadata(content);
      const tags = this.extractTags(content);

      // 简单的文本清理
      const cleanContent = this.cleanContent(content);

      return {
        id: filePath,
        filePath,
        title,
        content: cleanContent,
        metadata: {
          ...metadata,
          tags,
          filePath,
          fileSize: content.length,
          lastModified: (await fs.stat(filePath)).mtime
        },
        tags: tags.join(' ')
      };
    } catch (error) {
      console.warn(`读取文件失败: ${filePath}`, error);
      return null;
    }
  }

  private extractTitle(filePath: string, content: string): string {
    // 从文件名提取标题
    const fileName = path.basename(filePath, path.extname(filePath));
    
    // 尝试从内容中提取标题（Markdown 的 # 标题）
    const titleMatch = content.match(/^#\s+(.+)$/m);
    if (titleMatch) {
      return titleMatch[1].trim();
    }
    
    return fileName;
  }

  private extractMetadata(content: string): any {
    const metadata: any = {};
    
    // 提取 YAML front matter
    const frontMatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (frontMatterMatch) {
      const frontMatter = frontMatterMatch[1];
      const lines = frontMatter.split('\n');
      
      for (const line of lines) {
        const match = line.match(/^(\w+):\s*(.+)$/);
        if (match) {
          const [, key, value] = match;
          metadata[key] = value.trim();
        }
      }
    }
    
    // 提取书籍信息
    const bookMatch = content.match(/《([^》]+)》/);
    if (bookMatch) {
      metadata.book = bookMatch[1];
    }
    
    // 提取作者信息
    const authorMatch = content.match(/作者[:：]\s*([^\n]+)/);
    if (authorMatch) {
      metadata.author = authorMatch[1].trim();
    }
    
    return metadata;
  }

  private extractTags(content: string): string[] {
    const tags: string[] = [];
    
    // 提取标签（Obsidian 风格）
    const obsidianTags = content.match(/#([\w\u4e00-\u9fff\-]+)/g);
    if (obsidianTags) {
      tags.push(...obsidianTags.map(tag => tag.substring(1)));
    }
    
    // 提取标签（YAML front matter）
    const frontMatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (frontMatterMatch) {
      const frontMatter = frontMatterMatch[1];
      const tagsMatch = frontMatter.match(/tags:\s*\[([^\]]+)\]/);
      if (tagsMatch) {
        const tagList = tagsMatch[1].split(',').map(tag => tag.trim().replace(/['"]/g, ''));
        tags.push(...tagList);
      }
    }
    
    return [...new Set(tags)]; // 去重
  }

  private cleanContent(content: string): string {
    // 移除 YAML front matter
    let cleaned = content.replace(/^---\n[\s\S]*?\n---\n/, '');
    
    // 移除 Markdown 标题
    cleaned = cleaned.replace(/^#+\s+.+$/gm, '');
    
    // 移除代码块
    cleaned = cleaned.replace(/```[\s\S]*?```/g, '');
    
    // 移除链接
    cleaned = cleaned.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
    
    // 移除图片
    cleaned = cleaned.replace(/!\[([^\]]*)\]\([^)]+\)/g, '');
    
    // 移除多余的空格和换行
    cleaned = cleaned.replace(/\s+/g, ' ').trim();
    
    return cleaned;
  }

  private buildSearchQuery(parsed: ParsedInsight): string {
    // 构建搜索查询字符串
    const queryParts: string[] = [];
    
    // 添加关键词
    queryParts.push(...parsed.keywords);
    
    // 添加主题
    queryParts.push(...parsed.themes);
    
    // 如果是中文，添加模糊搜索
    if (parsed.language === 'zh') {
      // 对中文关键词进行模糊处理
      const fuzzyKeywords = parsed.keywords.map(keyword => {
        if (keyword.length > 1) {
          return `*${keyword}*`;
        }
        return keyword;
      });
      queryParts.push(...fuzzyKeywords);
    }
    
    // 去重并连接
    const uniqueParts = [...new Set(queryParts.filter(part => part.length > 0))];
    return uniqueParts.join(' ');
  }

  private executeSearch(query: string): lunr.Index.Result[] {
    if (!this.index || query.trim().length === 0) {
      return [];
    }
    
    try {
      return this.index.search(query);
    } catch (error) {
      console.warn('搜索失败:', error);
      return [];
    }
  }

  private filterResults(
    results: lunr.Index.Result[]
  ): lunr.Index.Result[] {
    return results
      .filter(result => result.score >= this.minRelevanceScore)
      .slice(0, this.maxResults * 2) // 多取一些用于后续过滤
      .sort((a, b) => b.score - a.score);
  }

  private formatResults(results: lunr.Index.Result[]): NoteSearchResult[] {
    return results.slice(0, this.maxResults).map(result => {
      const doc = this.documents.get(result.ref);
      if (!doc) {
        return null;
      }
      
      // 提取相关片段
      const excerpt = this.extractExcerpt(doc.content, result);
      
      return {
        filePath: doc.filePath,
        title: doc.title,
        excerpt,
        relevance: result.score,
        matchType: this.determineMatchType(result, doc),
        metadata: doc.metadata
      };
    }).filter(result => result !== null) as NoteSearchResult[];
  }

  private extractExcerpt(content: string, result: lunr.Index.Result): string {
    // 简单的内容摘要提取
    if (content.length <= 200) {
      return content;
    }
    
    // 尝试找到匹配关键词的位置
    const keywords = Object.keys(result.matchData.metadata);
    if (keywords.length > 0) {
      const firstKeyword = keywords[0];
      const position = content.toLowerCase().indexOf(firstKeyword.toLowerCase());
      
      if (position !== -1) {
        const start = Math.max(0, position - 100);
        const end = Math.min(content.length, position + 100);
        let excerpt = content.substring(start, end);
        
        if (start > 0) excerpt = '...' + excerpt;
        if (end < content.length) excerpt = excerpt + '...';
        
        return excerpt;
      }
    }
    
    // 如果没有找到关键词，返回开头部分
    return content.substring(0, 200) + '...';
  }

  private determineMatchType(result: lunr.Index.Result, doc: any): NoteSearchResult['matchType'] {
    const metadata = (result as any).matchData?.metadata || {};
    
    if (metadata.title) return 'title';
    if (metadata.tags) return 'tag';
    if (doc.metadata && Object.keys(doc.metadata).length > 0) return 'metadata';
    return 'content';
  }

  private resolvePath(inputPath: string): string {
    if (inputPath.startsWith('~/')) {
      return path.join(process.env.HOME || '', inputPath.substring(2));
    }
    return path.resolve(inputPath);
  }
}