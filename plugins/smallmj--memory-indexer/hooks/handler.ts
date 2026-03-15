import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

const handler = async (event: any) => {
  // Only trigger on 'new' command
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  console.log("[memory-indexer-on-new] 正在搜索相关记忆...");

  try {
    // 搜索与用户相关的记忆
    const { stdout, stderr } = await execAsync(
      "cd ~/.openclaw/workspace && uv run python skills/memory-indexer/memory-indexer.py search '何协 偏好 项目 任务'",
      { timeout: 30000 }
    );

    if (stdout && stdout.trim()) {
      console.log("[memory-indexer-on-new] 搜索结果:", stdout.trim());
      // 将结果添加到消息中（可选）
      // event.messages.push(`🔍 找到相关记忆: ${stdout.trim().substring(0, 200)}`);
    } else {
      console.log("[memory-indexer-on-new] 未找到相关记忆");
    }

    if (stderr) {
      console.error("[memory-indexer-on-new] 搜索错误:", stderr);
    }
  } catch (err: any) {
    console.error("[memory-indexer-on-new] 执行失败:", err.message);
  }
};

export default handler;
