const WebSocket = require('ws');
let msgId = 1;
function sendCDP(ws, method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = msgId++;
    ws.send(JSON.stringify({ id, method, params }));
    const handler = (data) => {
      const msg = JSON.parse(data.toString());
      if (msg.id === id) { ws.removeListener('message', handler); resolve(msg.result); }
    };
    ws.on('message', handler);
    setTimeout(() => reject(new Error('timeout')), 30000);
  });
}
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
async function eval_(ws, expr) {
  const r = await sendCDP(ws, 'Runtime.evaluate', { expression: expr, awaitPromise: true });
  return r.result?.value;
}

// CDP로 키 하나하나 입력
async function typeText(ws, text) {
  for (const char of text) {
    await sendCDP(ws, 'Input.dispatchKeyEvent', {
      type: 'keyDown',
      text: char,
      unmodifiedText: char,
      key: char,
    });
    await sendCDP(ws, 'Input.dispatchKeyEvent', {
      type: 'keyUp',
      key: char,
    });
    await sleep(50);
  }
}

async function pressEnter(ws) {
  await sendCDP(ws, 'Input.dispatchKeyEvent', { type: 'rawKeyDown', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 });
  await sendCDP(ws, 'Input.dispatchKeyEvent', { type: 'keyUp', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 });
}

(async () => {
  const ws = new WebSocket('ws://127.0.0.1:18800/devtools/page/05A159BAC2A7FE7547F5DA23AC3FC655');
  await new Promise(r => ws.on('open', r));
  
  let url = await eval_(ws, 'location.href');
  console.log('현재:', url.slice(0, 60));
  
  // 비밀번호 입력 필드 포커스
  console.log('🔑 비밀번호 입력 (키보드)...');
  await eval_(ws, `
    const pwInput = document.querySelector('input[type="password"]');
    if (pwInput) pwInput.focus();
  `);
  await sleep(500);
  
  await typeText(ws, 'tames0210!');
  await sleep(500);
  
  // 다음 버튼 클릭
  console.log('  ➡️ 다음 클릭...');
  await eval_(ws, `
    const btns = document.querySelectorAll('button, div[role="button"]');
    for (const b of btns) {
      if (b.textContent?.includes('다음') || b.textContent?.includes('Next') || b.id?.includes('passwordNext')) {
        b.click();
        break;
      }
    }
  `);
  
  await sleep(10000);
  
  url = await eval_(ws, 'location.href');
  console.log('로그인 후 URL:', url.slice(0, 80));
  
  const bodyText = await eval_(ws, 'document.body?.innerText?.slice(0, 300)');
  console.log('페이지:', bodyText);
  
  // clawhub 도착 확인
  if (url.includes('clawhub')) {
    console.log('✅ clawhub 로그인 성공!');
  } else if (url.includes('github.com')) {
    // OAuth authorize 필요할 수 있음
    const hasAuthorize = await eval_(ws, `
      const btn = document.querySelector('button[name="authorize"]');
      if (btn) { btn.click(); return 'authorized'; }
      return 'no authorize btn';
    `);
    console.log('GitHub:', hasAuthorize);
    await sleep(5000);
    url = await eval_(ws, 'location.href');
    console.log('최종:', url.slice(0, 80));
  }
  
  ws.close();
})().catch(e => console.error('❌', e.message));
