#!/usr/bin/env node
/**
 * 同一篇 Markdown 生成两个公众号预览链接：
 * 1) AI 结构化版：Markdown →（按 SPEC.md 的格式二做“轻量转换”或使用 --ai-html 指定文件）→ html-to-wechat-copy → 预览链接
 * 2) 预设主题版：Markdown → wechat 主题渲染（getFullHtml）→ 预览链接
 *
 * 用法：
 *   node wechat-dual-copy.js <input.md> [--preset 名称] [--ai-html path]
 *
 * 输出：
 *   AI: <url>
 *   PRESET: <url>
 *
 * 同时在 input.md 同目录写入 wechat-preview-urls.txt，避免复制时漏数字。
 */

import { readFileSync, writeFileSync } from 'fs'
import { dirname, isAbsolute, join, resolve as resolvePath } from 'path'
import { getFullHtml } from './lib/utils/markdown.js'
import { resolveOptions } from './opts.js'
import { createCopyUrlFromInputHtml, createCopyUrlFromWechatHtml } from './html-to-wechat-copy.js'
import MarkdownIt from 'markdown-it'

function parseArgs(argv) {
  const positional = []
  const flags = {}
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (a === '--preset' || a === '-p') flags.preset = argv[++i]
    else if (a === '--theme' || a === '-t') flags.themeId = argv[++i]
    else if (a === '--layout' || a === '-l') flags.layoutId = argv[++i]
    else if (a === '--image-style' || a === '-i') flags.imageStyleId = argv[++i]
    else if (a === '--code-theme' || a === '-c') flags.codeThemeId = argv[++i]
    else if (a === '--ai-html') flags.aiHtml = argv[++i]
    else if (a === '--emit-ai-draft') flags.emitAiDraft = true
    else positional.push(a)
  }
  return { positional, flags }
}

/**
 * Markdown → HTML（公共库 markdown-it）：
 * - 覆盖更全（标题/列表/引用/代码块/表格/内联等）
 * - 输出作为“自由模式”HTML：不使用 .article 壳；高亮块仍建议由 AI 直接输出 <section style="...">
 */
function mdToFreeHtml(md) {
  const mdIt = new MarkdownIt({
    html: false, // 不允许 md 内嵌原始 HTML，避免注入；需要高亮块请走 --ai-html（按 SPEC 自由模式输出）
    linkify: true,
    typographer: true,
  })
  const bodyInner = mdIt.render(md)
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>article</title>
</head>
<body>
  <section>
${bodyInner}
  </section>
</body>
</html>`
}

async function postCopy(html) {
  return await createCopyUrlFromWechatHtml(html)
}

const { positional, flags } = parseArgs(process.argv.slice(2))
const mdPathArg = positional[0]
if (!mdPathArg) {
  console.error('用法: node wechat-dual-copy.js <input.md> [--preset 名称] [--ai-html path]')
  process.exit(1)
}

const mdPath = isAbsolute(mdPathArg) ? mdPathArg : resolvePath(process.cwd(), mdPathArg)
const md = readFileSync(mdPath, 'utf8')
const outDir = dirname(mdPath)

// 1) AI 结构化版：优先使用 --ai-html，否则做轻量转换后走 html-to-wechat-copy 的逻辑（直接调用 copy API）
let aiInputHtml
if (flags.aiHtml) {
  const aiHtmlPath = isAbsolute(flags.aiHtml) ? flags.aiHtml : resolvePath(process.cwd(), flags.aiHtml)
  aiInputHtml = readFileSync(aiHtmlPath, 'utf8')
} else {
  aiInputHtml = mdToFreeHtml(md)
  if (flags.emitAiDraft) {
    try {
      const draftPath = join(outDir, 'article.ai.draft.html')
      writeFileSync(draftPath, aiInputHtml, 'utf8')
      process.stderr.write('AI 初稿 HTML 已写入: ' + draftPath + '\n')
    } catch {}
  }
}
const aiUrl = await createCopyUrlFromInputHtml(aiInputHtml)

// 2) 预设主题版：用 getFullHtml 渲染 Markdown（预设通过环境变量控制由 wechat-copy.js 负责，这里直接用默认主题也可）
const presetArgv = []
if (flags.preset) presetArgv.push('--preset', flags.preset)
if (flags.themeId) presetArgv.push('--theme', flags.themeId)
if (flags.layoutId) presetArgv.push('--layout', flags.layoutId)
if (flags.imageStyleId) presetArgv.push('--image-style', flags.imageStyleId)
if (flags.codeThemeId) presetArgv.push('--code-theme', flags.codeThemeId)
const presetOpts = resolveOptions(presetArgv)
if (presetOpts.exit) process.exit(0)
const presetHtml = getFullHtml(md, presetOpts.themeId, presetOpts.imageStyleId, presetOpts.layoutId, null, presetOpts.codeThemeId)
const presetUrl = await postCopy(presetHtml)

const output = `AI: ${aiUrl}\nPRESET: ${presetUrl}\n`
process.stdout.write(output)

try {
  const urlFile = join(outDir, 'wechat-preview-urls.txt')
  writeFileSync(urlFile, output, 'utf8')
  process.stderr.write('预览链接已写入: ' + urlFile + '\n')
} catch {}

