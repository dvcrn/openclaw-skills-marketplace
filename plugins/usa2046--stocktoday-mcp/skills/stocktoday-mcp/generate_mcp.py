#!/usr/bin/env python3
"""
从 ST_SERVER.py 自动生成 MCP Server
用法: python generate_mcp.py
"""

import re
import os

# 读取 ST_SERVER.py
server_file = os.path.join(os.path.dirname(__file__), "ST_SERVER.py")
with open(server_file, "r", encoding="utf-8") as f:
    content = f.read()

# 提取所有路由
route_pattern = r"@app.route\(['\"]([^'\"]+)['\"]"
routes = re.findall(route_pattern, content)

# 过滤出有效接口（排除重复和无效的）
valid_routes = []
seen = set()
for r in routes:
    if r not in seen and not r.startswith("/token") and not r.startswith("/register"):
        seen.add(r)
        valid_routes.append(r)

print(f"找到 {len(valid_routes)} 个有效接口")

# 生成 TypeScript MCP Server
ts_code = '''import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const TUSHARE_TOKEN = process.env.TUSHARE_TOKEN || process.env.STOCKTODAY_TOKEN || "citydata";
const BASE_URL = process.env.STOCKTODAY_URL || "https://tushare.citydata.club/";

const server = new Server(
  {
    name: "stocktoday-mcp",
    version: "1.0.0",
  },
  {
    capabilities: { tools: {} },
  }
);

async function callAPI(endpoint: string, params: Record<string, any> = {}): Promise<any> {
  const formData = new URLSearchParams();
  formData.append("TOKEN", TUSHARE_TOKEN);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") formData.append(k, String(v));
  }
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: "POST",
      body: formData,
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return await res.json();
  } catch (e: any) {
    return { error: e.message };
  }
}

// Tools
const tools = [
'''

# 添加所有工具
for route in valid_routes:
    tool_name = route.strip("/").replace("/", "_")
    # 简化名称
    tool_name = tool_name.replace("_", "_")
    
    ts_code += f'''  {{ name: "{tool_name}", description: "{route} API", 
    params: {{}} }},
'''

ts_code += '''];

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: tools.map(t => ({
    name: t.name,
    description: t.description,
    inputSchema: { type: "object", properties: {} },
  })),
}));

const endpointMap: Record<string, string> = {
'''

# 添加 endpoint 映射
for route in valid_routes:
    tool_name = route.strip("/").replace("/", "_")
    ts_code += f'  "{tool_name}": "{route}",\n'

ts_code += '''};

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const endpoint = endpointMap[name];
  if (!endpoint) return { content: [{ type: "text", text: JSON.stringify({ error: `Unknown: ${name}` })] };
  try {
    const params: Record<string, any> = {};
    for (const [k, v] of Object.entries(args || {})) {
      if (v !== undefined && v !== "" && v !== null) params[k] = v;
    }
    const result = await callAPI(endpoint, params);
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  } catch (e: any) {
    return { content: [{ type: "text", text: JSON.stringify({ error: e.message }) }] };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("StockToday MCP running");
}
main().catch(console.error);
'''

# 写入文件
output_file = os.path.join(os.path.dirname(__file__), "src", "index_generated.ts")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(ts_code)

print(f"已生成: {output_file}")
print(f"共 {len(valid_routes)} 个接口")
