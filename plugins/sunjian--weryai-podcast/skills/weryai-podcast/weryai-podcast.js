#!/usr/bin/env node

const https = require('https');

const API_KEY = process.env.WERYAI_API_KEY;

if (!API_KEY) {
  console.error("Error: WERYAI_API_KEY is not set.");
  process.exit(1);
}

const query = process.argv.slice(2).join(' ');
if (!query) {
  console.error("Please provide a topic. Usage: node weryai-podcast.js <topic>");
  process.exit(1);
}

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

async function generatePodcast() {
  console.log(`Submitting podcast text task for topic: "${query}"...`);
  
  const submitRes = await request('https://api.weryai.com/growthai/v1/generation/podcast/generate/text', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': API_KEY
    }
  }, {
    query: query,
    speakers: ["travel-girl-english", "leo-9328b6d2"],
    language: "en",
    mode: "quick"
  });

  if (!submitRes.success && !submitRes.data) {
    console.error("Text task submission failed:", submitRes);
    process.exit(1);
  }

  const taskId = submitRes.data ? submitRes.data.task_id : submitRes.task_id;
  console.log(`Task submitted successfully. Task ID: ${taskId}`);
  console.log(`Phase 1: Generating script...`);

  // Poll for text generation
  while (true) {
    await new Promise(r => setTimeout(r, 5000));
    const statusRes = await request(`https://api.weryai.com/growthai/v1/generation/${taskId}/status`, {
      method: 'GET',
      headers: { 'x-api-key': API_KEY }
    });

    const cStatus = statusRes.data ? statusRes.data.content_status : statusRes.content_status;
    if (cStatus === 'text-success') {
      console.log(`\nScript generation successful! Moving to Phase 2: Generating audio...`);
      break;
    } else if (cStatus === 'text-fail') {
      console.error("\nText generation failed:", JSON.stringify(statusRes));
      process.exit(1);
    } else {
      process.stdout.write(".");
    }
  }

  // Trigger Audio generation
  const audioSubmitRes = await request(`https://api.weryai.com/growthai/v1/generation/podcast/generate/${taskId}/audio`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': API_KEY
    }
  }, {});
  
  if (!audioSubmitRes.success && !audioSubmitRes.data) {
    console.error("Audio generation trigger failed:", audioSubmitRes);
    process.exit(1);
  }

  // Poll for audio generation
  while (true) {
    await new Promise(r => setTimeout(r, 5000));
    const statusRes = await request(`https://api.weryai.com/growthai/v1/generation/${taskId}/status`, {
      method: 'GET',
      headers: { 'x-api-key': API_KEY }
    });

    const cStatus = statusRes.data ? statusRes.data.content_status : statusRes.content_status;
    if (cStatus === 'audio-success') {
      console.log(`\nAudio generation successful!`);
      console.log(JSON.stringify(statusRes.data || statusRes, null, 2));
      // Extract URL depending on where it's found (maybe in audio_url, audios, or videos array)
      const data = statusRes.data || statusRes;
      const audioUrl = data.audio_url || data.audios?.[0] || data.podcast_audio_url || (data.videos && data.videos[0]);
      if (audioUrl) {
        console.log(`\nAudio URL: ${audioUrl}`);
      }
      break;
    } else if (cStatus === 'audio-fail') {
      console.error("\nAudio generation failed:", JSON.stringify(statusRes));
      process.exit(1);
    } else {
      process.stdout.write(".");
    }
  }
}

generatePodcast();
