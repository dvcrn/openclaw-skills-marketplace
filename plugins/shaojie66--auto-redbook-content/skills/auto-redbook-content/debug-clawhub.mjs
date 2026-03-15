import { spawn } from 'child_process';
import { resolve } from 'path';

const cwd = process.cwd();
console.log('CWD:', cwd);
console.log('Resolved path:', resolve(cwd, '.'));

const proc = spawn('clawhub', ['publish', '.', '--version', '2.0.0', '--slug', 'auto-redbook-content'], {
  cwd,
  stdio: 'inherit',
  env: { ...process.env, DEBUG: '*' }
});

proc.on('exit', (code) => {
  console.log('Exit code:', code);
});
