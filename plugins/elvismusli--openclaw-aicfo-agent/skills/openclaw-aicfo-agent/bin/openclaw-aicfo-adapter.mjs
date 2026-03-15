#!/usr/bin/env node

function usage() {
  console.log(`Usage:
  node scripts/openclaw-aicfo-adapter.mjs session
  node scripts/openclaw-aicfo-adapter.mjs tools
  node scripts/openclaw-aicfo-adapter.mjs companies
  node scripts/openclaw-aicfo-adapter.mjs dashboard [jsonInput]
  node scripts/openclaw-aicfo-adapter.mjs query [jsonInput]
  node scripts/openclaw-aicfo-adapter.mjs search [jsonInput]
  node scripts/openclaw-aicfo-adapter.mjs get-entity [jsonInput]
  node scripts/openclaw-aicfo-adapter.mjs get-file [jsonInput]
  node scripts/openclaw-aicfo-adapter.mjs connectors [jsonInput]
  node scripts/openclaw-aicfo-adapter.mjs connector [jsonInput]
  node scripts/openclaw-aicfo-adapter.mjs documents [jsonInput]

Named options:
  --url <baseUrl>
  --api-key <token>
  --company-id <companyId>

Env:
  AICFO_APP_URL      default: http://localhost:3000
  AICFO_API_KEY      required
  AICFO_COMPANY_ID   optional default for company-scoped commands
`);
}

function parseArgs(argv) {
  const positional = [];
  const named = {};
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!arg.startsWith("--")) {
      positional.push(arg);
      continue;
    }
    const key = arg.slice(2);
    const value = argv[i + 1];
    if (!value || value.startsWith("--")) {
      named[key] = "true";
      continue;
    }
    named[key] = value;
    i += 1;
  }
  return { positional, named };
}

function parseJsonObject(raw, label) {
  if (!raw) return {};
  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed;
    }
    throw new Error(`${label} must be a JSON object`);
  } catch (err) {
    const message = err instanceof Error ? err.message : "invalid json";
    console.error(`Failed to parse ${label}: ${message}`);
    process.exit(1);
  }
}

function toQueryString(params) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    search.set(key, String(value));
  }
  const rendered = search.toString();
  return rendered ? `?${rendered}` : "";
}

function resolveCompanyId(input, named) {
  const candidate =
    input.company_id ??
    input.companyId ??
    named["company-id"] ??
    process.env.AICFO_COMPANY_ID ??
    null;

  return typeof candidate === "string" && candidate.trim().length > 0
    ? candidate.trim()
    : null;
}

function buildHeaders({ apiKey, companyId, contentType } = {}) {
  const headers = {
    Authorization: `Bearer ${apiKey}`,
    Accept: "application/json",
  };

  if (companyId) {
    headers["x-company-id"] = companyId;
  }

  if (contentType) {
    headers["Content-Type"] = contentType;
  }

  return headers;
}

async function parseResponseBody(response) {
  const contentType = response.headers.get("content-type") ?? "application/octet-stream";
  const contentDisposition = response.headers.get("content-disposition");
  const text = await response.text();

  let parsed = text;
  if (contentType.includes("application/json")) {
    try {
      parsed = text ? JSON.parse(text) : null;
    } catch {
      parsed = text;
    }
  }

  return {
    ok: response.ok,
    status: response.status,
    contentType,
    contentDisposition,
    body: parsed,
  };
}

async function request({ appUrl, apiKey, companyId, path, method = "GET", query, jsonBody }) {
  const url = `${appUrl}${path}${toQueryString(query ?? {})}`;
  const response = await fetch(url, {
    method,
    headers: buildHeaders({
      apiKey,
      companyId,
      contentType: jsonBody ? "application/json" : undefined,
    }),
    body: jsonBody ? JSON.stringify(jsonBody) : undefined,
  });

  const parsed = await parseResponseBody(response);
  if (!parsed.ok) {
    const error =
      typeof parsed.body === "object" && parsed.body && "error" in parsed.body
        ? parsed.body.error
        : parsed.body;
    console.error(typeof error === "string" ? error : JSON.stringify(error, null, 2));
    process.exit(1);
  }

  return parsed;
}

const TOOL_SPECS = [
  {
    name: "session",
    surface: "REST",
    description: "Inspect API key scopes, company access, and endpoint map.",
  },
  {
    name: "tools",
    surface: "local",
    description: "List the adapter operations exposed to OpenClaw.",
  },
  {
    name: "companies",
    surface: "REST",
    description: "List companies available to the API key.",
  },
  {
    name: "dashboard",
    surface: "REST",
    description: "Read the company dashboard summary for the active company.",
  },
  {
    name: "query",
    surface: "REST",
    description: "Query Company-DB entities by domain/type/status/documentId.",
  },
  {
    name: "search",
    surface: "REST",
    description: "Full-text search Company-DB entities.",
  },
  {
    name: "get-entity",
    surface: "REST",
    description: "Read one Company-DB entity by qualified_id or domain + id.",
  },
  {
    name: "get-file",
    surface: "REST",
    description: "Read one raw Company-DB file by repo-relative path.",
  },
  {
    name: "connectors",
    surface: "REST",
    description: "List live connector connections and the machine catalog.",
  },
  {
    name: "connector",
    surface: "REST",
    description: "Run one connector action through the unified agent connector surface.",
  },
  {
    name: "documents",
    surface: "REST",
    description: "List company documents with limit and offset.",
  },
];

const { positional, named } = parseArgs(process.argv.slice(2));
const command = positional[0];

if (!command || command === "help" || command === "--help" || command === "-h") {
  usage();
  process.exit(0);
}

const appUrl = (named.url || process.env.AICFO_APP_URL || "http://localhost:3000").replace(/\/$/, "");
const apiKey = named["api-key"] || process.env.AICFO_API_KEY;

const input = parseJsonObject(positional[1], "jsonInput");
const companyId = resolveCompanyId(input, named);

let result;

switch (command) {
  case "tools":
    console.log(JSON.stringify(TOOL_SPECS, null, 2));
    process.exit(0);
}

if (!apiKey) {
  console.error("Missing API key. Set --api-key or AICFO_API_KEY");
  process.exit(1);
}

switch (command) {
  case "session":
    result = await request({
      appUrl,
      apiKey,
      path: "/api/agent/session",
    });
    console.log(JSON.stringify(result.body, null, 2));
    process.exit(0);

  case "companies":
    result = await request({
      appUrl,
      apiKey,
      path: "/api/agent/companies",
    });
    console.log(JSON.stringify(result.body, null, 2));
    process.exit(0);

  case "dashboard":
    result = await request({
      appUrl,
      apiKey,
      companyId,
      path: "/api/agent/dashboard",
    });
    console.log(JSON.stringify(result.body, null, 2));
    process.exit(0);

  case "query":
    result = await request({
      appUrl,
      apiKey,
      companyId,
      path: "/api/company/query",
      query: {
        domain: input.domain,
        type: input.type,
        status: input.status,
        documentId: input.documentId,
        limit: input.limit,
        offset: input.offset,
        view: input.view,
      },
    });
    console.log(JSON.stringify(result.body, null, 2));
    process.exit(0);

  case "search":
    result = await request({
      appUrl,
      apiKey,
      companyId,
      path: "/api/company/search",
      query: {
        q: input.query,
        limit: input.limit,
        view: input.view,
      },
    });
    console.log(JSON.stringify(result.body, null, 2));
    process.exit(0);

  case "get-entity":
    result = await request({
      appUrl,
      apiKey,
      companyId,
      path: "/api/company/entity",
      query: {
        qualified_id: input.qualified_id ?? input.qualifiedId,
        domain: input.domain,
        id: input.id,
      },
    });
    console.log(JSON.stringify(result.body, null, 2));
    process.exit(0);

  case "get-file":
    result = await request({
      appUrl,
      apiKey,
      companyId,
      path: "/api/company/file",
      query: {
        path: input.path,
        download: input.download ? "1" : undefined,
      },
    });
    console.log(
      JSON.stringify(
        {
          path: input.path,
          contentType: result.contentType,
          contentDisposition: result.contentDisposition,
          body: result.body,
        },
        null,
        2,
      ),
    );
    process.exit(0);

  case "connectors":
    result = await request({
      appUrl,
      apiKey,
      companyId,
      path: "/api/agent/connectors",
    });
    console.log(JSON.stringify(result.body, null, 2));
    process.exit(0);

  case "connector":
    result = await request({
      appUrl,
      apiKey,
      companyId,
      path: "/api/agent/connectors",
      method: "POST",
      jsonBody: {
        provider: input.provider,
        action: input.action,
        input: input.input ?? {},
      },
    });
    console.log(JSON.stringify(result.body, null, 2));
    process.exit(0);

  case "documents":
    result = await request({
      appUrl,
      apiKey,
      companyId,
      path: "/api/documents",
      query: {
        limit: input.limit,
        offset: input.offset,
      },
    });
    console.log(JSON.stringify(result.body, null, 2));
    process.exit(0);

  default:
    console.error(`Unknown command: ${command}`);
    usage();
    process.exit(1);
}
