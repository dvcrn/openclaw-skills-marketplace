#!/usr/bin/env node
/**
 * PicSee CLI — URL shortener, analytics, link management.
 *
 * Usage:
 *   picsee shorten <url> [--slug <slug>] [--domain <domain>] [--title <t>] [--desc <d>] [--image <url>] [--tags t1,t2] [--utm source:medium:campaign]
 *   picsee analytics <encodeId>
 *   picsee list [--start <time>] [--limit <n>] [--keyword <kw>] [--tag <t>] [--url <u>] [--slug <s>] [--starred] [--api-only] [--cursor <mapId>]
 *   picsee edit <encodeId> [--url <url>] [--slug <slug>] [--title <t>] [--desc <d>] [--image <url>] [--tags t1,t2] [--expire <iso>]
 *   picsee delete <encodeId>
 *   picsee recover <encodeId>
 *   picsee qr <shortUrl> [--size <px>]
 *   picsee chart <encodeId>          (fetches analytics then renders chart)
 *   picsee auth <token>
 *   picsee auth-status
 *   picsee help
 */
export {};
