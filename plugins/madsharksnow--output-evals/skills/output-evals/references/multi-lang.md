# Multi-Lang — TypeScript / Python 测试指南

Bash 之外的项目测试方法。L1-L5 分层逻辑不变，只是工具链不同。

## 语言检测与工具链选择

```
检测顺序：
1. ls package.json → 有 → 看 devDependencies 有无 vitest/jest → TypeScript 模式
2. ls *.py / requirements.txt / pyproject.toml → Python 模式
3. ls scripts/*.sh → Bash 模式
4. 混合 → 每种语言独立框架，统一 run-all-tests.sh 入口
```

## TypeScript 测试（Vitest 优先）

### Bootstrap

```bash
# 项目已有 package.json 时
npm install -D vitest @vitest/coverage-v8

# 在 package.json 中添加
# "scripts": { "test": "vitest run", "test:watch": "vitest", "test:coverage": "vitest run --coverage" }
```

### 目录结构

```
project/
├── src/
│   ├── session-router/
│   │   └── index.ts
│   └── memory-lancedb/
│       └── index.ts
├── tests/
│   ├── L1-unit/
│   │   ├── session-router.test.ts
│   │   └── memory-lancedb.test.ts
│   ├── L2-integration/
│   │   └── router-memory-flow.test.ts
│   ├── L3-scenario/
│   │   └── user-onboarding.test.ts
│   └── L4-experience/
│       └── output-quality.test.ts
├── vitest.config.ts
└── package.json
```

### 测试模板

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// L1: 单元测试 — 测试单个函数的输入输出
describe('L1: extractUserId', () => {
  it('extracts feishu DM user ID', () => {
    expect(extractUserId('agent:main:feishu:direct:ou_abc123')).toBe('ou_abc123');
  });

  it('returns __owner__ for webchat', () => {
    expect(extractUserId('agent:main:main')).toBe('__owner__');
  });

  it('returns __global__ for undefined', () => {
    expect(extractUserId(undefined)).toBe('__global__');
  });

  // 错误路径
  it('handles empty string', () => {
    expect(extractUserId('')).toBe('__global__');
  });
});

// L2: 集成测试 — 测试模块间数据流
describe('L2: memory store → recall flow', () => {
  let db: MemoryDB;

  beforeEach(async () => {
    db = new MemoryDB(':memory:', 768); // 测试用内存数据库
  });

  afterEach(async () => {
    // 清理
  });

  it('stored memory can be recalled', async () => {
    const vector = await embeddings.embed('test content');
    await db.store({ text: 'test content', vector, importance: 0.7, category: 'fact', userId: 'user1' }, 'user1');

    const results = await db.search(vector, 'user1', 5, 0.1);
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].entry.text).toBe('test content');
  });

  it('user isolation: user A cannot see user B memories', async () => {
    const vector = await embeddings.embed('secret');
    await db.store({ text: 'secret', vector, importance: 0.9, category: 'fact', userId: 'userA' }, 'userA');

    const results = await db.search(vector, 'userB', 5, 0.1);
    expect(results.length).toBe(0);
  });
});

// L4b: 内容质量测试
describe('L4b: session-router persona injection quality', () => {
  it('injected persona contains meaningful instructions, not empty', async () => {
    const persona = await loadPersona('pm');
    expect(persona).toBeDefined();
    expect(persona.length).toBeGreaterThan(50); // 不是空文件
    expect(persona).not.toContain('TODO');       // 不是占位符
  });
});
```

### Mock 策略

```typescript
// 外部 API 用 vi.mock
vi.mock('./feishu-api', () => ({
  sendMessage: vi.fn().mockResolvedValue({ message_id: 'mock_id' }),
  getChatHistory: vi.fn().mockResolvedValue({ messages: [] }),
}));

// LLM 用固定响应
vi.mock('./llm-client', () => ({
  complete: vi.fn().mockResolvedValue('{"memories": []}'),
}));

// 文件系统用 memfs 或 tmp
import { vol } from 'memfs';
vi.mock('fs', () => ({ ...memfs }));
```

### 覆盖率

```bash
npx vitest run --coverage
# 输出 coverage/index.html，关注：
# - 行覆盖率 > 80%
# - 分支覆盖率 > 70%（比文件级覆盖率重要得多）
```

## Python 测试（pytest）

### Bootstrap

```bash
pip install pytest pytest-cov pytest-asyncio
```

### 目录结构

```
project/
├── src/
│   └── module.py
├── tests/
│   ├── conftest.py          # 共享 fixture
│   ├── test_L1_unit.py
│   ├── test_L2_integration.py
│   └── test_L4b_quality.py
├── pyproject.toml
└── pytest.ini
```

### 测试模板

```python
import pytest

# L1: 单元
class TestL1ParseConfig:
    def test_valid_json(self):
        result = parse_config('{"key": "value"}')
        assert result["key"] == "value"

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError):
            parse_config("not json")

    def test_empty_input(self):
        result = parse_config("{}")
        assert result == {}

# L2: 集成
class TestL2DataPipeline:
    @pytest.fixture
    def sample_messages(self):
        return [{"role": "user", "content": "记住我喜欢Python"}]

    def test_extraction_stores_memory(self, sample_messages):
        memories = extract_memories(sample_messages)
        assert len(memories) > 0
        assert any("Python" in m["text"] for m in memories)

# L4b: 内容质量
class TestL4bReportQuality:
    def test_report_not_generic_filler(self):
        report = generate_report(project_data)
        assert "暂无" not in report
        assert len(report) > 100  # 不是空报告

    def test_report_contains_specific_data(self):
        report = generate_report(project_data)
        # 不能只说"有N条消息"，要有实质内容
        assert not re.match(r'^.*\d+条消息.*$', report)
```

### 覆盖率

```bash
pytest --cov=src --cov-report=html --cov-branch
# --cov-branch 是关键：测分支覆盖率，不只是行覆盖率
```

## 混合项目的统一入口

```bash
#!/bin/bash
# run-all-tests.sh — 统一测试入口

echo "=== Bash Tests ==="
bash tests/run-tests.sh

echo ""
echo "=== TypeScript Tests ==="
npx vitest run 2>/dev/null || echo "No TS tests found"

echo ""
echo "=== Python Tests ==="
pytest tests/ 2>/dev/null || echo "No Python tests found"
```

## Scan 适配

对非 Bash 项目，scan 逻辑需要适配：

| 语言 | 扫描方式 |
|------|---------|
| Bash | `grep` 搜测试文件中的 `bash scripts/xxx.sh` 调用 |
| TypeScript | `grep` 搜 `import.*from.*xxx` 或 `describe.*xxx` |
| Python | `grep` 搜 `from xxx import` 或 `def test_xxx` |

通用规则不变：文件存在性检查（`import` 但没有 `expect`/`assert`）不算覆盖。
