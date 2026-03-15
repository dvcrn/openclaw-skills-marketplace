import { spawn } from 'child_process';

let currentProcess = null;
let currentAddress = null;

export default async function handler({ command, params }) {
  const [subcommand, address] = params.split(' ');

  if (subcommand === 'run') {
    // if there's an existing process, kill it before starting a new one
    if (currentProcess) {
      currentProcess.kill();
      currentProcess = null;
      console.log('Stopped previous aibtc-worker before starting a new one.');
    }

	currentAddress = address;

    // start aibtc-worker with the given address and 4 threads
    currentProcess = spawn('npx', ['--yes', 'aibtc-worker', address, '--threads', '4'], {
      stdio: 'ignore', // ignore output
      detached: true,   // allow the child process to continue running after the parent exits
    });

    currentProcess.unref(); // allow the parent process to exit independently of the child
    return `⛏️  AIBTC mining started
worker : ${address}`;
  } else if (subcommand === 'stop') {
    if (!currentProcess) {
      return `AIBTC mining stopped
worker : idle`;
    }

	currentAddress = null;

    currentProcess.kill();
    currentProcess = null;
    return `AIBTC mining stopped
worker : idle`;
  } else if (subcommand === 'status') {
    if (currentProcess) {
      return `⛏️  AIBTC worker status
worker  : ${currentAddress}
status  : running ●`;
    } else {
      return `⛏️  AIBTC worker status
worker  : none
status  : idle ○`;
    }
  } else {
    return `unknown command
try :
  aibtc run <BSC address>   → start mining
  aibtc stop                → stop mining
  aibtc status              → check mining status`;
  }
}