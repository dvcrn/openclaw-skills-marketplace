/**
 * PicSee API client — thin wrapper over the REST endpoints.
 */
import https from "https";
// ---------------------------------------------------------------------------
// Low-level HTTP helper
// ---------------------------------------------------------------------------
function request(options, body) {
    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = "";
            res.on("data", (c) => (data += c));
            res.on("end", () => resolve({ status: res.statusCode ?? 0, data }));
        });
        req.on("error", reject);
        if (body)
            req.write(body);
        req.end();
    });
}
function authHeaders(token, body) {
    const h = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
    };
    if (body)
        h["Content-Length"] = String(Buffer.byteLength(body));
    return h;
}
// ---------------------------------------------------------------------------
// Public API methods
// ---------------------------------------------------------------------------
/** Shorten URL — unauthenticated mode */
export async function shortenUnauth(params) {
    const body = JSON.stringify({
        url: params.url,
        domain: params.domain ?? "pse.is",
        externalId: params.externalId ?? "openclaw",
        ...(params.encodeId && { encodeId: params.encodeId }),
    });
    const res = await request({
        hostname: "chrome-ext.picsee.tw",
        path: "/v1/links",
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Content-Length": String(Buffer.byteLength(body)),
        },
    }, body);
    if (res.status !== 200 && res.status !== 201)
        throw new Error(`API ${res.status}: ${res.data}`);
    return JSON.parse(res.data);
}
/** Shorten URL — authenticated mode */
export async function shortenAuth(token, params) {
    const payload = {
        url: params.url,
        domain: params.domain ?? "pse.is",
        externalId: params.externalId ?? "openclaw",
    };
    for (const k of [
        "encodeId",
        "title",
        "description",
        "imageUrl",
        "tags",
        "fbPixel",
        "gTag",
        "utm",
    ]) {
        if (params[k] !== undefined)
            payload[k] = params[k];
    }
    const body = JSON.stringify(payload);
    const res = await request({
        hostname: "api.pics.ee",
        path: "/v1/links",
        method: "POST",
        headers: authHeaders(token, body),
    }, body);
    if (res.status !== 200 && res.status !== 201)
        throw new Error(`API ${res.status}: ${res.data}`);
    return JSON.parse(res.data);
}
/** Get analytics for a link */
export async function getAnalytics(token, encodeId) {
    const res = await request({
        hostname: "api.pics.ee",
        path: `/v1/links/${encodeURIComponent(encodeId)}/overview?dailyClicks=true`,
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
    });
    if (res.status !== 200)
        throw new Error(`API ${res.status}: ${res.data}`);
    return JSON.parse(res.data);
}
/** List links */
export async function listLinks(token, params) {
    const qp = {
        startTime: params.startTime,
        limit: String(Math.min(params.limit ?? 50, 50)),
    };
    if (params.isAPI !== undefined)
        qp.isAPI = String(params.isAPI);
    if (params.isStar !== undefined)
        qp.isStar = String(params.isStar);
    if (params.prevMapId)
        qp.prevMapId = params.prevMapId;
    if (params.externalId)
        qp.externalId = params.externalId;
    const qs = Object.entries(qp)
        .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
        .join("&");
    const bodyObj = {};
    for (const k of [
        "tag",
        "encodeId",
        "keyword",
        "url",
        "authorId",
        "fbPixel",
        "gTag",
    ]) {
        if (params[k] !== undefined)
            bodyObj[k] = params[k];
    }
    const hasBody = Object.keys(bodyObj).length > 0;
    const body = hasBody ? JSON.stringify(bodyObj) : "";
    const res = await request({
        hostname: "api.pics.ee",
        path: `/v2/links/overview?${qs}`,
        method: "POST",
        headers: authHeaders(token, body || undefined),
    }, body || undefined);
    if (res.status !== 200)
        throw new Error(`API ${res.status}: ${res.data}`);
    return JSON.parse(res.data);
}
/** Edit a link */
export async function editLink(token, originalEncodeId, params) {
    const body = JSON.stringify(params);
    const res = await request({
        hostname: "api.pics.ee",
        path: `/v2/links/${encodeURIComponent(originalEncodeId)}`,
        method: "PUT",
        headers: authHeaders(token, body),
    }, body);
    if (res.status !== 200)
        throw new Error(`API ${res.status}: ${res.data}`);
    return JSON.parse(res.data);
}
/** Delete or recover a link */
export async function deleteLink(token, encodeId, action = "delete") {
    const body = JSON.stringify({ value: action });
    const res = await request({
        hostname: "api.pics.ee",
        path: `/v2/links/${encodeURIComponent(encodeId)}/delete`,
        method: "POST",
        headers: authHeaders(token, body),
    }, body);
    if (res.status !== 200)
        throw new Error(`API ${res.status}: ${res.data}`);
    return JSON.parse(res.data);
}
/** Verify token by calling API status endpoint */
export async function verifyToken(token) {
    const res = await request({
        hostname: "api.pics.ee",
        path: "/v2/my/api/status",
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
    });
    if (res.status !== 200)
        throw new Error(`API ${res.status}: ${res.data}`);
    return JSON.parse(res.data);
}
