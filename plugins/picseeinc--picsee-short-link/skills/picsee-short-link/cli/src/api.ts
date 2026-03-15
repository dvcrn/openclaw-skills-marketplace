/**
 * PicSee API client — thin wrapper over the REST endpoints.
 */

import https from "https";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ShortenParams {
  url: string;
  domain?: string;
  externalId?: string;
  encodeId?: string;
  title?: string;
  description?: string;
  imageUrl?: string;
  tags?: string[];
  fbPixel?: string;
  gTag?: string;
  utm?: Record<string, string>;
}

export interface ListParams {
  startTime: string;
  limit?: number;
  isAPI?: boolean;
  isStar?: boolean;
  prevMapId?: string;
  externalId?: string;
  // Body (search) params
  tag?: string;
  encodeId?: string;
  keyword?: string;
  url?: string;
  authorId?: string;
  fbPixel?: string;
  gTag?: string;
}

export interface EditParams {
  encodeId?: string;
  url?: string;
  domain?: string;
  title?: string;
  description?: string;
  imageUrl?: string;
  tags?: string[];
  fbPixel?: string;
  gTag?: string;
  utm?: Record<string, string>;
  expireTime?: string;
}

// ---------------------------------------------------------------------------
// Low-level HTTP helper
// ---------------------------------------------------------------------------

function request(
  options: https.RequestOptions,
  body?: string,
): Promise<{ status: number; data: string }> {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (c: Buffer) => (data += c));
      res.on("end", () => resolve({ status: res.statusCode ?? 0, data }));
    });
    req.on("error", reject);
    if (body) req.write(body);
    req.end();
  });
}

function authHeaders(token: string, body?: string) {
  const h: Record<string, string> = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  if (body) h["Content-Length"] = String(Buffer.byteLength(body));
  return h;
}

// ---------------------------------------------------------------------------
// Public API methods
// ---------------------------------------------------------------------------

/** Shorten URL — unauthenticated mode */
export async function shortenUnauth(params: ShortenParams) {
  const body = JSON.stringify({
    url: params.url,
    domain: params.domain ?? "pse.is",
    externalId: params.externalId ?? "openclaw",
    ...(params.encodeId && { encodeId: params.encodeId }),
  });
  const res = await request(
    {
      hostname: "chrome-ext.picsee.tw",
      path: "/v1/links",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": String(Buffer.byteLength(body)),
      },
    },
    body,
  );
  if (res.status !== 200 && res.status !== 201)
    throw new Error(`API ${res.status}: ${res.data}`);
  return JSON.parse(res.data);
}

/** Shorten URL — authenticated mode */
export async function shortenAuth(token: string, params: ShortenParams) {
  const payload: Record<string, unknown> = {
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
  ] as const) {
    if ((params as any)[k] !== undefined) payload[k] = (params as any)[k];
  }
  const body = JSON.stringify(payload);
  const res = await request(
    {
      hostname: "api.pics.ee",
      path: "/v1/links",
      method: "POST",
      headers: authHeaders(token, body),
    },
    body,
  );
  if (res.status !== 200 && res.status !== 201)
    throw new Error(`API ${res.status}: ${res.data}`);
  return JSON.parse(res.data);
}

/** Get analytics for a link */
export async function getAnalytics(token: string, encodeId: string) {
  const res = await request({
    hostname: "api.pics.ee",
    path: `/v1/links/${encodeURIComponent(encodeId)}/overview?dailyClicks=true`,
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status !== 200) throw new Error(`API ${res.status}: ${res.data}`);
  return JSON.parse(res.data);
}

/** List links */
export async function listLinks(token: string, params: ListParams) {
  const qp: Record<string, string> = {
    startTime: params.startTime,
    limit: String(Math.min(params.limit ?? 50, 50)),
  };
  if (params.isAPI !== undefined) qp.isAPI = String(params.isAPI);
  if (params.isStar !== undefined) qp.isStar = String(params.isStar);
  if (params.prevMapId) qp.prevMapId = params.prevMapId;
  if (params.externalId) qp.externalId = params.externalId;

  const qs = Object.entries(qp)
    .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
    .join("&");

  const bodyObj: Record<string, unknown> = {};
  for (const k of [
    "tag",
    "encodeId",
    "keyword",
    "url",
    "authorId",
    "fbPixel",
    "gTag",
  ] as const) {
    if ((params as any)[k] !== undefined) bodyObj[k] = (params as any)[k];
  }
  const hasBody = Object.keys(bodyObj).length > 0;
  const body = hasBody ? JSON.stringify(bodyObj) : "";

  const res = await request(
    {
      hostname: "api.pics.ee",
      path: `/v2/links/overview?${qs}`,
      method: "POST",
      headers: authHeaders(token, body || undefined),
    },
    body || undefined,
  );
  if (res.status !== 200) throw new Error(`API ${res.status}: ${res.data}`);
  return JSON.parse(res.data);
}

/** Edit a link */
export async function editLink(
  token: string,
  originalEncodeId: string,
  params: EditParams,
) {
  const body = JSON.stringify(params);
  const res = await request(
    {
      hostname: "api.pics.ee",
      path: `/v2/links/${encodeURIComponent(originalEncodeId)}`,
      method: "PUT",
      headers: authHeaders(token, body),
    },
    body,
  );
  if (res.status !== 200) throw new Error(`API ${res.status}: ${res.data}`);
  return JSON.parse(res.data);
}

/** Delete or recover a link */
export async function deleteLink(
  token: string,
  encodeId: string,
  action: "delete" | "recover" = "delete",
) {
  const body = JSON.stringify({ value: action });
  const res = await request(
    {
      hostname: "api.pics.ee",
      path: `/v2/links/${encodeURIComponent(encodeId)}/delete`,
      method: "POST",
      headers: authHeaders(token, body),
    },
    body,
  );
  if (res.status !== 200) throw new Error(`API ${res.status}: ${res.data}`);
  return JSON.parse(res.data);
}

/** Verify token by calling API status endpoint */
export async function verifyToken(token: string) {
  const res = await request({
    hostname: "api.pics.ee",
    path: "/v2/my/api/status",
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status !== 200) throw new Error(`API ${res.status}: ${res.data}`);
  return JSON.parse(res.data);
}
