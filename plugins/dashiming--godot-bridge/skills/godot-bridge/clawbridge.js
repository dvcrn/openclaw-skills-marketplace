#!/usr/bin/env node
// ClawBridge - Godot Bridge CLI v1.5.0
// Control Godot 4.x games via HTTP or WebSocket

const http = require('http');
const net = require('net');
const crypto = require('crypto');

const HOST = 'localhost';
const PORT = 9080;

// ========== HTTP ==========
async function sendHTTP(action, data = {}) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({ action, data });
    const options = {
      hostname: HOST, port: PORT, path: '/', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(postData) }
    };
    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => resolve(body));
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

// ========== WebSocket ==========
async function sendWS(action, data = {}) {
  return new Promise((resolve, reject) => {
    const ws = new net.Socket();
    ws.connect(PORT, HOST, () => {
      const key = Buffer.from(crypto.randomBytes(16)).toString('base64');
      const handshake = `GET / HTTP/1.1\r\nHost: ${HOST}:${PORT}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: ${key}\r\nSec-WebSocket-Version: 13\r\n\r\n`;
      ws.write(handshake);
    });
    let response = '';
    ws.on('data', (chunk) => {
      response += chunk.toString();
      if (response.includes('\r\n\r\n') && !ws.handshakeDone) {
        ws.handshakeDone = true;
        ws.write(createWSFrame(JSON.stringify({ action, data })));
      } else if (ws.handshakeDone) { ws.end(); resolve(response); }
    });
    ws.on('error', reject);
    ws.setTimeout(5000, () => { ws.destroy(); reject(new Error('Timeout')); });
  });
}

function createWSFrame(message) {
  const data = Buffer.from(message, 'utf8');
  const length = data.length;
  const frame = Buffer.alloc(2 + (length <= 125 ? 0 : length < 65536 ? 2 : 8) + length);
  frame[0] = 0x81;
  if (length <= 125) frame[1] = length;
  else if (length < 65536) { frame[1] = 126; frame[2] = (length >> 8) & 0xff; frame[3] = length & 0xff; }
  else { frame[1] = 127; frame[6] = (length >> 24) & 0xff; frame[7] = (length >> 16) & 0xff; frame[8] = (length >> 8) & 0xff; frame[9] = length & 0xff; }
  data.copy(frame, frame.length - length);
  return frame;
}

function parseArgs(args) {
  const options = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const key = arg.replace('--', '');
      const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : 'true';
      options[key] = value;
      if (value !== 'true') i++;
    }
  }
  return options;
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0 || args[0] === 'help' || args[0] === '--help') { printUsage(); return; }

  const cmd = args[0];
  const options = parseArgs(args.slice(1));
  const sendFunc = options.ws || options.websocket ? sendWS : sendHTTP;

  try {
    switch (cmd) {
      // ========== UI ==========
      case 'label': await sendFunc('create_label', { text: args[1] || 'Label', x: parseInt(options.x) || 100, y: parseInt(options.y) || 100, font_size: parseInt(options.size) || 16, color: options.color || '#ffffff', outline: options.outline === 'true', shadow: options.shadow === 'true' }); console.log('Created label'); break;
      case 'button': await sendFunc('create_button', { text: args[1] || 'Button', x: parseInt(options.x) || 100, y: parseInt(options.y) || 100, radius: parseInt(options.radius) || 0, color: options.color || '#4a90d9', hover_color: options.hover || '#5aa0e9' }); console.log('Created button'); break;
      case 'progress': await sendFunc('create_progress_bar', { value: parseFloat(options.value) || 50, x: parseInt(options.x) || 100, y: parseInt(options.y) || 100, color: options.color || '#4a90d9', bg_color: options.bg || '#333333', radius: parseInt(options.radius) || 0 }); console.log('Created progress bar'); break;
      case 'slider': await sendFunc('create_slider', { min: parseFloat(options.min) || 0, max: parseFloat(options.max) || 100, value: parseFloat(options.value) || 50, x: parseInt(options.x) || 100, y: parseInt(options.y) || 100, color: options.color || '#4a90d9' }); console.log('Created slider'); break;
      case 'panel': await sendFunc('create_panel', { x: parseInt(options.x) || 100, y: parseInt(options.y) || 100, width: parseInt(options.w) || 200, height: parseInt(options.h) || 100, color: options.color || '#333333', radius: parseInt(options.radius) || 0, opacity: parseFloat(options.opacity) || 1.0, shadow: options.shadow === 'true' }); console.log('Created panel'); break;

      // ========== UI Effects ==========
      case 'shadow': await sendFunc('ui_add_shadow', { path: options.path || '.', offset_x: parseInt(options.x) || 2, offset_y: parseInt(options.y) || 2, color: options.color || '#000000', size: parseInt(options.size) || 4 }); console.log('Added shadow'); break;
      case 'outline': await sendFunc('ui_add_outline', { path: options.path || '.', width: parseInt(options.width) || 2, color: options.color || '#000000' }); console.log('Added outline'); break;
      case 'gradient': await sendFunc('ui_set_gradient', { path: options.path || '.', color1: options.c1 || '#ff0000', color2: options.c2 || '#0000ff', angle: parseInt(options.angle) || 0 }); console.log('Set gradient'); break;
      case 'blur': await sendFunc('ui_set_blur', { path: options.path || '.', amount: parseFloat(options.amount) || 0.5 }); console.log('Set blur'); break;
      case 'fade_in': await sendFunc('ui_fade_in', { path: options.path || '.', duration: parseFloat(options.duration) || 0.5 }); console.log('Fade in'); break;
      case 'fade_out': await sendFunc('ui_fade_out', { path: options.path || '.', duration: parseFloat(options.duration) || 0.5 }); console.log('Fade out'); break;
      case 'pulse': await sendFunc('ui_pulse', { path: options.path || '.', scale: parseFloat(options.scale) || 1.1, duration: parseFloat(options.duration) || 0.3 }); console.log('Pulse effect'); break;
      case 'shake': await sendFunc('ui_shake', { path: options.path || '.', amount: parseInt(options.amount) || 5, duration: parseFloat(options.duration) || 0.3 }); console.log('Shake effect'); break;
      case 'bounce_in': await sendFunc('ui_bounce_in', { path: options.path || '.', duration: parseFloat(options.duration) || 0.5 }); console.log('Bounce in'); break;
      case 'slide_in': await sendFunc('ui_slide_in', { path: options.path || '.', direction: options.dir || 'left', duration: parseFloat(options.duration) || 0.3 }); console.log('Slide in'); break;

      // ========== UI Animations ==========
      case 'spin': await sendFunc('ui_spin', { path: options.path || '.', speed: parseFloat(options.speed) || 360, duration: parseFloat(options.duration) || 1.0, loops: parseInt(options.loops) || -1 }); console.log('Spin animation'); break;
      case 'flip': await sendFunc('ui_flip', { path: options.path || '.', horizontal: options.horiz === 'true', duration: parseFloat(options.duration) || 0.3 }); console.log('Flip animation'); break;
      case 'blink': await sendFunc('ui_blink', { path: options.path || '.', duration: parseFloat(options.duration) || 1.0 }); console.log('Blink animation'); break;
      case 'typewriter': await sendFunc('ui_typewriter', { path: options.path || '.', text: args[1] || 'Hello', speed: parseFloat(options.speed) || 0.1 }); console.log('Typewriter effect'); break;

      // ========== UI States ==========
      case 'hover': await sendFunc('ui_set_hover', { path: options.path || '.', color: options.color || '#5aa0e9', scale: parseFloat(options.scale) || 1.0 }); console.log('Set hover state'); break;
      case 'pressed': await sendFunc('ui_set_pressed', { path: options.path || '.', color: options.color || '#3a70b9', scale: parseFloat(options.scale) || 0.95 }); console.log('Set pressed state'); break;
      case 'disabled': await sendFunc('ui_set_disabled', { path: options.path || '.', opacity: parseFloat(options.opacity) || 0.5 }); console.log('Set disabled state'); break;

      // ========== 2D Graphics ==========
      case 'rect': case 'rectangle': await sendFunc('draw_rect', { x: parseInt(options.x) || 100, y: parseInt(options.y) || 100, width: parseInt(options.w) || 100, height: parseInt(options.h) || 50, color: options.color || '#ff0000', radius: parseInt(options.radius) || 0 }); console.log('Created rectangle'); break;
      case 'circle': await sendFunc('draw_circle', { x: parseInt(options.x) || 200, y: parseInt(options.y) || 200, radius: parseInt(options.r) || 50, color: options.color || '#00ff00' }); console.log('Created circle'); break;
      case 'line': await sendFunc('draw_line', { x1: parseInt(options.x1) || 0, y1: parseInt(options.y1) || 0, x2: parseInt(options.x2) || 100, y2: parseInt(options.y2) || 100, color: options.color || '#0000ff', width: parseInt(options.width) || 2 }); console.log('Created line'); break;
      case 'polygon': await sendFunc('draw_polygon', { x: parseInt(options.x) || 200, y: parseInt(options.y) || 200, sides: parseInt(options.sides) || 6, radius: parseInt(options.r) || 50, color: options.color || '#00ffff' }); console.log('Created polygon'); break;
      case 'star': await sendFunc('draw_star', { x: parseInt(options.x) || 200, y: parseInt(options.y) || 200, points: parseInt(options.points) || 5, outer_r: parseInt(options.or) || 50, inner_r: parseInt(options.ir) || 25, color: options.color || '#ff8800' }); console.log('Created star'); break;
      case 'color_rect': await sendFunc('draw_color_rect', { x: parseInt(options.x) || 100, y: parseInt(options.y) || 100, width: parseInt(options.w) || 100, height: parseInt(options.h) || 100, color: options.color || '#ff0000' }); console.log('Created color rect'); break;
      case 'gradient_rect': await sendFunc('draw_gradient_rect', { x: parseInt(options.x) || 100, y: parseInt(options.y) || 100, width: parseInt(options.w) || 200, height: parseInt(options.h) || 100, color1: options.c1 || '#ff0000', color2: options.c2 || '#0000ff', angle: parseInt(options.angle) || 0 }); console.log('Created gradient rect'); break;

      // ========== 3D ==========
      case 'box': await sendFunc('spawn_primitive', { shape: 'box', name: options.name || 'box' }); console.log('Created box'); break;
      case 'sphere': await sendFunc('spawn_primitive', { shape: 'sphere', name: options.name || 'sphere' }); console.log('Created sphere'); break;
      case 'cylinder': await sendFunc('spawn_primitive', { shape: 'cylinder', name: options.name || 'cylinder' }); console.log('Created cylinder'); break;
      case 'capsule': await sendFunc('spawn_primitive', { shape: 'capsule', name: options.name || 'capsule' }); console.log('Created capsule'); break;

      // ========== Particles ==========
      case 'particles': await sendFunc('create_particles', { name: options.name || 'Particles', emitting: true, amount: parseInt(options.amount) || 50, lifetime: parseFloat(options.lifetime) || 1.0, color: options.color || '#ffffff' }); console.log('Created particles'); break;
      case 'fire': await sendFunc('create_particles', { name: 'Fire', emitting: true, amount: 100, lifetime: 0.8, color: '#ff6600' }); console.log('Created fire'); break;
      case 'smoke': await sendFunc('create_particles', { name: 'Smoke', emitting: true, amount: 50, lifetime: 2.0, color: '#888888' }); console.log('Created smoke'); break;

      // ========== Lighting ==========
      case 'light': await sendFunc('add_light', { type: options.type || 'directional', energy: parseFloat(options.energy) || 1.0, color: options.color || '#ffffff' }); console.log('Created light'); break;
      case 'omni_light': await sendFunc('add_light', { type: 'omni', energy: parseFloat(options.energy) || 1.0, range: parseFloat(options.range) || 10, color: options.color || '#ffffff' }); console.log('Created omni light'); break;

      // ========== Camera ==========
      case 'camera': await sendFunc('create_camera', { x: parseFloat(options.x) || 0, y: parseFloat(options.y) || 5, z: parseFloat(options.z) || 10 }); console.log('Created camera'); break;

      // ========== Materials ==========
      case 'material': await sendFunc('create_material', { color: options.color || '#ffffff', metallic: parseFloat(options.metallic) || 0, roughness: parseFloat(options.roughness) || 0.5 }); console.log('Created material'); break;
      case 'red': await sendFunc('create_material', { name: 'Red', color: '#ff0000', metallic: 0.3, roughness: 0.3 }); console.log('Created red material'); break;
      case 'gold': await sendFunc('create_material', { name: 'Gold', color: '#ffd700', metallic: 1.0, roughness: 0.2 }); console.log('Created gold material'); break;

      // ========== Physics ==========
      case 'rigid_body': await sendFunc('add_rigid_body', { name: options.name || 'RigidBody', mass: parseFloat(options.mass) || 1.0, shape: options.shape || 'box' }); console.log('Created rigid body'); break;
      case 'character': await sendFunc('add_character_body', { name: options.name || 'Character' }); console.log('Created character body'); break;

      // ========== Scene ==========
      case 'tree': const result = await sendFunc('get_scene_tree', {}); console.log('Scene tree:', result); break;
      case 'clear': await sendFunc('clear_all', {}); console.log('Cleared scene'); break;
      case 'delete': await sendFunc('delete_node', { path: options.path || '.' }); console.log('Deleted node'); break;

      default: console.log('Unknown command:', cmd); printUsage(); process.exit(1);
    }
  } catch (err) { console.error('Error:', err.message); process.exit(1); }
}

function printUsage() {
  console.log(`ClawBridge - Godot Bridge CLI v1.5.0

=== UI Effects ===
  shadow --path /root/Label --offset_x 2 --offset_y 2 --color #000000
  outline --path /root/Button --width 2 --color #000000
  gradient --path /root/Panel --c1 #ff0000 --c2 #0000ff --angle 90
  blur --path /root/Node --amount 0.5
  fade_in --path /root/Node --duration 0.5
  fade_out --path /root/Node --duration 0.5
  pulse --path /root/Node --scale 1.1 --duration 0.3
  shake --path /root/Node --amount 5 --duration 0.3
  bounce_in --path /root/Node --duration 0.5
  slide_in --path /root/Node --direction left --duration 0.3

=== UI Animations ===
  spin --path /root/Node --speed 360 --duration 1.0
  flip --path /root/Node --horizontal --duration 0.3
  blink --path /root/Node --duration 1.0
  typewriter --path /root/Label "Hello World" --speed 0.1

=== UI States ===
  hover --path /root/Button --color #5aa0e9 --scale 1.05
  pressed --path /root/Button --color #3a70b9 --scale 0.95
  disabled --path /root/Button --opacity 0.5

=== UI Components ===
  label "Text" --x 100 --y 50 --color #ffffff --shadow --outline --size 24
  button "Click" --x 100 --y 100 --radius 8 --color #4a90d9
  progress 50 --x 100 --y 150 --radius 4 --color #4a90d9
  slider --min 0 --max 100 --value 50
  panel --x 100 --y 100 --w 200 --h 100 --radius 8 --opacity 0.8 --shadow

=== 2D Graphics ===
  rect --x 100 --y 100 --w 200 --h 100 --radius 8 --color #ff0000
  circle --x 200 --y 200 --r 50 --color #00ff00
  gradient_rect --x 100 --y 100 --w 200 --h 100 --c1 #ff0000 --c2 #0000ff

=== 3D, Particles, Physics... ===
  --ws Use WebSocket
`);
}

main();
