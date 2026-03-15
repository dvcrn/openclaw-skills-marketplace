// 测试环境设置

// 设置测试环境变量
process.env.NODE_ENV = 'test';

// 模拟环境变量（避免在测试中使用真实 API 密钥）
process.env.DEEPSEEK_API_KEY = 'test-api-key';
process.env.BOOK_REVIEW_NOTE_PATHS = '~/TestNotes';

// 设置测试超时
jest.setTimeout(30000); // 30秒

// 全局测试钩子
beforeAll(() => {
  console.log('测试环境初始化...');
});

afterAll(() => {
  console.log('测试环境清理...');
});

// 测试辅助函数
export function createTestInput(text: string = '测试读书心得') {
  return {
    text,
    options: {
      language: 'zh' as const,
      style: 'professional' as const,
      length: 'medium' as const,
      includeReferences: true,
      includeSuggestions: true
    }
  };
}

export function createMockNoteSearchResult(): any {
  return {
    filePath: '/path/to/test/note.md',
    title: '测试笔记',
    excerpt: '这是一个测试笔记内容，用于测试搜索功能。',
    relevance: 0.8,
    matchType: 'content' as const,
    metadata: {
      author: '测试作者',
      book: '测试书籍',
      date: '2026-03-07',
      tags: ['测试', '读书']
    }
  };
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}