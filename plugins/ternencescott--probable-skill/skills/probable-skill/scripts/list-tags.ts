// ========================
// 获取事件标签
// ========================
// 用法: bun run scripts/list-tags.ts <event_id> [--json]
// getEventTags 获取指定事件的标签，不是所有标签

import { getPublicClobClient, jsonStringify } from "./config";

const USAGE = `用法: bun run scripts/list-tags.ts <event_id> [--json]

示例:
  bun run scripts/list-tags.ts 752
  bun run scripts/list-tags.ts 752 --json`;

async function listTags(eventId: string, jsonMode: boolean) {
  const client = getPublicClobClient();
  const result = await client.getEventTags({ id: eventId });

  if (jsonMode) {
    console.log(jsonStringify(result));
    return;
  }

  const tags = Array.isArray(result) ? result : (result as any)?.tags ?? [];
  if (!tags.length) {
    console.log(`事件 ${eventId} 未找到标签`);
    return;
  }

  console.log(`事件 ${eventId} 的标签 (共 ${tags.length} 个)\n`);

  for (const tag of tags) {
    const label = tag.label ?? tag.name ?? "N/A";
    const slug = tag.slug ?? "N/A";
    const id = tag.id ?? "N/A";
    console.log(`  ${label}`);
    console.log(`    Slug: ${slug}  |  ID: ${id}`);
  }
  console.log();
}

function main() {
  const args = process.argv.slice(2);

  if (args.includes("--help") || args.includes("-h")) {
    console.log(USAGE);
    return;
  }

  const jsonMode = args.includes("--json");
  const eventId = args.find((a) => !a.startsWith("--"));

  if (!eventId) {
    console.error("错误: 请提供事件 ID");
    console.log(USAGE);
    process.exit(1);
  }

  return listTags(eventId, jsonMode);
}

main()?.catch(console.error);
