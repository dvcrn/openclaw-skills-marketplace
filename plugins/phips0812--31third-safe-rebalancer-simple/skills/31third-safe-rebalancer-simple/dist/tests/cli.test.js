import { describe, expect, it, vi } from 'vitest';
vi.mock('../index.js', () => ({
    rebalance_now: vi.fn(async () => ({ txHash: '0xabc' })),
    help: vi.fn(() => ({ summary: 'help' }))
}));
import { runCli } from '../scripts/cli.js';
import { rebalance_now } from '../index.js';
import { beforeEach } from 'vitest';
describe('cli', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });
    it('runs rebalance-now', async () => {
        const io = { log: vi.fn(), error: vi.fn() };
        const code = await runCli(['rebalance-now'], io);
        expect(code).toBe(0);
        expect(rebalance_now).toHaveBeenCalledTimes(1);
    });
    it('prints usage for unknown command', async () => {
        const io = { log: vi.fn(), error: vi.fn() };
        const code = await runCli(['wat'], io);
        expect(code).toBe(1);
        expect(io.error).toHaveBeenCalled();
    });
    it('passes --target-entries fallback payload to rebalance_now', async () => {
        const io = { log: vi.fn(), error: vi.fn() };
        const code = await runCli([
            'rebalance-now',
            '--target-entries',
            '[{\"tokenAddress\":\"0x3000000000000000000000000000000000000003\",\"allocation\":1}]'
        ], io);
        expect(code).toBe(0);
        expect(rebalance_now).toHaveBeenCalledTimes(1);
        const params = rebalance_now.mock.calls[0][0];
        expect(params.targetEntries).toEqual([
            { tokenAddress: '0x3000000000000000000000000000000000000003', allocation: 1 }
        ]);
    });
});
