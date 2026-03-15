#!/usr/bin/env node
/**
 * 将已有 HTML 文章转为公众号可复制的内联样式格式，并 POST 到 edit.shiker.tech 获取复制页 URL。
 *
 * - CLI 用法：node html-to-wechat-copy.js <path-to-article.html>
 * - 作为库使用：导出 convert/createCopyUrl 等函数（供 wechat-dual-copy.js 复用）
 *
 * 输入规范：见同目录 SPEC.md（公众号文章 HTML 生成规范）。脚本只解析该规范定义的格式一/格式二。
 * 兼容：若存在 .article 但内层无 .item，则按格式二处理；若无 body 则从 </head> 后或整文件取内容。
 */

import { readFileSync, writeFileSync } from 'fs'
import { resolve, dirname, join } from 'path'
import { pathToFileURL } from 'url'

function extractInnerAndMode(raw) {
  // 1) 提取正文：优先 .article 内层；否则 body 内；否则 </head> 后或整文件（无 body 时）
  let inner
  let useGeneric = false
  const articleMatch = raw.match(/<div\s+class="article"[^>]*>([\s\S]*?)<\/div>\s*<\/body>/i)
  if (articleMatch) {
    inner = articleMatch[1]
    // 2) 只有「格式一」才用早报解析：必须至少有一个 .item（含 .item-title/.item-content/.item-impact）
    const hasFormatOneItem = /<div\s+class="item"[^>]*>\s*<div\s+class="item-title"/.test(inner)
    if (!hasFormatOneItem) useGeneric = true
  } else {
    const bodyMatch = raw.match(/<body[^>]*>([\s\S]*?)<\/body>/is)
    if (bodyMatch) {
      inner = bodyMatch[1].trim()
      useGeneric = true
    } else {
      const afterHead = raw.match(/<\/head\s*>\s*([\s\S]*?)(?:<\/html>|$)/i)
      if (afterHead) {
        inner = afterHead[1].replace(/<\/html>.*/i, '').trim()
        useGeneric = true
      } else {
        inner = raw
          .replace(/<!DOCTYPE[^>]*>/i, '')
          .replace(/<html[^>]*>/i, '')
          .replace(/<\/html>/i, '')
          .trim()
        useGeneric = true
      }
    }
  }
  return { inner: inner || '', useGeneric }
}

// 内联样式：公众号仅对「引用 blockquote」和「表格」保留背景色与边框，整篇用统一背景
const styles = {
  // 整篇文章统一背景
  section: "margin:0;padding:16px 14px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Microsoft YaHei',sans-serif;font-size:16px;color:#333;line-height:1.6;word-break:break-word;background:#f5f5f5;box-sizing:border-box",
  h1: "font-size:20px;font-weight:700;color:#1a1a1a;margin-bottom:15px;line-height:1.4;text-align:center",
  // 引用：intro（公众号引用支持背景+边框）
  blockquoteIntro: "margin:20px 0 25px;padding:18px;border-left:4px solid #667eea;background:#f0f4ff;font-size:14px;color:#555;line-height:1.7;box-sizing:border-box",
  // 引用：每条资讯卡片
  blockquoteItem: "margin:22px 0;padding:18px;border-left:4px solid #ff6b6b;background:#fafafa;box-sizing:border-box",
  itemTitle: "font-size:15px;font-weight:600;color:#333;margin-bottom:10px",
  itemContent: "font-size:14px;color:#555;line-height:1.7;margin-bottom:8px",
  // 引用：影响（嵌套在 item 内的小引用块）
  blockquoteImpact: "margin-top:10px;padding:10px;border-left:3px solid #ff9500;background:#fff;font-size:13px;color:#666;box-sizing:border-box",
  // 引用：今日思考（深色块）
  blockquoteThinking: "margin:25px 0;padding:18px;border-left:4px solid #764ba2;background:#667eea;color:#fff;font-size:14px;line-height:1.7;box-sizing:border-box",
  thinkingP: "margin:0 0 8px 0",
  // 分割线：无背景/边框的 div 可能被吞，用段落间距代替
  divider: "margin:25px 0;font-size:0;line-height:0",
  // 页脚：仅文字样式，无背景边框
  footer: "margin-top:25px;padding-top:20px;text-align:center;color:#999;font-size:13px",
  footerStrong: "color:#666",
}

function escapeHtml(str) {
  if (!str) return ''
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

// 将原文结构转为公众号兼容 HTML：仅用 blockquote（引用）和整篇统一背景保留背景/边框
function convertToWechatHtml(html) {
  let out = ''
  // 标题（无背景无边框）
  const h1Match = html.match(/<h1>([\s\S]*?)<\/h1>/)
  if (h1Match) {
    out += `<h1 style="${styles.h1}">${h1Match[1].trim()}</h1>\n`
  }
  // intro → 引用（支持背景+边框）
  const introMatch = html.match(/<div class="intro">\s*([\s\S]*?)\s*<\/div>/)
  if (introMatch) {
    out += `<blockquote style="${styles.blockquoteIntro}">${introMatch[1].trim()}</blockquote>\n`
  }
  // items → 每条一条引用，内里「影响」再包一层引用
  const itemReg = /<div class="item">\s*<div class="item-title">([\s\S]*?)<\/div>\s*<div class="item-content">([\s\S]*?)<\/div>\s*<div class="item-impact">([\s\S]*?)<\/div>\s*<\/div>/g
  let m
  while ((m = itemReg.exec(html)) !== null) {
    out += `<blockquote style="${styles.blockquoteItem}">`
    out += `<div style="${styles.itemTitle}">${m[1].trim()}</div>`
    out += `<div style="${styles.itemContent}">${m[2].trim()}</div>`
    out += `<blockquote style="${styles.blockquoteImpact}">${m[3].trim()}</blockquote>`
    out += `</blockquote>\n`
  }
  // thinking → 引用（深色背景+边框）
  const thinkingMatch = html.match(/<div class="thinking">\s*([\s\S]*?)\s*<\/div>/)
  if (thinkingMatch) {
    const inner = thinkingMatch[1].trim()
      .replace(/<p>/g, `<p style="${styles.thinkingP}">`)
      .replace(/<p style="[^"]*">/g, `<p style="${styles.thinkingP}">`)
    out += `<blockquote style="${styles.blockquoteThinking}">${inner}</blockquote>\n`
  }
  // divider：仅留间距，不用带背景的 div
  if (/<div class="divider">/.test(html)) {
    out += `<p style="${styles.divider}">&#8203;</p>\n`
  }
  // footer：仅文字样式
  const footerMatch = html.match(/<div class="footer">\s*([\s\S]*?)\s*<\/div>/)
  if (footerMatch) {
    let footerInner = footerMatch[1]
      .replace(/<p style="margin-top: 8px;">/g, '<p style="margin:8px 0 0 0;">')
      .replace(/<p style="margin-top: 15px;">/g, '<p style="margin:15px 0 0 0;">')
      .replace(/<strong>/g, `<strong style="${styles.footerStrong}">`)
    out += `<div style="${styles.footer}">${footerInner.trim()}</div>\n`
  }
  return out
}

// 通用 HTML：带样式的 section 改为 blockquote（公众号保留引用背景/边框），表格不动，整篇包一层统一背景
function convertGenericToWechatHtml(html) {
  // section → blockquote，以便公众号保留背景与边框
  let out = html.replace(/<section\s/g, '<blockquote ').replace(/<\/section>/g, '</blockquote>')
  return out
}

export function convertInputHtmlToWechatSection(rawInputHtml) {
  const { inner, useGeneric } = extractInnerAndMode(rawInputHtml)
  const bodyHtml = useGeneric ? convertGenericToWechatHtml(inner) : convertToWechatHtml(inner)
  const sectionStyle = styles.section
  return `<section data-tool="公众号排版" style="${sectionStyle}">\n${bodyHtml}</section>`
}

export async function createCopyUrlFromWechatHtml(wechatHtmlSection) {
  const res = await fetch('https://edit.shiker.tech/api/copy', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ html: wechatHtmlSection }),
  })
  const data = await res.json()
  if (data.success && data.data?.url) return data.data.url
  throw new Error(data.message || String(res.status))
}

export async function createCopyUrlFromInputHtml(rawInputHtml) {
  const wechatHtml = convertInputHtmlToWechatSection(rawInputHtml)
  return await createCopyUrlFromWechatHtml(wechatHtml)
}

async function mainCli() {
  const articlePath = process.argv[2]
  if (!articlePath) {
    console.error('用法: node html-to-wechat-copy.js <path-to-article.html>')
    process.exit(1)
  }
  const raw = readFileSync(resolve(process.cwd(), articlePath), 'utf8')
  try {
    const url = await createCopyUrlFromInputHtml(raw)
    console.log(url)
    // 同时写入与输入 HTML 同目录的文本文件，避免 AI 转述时漏数字导致链接错误
    try {
      const outDir = dirname(resolve(process.cwd(), articlePath))
      const urlFile = join(outDir, 'wechat-preview-url.txt')
      writeFileSync(urlFile, url + '\n', 'utf8')
      console.error('预览链接已写入: ' + urlFile)
    } catch {}
  } catch (e) {
    console.error('请求失败:', e?.message || e)
    process.exit(1)
  }
}

// 作为 CLI 运行
try {
  const entry = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : ''
  if (entry && import.meta.url === entry) await mainCli()
} catch {
  // ignore
}
