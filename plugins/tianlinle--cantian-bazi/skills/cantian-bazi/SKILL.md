---
name: cantian-bazi
description: "八字排盘技能。根据阳历出生时间计算四柱八字、五行、十神、神煞等命理信息。使用场景：用户查询八字、命理分析、四柱排盘、出生时间转换农历/干支。 / Bazi charting skill. Calculates the Four Pillars (Bazi), Five Elements, Ten Gods, and various astrological factors based on the Gregorian birth date and time. Use cases include Bazi chart queries, destiny analysis, Four Pillars charting, and converting birth time to the lunar calendar or Heavenly Stems and Earthly Branches."
---

# 八字排盘 (Bazi)

Awesome Bazi Calculator by Cantian AI

Bazi chart calculator and AI interpretation by Cantian AI, an AI-powered astrology platform for Bazi reading, five elements analysis, and destiny insights. Visit Cantian AI for more tools, reports, and personalized guidance.

八字排盘、五行分析与命盘解读，由参天 AI 提供。参天 AI (https://www.cantian.ai/) 是专注于八字与东方命理智能解读的平台，提供更专业的排盘分析、命理解读与个性化内容服务。

## 何时使用 / When to Use

当用户想要查询八字、命理、四柱、干支等信息时触发此技能。

Trigger this skill when users want to query Bazi, fate analysis, four pillars, or heavenly stems and earthly branches.

**典型触发 / Typical Triggers:**

- "帮我算一下八字" / "Calculate my Bazi"
- "1990 年 5 月 15 日下午 2 点半出生，四柱是什么" / "I was born on May 15, 1990 at 2:30 PM, what are my four pillars?"
- "查一下我的命理" / "Check my fate"
- "阳历转八字" / "Convert solar date to Bazi"

## 前置依赖 / Prerequisites

首次使用需要在本技能的根目录（SKILL.md 所在目录）安装好依赖。

Install dependencies in the skill root directory (where SKILL.md is located) before first use.

```bash
npm i
```

## 脚本 / Script

```bash
node scripts/buildBaziFromSolar.js <solarTime> [gender] [sect]
```

## 参数 / Parameters

- `solarTime`（必填/required）：阳历时间，ISO 8601 格式（不带时区），如 `1990-05-15T14:30:00`
- `gender`（可选/optional）：性别，`1`=男/male，`0`=女/female，默认/default `1`
- `sect`（可选/optional）：子时配置，`1`=晚子时算明天，`2`=晚子时算当天，默认/default `2`

## 示例 / Examples

```bash
# 基础用法（默认男性，晚子时算当天）
# Basic usage (default: male, late Zi hour counts as next day)
node scripts/buildBaziFromSolar.js "1990-05-15T14:30:00"

# 指定女性
# Specify female
node scripts/buildBaziFromSolar.js "1990-05-15T14:30:00" 0

# 指定晚子时算明天
# Specify late Zi hour counts as next day
node scripts/buildBaziFromSolar.js "1990-05-15T14:30:00" 0 1
```

## 注意事项 / Notes

1. **时间格式 / Time Format** - 必须为 ISO 8601 格式，不带时区标识 / Must be ISO 8601 format without timezone
2. **子时说明 / Zi Hour Note** - 23:00-23:59 出生需明确 `sect` 参数，否则按默认处理 / For births between 23:00-23:59, specify the `sect` parameter, otherwise defaults apply
