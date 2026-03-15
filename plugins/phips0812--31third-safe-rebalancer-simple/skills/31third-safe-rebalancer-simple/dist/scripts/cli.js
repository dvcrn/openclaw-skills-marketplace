import { pathToFileURL } from 'node:url';
import { help, rebalance_now } from '../index.js';
function readFlagValue(args, flag) {
    const index = args.indexOf(flag);
    if (index < 0 || index + 1 >= args.length) {
        return undefined;
    }
    return args[index + 1];
}
function usage() {
    return [
        'Usage:',
        '  npm run cli -- help',
        '  npm run cli -- rebalance-now',
        '  npm run cli -- rebalance-now --target-entries \'[{"tokenAddress":"0x...","allocation":0.5},{"tokenAddress":"0x...","allocation":0.5}]\''
    ].join('\n');
}
export async function runCli(args, io = console) {
    const command = args[0];
    if (!command || command === 'help') {
        io.log(JSON.stringify(help(), null, 2));
        io.log(usage());
        return 0;
    }
    if (command !== 'rebalance-now') {
        io.error(`Unknown command: ${command}`);
        io.error(usage());
        return 1;
    }
    try {
        const targetEntriesRaw = readFlagValue(args, '--target-entries');
        const targetEntries = targetEntriesRaw ? JSON.parse(targetEntriesRaw) : undefined;
        const result = await rebalance_now({ targetEntries });
        io.log(JSON.stringify(result, null, 2));
        return 0;
    }
    catch (error) {
        io.error(error instanceof Error ? error.message : String(error));
        return 1;
    }
}
async function main() {
    process.exitCode = await runCli(process.argv.slice(2));
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
    void main();
}
