---
name: weryai-podcast
description: "Generate an AI podcast discussion or broadcast audio using the WeryAI Podcast Generation API. Use when the user asks to generate a podcast or audio discussion on a topic."
homepage: https://weryai.com
---

# 🎙️ WeryAI Podcast Generation

Welcome to the **WeryAI Podcast Gen** skill! This skill empowers your OpenClaw agent to instantly create high-quality media using the [WeryAI Platform](https://weryai.com).

## 🚀 Quick Setup (Onboarding)

To use this skill, you need a **WeryAI API Key**. Follow these simple steps to get started:

1. **Get your API Key:**
   - Go to [WeryAI](https://weryai.com) and sign up for an account.
   - Navigate to the **Developer / API Keys** section in your dashboard.
   - Click **"Create New Secret Key"** and copy the key (it usually starts with `sk-`).

2. **Configure OpenClaw:**
   - The safest way to configure this in OpenClaw is to set it as an environment variable in your Gateway or OS environment:
     ```bash
     export WERYAI_API_KEY="sk-your-api-key-here"
     ```
   - When launching your agent, ensure this environment variable is passed down to the OpenClaw process.

*(Note: During installation, OpenClaw will also prompt you to enter the `WERYAI_API_KEY` if it detects this skill).*

## 🤖 How the Agent Uses It

When a user asks for media generation, the agent will automatically execute the included script:

```bash
node ./weryai-podcast.js "The future of artificial intelligence and robotics in everyday life"
```

- The script automatically handles the WeryAI API request and complex authentication headers.
- It polls the WeryAI servers asynchronously until the task is fully generated.
- It returns the final podcast `.mp3` or `.wav` audio URL.

## ⚠️ Troubleshooting & Limits
- **API Key Missing:** The script will fail immediately and print an error if `WERYAI_API_KEY` is not found.
- **Timeouts & Network:** Generation can take anywhere from 10 seconds to several minutes depending on the task type (podcasts and videos take longer). The script includes automatic retries (exponential backoff) for network stability, so please be patient!
