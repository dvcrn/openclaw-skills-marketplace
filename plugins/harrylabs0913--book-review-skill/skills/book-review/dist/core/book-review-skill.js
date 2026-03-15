"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BookReviewSkill = void 0;
const insight_parser_1 = require("../parser/insight-parser");
const note_searcher_1 = require("../search/note-searcher");
const review_generator_1 = require("../generation/review-generator");
const formatter_1 = require("../output/formatter");
class BookReviewSkill {
    parser;
    searcher;
    generator;
    formatter;
    config;
    constructor(config) {
        this.config = config;
        this.parser = new insight_parser_1.InsightParser();
        this.searcher = new note_searcher_1.NoteSearcher(config.search.notePaths, config.search.maxResults, config.search.minRelevanceScore);
        this.generator = new review_generator_1.ReviewGenerator(config.generation.aiProvider, config.generation.model, config.generation.temperature, config.generation.maxTokens);
        this.formatter = new formatter_1.OutputFormatter();
    }
    async process(input) {
        const startTime = Date.now();
        try {
            console.log('开始处理读书心得点评...');
            // 1. 验证输入
            const validatedInput = this.validateInput(input);
            console.log('✓ 输入验证完成');
            // 2. 解析心得
            const parsedInsight = await this.parser.parse(validatedInput.text);
            console.log(`✓ 心得解析完成: ${parsedInsight.keywords.length} 个关键词, ${parsedInsight.themes.length} 个主题`);
            // 3. 搜索相关笔记
            const relevantNotes = await this.searcher.search(parsedInsight);
            console.log(`✓ 笔记搜索完成: 找到 ${relevantNotes.length} 条相关笔记`);
            // 4. 生成点评
            const reviewResult = await this.generator.generate(parsedInsight, relevantNotes);
            console.log('✓ 点评生成完成');
            // 5. 格式化输出
            const outputFormat = input.options?.format || this.config.output.defaultFormat;
            const skillOutput = this.formatter.format(reviewResult, outputFormat);
            const processingTime = Date.now() - startTime;
            console.log(`✓ 处理完成，耗时 ${processingTime}ms`);
            return skillOutput;
        }
        catch (error) {
            console.error('处理过程中发生错误:', error);
            return this.handleError(error, startTime);
        }
    }
    validateInput(input) {
        const { text, options } = input;
        // 检查文本是否为空
        if (!text || text.trim().length === 0) {
            throw new Error('读书心得文本不能为空');
        }
        // 检查文本长度
        if (text.length > this.config.processing.maxInputLength) {
            throw new Error(`文本过长，最大允许 ${this.config.processing.maxInputLength} 字符`);
        }
        // 处理选项
        const processedOptions = {
            language: options?.language || this.config.processing.defaultLanguage,
            style: options?.style || this.config.processing.defaultStyle,
            length: options?.length || this.config.processing.defaultLength,
            includeReferences: options?.includeReferences ?? this.config.output.includeReferences,
            includeSuggestions: options?.includeSuggestions ?? this.config.output.includeSuggestions,
            format: options?.format || this.config.output.defaultFormat
        };
        // 验证选项值
        this.validateOption('language', processedOptions.language, ['auto', 'zh', 'en']);
        this.validateOption('style', processedOptions.style, ['casual', 'professional', 'academic']);
        this.validateOption('length', processedOptions.length, ['short', 'medium', 'long']);
        this.validateOption('format', processedOptions.format, ['markdown', 'plain', 'html']);
        return {
            text: text.trim(),
            options: processedOptions
        };
    }
    validateOption(name, value, allowedValues) {
        if (!allowedValues.includes(value)) {
            throw new Error(`选项 ${name} 的值 "${value}" 无效，允许的值: ${allowedValues.join(', ')}`);
        }
    }
    handleError(error, startTime) {
        const processingTime = Date.now() - startTime;
        const errorContent = `
## ❌ 处理失败

**错误信息:** ${error.message}

**可能的原因:**
1. 输入格式不正确
2. 笔记库路径配置错误
3. API 密钥无效或网络问题
4. 系统资源不足

**解决方案:**
1. 检查输入文本是否有效
2. 确认笔记库路径配置正确
3. 验证 API 密钥和环境变量
4. 查看日志获取更多信息

**技术支持:**
- 查看文档: https://github.com/yourusername/openclaw-skill-book-review
- 提交问题: https://github.com/yourusername/openclaw-skill-book-review/issues

---
*处理时间: ${processingTime}ms*
*错误时间: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}*
`;
        return {
            content: errorContent,
            metadata: {
                format: 'markdown',
                processingTime,
                themes: [],
                generatedAt: new Date().toISOString()
            }
        };
    }
    // 辅助方法
    async testConnection() {
        try {
            // 测试解析器
            const testText = '测试连接';
            await this.parser.parse(testText);
            // 测试搜索器（不实际搜索，只检查配置）
            const notePaths = this.config.search.notePaths;
            if (notePaths.length === 0) {
                console.warn('警告: 未配置笔记路径');
            }
            console.log('✓ 连接测试通过');
            return true;
        }
        catch (error) {
            console.error('连接测试失败:', error);
            return false;
        }
    }
    async getStatistics() {
        // 这里可以添加获取统计信息的方法
        // 比如笔记数量、索引时间等
        return {
            noteCount: 0, // 实际实现中可以从搜索器获取
            lastIndexTime: null,
            config: {
                processing: this.config.processing,
                search: {
                    notePaths: this.config.search.notePaths,
                    maxResults: this.config.search.maxResults,
                    indexUpdateInterval: this.config.search.indexUpdateInterval,
                    minRelevanceScore: this.config.search.minRelevanceScore
                }
            }
        };
    }
    // 批量处理
    async batchProcess(inputs) {
        console.log(`开始批量处理 ${inputs.length} 个心得...`);
        const results = [];
        for (let i = 0; i < inputs.length; i++) {
            const input = inputs[i];
            console.log(`处理第 ${i + 1}/${inputs.length} 个心得...`);
            try {
                const result = await this.process(input);
                results.push(result);
            }
            catch (error) {
                console.error(`处理第 ${i + 1} 个心得失败:`, error);
                // 添加错误结果
                const errorOutput = {
                    content: `处理失败: ${error.message}`,
                    metadata: {
                        format: 'plain',
                        processingTime: 0,
                        themes: [],
                        generatedAt: new Date().toISOString()
                    }
                };
                results.push(errorOutput);
            }
        }
        console.log(`批量处理完成，成功 ${results.filter(r => !r.content.includes('处理失败')).length}/${inputs.length}`);
        return results;
    }
    // 配置管理
    updateConfig(newConfig) {
        // 合并配置
        this.config = {
            ...this.config,
            ...newConfig,
            processing: { ...this.config.processing, ...newConfig.processing },
            search: { ...this.config.search, ...newConfig.search },
            generation: { ...this.config.generation, ...newConfig.generation },
            output: { ...this.config.output, ...newConfig.output }
        };
        // 重新初始化组件
        this.searcher = new note_searcher_1.NoteSearcher(this.config.search.notePaths, this.config.search.maxResults, this.config.search.minRelevanceScore);
        this.generator = new review_generator_1.ReviewGenerator(this.config.generation.aiProvider, this.config.generation.model, this.config.generation.temperature, this.config.generation.maxTokens);
        console.log('配置已更新');
    }
    getConfig() {
        return JSON.parse(JSON.stringify(this.config)); // 返回深拷贝
    }
}
exports.BookReviewSkill = BookReviewSkill;
//# sourceMappingURL=book-review-skill.js.map