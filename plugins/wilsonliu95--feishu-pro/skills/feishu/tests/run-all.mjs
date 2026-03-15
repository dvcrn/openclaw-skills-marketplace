console.log('🧪 Feishu Skills Test Suite');
console.log('================================');

await import('./test-feishu-im.mjs');
await import('./test-feishu-docs.mjs');
await import('./test-feishu-data.mjs');
await import('./test-feishu-org.mjs');
await import('./test-feishu-ai.mjs');

console.log('\n✅ 全部测试执行完毕');
