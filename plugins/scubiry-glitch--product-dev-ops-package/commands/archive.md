# Command: /归档

## 名称
归档 / archive

## 描述
版本发布后的归档操作

## 用法
/归档 v1.0

## 执行流程

1. 复制核心文档到 07-archive/vX.X/snapshot/
2. 提取工作文档要点生成 insights.md
3. 提取关键决策生成 decisions.md
4. 生成 release-notes.md
5. 更新 iterations.md

## 输出
```
✅ 版本 v1.0 归档完成

归档内容：
📁 07-archive/v1.0/
  ├── snapshot-2026-02-18/
  │   ├── WHY.md
  │   ├── features/
  │   ├── insights.md
  │   └── decisions.md
  └── release-notes.md

归档统计：
- 核心文档：5个
- 功能完成：4个
- 自治修改：3次
- 开发周期：14天
```

## 相关角色
- 产品经理（王校长）执行
