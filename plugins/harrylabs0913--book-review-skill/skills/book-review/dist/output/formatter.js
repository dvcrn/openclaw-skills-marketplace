"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OutputFormatter = void 0;
class OutputFormatter {
    format(review, format = 'markdown') {
        const startTime = Date.now();
        let content;
        switch (format) {
            case 'markdown':
                content = this.formatMarkdown(review);
                break;
            case 'plain':
                content = this.formatPlain(review);
                break;
            case 'html':
                content = this.formatHtml(review);
                break;
            default:
                content = this.formatMarkdown(review);
        }
        const processingTime = Date.now() - startTime;
        return {
            content,
            metadata: {
                format,
                processingTime,
                themes: this.extractThemes(review),
                generatedAt: new Date().toISOString()
            }
        };
    }
    formatMarkdown(review) {
        const { original, expanded, references, suggestions, confidence } = review;
        let output = `## 📚 读书心得点评\n\n`;
        output += `**原始心得:** ${original}\n\n`;
        output += `**扩展点评:**\n${expanded}\n\n`;
        if (references.length > 0) {
            output += `**相关引用:**\n`;
            references.forEach(ref => {
                output += `- **${ref.source}:** "${ref.content}"`;
                if (ref.page)
                    output += ` (第${ref.page}页)`;
                output += `\n`;
            });
            output += `\n`;
        }
        if (suggestions.length > 0) {
            output += `**建议:**\n`;
            suggestions.forEach(suggestion => {
                output += `- ${suggestion}\n`;
            });
            output += `\n`;
        }
        output += `---\n`;
        output += `*生成置信度: ${(confidence * 100).toFixed(1)}%*\n`;
        output += `*生成时间: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}*\n`;
        return output;
    }
    formatPlain(review) {
        const { original, expanded, references, suggestions, confidence } = review;
        let output = `读书心得点评\n`;
        output += `============\n\n`;
        output += `原始心得: ${original}\n\n`;
        output += `扩展点评:\n${expanded}\n\n`;
        if (references.length > 0) {
            output += `相关引用:\n`;
            references.forEach(ref => {
                output += `  - ${ref.source}: "${ref.content}"`;
                if (ref.page)
                    output += ` (第${ref.page}页)`;
                output += `\n`;
            });
            output += `\n`;
        }
        if (suggestions.length > 0) {
            output += `建议:\n`;
            suggestions.forEach(suggestion => {
                output += `  - ${suggestion}\n`;
            });
            output += `\n`;
        }
        output += `---\n`;
        output += `生成置信度: ${(confidence * 100).toFixed(1)}%\n`;
        output += `生成时间: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}\n`;
        return output;
    }
    formatHtml(review) {
        const { original, expanded, references, suggestions, confidence } = review;
        let output = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>读书心得点评</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .original { background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }
        .review { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 20px 0; }
        .reference { background-color: #e8f4fd; padding: 10px 15px; margin: 10px 0; border-radius: 4px; border-left: 3px solid #2980b9; }
        .suggestion { background-color: #f0f7ff; padding: 10px 15px; margin: 10px 0; border-radius: 4px; }
        .metadata { color: #7f8c8d; font-size: 0.9em; margin-top: 30px; padding-top: 15px; border-top: 1px solid #ecf0f1; }
    </style>
</head>
<body>
    <h1>📚 读书心得点评</h1>
    
    <h2>原始心得</h2>
    <div class="original">
        <p>${this.escapeHtml(original)}</p>
    </div>
    
    <h2>扩展点评</h2>
    <div class="review">
        <p>${this.escapeHtml(expanded).replace(/\n/g, '<br>')}</p>
    </div>`;
        if (references.length > 0) {
            output += `
    <h2>相关引用</h2>`;
            references.forEach(ref => {
                output += `
    <div class="reference">
        <strong>${this.escapeHtml(ref.source)}:</strong> "${this.escapeHtml(ref.content)}"`;
                if (ref.page)
                    output += ` (第${ref.page}页)`;
                output += `
    </div>`;
            });
        }
        if (suggestions.length > 0) {
            output += `
    <h2>建议</h2>`;
            suggestions.forEach(suggestion => {
                output += `
    <div class="suggestion">
        <p>${this.escapeHtml(suggestion)}</p>
    </div>`;
            });
        }
        output += `
    <div class="metadata">
        <p>生成置信度: ${(confidence * 100).toFixed(1)}%</p>
        <p>生成时间: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}</p>
    </div>
</body>
</html>`;
        return output;
    }
    extractThemes(review) {
        const themes = [];
        // 从扩展点评中提取可能的关键词作为主题
        const text = review.expanded.toLowerCase();
        const themeKeywords = {
            '文学': ['小说', '散文', '诗歌', '文学', '作家', '作品', '写作'],
            '哲学': ['哲学', '思想', '思考', '反思', '意义', '价值', '存在'],
            '人生': ['人生', '生活', '生命', '成长', '经历', '体验', '感悟'],
            '社会': ['社会', '历史', '文化', '政治', '经济', '制度', '权力'],
            '心理': ['心理', '情感', '情绪', '感受', '内心', '心灵', '自我'],
            '科学': ['科学', '技术', '研究', '发现', '理论', '实践', '创新'],
            '艺术': ['艺术', '音乐', '绘画', '电影', '戏剧', '创作', '审美']
        };
        for (const [theme, keywords] of Object.entries(themeKeywords)) {
            for (const keyword of keywords) {
                if (text.includes(keyword)) {
                    themes.push(theme);
                    break;
                }
            }
        }
        // 去重
        return [...new Set(themes)];
    }
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
    // 为不同的输出格式提供便捷方法
    formatForConsole(review) {
        return this.formatPlain(review);
    }
    formatForClipboard(review) {
        // 简洁版本，适合复制到其他应用
        const { original, expanded } = review;
        return `📚 读书心得点评

原始心得：${original}

扩展点评：${expanded}

---\n生成时间：${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}`;
    }
    formatForSharing(review) {
        // 适合社交媒体分享的版本
        const { original, expanded } = review;
        // 截取前200字作为预览
        const preview = expanded.length > 200 ? expanded.substring(0, 200) + '...' : expanded;
        return `📖 刚刚扩展了一条读书心得：

"${original}"

💭 扩展思考：
${preview}

#读书心得 #阅读思考 #知识管理`;
    }
}
exports.OutputFormatter = OutputFormatter;
//# sourceMappingURL=formatter.js.map