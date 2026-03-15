---
name: code-review
description: "Complete code review workflow for GitCode PRs. Combines automated security scanning with manual code review, outputs formatted findings, and posts comments to PR. Use when reviewing GitCode pull requests - follows 5-step process: automated scan, manual review, issue selection, formatted output, and optional PR comment posting."
---

# Code Review Skill

Complete 5-step code review workflow for GitCode PRs.

## 5-Step Review Process

### Step 1: Automated Scanning

Run script to detect critical issues:

```bash
python scripts/review_pr.py <pr_url> [token]
```

Detects: SQL injection, command injection, XSS, eval(), hardcoded credentials, resource leaks, infinite loops.

**Output**: `review_result.json`

### Step 2: Manual Review (REQUIRED)

**Always read all changed code manually.** Script misses:

- Logic errors and edge cases
- Design flaws
- Performance issues
- Missing error handling
- Business logic errors
- Code duplication
- Test coverage gaps

**How to get diff**:

```bash
curl -H "Authorization: Bearer <token>" \
  "https://gitcode.com/api/v5/repos/<owner>/<repo>/pulls/<number>/diff"
```

**Important**: For each issue found, record:

- **File path**: e.g., `src/components/Table.tsx`
- **Line range**: e.g., `L42-L45` (the line numbers of the problematic code)
- **Problem code**: The actual code snippet
- **Description**: Detailed explanation of the issue
- **Suggestion**: Specific fix recommendation

### Step 3: Select Top 3 Issues

Combine automated + manual findings:

- Filter false positives from script
- Add issues found in manual review
- Sort by severity (1-10)
- Select top 3 most important

Generate json format file `top3_issues.json` for these 3 issues to use in next step.

`top3_issues.json` must be created in the directory of `format_review.py` for the next step to read.

**Important**:

- The `description` field must contain the **complete description** from Step 1 and Step 2 findings, not a simplified version. Include all context and details.
- The `position` field must be the **last line number** of the problematic code range (e.g., if problem code is at L42-L45, use `45`)

**Structure**:

```json
{
  "meta": {
    "total_issues": 5,
    "selected_issues": 3,
    "automated_count": 2,
    "manual_count": 3
  },
  "top3_issues": [
    {
      "number": 1,
      "path": "src/file.py",
      "position": 45,
      "severity": 8,
      "type": "安全问题",
      "description": "Complete description from Step 1/2 findings, not simplified",
      "suggestion": "Detailed suggestion with specific actions",
      "code": "problematic code snippet from L42-L45",
      "code_context": ""
    }
  ]
}
```

**Note**: `position` uses the **last line** of the code range for GitCode API positioning.

**After generating `top3_issues.json`, display the top 3 issues in Markdown format**:

## Top 3 Issues Selected

---

### 🔴 问题 #1 | 可维护性问题 | 6/10

**文件**: `server/src/.../CheckProjectValidHandler.cpp`\*\*

**问题代码行**: `L119-L124`

**问题代码**:

```cpp
bool CheckProjectValidHandler::CheckPathSafety(
    const std::string& path,
    ProjectErrorType& error)
{
    ...
}
```

| review | 内容                         |
| :----- | :--------------------------- |
| 描述   | 代码重复，违反DRY原则        |
| 建议   | 提取公共函数到 FileUtil 类中 |

---

### 🟠 问题 #2 | 测试覆盖问题 | 6/10

**文件**: `server/src/.../CheckProjectValidHandler.cpp`\*\*

**问题代码行**: `L119`

**问题代码**:

```cpp
bool CheckProjectValidHandler::CheckPathSafety
```

| review | 内容                     |
| :----- | :----------------------- |
| 描述   | 缺少单元测试             |
| 建议   | 补充单元测试覆盖各种场景 |

---

### 🟡 问题 #3 | 代码一致性问题 | 5/10

**文件**: `server/src/.../TimelineProtocolRequest.h`\*\*

**问题代码行**: `L68-L72`

**问题代码**:

```cpp
bool isSafePath = std::any_of(path.begin(), path.end(), ...)
```

| review | 内容                                |
| :----- | :---------------------------------- |
| 描述   | 逻辑不一致，缺少 IsRegularFile 检查 |
| 建议   | 统一使用 FileUtil::CheckPathSafety  |

---

**Total**: 3 issues selected

**Note**: `position` in JSON uses the last line number (e.g., L119-L124 → position: 124)

### Step 4: Format Output

Format issues to structured JSON:

```bash
python scripts/format_review.py <top3_issues.json> [output.json]
```

**Input**:

- `top3_issues.json` from Step 3

**Output**: `formatted_review.json`

`formatted_review.json` must be created in the directory of `post_review.py` for the next step to read.

**Structure**:

```json
{
  "comments": [
    {
      "number": 1,
      "path": "src/file.py",
      "position": 42,
      "severity": 8,
      "type": "安全问题",
      "body": "【review】..."
    }
  ]
}
```

**Comment Format** (in `body` field):

```markdown
【review】{问题类型}。{问题描述}。{修改建议}。
```

**After generating `formatted_review.json`, display the formatted content**:

```
Step 4: Formatted Review Comments (Ready to Post)

以下 3 条评论将提交到 PR:

1. `CheckProjectValidHandler.cpp:119`
   类型: 可维护性问题 | 严重程度: 6/10
   内容: 【review】代码重复，违反DRY原则...

2. `CheckProjectValidHandler.cpp:119`
   类型: 测试覆盖问题 | 严重程度: 6/10
   内容: 【review】缺少单元测试...

3. `TimelineProtocolRequest.h:68`
   类型: 代码一致性问题 | 严重程度: 5/10
   内容: 【review】逻辑不一致...

Output: formatted_review.json
```

### Step 5: Post to PR (Optional)

Preview and confirm before posting:

```bash
python scripts/post_review.py <owner> <repo> <pr_number> <token> [formatted_review.json]
```

**Parameters**:

- `owner`: Repository owner (e.g., `Ascend`)
- `repo`: Repository name (e.g., `msinsight`)
- `pr_number`: PR number (e.g., `277`)
- `token`: GitCode access token
- `formatted_review.json`: Output from Step 4 (default: `formatted_review.json`)

**Example**:

```bash
python scripts/post_review.py Ascend msinsight 277 your_token_here formatted_review.json
```

**Flow**:

1. Read `formatted_review.json` from Step 4
2. Display preview of all comments
3. Wait for user confirmation (`yes`/`no`)
4. Only post if user confirms

**Note**: Only posts individual issue comments, no summary comment.

**API Reference**: If unsure how to post PR comments, read `API.md` for detailed API documentation.

---

## Severity Scale

| Score | Level    | Action                 |
| ----- | -------- | ---------------------- |
| 9-10  | Critical | Block merge            |
| 7-8   | High     | Strongly recommend fix |
| 5-6   | Medium   | Recommend fix          |
| 3-4   | Low      | Optional fix           |
| 1-2   | Nit      | Style suggestion       |

---

## Manual Review Checklist

### Logic & Correctness

- [ ] Edge cases (null, empty, max values)
- [ ] Error handling paths
- [ ] Concurrency/thread safety
- [ ] Resource cleanup

### Design & Architecture

- [ ] Single responsibility
- [ ] No code duplication
- [ ] Clean interfaces
- [ ] Clear dependencies

### Performance

- [ ] Algorithm complexity
- [ ] N+1 queries
- [ ] Large data handling
- [ ] Memory usage

### Security

- [ ] Input validation
- [ ] Output encoding
- [ ] Authorization checks
- [ ] Sensitive data handling

### Testing

- [ ] Tests cover changes
- [ ] Edge cases tested
- [ ] Error paths tested

---

## API Reference

- **Get PR files**: `GET /api/v5/repos/{owner}/{repo}/pulls/{number}/files`
- **Get diff**: `GET /api/v5/repos/{owner}/{repo}/pulls/{number}/diff`
- **Post comment**: `POST /api/v5/repos/{owner}/{repo}/pulls/{number}/comments`

---

## Scripts

| Script             | Purpose            | Step | Input                   | Output                  |
| ------------------ | ------------------ | ---- | ----------------------- | ----------------------- |
| `review_pr.py`     | Automated scanning | 1    | PR URL + Token          | `review_result.json`    |
| `format_review.py` | Format to JSON     | 4    | `top3_issues.json`      | `formatted_review.json` |
| `post_review.py`   | Post to PR         | 5    | `formatted_review.json` | PR comments             |
