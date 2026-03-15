#!/usr/bin/env node

const https = require('https');

const API_KEY = process.env.WERYAI_API_KEY;

if (!API_KEY) {
  console.error("Error: WERYAI_API_KEY is not set.");
  process.exit(1);
}

const prompt = process.argv.slice(2).join(' ');
if (!prompt) {
  console.error("Please provide a prompt. Usage: node weryai-video.js <prompt>");
  process.exit(1);
}

const MODEL = "WERYAI_VIDEO_1_0";

async function request(url, options, body = null, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await new Promise((resolve, reject) => {
        const req = require('https').request(url, options, (res) => {
          let data = '';
          res.on('data', chunk => data += chunk);
          res.on('end', () => {
            try { resolve(JSON.parse(data)); } catch (e) { resolve(data); }
          });
        });
        req.on('error', reject);
        req.setTimeout(30000, () => req.destroy(new Error('Request timeout')));
        if (body) req.write(JSON.stringify(body));
        req.end();
      });
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(res => setTimeout(res, 2000 * (i + 1)));
    }
  }
}

async function generateVideo() {
  console.log(`Submitting video task for prompt: "${prompt}"...`);
  
  const submitRes = await request('https://api.weryai.com/growthai/v1/generation/text-to-video', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': API_KEY
    }
  }, {
    model: MODEL,
    prompt: prompt,
    aspect_ratio: '16:9',
    resolution: '720p',
    duration: 5,
    generate_audio: false
  });

  if (!submitRes.success && !submitRes.data) {
    console.error("Video task submission failed:", submitRes);
    process.exit(1);
  }

  const taskId = submitRes.data ? submitRes.data.task_id : submitRes.task_id;
  console.log(`Task submitted successfully. Task ID: ${taskId}`);

  while (true) {
    await new Promise(r => setTimeout(r, 5000));
    
    const statusRes = await request(`https://api.weryai.com/growthai/v1/generation/${taskId}/status`, {
      method: 'GET',
      headers: {
        'x-api-key': API_KEY
      }
    });

    const status = statusRes.data ? statusRes.data.task_status : statusRes.task_status;
    if (status === 'succeed') {
      console.log(`\nSuccess! Video URL:`);
      const vids = statusRes.data ? statusRes.data.videos : statusRes.videos;
      if (vids && vids.length > 0) {
        console.log(vids[0]);
      } else {
        console.log("No video URL found in response:", JSON.stringify(statusRes));
      }
      break;
    } else if (status === 'fail' || status === 'failed') {
      console.error("\nTask failed:", JSON.stringify(statusRes));
      process.exit(1);
    } else {
      process.stdout.write(".");
    }
  }
}

generateVideo();
