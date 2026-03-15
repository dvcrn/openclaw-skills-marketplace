---
name: xhs-content-creator
description: "Xiaohongshu viral note writer. 小红书爆款笔记生成器、标题优化、标签推荐、封面建议。Generate viral notes, trending titles, SEO tags, hooks, and cover suggestions. 小红书运营、种草文案、爆款标题公式、流量密码。"
---

# 小红书爆款笔记生成器

纯本地模板+随机组合，生成地道小红书风格内容。

## 用法

```bash
# 生成完整笔记（标题+正文+标签+emoji）
scripts/xhs.sh note "护肤"

# 生成5个爆款标题
scripts/xhs.sh title "穿搭"

# 推荐标签组合
scripts/xhs.sh tags "美食"

# 生成开头钩子（吸引点击）
scripts/xhs.sh hook "旅行"

# 改写/优化已有笔记
scripts/xhs.sh rewrite "原文内容..."

# 生成封面文案建议
scripts/xhs.sh cover "减肥"

# 查看热门话题方向
scripts/xhs.sh trending

# 帮助
scripts/xhs.sh help
```

## 风格要点

- 大量emoji，口语化、亲切感
- 标题含数字、情绪词、好奇心元素
- 善用网络用语（绝绝子、yyds、姐妹们等）
- 标签格式：`#标签1 #标签2`
