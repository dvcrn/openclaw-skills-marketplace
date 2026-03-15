"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReviewGenerator = void 0;
const axios_1 = __importDefault(require("axios"));
class ReviewGenerator {
    aiProvider;
    model;
    temperature;
    maxTokens;
    apiKey;
    constructor(aiProvider = 'deepseek', model = 'deepseek-chat', temperature = 0.7, maxTokens = 1000) {
        this.aiProvider = aiProvider;
        this.model = model;
        this.temperature = temperature;
        this.maxTokens = maxTokens;
        this.apiKey = this.getApiKey();
    }
    async generate(parsed, notes) {
        // 1. 准备生成上下文
        const context = this.prepareContext(parsed, notes);
        // 2. 调用 AI 生成点评
        const rawReview = await this.generateWithAI(context);
        // 3. 后处理优化
        const processed = this.postProcess(rawReview, context);
        // 4. 提取引用信息
        const references = this.extractReferences(processed, notes);
        // 5. 生成建议
        const suggestions = this.generateSuggestions(parsed, notes);
        return {
            original: parsed.text,
            expanded: processed,
            references,
            suggestions,
            confidence: this.calculateConfidence(parsed, notes, processed)
        };
    }
    prepareContext(parsed, notes) {
        return {
            insight: parsed.text,
            themes: parsed.themes,
            relevantNotes: notes.map(note => ({
                title: note.title,
                excerpt: note.excerpt,
                relevance: note.relevance
            })),
            language: parsed.language,
            style: 'professional',
            length: 'medium'
        };
    }
    async generateWithAI(context) {
        if (this.aiProvider === 'deepseek') {
            return this.generateWithDeepSeek(context);
        }
        else if (this.aiProvider === 'openai') {
            return this.generateWithOpenAI(context);
        }
        else {
            return this.generateWithTemplate(context);
        }
    }
    async generateWithDeepSeek(context) {
        try {
            const prompt = this.buildPrompt(context);
            const response = await axios_1.default.post('https://api.deepseek.com/v1/chat/completions', {
                model: this.model,
                messages: [
                    {
                        role: 'system',
                        content: this.buildSystemPrompt(context)
                    },
                    {
                        role: 'user',
                        content: prompt
                    }
                ],
                temperature: this.temperature,
                max_tokens: this.maxTokens,
                stream: false
            }, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                },
                timeout: 30000 // 30秒超时
            });
            return response.data.choices[0]?.message?.content || '';
        }
        catch (error) {
            console.error('DeepSeek API 调用失败:', error);
            return this.generateWithTemplate(context);
        }
    }
    async generateWithOpenAI(context) {
        // 类似 DeepSeek 的实现，但使用 OpenAI API
        // 为简化，这里返回模板生成
        return this.generateWithTemplate(context);
    }
    generateWithTemplate(context) {
        // 模板化生成，作为 AI 生成失败时的备选方案
        const { insight, themes, relevantNotes, language } = context;
        let review = '';
        if (language === 'zh') {
            review = `基于你的读书心得"${insight}"，我进行了深入思考。`;
            if (themes.length > 0) {
                review += ` 这个心得涉及到${themes.join('、')}等主题。`;
            }
            if (relevantNotes.length > 0) {
                const note = relevantNotes[0];
                review += ` 在你的笔记中，你曾写道："${note.excerpt}"，这与当前的心得形成了有趣的对话。`;
            }
            review += ` 这种思考体现了你对阅读材料的深度 engagement，建议你可以进一步探索相关主题，建立更系统的知识框架。`;
        }
        else {
            review = `Based on your reading insight "${insight}", I've reflected deeply.`;
            if (themes.length > 0) {
                review += ` This insight touches on themes such as ${themes.join(', ')}.`;
            }
            if (relevantNotes.length > 0) {
                const note = relevantNotes[0];
                review += ` In your notes, you wrote: "${note.excerpt}", which creates an interesting dialogue with your current insight.`;
            }
            review += ` This kind of thinking shows deep engagement with the reading material. I suggest exploring related themes further to build a more systematic knowledge framework.`;
        }
        return review;
    }
    buildSystemPrompt(context) {
        const { language } = context;
        if (language === 'zh') {
            return `你是一位专业的读书导师，擅长将简短的读书心得扩展成有深度的点评。
你的任务是：
1. 理解用户的心得核心
2. 结合提供的相关笔记内容
3. 生成有见解、有深度的扩展点评
4. 使用专业但亲切的语气
5. 适当引用笔记中的内容
6. 保持点评的连贯性和逻辑性

请确保点评：
- 保持原文的核心意思
- 添加有价值的扩展和深化
- 引用相关笔记内容时注明来源
- 语言流畅自然
- 长度适中（300-500字）`;
        }
        else {
            return `You are a professional reading mentor, skilled at expanding brief reading insights into in-depth reviews.
Your task is to:
1. Understand the core of the user's insight
2. Incorporate provided relevant note content
3. Generate insightful, in-depth expanded reviews
4. Use a professional yet warm tone
5. Appropriately reference content from notes
6. Maintain coherence and logical flow in the review

Ensure the review:
- Preserves the core meaning of the original
- Adds valuable expansion and depth
- Cites sources when referencing note content
- Has fluent and natural language
- Is of moderate length (300-500 words)`;
        }
    }
    buildPrompt(context) {
        const { insight, themes, relevantNotes, language } = context;
        if (language === 'zh') {
            let prompt = `请将以下读书心得扩展成有深度的点评：

原始心得：${insight}

相关主题：${themes.join('、')}

相关笔记内容：`;
            relevantNotes.forEach((note, index) => {
                prompt += `\n${index + 1}. ${note.title}：${note.excerpt}`;
            });
            prompt += `\n\n请生成扩展点评，要求：
1. 保持原文核心意思
2. 适当引用相关笔记内容
3. 深化思考，提供新的视角
4. 语言专业但亲切
5. 长度约300-500字

扩展点评：`;
            return prompt;
        }
        else {
            let prompt = `Please expand the following reading insight into an in-depth review:

Original insight: ${insight}

Related themes: ${themes.join(', ')}

Relevant note content:`;
            relevantNotes.forEach((note, index) => {
                prompt += `\n${index + 1}. ${note.title}: ${note.excerpt}`;
            });
            prompt += `\n\nPlease generate an expanded review with these requirements:
1. Preserve the core meaning of the original
2. Appropriately reference relevant note content
3. Deepen the thinking and provide new perspectives
4. Use professional yet warm language
5. Length approximately 300-500 words

Expanded review:`;
            return prompt;
        }
    }
    postProcess(text, context) {
        let processed = text.trim();
        // 移除可能的标记语言
        processed = processed.replace(/^(点评|Review):\s*/i, '');
        processed = processed.replace(/^(扩展点评|Expanded review):\s*/i, '');
        // 确保以句号结束
        if (!/[.!?。！？]$/.test(processed)) {
            processed += context.language === 'zh' ? '。' : '.';
        }
        // 移除多余的空行
        processed = processed.replace(/\n\s*\n\s*\n/g, '\n\n');
        return processed;
    }
    extractReferences(text, notes) {
        const references = [];
        // 简单引用提取：查找文本中可能引用笔记内容的部分
        notes.forEach(note => {
            // 检查文本中是否包含笔记标题或关键内容
            if (text.includes(note.title) ||
                (note.excerpt.length > 20 && text.includes(note.excerpt.substring(0, 20)))) {
                // 尝试提取更精确的引用内容
                let referenceContent = note.excerpt;
                if (referenceContent.length > 100) {
                    referenceContent = referenceContent.substring(0, 100) + '...';
                }
                references.push({
                    source: note.title,
                    content: referenceContent
                });
            }
        });
        // 如果没有找到引用，使用笔记中的内容创建引用
        if (references.length === 0 && notes.length > 0) {
            const note = notes[0];
            let content = note.excerpt;
            if (content.length > 100) {
                content = content.substring(0, 100) + '...';
            }
            references.push({
                source: note.title,
                content
            });
        }
        return references;
    }
    generateSuggestions(parsed, notes) {
        const suggestions = [];
        const { language, themes, complexity } = parsed;
        if (language === 'zh') {
            // 基于主题的建议
            if (themes.includes('人生哲理') || themes.includes('生命意义')) {
                suggestions.push('可以进一步阅读存在主义哲学相关的作品，如加缪、萨特的作品');
                suggestions.push('尝试写一篇关于生命意义的短文，深化这个主题的思考');
            }
            if (themes.includes('文学欣赏')) {
                suggestions.push('可以对比阅读同作者的其他作品，了解其创作风格的发展');
                suggestions.push('尝试分析作品中的象征手法和隐喻，提升文学鉴赏能力');
            }
            if (themes.includes('个人成长')) {
                suggestions.push('将这个心得与你的个人经历联系起来，思考实际应用');
                suggestions.push('制定一个相关的学习或实践计划，将思考转化为行动');
            }
            // 基于复杂度的建议
            if (complexity === 'simple') {
                suggestions.push('这个心得比较简洁，可以尝试扩展成更详细的思考');
            }
            else if (complexity === 'complex') {
                suggestions.push('这个心得思考深入，可以考虑整理成完整的文章或分享');
            }
            // 基于笔记数量的建议
            if (notes.length === 0) {
                suggestions.push('建议在笔记中记录更多相关的内容，便于未来回顾和深化');
            }
            else if (notes.length >= 3) {
                suggestions.push('你已经有多个相关笔记，可以考虑整理成一个专题笔记');
            }
            // 通用建议
            suggestions.push('可以将这个点评添加到你的读书笔记中，作为阅读反思的一部分');
            suggestions.push('定期回顾这类心得，观察自己思考的演变和成长');
        }
        else {
            // English suggestions
            if (themes.includes('Life Philosophy') || themes.includes('Meaning of Life')) {
                suggestions.push('Consider reading existentialist philosophy works by authors like Camus or Sartre');
                suggestions.push('Try writing a short essay on the meaning of life to deepen your thinking on this theme');
            }
            if (themes.includes('Literary Appreciation')) {
                suggestions.push('Compare with other works by the same author to understand their stylistic development');
                suggestions.push('Analyze symbolic techniques and metaphors in the work to enhance literary appreciation');
            }
            if (themes.includes('Personal Growth')) {
                suggestions.push('Connect this insight with your personal experiences and consider practical applications');
                suggestions.push('Create a related learning or practice plan to turn thinking into action');
            }
            if (complexity === 'simple') {
                suggestions.push('This insight is quite concise; consider expanding it into more detailed reflection');
            }
            else if (complexity === 'complex') {
                suggestions.push('This insight shows deep thinking; consider organizing it into a complete article or sharing');
            }
            if (notes.length === 0) {
                suggestions.push('Consider recording more related content in your notes for future review and deepening');
            }
            else if (notes.length >= 3) {
                suggestions.push('You already have multiple related notes; consider organizing them into a thematic notebook');
            }
            suggestions.push('Add this review to your reading notes as part of your reading reflection');
            suggestions.push('Regularly review such insights to observe the evolution and growth of your thinking');
        }
        // 返回前3条建议
        return suggestions.slice(0, 3);
    }
    calculateConfidence(parsed, notes, review) {
        let confidence = 0.7; // 基础置信度
        // 基于心得复杂度
        if (parsed.complexity === 'complex')
            confidence += 0.1;
        else if (parsed.complexity === 'simple')
            confidence -= 0.05;
        // 基于相关笔记数量
        if (notes.length >= 3)
            confidence += 0.1;
        else if (notes.length === 0)
            confidence -= 0.1;
        // 基于生成点评的质量（简单启发式）
        const reviewLength = review.length;
        if (reviewLength > 300 && reviewLength < 800)
            confidence += 0.1;
        if (reviewLength < 100)
            confidence -= 0.1;
        // 确保在合理范围内
        return Math.max(0.3, Math.min(0.95, confidence));
    }
    getApiKey() {
        if (this.aiProvider === 'deepseek') {
            return process.env.DEEPSEEK_API_KEY || '';
        }
        else if (this.aiProvider === 'openai') {
            return process.env.OPENAI_API_KEY || '';
        }
        return '';
    }
}
exports.ReviewGenerator = ReviewGenerator;
//# sourceMappingURL=review-generator.js.map