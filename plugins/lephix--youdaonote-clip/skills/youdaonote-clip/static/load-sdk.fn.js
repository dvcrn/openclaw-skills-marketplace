/**
 * load-sdk.fn.js — 从 CDN 加载 collect-window.js
 *
 * 优化：41KB 命令行参数 → ~700 bytes
 * CDN: https://cdn.jsdelivr.net/gh/FuDesign2008/open-js@v1.0.0/collect-window.js
 */
async () => {
  const SCRIPT_URL = 'https://cdn.jsdelivr.net/gh/FuDesign2008/open-js@v1.0.0/collect-window.js';
  const LOAD_TIMEOUT_MS = 10000;
  const MOUNT_TIMEOUT_MS = 8000;

  // 已加载则跳过
  if (typeof window.collectParser !== 'undefined') {
    return;
  }

  // 从 CDN 加载脚本
  const s = document.createElement('script');
  s.src = SCRIPT_URL;
  s.crossOrigin = 'anonymous';
  document.head.appendChild(s);

  // 等待脚本加载完成
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('脚本加载超时')), LOAD_TIMEOUT_MS);
    s.onload = () => { clearTimeout(timer); resolve(); };
    s.onerror = () => { clearTimeout(timer); reject(new Error('脚本加载失败')); };
  });

  // 等待 SDK 挂载
  const startTime = Date.now();
  while (typeof window.collectParser === 'undefined') {
    if (Date.now() - startTime > MOUNT_TIMEOUT_MS) {
      throw new Error('SDK 挂载超时');
    }
    await new Promise(r => setTimeout(r, 50));
  }
}
