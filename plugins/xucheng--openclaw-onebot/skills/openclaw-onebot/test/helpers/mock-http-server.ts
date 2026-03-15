import http from 'node:http';

export interface CapturedRequest {
  method: string;
  url: string;
  headers: http.IncomingHttpHeaders;
  bodyRaw: string;
  bodyJson: any;
}

export interface MockHttpServer {
  baseUrl: string;
  requests: CapturedRequest[];
  close: () => Promise<void>;
}

export function startMockOneBotHttpServer(opts?: {
  handler?: (req: http.IncomingMessage, bodyJson: any) => any;
}): Promise<MockHttpServer> {
  const requests: CapturedRequest[] = [];

  const server = http.createServer(async (req, res) => {
    const chunks: Buffer[] = [];
    req.on('data', (c) => chunks.push(Buffer.from(c)));
    req.on('end', () => {
      const bodyRaw = Buffer.concat(chunks).toString('utf8');
      let bodyJson: any = null;
      try {
        bodyJson = bodyRaw ? JSON.parse(bodyRaw) : null;
      } catch {
        bodyJson = null;
      }

      requests.push({
        method: req.method ?? 'GET',
        url: req.url ?? '/',
        headers: req.headers,
        bodyRaw,
        bodyJson,
      });

      const result = opts?.handler?.(req, bodyJson);

      // Default: OneBot OK
      const payload =
        result ??
        ({
          status: 'ok',
          retcode: 0,
          data: { message_id: 123 },
        } as const);

      res.statusCode = 200;
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify(payload));
    });
  });

  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      const addr = server.address();
      if (!addr || typeof addr === 'string') throw new Error('Unexpected listen address');
      const baseUrl = `http://127.0.0.1:${addr.port}`;
      resolve({
        baseUrl,
        requests,
        close: () => new Promise((r) => server.close(() => r())),
      });
    });
  });
}
