#!/usr/bin/env node

import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const baseDir = path.resolve(__dirname, '..');

function parseArgs() {
  const args = process.argv.slice(2);
  let url = '';
  let output = process.cwd();
  let filename = '';
  let quality = 'best';

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('http')) {
      url = arg;
    } else if ((arg === '-o' || arg === '--output') && args[i + 1]) {
      output = args[++i];
    } else if ((arg === '-f' || arg === '--filename') && args[i + 1]) {
      filename = args[++i];
    } else if ((arg === '-q' || arg === '--quality') && args[i + 1]) {
      quality = args[++i];
    }
  }

  return { url, output, filename, quality };
}

async function download() {
  const { url, output, filename, quality } = parseArgs();

  if (!url) {
    console.error('Error: Please provide a Twitter/X URL');
    console.log('Usage: node download.mjs <twitter_url> [--output <dir>] [--filename <name>] [--quality <quality>]');
    process.exit(1);
  }

  // Validate URL
  if (!url.includes('twitter.com') && !url.includes('x.com')) {
    console.error('Error: Please provide a valid Twitter or X URL');
    process.exit(1);
  }

  // Ensure output directory exists
  if (!fs.existsSync(output)) {
    fs.mkdirSync(output, { recursive: true });
  }

  // Build yt-dlp command
  const outputTemplate = path.join(output, filename ? `${filename}.%(ext)s` : '%(title)s.%(ext)s');
  
  const ydlOpts = [
    '-f', `${quality}[ext=mp4]/best`,
    '--output', outputTemplate,
    '--no-warnings',
    '--socket-timeout', '30'
  ];

  // Add proxy if set
  const proxy = process.env.PROXY_URL;
  if (proxy) {
    ydlOpts.push('--proxy', proxy);
    console.log(`Using proxy: ${proxy}`);
  }

  console.log(`Downloading: ${url}`);
  console.log(`Output: ${output}`);

  return new Promise((resolve, reject) => {
    const ytDlp = spawn('yt-dlp', [...ydlOpts, url], {
      stdio: 'inherit',
      shell: true
    });

    ytDlp.on('close', (code) => {
      if (code === 0) {
        console.log('✅ Download complete!');
        
        // List downloaded files
        const files = fs.readdirSync(output);
        const videoFiles = files.filter(f => 
          f.endsWith('.mp4') || f.endsWith('.webm') || f.endsWith('.mkv')
        );
        
        if (videoFiles.length > 0) {
          const latestFile = videoFiles.sort((a, b) => {
            return fs.statSync(path.join(output, b)).mtime - fs.statSync(path.join(output, a)).mtime;
          })[0];
          
          console.log(`📁 Saved to: ${path.join(output, latestFile)}`);
        }
        
        resolve();
      } else {
        console.error(`❌ Download failed with code ${code}`);
        reject(new Error(`yt-dlp exited with code ${code}`));
      }
    });

    ytDlp.on('error', (err) => {
      console.error('❌ Error running yt-dlp:', err.message);
      console.log('\nMake sure yt-dlp is installed: pip install yt-dlp');
      reject(err);
    });
  });
}

download().catch(console.error);
