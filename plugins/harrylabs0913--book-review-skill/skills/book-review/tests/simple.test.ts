import { InsightParser } from '../src/parser/insight-parser';

describe('InsightParser 基础测试', () => {
  let parser: InsightParser;

  beforeAll(() => {
    parser = new InsightParser();
  });

  test('应该正确解析中文读书心得', async () => {
    const text = '《活着》让我明白了生命的坚韧';
    const result = await parser.parse(text);
    
    expect(result.text).toBe(text);
    expect(result.language).toBe('zh');
    expect(result.keywords.length).toBeGreaterThan(0);
    expect(result.themes.length).toBeGreaterThan(0);
    expect(result.emotions.length).toBeGreaterThan(0);
  });

  test('应该正确解析英文读书心得', async () => {
    const text = 'Reading "To Kill a Mockingbird" taught me about courage';
    const result = await parser.parse(text);
    
    expect(result.text).toBe(text);
    expect(result.language).toBe('en');
    expect(result.keywords.length).toBeGreaterThan(0);
  });

  test('应该处理空输入', async () => {
    await expect(parser.parse('')).rejects.toThrow('输入文本不能为空');
  });

  test('应该识别主题', async () => {
    const text = '《红楼梦》展现了封建社会的家族命运';
    const result = await parser.parse(text);
    
    expect(result.themes.length).toBeGreaterThan(0);
  });

  test('应该分析情感', async () => {
    const text = '这本书让我感到非常快乐和满足';
    const result = await parser.parse(text);
    
    expect(result.emotions.length).toBeGreaterThan(0);
  });
});