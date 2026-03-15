#!/usr/bin/env node
/**
 * Cognitive Brain - Embedding 预热脚本
 * 在启动时加载模型，避免首次检索慢
 */

const { execSync, spawn } = require('child_process');
const path = require('path');

const EMBED_SCRIPT = path.join(__dirname, 'embed.py');

async function warmup() {
  console.log('🔥 预热 Embedding 模型...');
  
  const start = Date.now();
  
  try {
    const result = execSync(`python3 "${EMBED_SCRIPT}" --warmup`, {
      encoding: 'utf8',
      timeout: 60000,
      stdio: ['pipe', 'pipe', 'pipe'] // 捕获 stderr
    });
    
    const data = JSON.parse(result);
    const elapsed = data.elapsed_seconds || ((Date.now() - start) / 1000);
    
    console.log(`✅ 模型预热完成 (${elapsed.toFixed(2)}s)`);
    return true;
    
  } catch (e) {
    // 解析输出（可能在 stderr）
    const output = e.stdout || e.stderr || '';
    
    if (output.includes('warmed_up') || output.includes('ready')) {
      const elapsed = (Date.now() - start) / 1000;
      console.log(`✅ 模型预热完成 (${elapsed.toFixed(2)}s)`);
      return true;
    }
    
    console.log('⚠️  模型预热失败:', e.message);
    console.log('   提示: 请确保已安装 sentence-transformers');
    console.log('   运行: pip3 install sentence-transformers --break-system-packages');
    return false;
  }
}

/**
 * 启动 Embedding 服务（长期运行的进程）
 * 返回一个可以向其发送请求的进程
 */
function startEmbeddingService() {
  console.log('🚀 启动 Embedding 服务...');
  
  const proc = spawn('python3', [EMBED_SCRIPT, '--serve'], {
    stdio: ['pipe', 'pipe', 'pipe']
  });
  
  let ready = false;
  
  proc.stderr.on('data', (data) => {
    const msg = data.toString();
    if (msg.includes('"status": "ready"')) {
      ready = true;
      console.log('✅ Embedding 服务已就绪');
    }
  });
  
  proc.on('error', (err) => {
    console.error('Embedding 服务错误:', err);
  });
  
  proc.on('exit', (code) => {
    if (code !== 0 && code !== null) {
      console.log(`Embedding 服务退出 (code ${code})`);
    }
  });
  
  return {
    process: proc,
    isReady: () => ready,
    
    async embed(text) {
      return new Promise((resolve, reject) => {
        if (!ready) {
          reject(new Error('服务未就绪'));
          return;
        }
        
        let response = '';
        
        const onData = (data) => {
          response += data.toString();
          
          if (response.includes('\n')) {
            proc.stdout.off('data', onData);
            try {
              const result = JSON.parse(response.trim());
              resolve(result);
            } catch (e) {
              reject(e);
            }
          }
        };
        
        proc.stdout.on('data', onData);
        proc.stdin.write(JSON.stringify({ text }) + '\n');
        
        // 超时
        setTimeout(() => {
          proc.stdout.off('data', onData);
          reject(new Error('超时'));
        }, 10000);
      });
    },
    
    stop() {
      proc.kill();
    }
  };
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const action = args[0] || 'warmup';
  
  switch (action) {
    case 'warmup':
      const ok = await warmup();
      process.exit(ok ? 0 : 1);
      break;
      
    case 'serve':
      // 启动长期服务
      const service = startEmbeddingService();
      
      // 保持运行
      process.on('SIGINT', () => {
        console.log('\n停止服务...');
        service.stop();
        process.exit(0);
      });
      
      // 等待服务就绪后保持运行
      const checkReady = setInterval(() => {
        if (service.isReady()) {
          clearInterval(checkReady);
          console.log('Embedding 服务运行中 (Ctrl+C 停止)');
        }
      }, 100);
      break;
      
    default:
      console.log(`
Embedding 预热脚本

用法:
  node warmup_embedding.cjs warmup  # 预热模型（一次性）
  node warmup_embedding.cjs serve   # 启动长期服务
      `);
  }
}

main();
