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
import { getToken, setToken } from "./keychain.js";
import * as api from "./api.js";
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function die(msg) {
    console.error(`Error: ${msg}`);
    process.exit(1);
}
function out(data) {
    console.log(JSON.stringify(data, null, 2));
}
function requireToken() {
    const token = getToken();
    if (!token)
        die("Not authenticated. Run: picsee auth <token>");
    return token;
}
function flag(args, name) {
    const i = args.indexOf(`--${name}`);
    if (i === -1 || i + 1 >= args.length)
        return undefined;
    return args[i + 1];
}
function hasFlag(args, name) {
    return args.includes(`--${name}`);
}
// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------
async function cmdShorten(args) {
    const url = args[0];
    if (!url)
        die("Usage: picsee shorten <url>");
    const params = { url };
    const slug = flag(args, "slug");
    if (slug)
        params.encodeId = slug;
    const domain = flag(args, "domain");
    if (domain)
        params.domain = domain;
    const title = flag(args, "title");
    if (title)
        params.title = title;
    const desc = flag(args, "desc");
    if (desc)
        params.description = desc;
    const image = flag(args, "image");
    if (image)
        params.imageUrl = image;
    const tags = flag(args, "tags");
    if (tags)
        params.tags = tags.split(",").map((t) => t.trim());
    const utmRaw = flag(args, "utm");
    if (utmRaw) {
        const [source, medium, campaign, term, content] = utmRaw.split(":");
        params.utm = {};
        if (source)
            params.utm.source = source;
        if (medium)
            params.utm.medium = medium;
        if (campaign)
            params.utm.campaign = campaign;
        if (term)
            params.utm.term = term;
        if (content)
            params.utm.content = content;
    }
    const token = getToken();
    const result = token
        ? await api.shortenAuth(token, params)
        : await api.shortenUnauth(params);
    const shortUrl = result.data?.picseeUrl ?? result.picseeUrl ?? "(unknown)";
    const encodeId = result.data?.encodeId ?? result.encodeId;
    out({
        success: true,
        shortUrl,
        encodeId,
        mode: token ? "authenticated" : "unauthenticated",
    });
}
async function cmdAnalytics(args) {
    const encodeId = args[0];
    if (!encodeId)
        die("Usage: picsee analytics <encodeId>");
    const token = requireToken();
    const result = await api.getAnalytics(token, encodeId);
    out({ success: true, data: result.data });
}
async function cmdList(args) {
    const token = requireToken();
    const now = new Date();
    const defaultStart = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}T23:59:59`;
    const params = {
        startTime: flag(args, "start") ?? defaultStart,
        limit: Number(flag(args, "limit")) || undefined,
        isAPI: hasFlag(args, "api-only") ? true : undefined,
        isStar: hasFlag(args, "starred") ? true : undefined,
        prevMapId: flag(args, "cursor"),
        keyword: flag(args, "keyword"),
        tag: flag(args, "tag"),
        url: flag(args, "url"),
        encodeId: flag(args, "slug"),
    };
    const result = await api.listLinks(token, params);
    out({ success: true, data: result.data });
}
async function cmdEdit(args) {
    const originalEncodeId = args[0];
    if (!originalEncodeId)
        die("Usage: picsee edit <encodeId> [options]");
    const token = requireToken();
    const params = {};
    const url = flag(args, "url");
    if (url)
        params.url = url;
    const slug = flag(args, "slug");
    if (slug)
        params.encodeId = slug;
    const domain = flag(args, "domain");
    if (domain)
        params.domain = domain;
    const title = flag(args, "title");
    if (title)
        params.title = title;
    const desc = flag(args, "desc");
    if (desc)
        params.description = desc;
    const image = flag(args, "image");
    if (image)
        params.imageUrl = image;
    const tags = flag(args, "tags");
    if (tags)
        params.tags = tags.split(",").map((t) => t.trim());
    const expire = flag(args, "expire");
    if (expire)
        params.expireTime = expire;
    await api.editLink(token, originalEncodeId, params);
    out({ success: true, message: "Link updated successfully" });
}
async function cmdDelete(args) {
    const encodeId = args[0];
    if (!encodeId)
        die("Usage: picsee delete <encodeId>");
    const token = requireToken();
    await api.deleteLink(token, encodeId, "delete");
    out({ success: true, message: "Link deleted successfully" });
}
async function cmdRecover(args) {
    const encodeId = args[0];
    if (!encodeId)
        die("Usage: picsee recover <encodeId>");
    const token = requireToken();
    await api.deleteLink(token, encodeId, "recover");
    out({ success: true, message: "Link recovered successfully" });
}
async function cmdQr(args) {
    const shortUrl = args[0];
    if (!shortUrl)
        die("Usage: picsee qr <shortUrl> [--size <px>]");
    const size = Number(flag(args, "size")) || 300;
    const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=${size}x${size}&data=${encodeURIComponent(shortUrl)}`;
    let shortQrUrl = qrCodeUrl;
    try {
        const r = await api.shortenUnauth({ url: qrCodeUrl });
        shortQrUrl = r.data?.picseeUrl || qrCodeUrl;
    }
    catch { }
    out({ success: true, qrCodeUrl: shortQrUrl, originalQrUrl: qrCodeUrl, shortUrl, size });
}
async function cmdChart(args) {
    const encodeId = args[0];
    if (!encodeId)
        die("Usage: picsee chart <encodeId>");
    const token = requireToken();
    const result = await api.getAnalytics(token, encodeId);
    const dailyClicks = result.data?.dailyClicks ?? [];
    if (dailyClicks.length === 0)
        die("No daily click data available");
    const chartConfig = {
        type: "line",
        data: {
            labels: dailyClicks.map((d) => d.date),
            datasets: [
                {
                    label: "Clicks",
                    data: dailyClicks.map((d) => d.clicks),
                    borderColor: "rgb(59,130,246)",
                    backgroundColor: "rgba(59,130,246,0.1)",
                    fill: true,
                },
            ],
        },
        options: {
            title: { display: true, text: `Daily Clicks: ${encodeId}` },
            scales: { yAxes: [{ ticks: { beginAtZero: true } }] },
        },
    };
    const chartUrl = `https://quickchart.io/chart?w=600&h=300&c=${encodeURIComponent(JSON.stringify(chartConfig))}`;
    let shortChartUrl = chartUrl;
    try {
        const r = await api.shortenUnauth({ url: chartUrl });
        shortChartUrl = r.data?.picseeUrl || chartUrl;
    }
    catch { }
    out({ success: true, chartUrl: shortChartUrl, originalChartUrl: chartUrl, dataPoints: dailyClicks.length });
}
async function cmdAuth(args) {
    const token = args[0];
    if (!token)
        die("Usage: picsee auth <token>\nGet token: https://picsee.io → Settings → API");
    const status = await api.verifyToken(token);
    setToken(token);
    const d = status.data ?? {};
    out({
        success: true,
        plan: d.plan ?? d.planName ?? "unknown",
        quota: d.quota ?? 0,
        usage: d.usage ?? 0,
        message: "Token verified and stored securely (AES-256-CBC).",
    });
}
async function cmdAuthStatus() {
    const token = getToken();
    if (!token) {
        out({ authenticated: false, message: "No token stored." });
        return;
    }
    try {
        const status = await api.verifyToken(token);
        const d = status.data ?? {};
        out({
            authenticated: true,
            plan: d.plan ?? d.planName ?? "unknown",
            quota: d.quota ?? 0,
            usage: d.usage ?? 0,
        });
    }
    catch (e) {
        out({ authenticated: false, message: `Token invalid: ${e.message}` });
    }
}
function showHelp() {
    console.log(`PicSee CLI — URL shortener & link management

Commands:
  shorten <url>           Shorten a URL
    --slug <slug>         Custom slug (3-90 chars)
    --domain <domain>     Short link domain (default: pse.is)
    --title <title>       Preview title (Advanced plan)
    --desc <desc>         Preview description (Advanced plan)
    --image <url>         Preview thumbnail (Advanced plan)
    --tags t1,t2          Tags (Advanced plan)
    --utm s:m:c:t:n       UTM params (source:medium:campaign:term:content)

  analytics <encodeId>    Get click analytics (requires auth)

  list                    List recent links (requires auth)
    --start <time>        Query from this time backward (default: now)
    --limit <n>           Results per page (max 50)
    --keyword <kw>        Search title/description (Advanced, 3-30 chars)
    --tag <tag>           Filter by tag (Advanced)
    --url <url>           Filter by destination URL
    --slug <slug>         Filter by exact slug
    --starred             Starred links only
    --api-only            API-generated links only
    --cursor <mapId>      Pagination cursor

  edit <encodeId>         Edit a link (requires Advanced plan)
    --url <url>           New destination URL
    --slug <slug>         New slug
    --title/--desc/--image/--tags/--expire

  delete <encodeId>       Delete a link (requires auth)
  recover <encodeId>      Recover a deleted link (requires auth)

  qr <shortUrl>           Generate QR code URL
    --size <px>           QR size in pixels (default: 300)

  chart <encodeId>        Generate analytics chart URL (requires auth)

  auth <token>            Store PicSee API token
  auth-status             Check current auth status
  help                    Show this help`);
}
// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
    const [cmd, ...args] = process.argv.slice(2);
    try {
        switch (cmd) {
            case "shorten":
                await cmdShorten(args);
                break;
            case "analytics":
                await cmdAnalytics(args);
                break;
            case "list":
                await cmdList(args);
                break;
            case "edit":
                await cmdEdit(args);
                break;
            case "delete":
                await cmdDelete(args);
                break;
            case "recover":
                await cmdRecover(args);
                break;
            case "qr":
                await cmdQr(args);
                break;
            case "chart":
                await cmdChart(args);
                break;
            case "auth":
                await cmdAuth(args);
                break;
            case "auth-status":
                await cmdAuthStatus();
                break;
            case "help":
            case "--help":
            case "-h":
            case undefined:
                showHelp();
                break;
            default:
                die(`Unknown command: ${cmd}. Run "picsee help" for usage.`);
        }
    }
    catch (e) {
        die(e.message);
    }
}
main();
