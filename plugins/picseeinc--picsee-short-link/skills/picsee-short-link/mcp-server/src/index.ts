#!/usr/bin/env node
/**
 * PicSee MCP Server
 *
 * Exposes PicSee URL shortener as MCP tools.
 * Supports authenticated (token-based) and unauthenticated modes.
 * Token is stored with AES-256-CBC encryption at ~/.openclaw/.picsee_token.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { getToken, setToken } from "./keychain.js";
import * as api from "./api.js";

// ---------------------------------------------------------------------------
// Server setup
// ---------------------------------------------------------------------------

const server = new McpServer({
  name: "picsee",
  version: "1.3.1",
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function requireToken(): string {
  const token = getToken();
  if (!token)
    throw new Error(
      "Not authenticated. Use the setup_auth tool to store your PicSee API token first.",
    );
  return token;
}

function ok(data: unknown) {
  return {
    content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }],
  };
}

function err(message: string) {
  return { content: [{ type: "text" as const, text: message }], isError: true };
}

// ---------------------------------------------------------------------------
// Tools
// ---------------------------------------------------------------------------

server.tool(
  "shorten_url",
  "Shorten a URL with PicSee. Auto-detects auth mode: if a token is stored, uses authenticated API (api.pics.ee) with advanced features; otherwise falls back to unauthenticated mode (chrome-ext.picsee.tw).",
  {
    url: z.string().url().describe("Destination URL to shorten"),
    encodeId: z
      .string()
      .min(3)
      .max(90)
      .optional()
      .describe("Custom slug (3-90 chars)"),
    domain: z
      .string()
      .optional()
      .describe('Short link domain (default: "pse.is")'),
    title: z
      .string()
      .optional()
      .describe("Custom preview title (Advanced plan)"),
    description: z
      .string()
      .optional()
      .describe("Custom preview description (Advanced plan)"),
    imageUrl: z
      .string()
      .url()
      .optional()
      .describe("Custom preview thumbnail URL (Advanced plan)"),
    tags: z
      .array(z.string())
      .optional()
      .describe("Tags for organisation (Advanced plan)"),
    utm: z
      .object({
        source: z.string().optional(),
        medium: z.string().optional(),
        campaign: z.string().optional(),
        term: z.string().optional(),
        content: z.string().optional(),
      })
      .optional()
      .describe("UTM parameters (Advanced plan)"),
  },
  async (params) => {
    try {
      const token = getToken();
      const result = token
        ? await api.shortenAuth(token, params)
        : await api.shortenUnauth(params);
      const shortUrl =
        result.data?.picseeUrl ?? result.picseeUrl ?? "(unknown)";
      const encodeId = result.data?.encodeId ?? result.encodeId;
      return ok({
        success: true,
        shortUrl,
        encodeId,
        mode: token ? "authenticated" : "unauthenticated",
      });
    } catch (e: any) {
      return err(`Failed to shorten URL: ${e.message}`);
    }
  },
);

server.tool(
  "get_analytics",
  "Get click analytics for a PicSee short link (requires authentication).",
  {
    encodeId: z.string().describe("The slug / encodeId of the short link"),
  },
  async ({ encodeId }) => {
    try {
      const token = requireToken();
      const result = await api.getAnalytics(token, encodeId);
      return ok({ success: true, data: result.data });
    } catch (e: any) {
      return err(`Analytics failed: ${e.message}`);
    }
  },
);

server.tool(
  "list_links",
  'List and search PicSee short links (requires authentication). startTime should be the END of the period you want to query backward from, in ISO-like format "YYYY-MM-DDTHH:MM:SS". For example, to see links from March 2026, use "2026-03-31T23:59:59".',
  {
    startTime: z
      .string()
      .describe(
        'Query backward from this time, format: YYYY-MM-DDTHH:MM:SS. Use the LAST moment of the desired period, e.g. "2026-03-31T23:59:59"',
      ),
    limit: z
      .number()
      .int()
      .min(1)
      .max(50)
      .optional()
      .describe("Results per page (max 50, default 50)"),
    isAPI: z.boolean().optional().describe("Filter API-generated links only"),
    isStar: z.boolean().optional().describe("Filter starred links only"),
    prevMapId: z
      .string()
      .optional()
      .describe("Pagination cursor — get links older than this mapId"),
    externalId: z.string().optional().describe("Filter by external ID"),
    keyword: z
      .string()
      .optional()
      .describe("Search in title/description (Advanced plan, 3-30 chars)"),
    tag: z.string().optional().describe("Search by tag (Advanced plan)"),
    url: z.string().optional().describe("Search by exact destination URL"),
    encodeId: z.string().optional().describe("Search by exact slug"),
    authorId: z.string().optional().describe("Filter by author ID"),
  },
  async (params) => {
    try {
      const token = requireToken();
      const result = await api.listLinks(token, params);
      return ok({ success: true, data: result.data });
    } catch (e: any) {
      return err(`List failed: ${e.message}`);
    }
  },
);

server.tool(
  "edit_link",
  "Edit an existing PicSee short link (requires Advanced plan authentication). Only include the fields you want to change.",
  {
    originalEncodeId: z
      .string()
      .describe("Current slug of the link to edit"),
    url: z.string().url().optional().describe("New destination URL"),
    encodeId: z.string().optional().describe("New custom slug"),
    domain: z.string().optional().describe("New domain"),
    title: z.string().optional().describe("New preview title"),
    description: z.string().optional().describe("New preview description"),
    imageUrl: z
      .string()
      .url()
      .optional()
      .describe("New preview thumbnail URL"),
    tags: z.array(z.string()).optional().describe("New tags"),
    fbPixel: z.string().optional().describe("Meta Pixel ID"),
    gTag: z.string().optional().describe("Google Tag Manager ID"),
    utm: z
      .object({
        source: z.string().optional(),
        medium: z.string().optional(),
        campaign: z.string().optional(),
        term: z.string().optional(),
        content: z.string().optional(),
      })
      .optional()
      .describe("New UTM parameters"),
    expireTime: z
      .string()
      .optional()
      .describe("Expiration time (ISO 8601)"),
  },
  async ({ originalEncodeId, ...editParams }) => {
    try {
      const token = requireToken();
      await api.editLink(token, originalEncodeId, editParams);
      return ok({ success: true, message: "Link updated successfully" });
    } catch (e: any) {
      return err(`Edit failed: ${e.message}`);
    }
  },
);

server.tool(
  "delete_link",
  "Delete or recover a PicSee short link (requires authentication).",
  {
    encodeId: z.string().describe("The slug of the short link"),
    action: z
      .enum(["delete", "recover"])
      .default("delete")
      .describe('"delete" or "recover"'),
  },
  async ({ encodeId, action }) => {
    try {
      const token = requireToken();
      await api.deleteLink(token, encodeId, action);
      return ok({
        success: true,
        message: `Link ${action}d successfully`,
      });
    } catch (e: any) {
      return err(`${action} failed: ${e.message}`);
    }
  },
);

server.tool(
  "setup_auth",
  "Store and verify a PicSee API token. The token is encrypted with AES-256-CBC (machine-specific key) and saved to ~/.openclaw/.picsee_token. The token is verified against the PicSee API before storing.",
  {
    token: z.string().min(1).describe("PicSee API token"),
  },
  async ({ token }) => {
    try {
      const status = await api.verifyToken(token);
      setToken(token);
      const d = status.data ?? {};
      return ok({
        success: true,
        plan: d.plan ?? d.planName ?? "unknown",
        quota: d.quota ?? 0,
        usage: d.usage ?? 0,
        message: "Token verified and stored securely (AES-256-CBC).",
      });
    } catch (e: any) {
      return err(`Auth failed: ${e.message}`);
    }
  },
);

server.tool(
  "generate_qr_code",
  "Generate a QR code URL for a PicSee short link. **Only call this if the user explicitly requests a QR code.** Returns a shortened URL to the QR code image.",
  {
    shortUrl: z.string().url().describe("The short URL to encode in QR code"),
    size: z
      .number()
      .int()
      .min(100)
      .max(1000)
      .default(300)
      .describe("QR code size in pixels (default: 300)"),
  },
  async ({ shortUrl, size }) => {
    try {
      const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=${size}x${size}&data=${encodeURIComponent(shortUrl)}`;
      
      // Shorten the QR code URL using unauthenticated mode (no quota consumed)
      let shortQrUrl = qrCodeUrl;
      try {
        const shortenResult = await api.shortenUnauth({ url: qrCodeUrl });
        shortQrUrl = shortenResult.data?.picseeUrl || qrCodeUrl;
      } catch (shortenError: any) {
        // If shortening fails, fall back to original URL
        console.error("Failed to shorten QR code URL:", shortenError.message);
      }
      
      return ok({
        success: true,
        qrCodeUrl: shortQrUrl,
        originalQrUrl: qrCodeUrl,
        shortUrl,
        size,
        note: shortQrUrl !== qrCodeUrl
          ? "QR code URL automatically shortened via PicSee (unauthenticated, no quota used)"
          : "QR code URL (shortening unavailable)",
      });
    } catch (e: any) {
      return err(`QR code generation failed: ${e.message}`);
    }
  },
);

server.tool(
  "generate_analytics_chart",
  "Generate a line chart URL visualizing daily click statistics. **Only call this if the user explicitly requests a chart or visualization.** Returns a shortened URL to the chart image.",
  {
    dailyClicks: z
      .array(
        z.object({
          date: z.string().describe("Date in format YYYY-MM-DD or MM/DD"),
          clicks: z.number().int().min(0).describe("Number of clicks"),
        }),
      )
      .describe("Array of daily click data"),
    encodeId: z
      .string()
      .optional()
      .describe("Link slug (used in chart title)"),
  },
  async ({ dailyClicks, encodeId }) => {
    try {
      if (dailyClicks.length === 0)
        throw new Error("dailyClicks array cannot be empty");
      const labels = dailyClicks.map((d) => d.date);
      const data = dailyClicks.map((d) => d.clicks);
      const chartConfig = {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Clicks",
              data,
              borderColor: "rgb(59,130,246)",
              backgroundColor: "rgba(59,130,246,0.1)",
              fill: true,
            },
          ],
        },
        options: {
          title: {
            display: !!encodeId,
            text: encodeId ? `Daily Clicks: ${encodeId}` : "",
          },
          scales: {
            yAxes: [{ ticks: { beginAtZero: true } }],
          },
        },
      };
      const chartUrl = `https://quickchart.io/chart?w=600&h=300&c=${encodeURIComponent(JSON.stringify(chartConfig))}`;
      
      // Shorten the long chart URL using unauthenticated mode (no quota consumed)
      let shortChartUrl = chartUrl;
      try {
        const shortenResult = await api.shortenUnauth({ url: chartUrl });
        shortChartUrl = shortenResult.data?.picseeUrl || chartUrl;
      } catch (shortenError: any) {
        // If shortening fails, fall back to original URL
        console.error("Failed to shorten chart URL:", shortenError.message);
      }
      
      return ok({
        success: true,
        chartUrl: shortChartUrl,
        originalChartUrl: chartUrl,
        dataPoints: dailyClicks.length,
        note: shortChartUrl !== chartUrl 
          ? "Chart URL automatically shortened via PicSee (unauthenticated, no quota used)"
          : "Chart URL (shortening unavailable)",
      });
    } catch (e: any) {
      return err(`Chart generation failed: ${e.message}`);
    }
  },
);

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((e) => {
  console.error("Fatal:", e);
  process.exit(1);
});
