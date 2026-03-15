import { InsightParser } from '../../src/parser/insight-parser';

describe('InsightParser', () => {
  let parser: InsightParser;

  beforeAll(() => {
    parser = new InsightParser();
  });

  describe('parse', () => {
    test('应该正确解析中文读书心得', async () => {
      const text = '《活着》让我明白了生命的坚韧，即使在最艰难的时刻也要坚持';
      const result = await parser.parse(text);
      
      expect(result.text).toBe(text);
      expect(result.language).toBe('zh');
      expect(result.keywords.some(k => k.includes('活着') || k.includes('生命'))).toBe(true);
      expect(result.themes.length).toBeGreaterThan(0);
      expect(result.emotions.length).toBeGreaterThan(0);
      expect(['simple', 'medium', 'complex']).toContain(result.complexity);
    });

    test('应该正确解析英文读书心得', async () => {
      const text = 'Reading "To Kill a Mockingbird" taught me about courage and justice in society';
      const result = await parser.parse(text);
      
      expect(result.text).toBe(text);
      expect(result.language).toBe('en');
      expect(result.keywords.some(k => k.toLowerCase().includes('reading') || k.toLowerCase().includes('courage'))).toBe(true);
      expect(result.themes.some(t => t.includes('社会') || t.includes('个人'))).toBe(true);
      expect(result.emotions.length).toBeGreaterThan(0);
    });

    test('应该处理空输入', async () => {
      await expect(parser.parse('')).rejects.toThrow('输入文本不能为空');
      await expect(parser.parse('   ')).rejects.toThrow('输入文本不能为空');
    });

    test('应该截断过长的文本', async () => {
      const longText = '这是一个非常长的读书心得'.repeat(100);
      const result = await parser.parse(longText);
      
      expect(result.text.length).toBeLessThanOrEqual(503); // 500 + '...'
      expect(result.text.endsWith('...')).toBe(true);
    });

    test('应该识别不同的主题', async () => {
      const texts = [
        { text: '《红楼梦》展现了封建社会的家族命运', minThemes: 1 },
        { text: '学习科学让我理解了自然规律', minThemes: 1 },
        { text: '音乐让我感受到情感的流动', minThemes: 1 },
        { text: '个人成长需要不断的自我反思', minThemes: 1 }
      ];

      for (const { text, minThemes } of texts) {
        const result = await parser.parse(text);
        expect(result.themes.length).toBeGreaterThanOrEqual(minThemes);
      }
    });

    test('应该分析情感倾向', async () => {
      const texts = [
        { text: '这本书让我感到非常快乐和满足', expectedEmotions: ['积极'] },
        { text: '阅读这个故事让我感到悲伤和思考', expectedEmotions: ['消极'] },
        { text: '这个理论很有启发性', expectedEmotions: ['启发'] },
        { text: '这是一个中性的观察记录', expectedEmotions: ['中性'] }
      ];

      for (const { text, expectedEmotions } of texts) {
        const result = await parser.parse(text);
        expectedEmotions.forEach(emotion => {
          expect(result.emotions.some(e => e.includes(emotion))).toBe(true);
        });
      }
    });
  });

  describe('关键词提取', () => {
    test('应该从中文文本中提取关键词', async () => {
      const text = '《百年孤独》中魔幻现实主义的运用让我印象深刻';
      const result = await parser.parse(text);
      
      expect(result.keywords.some(k => k.includes('百年') || k.includes('孤独'))).toBe(true);
      expect(result.keywords.length).toBeGreaterThan(0);
    });

    test('应该从英文文本中提取关键词', async () => {
      const text = 'The Great Gatsby explores the American Dream and social class';
      const result = await parser.parse(text);
      
      expect(result.keywords).toContain('great');
      expect(result.keywords).toContain('gatsby');
      expect(result.keywords).toContain('american');
      expect(result.keywords).toContain('dream');
      expect(result.keywords.length).toBeGreaterThan(0);
    });

    test('应该过滤停用词', async () => {
      const text = '的了我是在有和就人不都一一个上也';
      const result = await parser.parse(text);
      
      // 停用词过滤后关键词应该较少
      expect(result.keywords.length).toBeLessThan(10);
    });
  });

  describe('复杂度评估', () => {
    test('应该评估简单文本为简单复杂度', async () => {
      const text = '好书';
      const result = await parser.parse(text);
      expect(result.complexity).toBe('simple');
    });

    test('应该评估中等长度文本为中等复杂度', async () => {
      const text = '这本书讲述了主人公的成长历程，让我深受启发。';
      const result = await parser.parse(text);
      expect(result.complexity).toBe('medium');
    });

    test('应该评估复杂文本为高复杂度', async () => {
      const text = '《战争与和平》通过对多个家族命运的描绘，深刻展现了19世纪初俄国社会的历史变迁、人性探索以及存在意义的哲学思考，这种宏大的叙事结构和深刻的思想内涵让我对文学的社会功能有了新的认识。';
      const result = await parser.parse(text);
      expect(result.complexity).toBe('complex');
    });
  });

  describe('语言检测', () => {
    test('应该检测中文文本', async () => {
      const texts = [
        '中文文本',
        '混合English和中文',
        '《书名》中文内容'
      ];

      for (const text of texts) {
        const result = await parser.parse(text);
        expect(result.language).toBe('zh');
      }
    });

    test('应该检测英文文本', async () => {
      const texts = [
        'English text only',
        'This is a book about science and technology',
        'Reading is fundamental to learning'
      ];

      for (const text of texts) {
        const result = await parser.parse(text);
        expect(result.language).toBe('en');
      }
    });
  });
});