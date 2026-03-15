export interface MockRuntimeState {
  recordedActivity: any[];
  lastRouteArgs: any | null;
  lastEnvelopeArgs: any | null;
  lastFinalizeArgs: any | null;
  lastDispatchArgs: any | null;
  nextDeliverPayload?: { text?: string; mediaUrl?: string; mediaUrls?: string[] };
}

export function createMockRuntime(state?: Partial<MockRuntimeState>) {
  const s: MockRuntimeState = {
    recordedActivity: [],
    lastRouteArgs: null,
    lastEnvelopeArgs: null,
    lastFinalizeArgs: null,
    lastDispatchArgs: null,
    nextDeliverPayload: { text: 'mock-reply' },
    ...state,
  };

  const runtime = {
    channel: {
      activity: {
        record: (x: any) => s.recordedActivity.push(x),
      },
      routing: {
        resolveAgentRoute: (args: any) => {
          s.lastRouteArgs = args;
          return { sessionKey: 'session:test', accountId: args.accountId ?? 'default', agentId: 'agent:test' };
        },
      },
      reply: {
        resolveEnvelopeFormatOptions: (_cfg: any) => ({ mode: 'raw' }),
        formatInboundEnvelope: (args: any) => {
          s.lastEnvelopeArgs = args;
          // just return the body
          return args.body;
        },
        finalizeInboundContext: (args: any) => {
          s.lastFinalizeArgs = args;
          return args;
        },
        resolveEffectiveMessagesConfig: (_cfg: any, _agentId: string) => ({ responsePrefix: '' }),
        dispatchReplyWithBufferedBlockDispatcher: async ({ ctx, dispatcherOptions }: any) => {
          s.lastDispatchArgs = { ctx, dispatcherOptions };
          // Immediately deliver a response
          await dispatcherOptions.deliver(s.nextDeliverPayload ?? { text: '' }, { kind: 'final' });
        },
      },
    },
  };

  return { runtime, state: s };
}
