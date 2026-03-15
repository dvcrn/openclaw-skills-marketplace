export interface UserInput {
    text: string;
    options?: {
        language?: 'auto' | 'zh' | 'en';
        style?: 'casual' | 'professional' | 'academic';
        length?: 'short' | 'medium' | 'long';
        format?: OutputFormat;
        includeReferences?: boolean;
        includeSuggestions?: boolean;
    };
}
export interface ParsedInsight {
    text: string;
    themes: string[];
    emotions: string[];
    keywords: string[];
    language: 'zh' | 'en';
    complexity: 'simple' | 'medium' | 'complex';
}
export interface NoteSearchResult {
    filePath: string;
    title: string;
    excerpt: string;
    relevance: number;
    matchType: 'title' | 'content' | 'tag' | 'metadata';
    metadata?: {
        author?: string;
        book?: string;
        date?: string;
        tags?: string[];
    };
}
export interface ReviewReference {
    source: string;
    content: string;
    page?: string;
}
export interface ReviewResult {
    original: string;
    expanded: string;
    references: ReviewReference[];
    suggestions: string[];
    confidence: number;
}
export type OutputFormat = 'markdown' | 'plain' | 'html';
export interface SkillOutput {
    content: string;
    metadata: {
        format: OutputFormat;
        processingTime: number;
        themes: string[];
        generatedAt: string;
    };
}
export interface SkillConfig {
    processing: {
        maxInputLength: number;
        defaultLanguage: 'auto' | 'zh' | 'en';
        defaultStyle: 'casual' | 'professional' | 'academic';
        defaultLength: 'short' | 'medium' | 'long';
    };
    search: {
        notePaths: string[];
        indexUpdateInterval: number;
        maxResults: number;
        minRelevanceScore: number;
    };
    generation: {
        aiProvider: 'deepseek' | 'openai' | 'local';
        model: string;
        temperature: number;
        maxTokens: number;
        enableCache: boolean;
    };
    output: {
        defaultFormat: OutputFormat;
        includeReferences: boolean;
        includeSuggestions: boolean;
        enableCopyToClipboard: boolean;
    };
}
export interface IndexedDocument {
    id: string;
    filePath: string;
    title: string;
    content: string;
    metadata: {
        author?: string;
        book?: string;
        date?: Date;
        tags?: string[];
        language?: string;
        wordCount?: number;
    };
    tokens: string[];
}
export interface SearchQuery {
    keywords: string[];
    themes: string[];
    boostFields: {
        title: number;
        content: number;
        tags: number;
    };
}
export interface GenerationContext {
    insight: string;
    themes: string[];
    relevantNotes: Array<{
        title: string;
        excerpt: string;
        relevance: number;
    }>;
    language: 'zh' | 'en';
    style: 'casual' | 'professional' | 'academic';
    length: 'short' | 'medium' | 'long';
}
//# sourceMappingURL=index.d.ts.map