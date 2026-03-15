import { writeFile } from "node:fs/promises";
import process from "node:process";

const DEFAULT_MODEL = "gpt-5-mini";
const API_BASE = process.env.CRAZYROUTER_BASE_URL || "https://crazyrouter.com/v1";

const POPULAR_MODELS: Record<string, string[]> = {
  "OpenAI": ["gpt-5", "gpt-5-mini", "gpt-4.1", "gpt-4.1-mini", "gpt-4o", "o3", "o4-mini"],
  "Anthropic": ["claude-opus-4-6", "claude-sonnet-4", "claude-haiku-3.5"],
  "Google": ["gemini-3-pro", "gemini-2.5-flash"],
  "DeepSeek": ["deepseek-r1", "deepseek-v3"],
  "Meta": ["llama-4-scout", "llama-4-maverick"],
  "Alibaba": ["qwen3-235b", "qwen3-32b"],
  "xAI": ["grok-4", "grok-3"],
  "Mistral": ["mistral-large", "codestral"],
};

interface CliArgs {
  prompt: string | null;
  model: string;
  system: string | null;
  temperature: number | null;
  maxTokens: number | null;
  output: string | null;
  listModels: boolean;
  json: boolean;
}

function parseArgs(argv: string[]): CliArgs {
  const args: CliArgs = {
    prompt: null,
    model: DEFAULT_MODEL,
    system: null,
    temperature: null,
    maxTokens: null,
    output: null,
    listModels: false,
    json: false,
  };

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    switch (arg) {
      case "--prompt": case "-p": args.prompt = argv[++i]; break;
      case "--model": case "-m": args.model = argv[++i]; break;
      case "--system": case "-s": args.system = argv[++i]; break;
      case "--temperature": case "-t": args.temperature = parseFloat(argv[++i]); break;
      case "--max-tokens": args.maxTokens = parseInt(argv[++i], 10); break;
      case "--output": case "-o": args.output = argv[++i]; break;
      case "--list-models": args.listModels = true; break;
      case "--json": args.json = true; break;
      case "--help": case "-h":
        console.log(`Usage: main.ts --prompt "..." [--model gpt-5-mini] [--system "..."] [--temperature 0.7] [--output file.md]
  --list-models  Show popular models
  --json         Raw JSON output
Env: CRAZYROUTER_API_KEY (required)`);
        process.exit(0);
    }
  }
  return args;
}

function getApiKey(): string {
  const key = process.env.CRAZYROUTER_API_KEY;
  if (!key) {
    console.error("Error: CRAZYROUTER_API_KEY not set. Get your key at https://crazyrouter.com");
    process.exit(1);
  }
  return key;
}

async function chat(args: CliArgs): Promise<void> {
  if (args.listModels) {
    console.log("Popular models on Crazyrouter (627+ total):\n");
    for (const [provider, models] of Object.entries(POPULAR_MODELS)) {
      console.log(`  ${provider}: ${models.join(", ")}`);
    }
    console.log("\nFull list: https://crazyrouter.com/models");
    return;
  }

  if (!args.prompt) {
    console.error("Error: --prompt is required");
    process.exit(1);
  }

  const apiKey = getApiKey();

  const messages: Array<{ role: string; content: string }> = [];
  if (args.system) {
    messages.push({ role: "system", content: args.system });
  }
  messages.push({ role: "user", content: args.prompt });

  const body: Record<string, unknown> = {
    model: args.model,
    messages,
  };

  if (args.temperature !== null) body.temperature = args.temperature;
  if (args.maxTokens !== null) body.max_tokens = args.maxTokens;

  console.error(`Model: ${args.model}`);

  const response = await fetch(`${API_BASE}/chat/completions`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`API Error (${response.status}): ${errorText}`);
    process.exit(1);
  }

  const result = await response.json() as {
    choices?: Array<{ message?: { content?: string } }>;
    usage?: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number };
    model?: string;
  };

  if (args.json) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  const content = result.choices?.[0]?.message?.content ?? "";
  const usage = result.usage;

  if (args.output) {
    await writeFile(args.output, content);
    console.error(`✅ Saved to ${args.output}`);
  } else {
    console.log(content);
  }

  if (usage) {
    console.error(`\n📊 ${result.model || args.model} | ${usage.prompt_tokens}→${usage.completion_tokens} (${usage.total_tokens} tokens)`);
  }
}

const args = parseArgs(process.argv);
chat(args).catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
