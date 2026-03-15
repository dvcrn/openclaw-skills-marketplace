#!/usr/bin/env node

const https = require('https');

// Fallback to env variable if config file isn't set up yet
let API_KEY = process.env.WERYAI_API_KEY || '';

// Try reading from openclaw.json config if API_KEY is empty
if (!API_KEY) {
  try {
    const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      if (config.weryai && config.weryai.apiKey) {
        API_KEY = config.weryai.apiKey;
      }
    }
  } catch (e) {
    // Ignore read errors
  }
}

if (!API_KEY) {
  console.error("Error: WERYAI_API_KEY is not set. Please set it in your environment or openclaw.json.");
  process.exit(1);
}

// Ensure the prompt is provided
const prompt = process.argv.slice(2).join(' ');
if (!prompt) {
  console.error("Please provide a prompt. Usage: node weryai-generate.js <prompt>");
  process.exit(1);
}

const MODEL = "WERYAI_IMAGE_2_0";

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

async function generateImage() {
  console.log(`Submitting task for prompt: "${prompt}"...`);
  
  const submitRes = await request('https://api.weryai.com/growthai/v1/generation/text-to-image', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': API_KEY
    }
  }, {
    model: MODEL,
    prompt: prompt,
    aspect_ratio: '1:1'
  });

  if (!submitRes.success) {
    console.error("Task submission failed:", submitRes);
    process.exit(1);
  }

  const taskId = submitRes.data.task_id;
  console.log(`Task submitted successfully. Task ID: ${taskId}`);

  while (true) {
    // Wait 3 seconds between polls
    await new Promise(r => setTimeout(r, 3000));
    
    const statusRes = await request(`https://api.weryai.com/growthai/v1/generation/${taskId}/status`, {
      method: 'GET',
      headers: {
        'x-api-key': API_KEY
      }
    });

    if (!statusRes.success) {
      console.error("Task status check failed:", statusRes);
      process.exit(1);
    }

    const status = statusRes.data.task_status;
    if (status === 'succeed') {
      console.log(`\nSuccess! Image URL:`);
      console.log(statusRes.data.images[0]);
      break;
    } else if (status === 'fail' || status === 'failed') {
      console.error("\nTask failed.");
      process.exit(1);
    } else {
      process.stdout.write(".");
    }
  }
}

generateImage();
