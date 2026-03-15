const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const CDP_WS = 'ws://127.0.0.1:18800/devtools/page/05A159BAC2A7FE7547F5DA23AC3FC655';
let msgId = 1;

function sendCDP(ws, method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = msgId++;
    ws.send(JSON.stringify({ id, method, params }));
    const handler = (data) => {
      const msg = JSON.parse(data.toString());
      if (msg.id === id) {
        ws.removeListener('message', handler);
        if (msg.error) reject(new Error(msg.error.message));
        else resolve(msg.result);
      }
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

(async () => {
  const ws = new WebSocket(CDP_WS);
  await new Promise(r => ws.on('open', r));
  console.log('✅ CDP 연결');

  // 현재 URL 확인
  let url = await eval_(ws, 'location.href');
  console.log('📍 URL:', url);

  // GitHub 로그인 페이지인 경우
  if (url.includes('github.com/login')) {
    console.log('🔐 GitHub 로그인 중...');
    
    // username
    await eval_(ws, `
      document.getElementById('login_field').value = 'tames@tags.kr';
      document.getElementById('login_field').dispatchEvent(new Event('input', {bubbles:true}));
    `);
    await sleep(500);
    
    // password
    await eval_(ws, `
      document.getElementById('password').value = 'tames0210!';
      document.getElementById('password').dispatchEvent(new Event('input', {bubbles:true}));
    `);
    await sleep(500);
    
    // submit
    await eval_(ws, `document.querySelector('input[type="submit"]').click()`);
    console.log('  📤 로그인 제출');
    await sleep(5000);
    
    url = await eval_(ws, 'location.href');
    console.log('📍 로그인 후 URL:', url);
    
    // OAuth authorize 페이지일 수 있음
    if (url.includes('authorize')) {
      console.log('🔑 OAuth 승인 중...');
      await eval_(ws, `
        const btn = document.querySelector('button[type="submit"][name="authorize"]') || 
                    document.querySelector('#js-oauth-authorize-btn') ||
                    document.querySelector('button.js-oauth-authorize-btn');
        if (btn) btn.click();
      `);
      await sleep(5000);
      url = await eval_(ws, 'location.href');
      console.log('📍 승인 후 URL:', url);
    }
  }

  // clawhub.ai로 돌아왔는지 확인
  if (!url.includes('clawhub')) {
    console.log('⏳ clawhub으로 리다이렉트 대기...');
    await sleep(3000);
    url = await eval_(ws, 'location.href');
    console.log('📍 URL:', url);
  }

  // upload 페이지로 이동
  if (!url.includes('/upload')) {
    await sendCDP(ws, 'Page.navigate', { url: 'https://clawhub.ai/upload' });
    await sleep(3000);
    url = await eval_(ws, 'location.href');
    console.log('📍 upload 페이지:', url);
  }

  // 로그인 상태 확인
  const loginState = await eval_(ws, `
    const el = document.querySelector('[class*="avatar"]') || document.querySelector('[class*="user"]');
    const signIn = document.querySelector('.btn-primary');
    if (signIn && signIn.textContent.includes('Sign in')) return 'NOT_LOGGED_IN';
    return 'LOGGED_IN';
  `);
  console.log('🔐 상태:', loginState);

  if (loginState === 'NOT_LOGGED_IN') {
    console.log('❌ 로그인 실패. 수동으로 진행 필요.');
    ws.close();
    return;
  }

  // 폼 채우기
  console.log('📝 폼 채우기...');
  await sleep(1000);
  
  const formResult = await eval_(ws, `
    (async () => {
      const inputs = document.querySelectorAll('input');
      const results = [];
      
      for (const inp of inputs) {
        const parent = inp.closest('div')?.parentElement;
        const labelEl = parent?.querySelector('label') || parent?.previousElementSibling;
        const label = (labelEl?.textContent || inp.placeholder || '').toUpperCase();
        
        if (label.includes('SLUG') || inp.placeholder?.includes('claw')) {
          inp.focus();
          document.execCommand('selectAll');
          document.execCommand('insertText', false, 'openclaw-messenger');
          inp.dispatchEvent(new Event('input', {bubbles:true}));
          inp.dispatchEvent(new Event('change', {bubbles:true}));
          results.push('slug: ok');
        } else if (label.includes('DISPLAY') || label.includes('MY SKILL') || inp.placeholder?.includes('My skill')) {
          inp.focus();
          document.execCommand('selectAll');
          document.execCommand('insertText', false, 'OpenClaw Messenger');
          inp.dispatchEvent(new Event('input', {bubbles:true}));
          inp.dispatchEvent(new Event('change', {bubbles:true}));
          results.push('name: ok');
        } else if (label.includes('VERSION')) {
          // keep 1.0.0
          results.push('version: default');
        }
      }
      
      // changelog
      const ta = document.querySelector('textarea');
      if (ta) {
        ta.focus();
        document.execCommand('selectAll');
        document.execCommand('insertText', false, 'Initial release - Send messages between OpenClaw instances');
        ta.dispatchEvent(new Event('input', {bubbles:true}));
        results.push('changelog: ok');
      }
      
      return results.join(', ');
    })()
  `);
  console.log('📝 결과:', formResult);

  // 파일 업로드 — input[type=file] 사용
  console.log('📦 파일 업로드...');
  
  const skillDir = '/Users/tag/.openclaw/workspace/skills/openclaw-messenger';
  const filesToUpload = [
    { path: 'SKILL.md', content: fs.readFileSync(path.join(skillDir, 'SKILL.md'), 'utf-8') },
    { path: 'scripts/messenger.js', content: fs.readFileSync(path.join(skillDir, 'scripts/messenger.js'), 'utf-8') },
    { path: 'package.json', content: fs.readFileSync(path.join(skillDir, 'package.json'), 'utf-8') },
  ];

  const uploadResult = await eval_(ws, `
    (async () => {
      const files = ${JSON.stringify(filesToUpload)};
      const dt = new DataTransfer();
      
      for (const f of files) {
        const blob = new Blob([f.content], { type: 'text/plain' });
        // webkitRelativePath를 설정하기 위해 trick 사용
        const file = new File([blob], 'openclaw-messenger/' + f.path, { type: 'text/plain' });
        dt.items.add(file);
      }
      
      // 방법 1: input[type=file] 찾기
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) {
        fileInput.files = dt.files;
        fileInput.dispatchEvent(new Event('change', {bubbles:true}));
        return 'input: ' + dt.files.length + ' files';
      }
      
      // 방법 2: 드롭 이벤트
      const dropZones = document.querySelectorAll('[class*="border-dashed"], [class*="dropzone"], [class*="drop"]');
      for (const dz of dropZones) {
        const ev = new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt });
        dz.dispatchEvent(ev);
        return 'drop: ' + dt.files.length + ' files on ' + dz.className?.slice(0,30);
      }
      
      // 방법 3: 모든 div 중 "Choose folder" 텍스트 포함하는 것
      const allDivs = document.querySelectorAll('div');
      for (const div of allDivs) {
        if (div.textContent?.includes('Choose folder') || div.textContent?.includes('Drop a folder')) {
          const ev = new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt });
          div.dispatchEvent(ev);
          return 'drop-text: ' + dt.files.length + ' files';
        }
      }
      
      return 'no upload target found. inputs: ' + document.querySelectorAll('input').length;
    })()
  `);
  console.log('📂 업로드:', uploadResult);
  
  await sleep(2000);
  
  // Validation 상태 확인
  const validation = await eval_(ws, `
    const allText = document.body.innerText;
    const validIdx = allText.indexOf('Validation');
    if (validIdx >= 0) return allText.slice(validIdx, validIdx + 200);
    return 'no validation section found';
  `);
  console.log('✅ Validation:', validation);

  // 페이지 전체 input 상태
  const pageState = await eval_(ws, `
    JSON.stringify({
      url: location.href,
      inputs: [...document.querySelectorAll('input')].map(i => ({ type: i.type, value: i.value?.slice(0,30), placeholder: i.placeholder })),
      buttons: [...document.querySelectorAll('button')].map(b => b.textContent?.trim()?.slice(0,30)),
      fileCount: document.querySelectorAll('input[type="file"]').length
    })
  `);
  console.log('📄 페이지 상태:', pageState);

  ws.close();
  console.log('\n🏁 완료');
})().catch(e => console.error('❌', e.message));
