import { describe, it, expect } from 'vitest';

import { getOneBotRuntime, setOneBotRuntime } from '../src/runtime.js';

describe('runtime', () => {
  it('getOneBotRuntime throws before initialization', () => {
    // runtime is module singleton; ensure it starts empty in this file's context
    expect(() => getOneBotRuntime()).toThrow(/not initialized/);
  });

  it('setOneBotRuntime then getOneBotRuntime returns same object', () => {
    const r = { channel: { activity: { record: () => {} }, routing: {}, reply: {} } } as any;
    setOneBotRuntime(r);
    expect(getOneBotRuntime()).toBe(r);
  });
});
