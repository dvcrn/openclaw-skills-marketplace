"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InsightParser = void 0;
class InsightParser {
    constructor() {
        // nodejieba 初始化在需要时进行
    }
    async parse(text) {
        // 1. 文本预处理
        const cleaned = this.preprocess(text);
        // 2. 语言检测
        const language = this.detectLanguage(cleaned);
        // 3. 关键词提取
        const keywords = this.extractKeywords(cleaned, language);
        // 4. 主题识别
        const themes = this.identifyThemes(keywords);
        // 5. 情感分析
        const emotions = this.analyzeEmotion(cleaned);
        // 6. 复杂度评估
        const complexity = this.assessComplexity(cleaned, keywords);
        return {
            text: cleaned,
            themes,
            emotions,
            keywords,
            language,
            complexity,
        };
    }
    preprocess(text) {
        if (!text || text.trim().length === 0) {
            throw new Error('输入文本不能为空');
        }
        // 去除多余空格和换行
        let cleaned = text.trim().replace(/\s+/g, ' ');
        // 限制长度
        const maxLength = 500;
        if (cleaned.length > maxLength) {
            cleaned = cleaned.substring(0, maxLength) + '...';
        }
        return cleaned;
    }
    detectLanguage(text) {
        // 简单的中英文检测
        const chineseChars = text.match(/[\u4e00-\u9fff]/g);
        const englishChars = text.match(/[a-zA-Z]/g);
        if (chineseChars && chineseChars.length > text.length * 0.3) {
            return 'zh';
        }
        else if (englishChars && englishChars.length > text.length * 0.7) {
            return 'en';
        }
        // 默认为中文（考虑到主要用户是中文用户）
        return 'zh';
    }
    extractKeywords(text, language) {
        if (language === 'zh') {
            return this.extractChineseKeywords(text);
        }
        else {
            return this.extractEnglishKeywords(text);
        }
    }
    extractChineseKeywords(text) {
        // 使用简单分词方法
        return this.simpleChineseKeywordExtraction(text);
    }
    extractEnglishKeywords(text) {
        // 简单的英文关键词提取
        const words = text.toLowerCase()
            .replace(/[^\w\s]/g, ' ')
            .split(/\s+/)
            .filter(word => word.length > 2 && !this.isStopWord(word));
        // 去重并统计频率
        const wordCount = new Map();
        words.forEach(word => {
            wordCount.set(word, (wordCount.get(word) || 0) + 1);
        });
        // 按频率排序，取前10个
        return Array.from(wordCount.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10)
            .map(([word]) => word);
    }
    simpleChineseKeywordExtraction(text) {
        // 简单的中文关键词提取：按标点分割，取名词性短语
        const segments = text.split(/[，。！？；,\.!?;]/);
        const keywords = [];
        segments.forEach(segment => {
            if (segment.trim().length >= 2) {
                // 提取可能的书名、作者名、主题词
                const matches = segment.match(/《([^》]+)》|([\u4e00-\u9fff]{2,4})/g);
                if (matches) {
                    matches.forEach(match => {
                        if (match.startsWith('《')) {
                            keywords.push(match);
                        }
                        else if (match.length >= 2) {
                            keywords.push(match);
                        }
                    });
                }
            }
        });
        return [...new Set(keywords)]; // 去重
    }
    isStopWord(word) {
        const stopWords = [
            // 中文停用词
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
            // 英文停用词
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
        ];
        return stopWords.includes(word.toLowerCase());
    }
    identifyThemes(keywords) {
        const themeMap = {
            // 文学主题
            '文学欣赏': ['小说', '散文', '诗歌', '文学', '作家', '作品', '写作', '文字'],
            '人生哲理': ['生命', '生活', '人生', '意义', '价值', '存在', '死亡', '时间'],
            '情感体验': ['爱情', '友情', '亲情', '情感', '感受', '情绪', '心灵', '内心'],
            '社会思考': ['社会', '历史', '文化', '政治', '经济', '制度', '权力', '公平'],
            '个人成长': ['成长', '学习', '改变', '进步', '挑战', '成功', '失败', '经验'],
            // 知识主题
            '科学技术': ['科学', '技术', '创新', '研究', '发现', '理论', '实践', '应用'],
            '艺术文化': ['艺术', '音乐', '绘画', '电影', '戏剧', '文化', '传统', '现代'],
        };
        const themes = [];
        const keywordSet = new Set(keywords.map(k => k.toLowerCase()));
        for (const [theme, themeKeywords] of Object.entries(themeMap)) {
            const matchCount = themeKeywords.filter(keyword => keywordSet.has(keyword.toLowerCase())).length;
            if (matchCount >= 2 || (matchCount === 1 && themeKeywords.length <= 3)) {
                themes.push(theme);
            }
        }
        // 如果没有匹配到主题，使用通用主题
        if (themes.length === 0) {
            if (keywords.some(k => /^《/.test(k))) {
                themes.push('书籍阅读');
            }
            else {
                themes.push('个人感悟');
            }
        }
        return themes;
    }
    analyzeEmotion(text) {
        const emotionWords = {
            '积极': ['快乐', '幸福', '喜悦', '兴奋', '满足', '感动', '温暖', '美好', '精彩', '优秀'],
            '消极': ['悲伤', '痛苦', '难过', '愤怒', '失望', '恐惧', '焦虑', '孤独', '无奈', '遗憾'],
            '中性': ['思考', '分析', '观察', '描述', '记录', '总结', '反思', '理解', '认识', '发现'],
            '深刻': ['深刻', '深邃', '深远', '厚重', '沉重', '复杂', '多元', '丰富', '立体', '全面'],
            '启发': ['启发', '启迪', '启示', '领悟', '觉悟', '明白', '懂得', '认识', '理解', '收获'],
        };
        const emotions = [];
        const textLower = text.toLowerCase();
        for (const [emotion, words] of Object.entries(emotionWords)) {
            const matchCount = words.filter(word => textLower.includes(word.toLowerCase())).length;
            if (matchCount > 0) {
                emotions.push(emotion);
            }
        }
        // 默认情感
        if (emotions.length === 0) {
            emotions.push('中性');
        }
        return emotions;
    }
    assessComplexity(text, keywords) {
        const length = text.length;
        const keywordCount = keywords.length;
        const hasQuotes = /["'《》]/.test(text);
        const hasComplexStructure = /[，。；：]/.test(text);
        let score = 0;
        if (length > 100)
            score += 2;
        else if (length > 50)
            score += 1;
        if (keywordCount > 5)
            score += 2;
        else if (keywordCount > 2)
            score += 1;
        if (hasQuotes)
            score += 1;
        if (hasComplexStructure)
            score += 1;
        if (score >= 4)
            return 'complex';
        if (score >= 2)
            return 'medium';
        return 'simple';
    }
}
exports.InsightParser = InsightParser;
//# sourceMappingURL=insight-parser.js.map