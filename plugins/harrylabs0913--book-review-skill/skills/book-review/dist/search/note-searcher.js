"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.NoteSearcher = void 0;
const fs = __importStar(require("fs/promises"));
const path = __importStar(require("path"));
const glob_1 = require("glob");
const lunr_1 = __importDefault(require("lunr"));
class NoteSearcher {
    notePaths;
    maxResults;
    minRelevanceScore;
    index = null;
    documents = new Map();
    lastIndexTime = 0;
    indexUpdateInterval = 3600; // 1 hour
    constructor(notePaths, maxResults = 5, minRelevanceScore = 0.3) {
        this.notePaths = notePaths;
        this.maxResults = maxResults;
        this.minRelevanceScore = minRelevanceScore;
    }
    async search(parsed) {
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
    async ensureIndexUpdated() {
        const now = Date.now();
        const shouldUpdate = !this.index ||
            (now - this.lastIndexTime) > this.indexUpdateInterval * 1000;
        if (shouldUpdate) {
            await this.buildIndex();
            this.lastIndexTime = now;
        }
    }
    async buildIndex() {
        console.log('正在构建笔记索引...');
        const documents = [];
        // 收集所有笔记文件
        const noteFiles = await this.collectNoteFiles();
        for (const filePath of noteFiles) {
            try {
                const document = await this.processNoteFile(filePath);
                if (document) {
                    documents.push(document);
                }
            }
            catch (error) {
                console.warn(`处理笔记文件失败: ${filePath}`, error);
            }
        }
        console.log(`索引构建完成，共 ${documents.length} 个文档`);
        // 构建 Lunr 索引
        this.index = (0, lunr_1.default)(function () {
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
    async collectNoteFiles() {
        const patterns = [
            '**/*.md',
            '**/*.txt',
            '**/*.markdown'
        ];
        const files = [];
        for (const notePath of this.notePaths) {
            const resolvedPath = this.resolvePath(notePath);
            for (const pattern of patterns) {
                const fullPattern = path.join(resolvedPath, pattern);
                const matches = await (0, glob_1.glob)(fullPattern, { nodir: true });
                files.push(...matches);
            }
        }
        return [...new Set(files)]; // 去重
    }
    async processNoteFile(filePath) {
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
        }
        catch (error) {
            console.warn(`读取文件失败: ${filePath}`, error);
            return null;
        }
    }
    extractTitle(filePath, content) {
        // 从文件名提取标题
        const fileName = path.basename(filePath, path.extname(filePath));
        // 尝试从内容中提取标题（Markdown 的 # 标题）
        const titleMatch = content.match(/^#\s+(.+)$/m);
        if (titleMatch) {
            return titleMatch[1].trim();
        }
        return fileName;
    }
    extractMetadata(content) {
        const metadata = {};
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
    extractTags(content) {
        const tags = [];
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
    cleanContent(content) {
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
    buildSearchQuery(parsed) {
        // 构建搜索查询字符串
        const queryParts = [];
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
    executeSearch(query) {
        if (!this.index || query.trim().length === 0) {
            return [];
        }
        try {
            return this.index.search(query);
        }
        catch (error) {
            console.warn('搜索失败:', error);
            return [];
        }
    }
    filterResults(results) {
        return results
            .filter(result => result.score >= this.minRelevanceScore)
            .slice(0, this.maxResults * 2) // 多取一些用于后续过滤
            .sort((a, b) => b.score - a.score);
    }
    formatResults(results) {
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
        }).filter(result => result !== null);
    }
    extractExcerpt(content, result) {
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
                if (start > 0)
                    excerpt = '...' + excerpt;
                if (end < content.length)
                    excerpt = excerpt + '...';
                return excerpt;
            }
        }
        // 如果没有找到关键词，返回开头部分
        return content.substring(0, 200) + '...';
    }
    determineMatchType(result, doc) {
        const metadata = result.matchData?.metadata || {};
        if (metadata.title)
            return 'title';
        if (metadata.tags)
            return 'tag';
        if (doc.metadata && Object.keys(doc.metadata).length > 0)
            return 'metadata';
        return 'content';
    }
    resolvePath(inputPath) {
        if (inputPath.startsWith('~/')) {
            return path.join(process.env.HOME || '', inputPath.substring(2));
        }
        return path.resolve(inputPath);
    }
}
exports.NoteSearcher = NoteSearcher;
//# sourceMappingURL=note-searcher.js.map