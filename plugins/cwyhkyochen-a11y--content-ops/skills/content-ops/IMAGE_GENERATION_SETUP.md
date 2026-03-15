# 配图生成初始化指南

> 教其他 Agent 如何配置和使用图片生成功能

---

## 快速决策

| 场景 | 推荐方案 | 配置时间 |
|------|---------|---------|
| 有 OpenAI API Key | **DALL-E 3** | 2分钟 |
| 有本地 GPU | **Stable Diffusion** | 30分钟 |
| 无 API/无 GPU | **从语料下载原图** | 即时（需版权确认） |

---

## 方案1: DALL-E 3 (推荐)

### Step 1: 获取 API Key

```bash
# 方式A: 环境变量（推荐）
export OPENAI_API_KEY="sk-..."

# 方式B: 配置文件
echo '{"openai_api_key": "sk-..."}' > ~/.openclaw/workspace/content-ops-workspace/config/secrets.json
```

### Step 2: 安装依赖

```bash
cd ~/.openclaw/workspace/skills/content-ops
npm install openai
```

### Step 3: 测试生成

```typescript
// scripts/test-image-generation.ts
import OpenAI from 'openai';
import fs from 'fs';
import path from 'path';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

async function testGenerate() {
  const response = await openai.images.generate({
    model: "dall-e-3",
    prompt: "A minimalist spring outfit flat lay, beige trench coat with white sneakers and light blue jeans, natural lighting, clean background, fashion photography style",
    size: "1024x1024",
    quality: "standard",
    n: 1,
  });

  // 下载图片
  const imageUrl = response.data[0].url;
  const imageResponse = await fetch(imageUrl);
  const buffer = await imageResponse.arrayBuffer();
  
  const outputPath = path.join(
    process.env.HOME || '/home/admin',
    '.openclaw/workspace/content-ops-workspace/corpus/published/test-image.png'
  );
  
  fs.writeFileSync(outputPath, Buffer.from(buffer));
  console.log('Image saved to:', outputPath);
}

testGenerate();
```

```bash
npx ts-node scripts/test-image-generation.ts
```

### Step 4: 配置 pricing（成本控制）

```typescript
// src/config/image-gen.ts
export const imageGenConfig = {
  provider: 'openai',
  model: 'dall-e-3',
  
  // 成本限制
  dailyBudget: 5.0,        // 每日最多 $5
  maxImagesPerDay: 50,     // 每日最多 50 张
  
  // 尺寸配置
  defaultSize: '1024x1024', // $0.04/张
  // options: '1024x1024' | '1024x1792' | '1792x1024'
  
  // 质量配置
  defaultQuality: 'standard', // $0.04/张
  // options: 'standard' | 'hd' ($0.08/张)
  
  // 保存路径
  outputDir: '~/.openclaw/workspace/content-ops-workspace/corpus/published'
};
```

---

## 方案2: 本地 Stable Diffusion

### Step 1: 部署 SD WebUI

```bash
# 需要 NVIDIA GPU (VRAM >= 8GB)
# 或使用 RunPod/AutoDL 等云服务

git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui

# 启动 with API
./webui.sh --api --listen
```

### Step 2: 配置连接

```typescript
// src/config/image-gen.ts
export const imageGenConfig = {
  provider: 'stable-diffusion',
  apiUrl: 'http://localhost:7860',  // 或远程地址
  
  // 模型配置
  checkpoint: 'realisticVisionV51_v51VAE.safetensors',
  steps: 30,
  cfgScale: 7,
  sampler: 'DPM++ 2M Karras',
  
  // 尺寸
  width: 512,
  height: 768,
  
  // 保存路径
  outputDir: '~/.openclaw/workspace/content-ops-workspace/corpus/published'
};
```

### Step 3: 测试 API

```bash
curl -X POST http://localhost:7860/sdapi/v1/txt2img \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "spring outfit, minimalist style, natural lighting",
    "steps": 30,
    "width": 512,
    "height": 768
  }'
```

---

## 方案3: 从语料下载原图

### 适用场景
- 无 API Key
- 成本敏感
- 需要真实用户生成内容(UGC)风格

### ⚠️ 版权风险

```typescript
// 使用前必须确认
interface CopyrightCheck {
  // 1. 检查平台协议
  platformAllows: boolean;  // 小红书允许下载吗？
  
  // 2. 检查作者声明
  authorAllows: boolean;    // 作者允许转载吗？
  
  // 3. 使用范围
  usageType: 'personal' | 'commercial' | 'transformative';
  
  // 4. 处理方式
  modification: 'none' | 'cropped' | 'edited' | 'referenced-only';
}
```

### 实现代码

```typescript
// scripts/download-corpus-images.ts
import fs from 'fs';
import path from 'path';
import fetch from 'node-fetch';

export async function downloadCorpusImages(
  corpusId: string,
  mediaUrls: string[]
): Promise<string[]> {
  const downloadDir = path.join(
    process.env.HOME || '/home/admin',
    '.openclaw/workspace/content-ops-workspace/corpus/downloaded',
    corpusId
  );
  
  if (!fs.existsSync(downloadDir)) {
    fs.mkdirSync(downloadDir, { recursive: true });
  }
  
  const localPaths: string[] = [];
  
  for (let i = 0; i < mediaUrls.length; i++) {
    const url = mediaUrls[i];
    const ext = path.extname(url) || '.jpg';
    const filename = `image-${i + 1}${ext}`;
    const filepath = path.join(downloadDir, filename);
    
    try {
      const response = await fetch(url);
      const buffer = await response.arrayBuffer();
      fs.writeFileSync(filepath, Buffer.from(buffer));
      localPaths.push(filepath);
    } catch (err) {
      console.error(`Failed to download ${url}:`, err);
    }
  }
  
  return localPaths;
}
```

---

## Agent 使用指南

### 生成配图的标准流程

```typescript
import { imageGenConfig } from '../config/image-gen.js';
import { generateImage } from '../utils/image-generator.js';

async function generateContentImages(
  contentTitle: string,
  contentBody: string,
  referenceImages?: string[]
) {
  // 1. 分析内容，确定需要的图片
  const imageNeeds = analyzeImageNeeds(contentTitle, contentBody);
  // 输出: [{ type: 'hero', description: '主图: 风衣穿搭全身照' }, ...]
  
  // 2. 生成 Prompt
  const prompts = imageNeeds.map(need => ({
    ...need,
    prompt: generateImagePrompt(need, referenceImages)
  }));
  
  // 3. 生成图片
  const generatedImages = [];
  for (const { type, prompt } of prompts) {
    const imagePath = await generateImage({
      prompt,
      size: imageGenConfig.defaultSize,
      quality: imageGenConfig.defaultQuality
    });
    generatedImages.push({ type, path: imagePath });
  }
  
  // 4. 保存到 publish_tasks.content.media
  return generatedImages;
}

// Prompt 生成示例
function generateImagePrompt(
  need: ImageNeed,
  references?: string[]
): string {
  const basePrompt = {
    'hero': 'A stylish fashion flat lay photograph',
    'detail': 'A close-up product photography',
    'comparison': 'A side-by-side comparison photo'
  }[need.type];
  
  const style = 'minimalist, natural lighting, clean background';
  const subject = need.description;
  
  return `${basePrompt}, ${subject}, ${style}, high quality, professional photography`;
}
```

### 成本预估

| 方案 | 单张成本 | 每日50张成本 | 备注 |
|------|---------|-------------|------|
| DALL-E 3 (1024x1024) | $0.04 | $2.00 | 推荐 |
| DALL-E 3 (HD) | $0.08 | $4.00 | 高质量需求 |
| Stable Diffusion (本地) | ~$0 | ~$0 | 需要GPU |
| Stable Diffusion (云端) | ~$0.02 | ~$1.00 | 按租用时间算 |

### 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| API Key 无效 | 额度用完/过期 | 检查 OpenAI 账单 |
| 生成内容被过滤 | 违反内容政策 | 修改 prompt，避免敏感词 |
| 图片质量差 | prompt 不够详细 | 添加 style, lighting, camera angle |
| 下载失败 | 原图链接过期 | 语料抓取时立即下载 |

---

## 配置检查清单

Agent 启动时自检：

```typescript
export async function checkImageGenSetup(): Promise<{
  ready: boolean;
  provider?: string;
  error?: string;
}> {
  // 1. 检查 API Key
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return { ready: false, error: '未配置 OPENAI_API_KEY' };
  }
  
  // 2. 测试连接
  try {
    const openai = new OpenAI({ apiKey });
    await openai.models.list();  // 轻量级测试
    return { ready: true, provider: 'openai' };
  } catch (err) {
    return { ready: false, error: `API 连接失败: ${err.message}` };
  }
}

// 用户询问时返回
/*
🖼️ 配图生成状态

提供商: OpenAI DALL-E 3
状态: ✅ 已配置
剩余额度: $45.32
今日已生成: 12/50 张

可用功能:
- 自动生成配图
- 根据语料生成风格一致图片
- 多版本对比

成本预估: 每篇内容 $0.12 (3张图)
*/
```
