#!/usr/bin/env node
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.main = main;
const book_review_skill_1 = require("./core/book-review-skill");
const default_1 = require("./config/default");
// OpenClaw Skill 入口点
async function main(input) {
    try {
        // 加载配置
        const config = (0, default_1.loadConfig)();
        // 验证配置
        const configErrors = (0, default_1.validateConfig)(config);
        if (configErrors.length > 0) {
            throw new Error(`配置错误: ${configErrors.join(', ')}`);
        }
        // 创建 Skill 实例
        const skill = new book_review_skill_1.BookReviewSkill(config);
        // 处理输入
        let userInput;
        if (typeof input === 'string') {
            userInput = {
                text: input,
                options: {
                    language: 'auto',
                    style: 'professional',
                    length: 'medium',
                    includeReferences: true,
                    includeSuggestions: true
                }
            };
        }
        else {
            userInput = input;
        }
        // 执行 Skill
        const result = await skill.process(userInput);
        return result;
    }
    catch (error) {
        console.error('Skill 执行失败:', error);
        throw error;
    }
}
// CLI 入口点
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.length === 0) {
        console.log(`
📚 读书心得点评 Skill

用法:
  node dist/index.js "你的读书心得"
  
示例:
  node dist/index.js "《活着》让我明白了生命的坚韧"
  
选项:
  --help              显示帮助信息
  --version           显示版本信息
  --format <format>   输出格式 (markdown, plain, html)
  --language <lang>   语言 (zh, en, auto)
  --style <style>     风格 (casual, professional, academic)
  --length <length>   长度 (short, medium, long)
  
环境变量:
  DEEPSEEK_API_KEY    DeepSeek API 密钥
  BOOK_REVIEW_NOTE_PATHS 笔记路径 (逗号分隔)
    `);
        process.exit(0);
    }
    if (args[0] === '--help') {
        console.log(`
📚 读书心得点评 Skill - 帮助

功能:
  将一句读书心得扩展成有深度的点评，基于你的笔记库提供个性化引用。

基本用法:
  book-review "你的读书心得"
  
高级用法:
  book-review "心得" --format html --language zh --style professional
  
配置:
  通过环境变量或配置文件设置:
  - 笔记路径: BOOK_REVIEW_NOTE_PATHS
  - API 密钥: DEEPSEEK_API_KEY
  
示例:
  export DEEPSEEK_API_KEY=your_key
  export BOOK_REVIEW_NOTE_PATHS=~/Notes,~/Obsidian
  book-review "《百年孤独》展现了家族命运的轮回"
    `);
        process.exit(0);
    }
    if (args[0] === '--version') {
        const packageJson = require('../package.json');
        console.log(`book-review Skill v${packageJson.version}`);
        process.exit(0);
    }
    // 解析命令行参数
    let text = '';
    const options = {};
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg.startsWith('--')) {
            const key = arg.substring(2);
            const value = args[i + 1];
            switch (key) {
                case 'format':
                    options.format = value;
                    i++;
                    break;
                case 'language':
                    options.language = value;
                    i++;
                    break;
                case 'style':
                    options.style = value;
                    i++;
                    break;
                case 'length':
                    options.length = value;
                    i++;
                    break;
            }
        }
        else if (!text) {
            text = arg;
        }
    }
    if (!text) {
        console.error('错误: 请提供读书心得文本');
        process.exit(1);
    }
    const input = {
        text,
        options
    };
    // 执行 Skill
    main(input)
        .then(result => {
        console.log(result.content);
    })
        .catch(error => {
        console.error('执行失败:', error.message);
        process.exit(1);
    });
}
// OpenClaw Skill 注册
exports.default = {
    name: 'book-review',
    description: '将读书心得扩展成有深度的点评',
    version: '1.0.0',
    author: 'Digital Partners Team',
    async execute(args) {
        if (args.length === 0) {
            return '请提供读书心得文本。用法: /book-review [你的心得]';
        }
        const input = {
            text: args.join(' '),
            options: {
                language: 'auto',
                style: 'professional',
                length: 'medium'
            }
        };
        try {
            const result = await main(input);
            return result.content;
        }
        catch (error) {
            return `处理失败: ${error.message}`;
        }
    },
    help() {
        return `
📚 读书心得点评 Skill

功能: 将一句读书心得扩展成有深度的点评，基于你的笔记库提供个性化引用。

用法:
  /book-review [你的读书心得]
  
示例:
  /book-review 《活着》让我明白了生命的坚韧
  
选项:
  你可以在心得后添加选项:
  --format markdown|plain|html
  --language zh|en|auto
  --style casual|professional|academic
  --length short|medium|long
  
示例:
  /book-review 《百年孤独》展现了家族命运的轮回 --format markdown --language zh
    `;
    }
};
//# sourceMappingURL=index.js.map