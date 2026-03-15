#!/usr/bin/env node
/**
 * 生成 HTML 并 POST 到 edit.shiker.tech/api/copy，输出复制页 URL（支持主题混搭）。
 * 用法：node wechat-copy.js [选项] <input.md>
 * 选项：--preset|-p <名称>  --theme|-t <id>  --layout|-l <id>  --image-style|-i <id>  --code-theme|-c <id>
 *       --list-presets|-L  --list-themes  --list-layouts
 * 环境变量：WEWORK_PRESET, WEWORK_THEME_ID, WEWORK_LAYOUT_ID, WEWORK_IMAGE_STYLE_ID, WEWORK_CODE_THEME_ID
 */

import { getFullHtml } from './lib/utils/markdown.js'
import { resolveOptions } from './opts.js'
import { readFileSync } from 'fs'
import { join } from 'path'

const opts = resolveOptions()
if (opts.exit) process.exit(0)

const fileArg = opts.positional[0]
if (!fileArg) {
  console.error('用法: node wechat-copy.js [--preset 预设名|--theme id --layout id] <input.md>')
  console.error('  例: node wechat-copy.js --preset 墨色下划线 article.md')
  process.exit(1)
}
const content = readFileSync(join(process.cwd(), fileArg), 'utf8')

const html = getFullHtml(content, opts.themeId, opts.imageStyleId, opts.layoutId, null, opts.codeThemeId)

const res = await fetch('https://edit.shiker.tech/api/copy', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ html }),
})

const data = await res.json()
if (data.success && data.data?.url) {
  console.log(data.data.url)
} else {
  console.error('请求失败:', data.message || res.status)
  process.exit(1)
}
