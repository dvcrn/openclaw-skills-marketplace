const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec, spawn, execSync } = require('child_process');
const formidable = require('formidable');
const readline = require('readline');

// 配置路径
const SKILL_DIR = __dirname;
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');
const AUDIO_CONFIG_PATH = path.join(SKILL_DIR, 'audio_config.json');
const VENV_PATH = path.join(SKILL_DIR, 'venv');
const INSTALL_SCRIPT = path.join(SKILL_DIR, 'install.sh');

// 检查配置是否完整
function checkConfigStatus() {
  const issues = [];
  
  // 检查 audio_config.json
  if (!fs.existsSync(AUDIO_CONFIG_PATH)) {
    issues.push('缺少 audio_config.json 配置文件');
  } else {
    try {
      const audioConfig = JSON.parse(fs.readFileSync(AUDIO_CONFIG_PATH, 'utf8'));
      if (!audioConfig.qwen3_asr_ov?.model) {
        issues.push('audio_config.json 中未配置模型路径');
      } else if (!fs.existsSync(audioConfig.qwen3_asr_ov.model)) {
        issues.push(`模型路径不存在：${audioConfig.qwen3_asr_ov.model}`);
      }
    } catch (e) {
      issues.push('audio_config.json 格式错误');
    }
  }
  
  // 检查 Python 虚拟环境
  if (!fs.existsSync(VENV_PATH)) {
    issues.push('缺少 Python 虚拟环境 (venv/)');
  } else {
    const pipPath = path.join(VENV_PATH, 'bin', 'pip');
    if (!fs.existsSync(pipPath)) {
      issues.push('Python 虚拟环境不完整');
    }
  }
  
  // 检查 xdp-audio-service 是否安装
  const venvPip = path.join(VENV_PATH, 'bin', 'pip');
  if (fs.existsSync(venvPip)) {
    try {
      const result = execSync(`${venvPip} show xdp-audio-service`, { encoding: 'utf8' });
      if (!result) {
        issues.push('未安装 xdp-audio-service');
      }
    } catch (e) {
      issues.push('未安装 xdp-audio-service');
    }
  }
  
  return issues;
}

// 交互式询问用户
function askUser(question) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim().toLowerCase());
    });
  });
}

// 运行安装脚本
async function runInstallScript() {
  console.log('\n[ASR] 开始运行安装脚本...\n');
  
  return new Promise((resolve, reject) => {
    const install = spawn('bash', [INSTALL_SCRIPT], {
      stdio: 'inherit',
      cwd: SKILL_DIR
    });
    
    install.on('close', (code) => {
      if (code === 0) {
        console.log('\n[ASR] 安装完成！请重启服务。\n');
        resolve(true);
      } else {
        reject(new Error(`安装脚本退出码：${code}`));
      }
    });
    
    install.on('error', (err) => {
      reject(err);
    });
  });
}

// 初始化检查
async function initializeAndCheck() {
  console.log('[ASR] 检查配置状态...');
  
  const issues = checkConfigStatus();
  
  if (issues.length > 0) {
    console.log('\n⚠️  检测到配置不完整：');
    issues.forEach(issue => console.log(`   - ${issue}`));
    console.log('\n需要运行 install.sh 进行初始化配置。\n');
    
    // 询问用户是否现在运行安装
    const answer = await askUser('是否现在运行安装脚本？(y/N): ');
    
    if (answer === 'y' || answer === 'yes') {
      try {
        await runInstallScript();
        // 安装完成后重新加载配置
        return true;
      } catch (err) {
        console.error('[ASR] 安装失败:', err.message);
        console.log('[ASR] 请手动运行：bash install.sh\n');
        return false;
      }
    } else {
      console.log('\n[ASR] 已跳过安装。请先运行 install.sh 再启动服务。\n');
      console.log('命令：cd /root/upstream/xeon_asr && bash install.sh\n');
      return false;
    }
  }
  
  console.log('[ASR] 配置检查通过 ✓\n');
  return true;
}

// 加载配置
let config = { port: 9001, flaskAsrUrl: 'http://127.0.0.1:5000/transcribe' };
if (fs.existsSync(CONFIG_PATH)) {
  config = { ...config, ...require(CONFIG_PATH) };
}

const PORT = config.port || 9001;
const FLASK_URL = config.flaskAsrUrl || 'http://127.0.0.1:5000/transcribe';

// 临时文件目录
const TEMP_DIR = path.join(__dirname, 'temp');
if (!fs.existsSync(TEMP_DIR)) {
  fs.mkdirSync(TEMP_DIR, { recursive: true });
}

const server = http.createServer(async (req, res) => {
  console.log(`[ASR] 收到请求：${req.method} ${req.url}`);
  
  // 健康检查
  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', port: PORT }));
    return;
  }
  
  // OpenAI 兼容接口 - 用于 qqbot STT
  if (req.method === 'POST' && req.url === '/audio/transcriptions') {
    const form = new formidable.IncomingForm({ uploadDir: TEMP_DIR, keepExtensions: true });
    
    form.parse(req, async (err, fields, files) => {
      if (err) {
        console.error('[ASR] Form 解析失败:', err);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: err.message }));
        return;
      }
      
      const audioFile = files.file?.[0]?.filepath || files.file?.filepath;
      if (!audioFile) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'No audio file provided' }));
        return;
      }
      
      try {
        console.log(`[ASR] 收到音频文件：${audioFile}`);
        
        // 获取模型名称（从请求字段或配置）
        const modelName = fields.model?.[0] || fields.model || config.modelName;
        console.log(`[ASR] 使用模型：${modelName || 'default'}`);
        
        // 调用 Flask ASR 服务
        const text = await callFlaskAsr(audioFile, modelName);
        console.log(`[ASR] 转写结果：${text}`);
        
        // 清理临时文件
        try { fs.unlinkSync(audioFile); } catch (e) {}
        
        // 返回 OpenAI 兼容格式
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ text }));
      } catch (err) {
        console.error('[ASR] 错误:', err);
        try { fs.unlinkSync(audioFile); } catch (e) {}
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }
  
  // 转写接口（原始接口）
  if (req.method === 'POST' && req.url === '/transcribe') {
    const contentType = req.headers['content-type'] || '';
    const messageId = req.headers['x-message-id'] || '';
    const senderId = req.headers['x-sender-id'] || '';
    
    let chunks = [];
    req.on('data', chunk => chunks.push(chunk));
    req.on('end', async () => {
      const audioBuffer = Buffer.concat(chunks);
      const ext = getAudioExtension(contentType);
      const tempFile = path.join(TEMP_DIR, `audio_${Date.now()}${ext}`);
      
      try {
        // 保存临时文件
        fs.writeFileSync(tempFile, audioBuffer);
        console.log(`[ASR] 音频已保存：${tempFile}`);
        
        // 调用 Flask ASR 服务
        const text = await callFlaskAsr(tempFile);
        console.log(`[ASR] 转写结果：${text}`);
        
        // 清理临时文件
        fs.unlinkSync(tempFile);
        
        // 将结果发送给 OpenClaw
        if (text && text.trim()) {
          await sendToOpenClaw(text, messageId, senderId);
        }
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          success: true, 
          text,
          messageId,
          senderId
        }));
      } catch (err) {
        console.error('[ASR] 错误:', err);
        if (fs.existsSync(tempFile)) {
          fs.unlinkSync(tempFile);
        }
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          success: false, 
          error: err.message 
        }));
      }
    });
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

// 根据 Content-Type 获取文件扩展名
function getAudioExtension(contentType) {
  const extMap = {
    'audio/x-silk': '.silk',
    'audio/x-slk': '.slk',
    'audio/amr': '.amr',
    'audio/wav': '.wav',
    'audio/x-wav': '.wav',
    'audio/mpeg': '.mp3',
    'audio/ogg': '.ogg',
    'audio/pcm': '.pcm',
    'audio/x-pcm': '.pcm',
  };
  
  for (const [type, ext] of Object.entries(extMap)) {
    if (contentType.includes(type)) {
      return ext;
    }
  }
  return '.wav';
}

// 调用 Flask ASR 服务
function callFlaskAsr(audioFile, modelName) {
  const model = modelName || config.modelName || 'whisper-1';
  return new Promise((resolve, reject) => {
    const curl = `curl -X POST -F "file=@${audioFile}" -F "model=${model}" "${FLASK_URL}"`;
    console.log(`[ASR] 调用 Flask: ${curl} (model=${model})`);
    
    exec(curl, { timeout: 30000 }, (err, stdout, stderr) => {
      if (err) {
        console.error('[ASR] Flask 调用失败:', stderr);
        reject(new Error(`Flask ASR 服务错误：${stderr || err.message}`));
        return;
      }
      
      try {
        const result = JSON.parse(stdout);
        const text = result.text || result.transcription || result.result || stdout;
        resolve(text.trim());
      } catch (e) {
        resolve(stdout.trim());
      }
    });
  });
}

// 发送结果到 OpenClaw
function sendToOpenClaw(text, messageId, senderId) {
  return new Promise((resolve) => {
    const output = {
      type: 'asr_result',
      text,
      messageId,
      senderId,
      timestamp: Date.now()
    };
    
    console.log('[ASR] 转写结果 ready:', JSON.stringify(output));
    
    const resultFile = path.join(TEMP_DIR, `result_${Date.now()}.json`);
    fs.writeFileSync(resultFile, JSON.stringify(output, null, 2));
    console.log(`[ASR] 结果已写入：${resultFile}`);
    
    resolve(output);
  });
}

// 启动服务器
async function startServer() {
  // 先进行初始化检查
  const configOk = await initializeAndCheck();
  
  if (!configOk) {
    console.log('[ASR] 由于配置不完整，服务将以健康检查模式运行。');
    console.log('[ASR] 请先运行 install.sh 完成配置。\n');
  }
  
  server.listen(PORT, '0.0.0.0', () => {
    console.log('========================================');
    console.log('[ASR] 语音转文字服务已启动');
    console.log(`[ASR] 监听端口：${PORT}`);
    console.log(`[ASR] Flask ASR 地址：${FLASK_URL}`);
    console.log(`[ASR] 健康检查：http://localhost:${PORT}/health`);
    console.log(`[ASR] 转写接口：POST http://localhost:${PORT}/transcribe`);
    if (!configOk) {
      console.log('[ASR] ⚠️  配置不完整，请先运行 install.sh');
    }
    console.log('========================================');
  });
}

startServer();

process.on('SIGINT', () => {
  console.log('\n[ASR] 正在关闭服务...');
  if (fs.existsSync(TEMP_DIR)) {
    const files = fs.readdirSync(TEMP_DIR);
    files.forEach(file => {
      const filePath = path.join(TEMP_DIR, file);
      try { fs.unlinkSync(filePath); } catch (e) {}
    });
  }
  server.close(() => {
    console.log('[ASR] 服务已关闭');
    process.exit(0);
  });
});
