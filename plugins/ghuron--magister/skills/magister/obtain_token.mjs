const host = process.env.MAGISTER_HOST;
const user = process.env.MAGISTER_USER;
const pass = process.env.MAGISTER_PASSWORD;
const rand = () => btoa(String.fromCharCode(...Array.from({length: 16}, () => Math.random() * 256 | 0))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
const jar  = new Map();

function saveCookies(r) {
  for (const sc of r.headers.getSetCookie()) {
    const [kv] = sc.split(';');
    const eq   = kv.indexOf('=');
    jar.set(kv.slice(0, eq).trim(), kv.slice(eq + 1).trim());
  }
}
const cookies = () => [...jar].map(([k, v]) => `${k}=${v}`).join('; ');

async function follow(url, init = {}) {
  const r = await fetch(url, { ...init, redirect: 'manual', headers: { ...init.headers, Cookie: cookies() } });
  saveCookies(r);
  const loc = r.headers.get('location');
  if (!loc) return r;
  const locUrl = new URL(loc, url);
  if (locUrl.pathname.endsWith('redirect_callback.html')) return r;
  return follow(locUrl.href);
}

const qs = new URLSearchParams({
  client_id: `M6-${host}`, state: rand(),
  redirect_uri:  `https://${host}/oidc/redirect_callback.html`,
  response_type: 'id_token token', acr_values: `tenant:${host}`,
  nonce: rand(), scope: 'openid profile attendance.overview calendar.user grades.read',
});

const login     = await follow(`https://accounts.magister.net/connect/authorize?${qs}`);
const sessionId = login.url.match(/sessionId=([a-f0-9A-F-]+)/)[1];
const returnUrl = decodeURIComponent(login.url.match(/returnUrl=([^&]+)/)[1]);
const xsrf      = decodeURIComponent(jar.get('XSRF-TOKEN') ?? '');

const challenge = async (path, body) => {
  const r = await fetch(`https://accounts.magister.net/challenges/${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-XSRF-TOKEN': xsrf, Cookie: cookies() },
    body: JSON.stringify({ sessionId, returnUrl, ...body }),
  });
  saveCookies(r);
  return r.json();
};

await challenge('username', { username: user });
const { redirectURL } = await challenge('password', { password: pass });

const r     = await follow(`https://accounts.magister.net${redirectURL}`);
const token = new URLSearchParams(new URL(r.headers.get('location')).hash.slice(1)).get('access_token');
console.log(token);
