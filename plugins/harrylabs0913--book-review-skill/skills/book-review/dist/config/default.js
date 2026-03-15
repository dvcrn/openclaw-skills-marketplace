"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.defaultConfig = void 0;
exports.loadConfig = loadConfig;
exports.validateConfig = validateConfig;
exports.defaultConfig = {
    processing: {
        maxInputLength: 500,
        defaultLanguage: 'auto',
        defaultStyle: 'professional',
        defaultLength: 'medium',
    },
    search: {
        notePaths: [
            '~/Documents/Notes',
            '~/Obsidian',
            '~/Library/Mobile Documents/iCloud~com~logseq~logseq/Documents',
        ],
        indexUpdateInterval: 3600, // 1 hour in seconds
        maxResults: 5,
        minRelevanceScore: 0.3,
    },
    generation: {
        aiProvider: 'deepseek',
        model: 'deepseek-chat',
        temperature: 0.7,
        maxTokens: 1000,
        enableCache: true,
    },
    output: {
        defaultFormat: 'markdown',
        includeReferences: true,
        includeSuggestions: true,
        enableCopyToClipboard: true,
    },
};
function loadConfig() {
    // 从环境变量加载配置
    const config = { ...exports.defaultConfig };
    // 处理笔记路径
    const notePathsEnv = process.env.BOOK_REVIEW_NOTE_PATHS;
    if (notePathsEnv) {
        config.search.notePaths = notePathsEnv.split(',').map(path => path.trim());
    }
    // AI 模型配置
    if (process.env.BOOK_REVIEW_AI_MODEL) {
        config.generation.model = process.env.BOOK_REVIEW_AI_MODEL;
    }
    // 温度配置
    if (process.env.BOOK_REVIEW_TEMPERATURE) {
        config.generation.temperature = parseFloat(process.env.BOOK_REVIEW_TEMPERATURE);
    }
    return config;
}
function validateConfig(config) {
    const errors = [];
    // 验证处理配置
    if (config.processing.maxInputLength <= 0) {
        errors.push('maxInputLength must be positive');
    }
    // 验证搜索配置
    if (config.search.notePaths.length === 0) {
        errors.push('至少需要配置一个笔记路径');
    }
    if (config.search.maxResults <= 0) {
        errors.push('maxResults must be positive');
    }
    if (config.search.minRelevanceScore < 0 || config.search.minRelevanceScore > 1) {
        errors.push('minRelevanceScore must be between 0 and 1');
    }
    // 验证生成配置
    if (config.generation.temperature < 0 || config.generation.temperature > 2) {
        errors.push('temperature must be between 0 and 2');
    }
    if (config.generation.maxTokens <= 0) {
        errors.push('maxTokens must be positive');
    }
    return errors;
}
//# sourceMappingURL=default.js.map