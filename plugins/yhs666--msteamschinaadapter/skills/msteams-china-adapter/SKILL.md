---
name: msteams-china-adapter
description: "将 Microsoft Teams 插件从全球版适配到中国区环境的标准化流程"
---

# MS Teams 中国区适配 Skill

## 触发条件

当用户需要：
- 将 MS Teams 插件适配到中国区环境
- 修改 Azure 端点到中国云（Azure China）
- 比较两个版本的源码差异并提取适配模式
- 为其他 Microsoft 服务创建中国区适配方案

## 端点参考表

| 服务 | 全球版 | 中国区 |
|------|--------|--------|
| Azure AD | `login.microsoftonline.com` | `login.partner.microsoftonline.cn` |
| Graph API | `graph.microsoft.com` | `microsoftgraph.chinacloudapi.cn` |
| Bot Framework | `api.botframework.com` | `api.botframework.azure.cn` |
| JWT Issuer | `api.botframework.com` | `api.botframework.azure.cn`, `sts.chinacloudapi.cn` |
| JWKS | `login.botframework.com` | `login.botframework.azure.cn` |

---

## 适配清单

### 第一步：识别源码类型

确认项目使用的 Microsoft SDK 和端点类型：

```bash
# 搜索全球版端点
grep -r "login.microsoftonline.com" src/
grep -r "graph.microsoft.com" src/
grep -r "api.botframework.com" src/
```

### 第二步：创建适配层文件

#### 1. 创建 `sdk.ts` (如果不存在)

```typescript
import type { CloudAdapter } from "@microsoft/agents-hosting";
import type { MSTeamsCredentials } from "./token.js";

export type MSTeamsSdk = typeof import("@microsoft/agents-hosting");
export type MSTeamsAuthConfig = ReturnType<MSTeamsSdk["getAuthConfigWithDefaults"]>;

export async function loadMSTeamsSdk(): Promise<MSTeamsSdk> {
  return await import("@microsoft/agents-hosting");
}

export function buildMSTeamsAuthConfig(
  creds: MSTeamsCredentials,
  sdk: MSTeamsSdk,
): MSTeamsAuthConfig {
  // China region endpoints
  const authority = creds.authority || "https://login.partner.microsoftonline.cn";
  const defaultIssuers = [
    "https://api.botframework.azure.cn",
    "https://sts.chinacloudapi.cn/",
  ];
  const defaultScope = "https://api.botframework.azure.cn";

  const connectionConfig = {
    clientId: creds.appId,
    clientSecret: creds.appPassword,
    tenantId: creds.tenantId,
    authority: authority,
    issuers: defaultIssuers,
    scope: defaultScope,
  };

  const connections = new Map<string, any>();
  connections.set("serviceConnection", connectionConfig);

  return sdk.getAuthConfigWithDefaults({
    clientId: creds.appId,
    clientSecret: creds.appPassword,
    tenantId: creds.tenantId,
    authority: authority,
    issuers: defaultIssuers,
    scope: defaultScope,
    connections: connections,
    connectionsMap: [{ serviceUrl: "*", connection: "serviceConnection" }],
  });
}

export async function createMSTeamsAdapter(
  authConfig: MSTeamsAuthConfig,
  sdk: MSTeamsSdk,
): Promise<CloudAdapter> {
  const { createPatchedAdapter } = await import("./cloud-adapter.js");
  return await createPatchedAdapter(authConfig, sdk);
}

export async function loadMSTeamsSdkWithAuth(creds: MSTeamsCredentials) {
  const sdk = await loadMSTeamsSdk();
  const authConfig = buildMSTeamsAuthConfig(creds, sdk);
  return { sdk, authConfig };
}
```

#### 2. 创建 `cloud-adapter.ts`

```typescript
import type { CloudAdapter } from "@microsoft/agents-hosting";
import type { JwtPayload } from "jsonwebtoken";
import type { MSTeamsAuthConfig, MSTeamsSdk } from "./sdk.js";

const CHINA_SCOPE = "https://api.botframework.azure.cn";

export async function createPatchedAdapter(
  authConfig: MSTeamsAuthConfig,
  sdk?: MSTeamsSdk,
): Promise<CloudAdapter> {
  let CloudAdapterCtor: typeof CloudAdapter;

  if (sdk) {
    CloudAdapterCtor = sdk.CloudAdapter;
  } else {
    const loadedSdk = await import("@microsoft/agents-hosting");
    CloudAdapterCtor = loadedSdk.CloudAdapter;
  }

  class PatchedCloudAdapter extends CloudAdapterCtor {
    private _authConfig: MSTeamsAuthConfig;

    constructor(authConfig: MSTeamsAuthConfig) {
      super(authConfig);
      this._authConfig = authConfig;
    }

    protected async createConnectorClientWithIdentity(
      identity: JwtPayload,
      activity: any,
      headers?: any,
    ): Promise<any> {
      if (!identity?.aud) {
        identity = {
          ...identity,
          aud: this._authConfig.clientId,
          azp: CHINA_SCOPE,
        };
      }

      const tokenProvider = this.connectionManager.getTokenProviderFromActivity(identity, activity);

      if (activity.isAgenticRequest?.()) {
        return super.createConnectorClientWithIdentity(identity, activity, headers);
      }

      const scope = CHINA_SCOPE;
      const token = await tokenProvider.getAccessToken(scope);

      return this.createConnectorClient(activity.serviceUrl!, scope, identity, headers);
    }

    protected async createUserTokenClient(
      identity: JwtPayload,
      tokenServiceEndpoint?: string,
      scope?: string,
      audience?: string,
      headers?: any,
    ): Promise<any> {
      return super.createUserTokenClient(identity, tokenServiceEndpoint, CHINA_SCOPE, audience, headers);
    }

    protected async createConnectorClient(
      serviceUrl: string,
      scope: string,
      identity: JwtPayload,
      headers?: any,
    ): Promise<any> {
      return super.createConnectorClient(serviceUrl, CHINA_SCOPE, identity, headers);
    }
  }

  return new PatchedCloudAdapter(authConfig);
}
```

#### 3. 创建 `auth.ts`

```typescript
import * as jwt from "jsonwebtoken";
import jwksRsa from "jwks-rsa";
import type { JwtPayload } from "jsonwebtoken";

interface DecodedToken {
  aud: string | string[];
  iss: string;
  exp?: number;
  nbf?: number;
}

type VerifyCallback = (error: Error | null, decoded?: string | JwtPayload) => void;

export async function verifyJWTToken(rawToken: string, authConfig: any): Promise<JwtPayload> {
  const decoded = jwt.decode(rawToken);
  if (!decoded || typeof decoded === 'string') {
    throw new Error('invalid token');
  }

  if (typeof decoded !== 'object' || decoded === null) {
    throw new Error('invalid token payload');
  }

  const payload = decoded as DecodedToken;
  const audience = Array.isArray(payload.aud) ? payload.aud[0] : payload.aud;

  if (audience !== authConfig.clientId) {
    throw new Error(`Audience mismatch: expected ${authConfig.clientId}, got ${audience}`);
  }

  let jwksUri: string;
  if (payload.iss === 'https://api.botframework.azure.cn') {
    jwksUri = 'https://login.botframework.azure.cn/v1/.well-known/keys';
  } else if (payload.iss === 'https://api.botframework.com') {
    jwksUri = 'https://login.botframework.azure.cn/v1/.well-known/keys';
  } else {
    jwksUri = `${authConfig.authority}/${authConfig.tenantId}/discovery/v2.0/keys`;
  }

  const jwksClient = jwksRsa({ jwksUri });

  const forceChinaScope = authConfig.scope?.includes('botframework.azure.cn') ||
                          authConfig.issuers?.includes('https://api.botframework.azure.cn') ||
                          authConfig.authority?.includes('chinacloudapi.cn') ||
                          authConfig.authority?.includes('partner.microsoftonline.cn');

  const getKey = (header: jwt.JwtHeader, callback: (error: Error | null, key?: string) => void) => {
    jwksClient.getSigningKey(header.kid, (err: Error | null, key?: jwksRsa.SigningKey) => {
      if (err) {
        callback(err, undefined);
        return;
      }
      const signingKey = key?.getPublicKey();
      callback(null, signingKey);
    });
  };

  return new Promise((resolve, reject) => {
    const verifyOptions: jwt.VerifyOptions = {
      audience: [authConfig.clientId, payload.iss],
      ignoreExpiration: false,
      algorithms: ['RS256' as jwt.Algorithm],
      clockTolerance: 300
    };

    jwt.verify(rawToken, getKey, verifyOptions, (err: Error | null, decoded: string | JwtPayload | undefined) => {
      if (err) {
        if (forceChinaScope && payload.iss === 'https://api.botframework.azure.cn') {
          const fallbackOptions: jwt.VerifyOptions = {
            audience: [authConfig.clientId, payload.iss, 'https://api.botframework.com'],
            ignoreExpiration: false,
            algorithms: ['RS256' as jwt.Algorithm],
            clockTolerance: 300
          };
          jwt.verify(rawToken, getKey, fallbackOptions, (fallbackErr: Error | null, fallbackDecoded: string | JwtPayload | undefined) => {
            if (fallbackErr) {
              reject(new Error(`JWT verification failed: ${err.message}. China region scope enabled, try global scope as fallback`));
            } else {
              resolve(fallbackDecoded as JwtPayload);
            }
          });
        } else {
          reject(err);
        }
      } else {
        resolve(decoded as JwtPayload);
      }
    });
  });
}

export function createCustomJwtMiddleware(authConfig: any, log: any) {
  return async (req: any, res: any, next: any) => {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return next(new Error('Missing or invalid authorization header'));
    }

    const rawToken = authHeader.substring(7);

    try {
      const decoded = await verifyJWTToken(rawToken, authConfig);
      req.user = decoded;
      next();
    } catch (error) {
      log?.('JWT verification failed:', error);
      next(error);
    }
  };
}
```

### 第三步：修改现有文件

#### 4. 修改 `token.ts`

在凭证接口中添加 `authority` 字段：

```typescript
export interface MSTeamsCredentials {
  appId: string;
  appPassword: string;
  tenantId: string;
  authority?: string;  // 新增：支持自定义 Authority 端点
}
```

并在解析函数中添加：

```typescript
const authority =
  normalizeSecretInputString(cfg?.authority) ||
  normalizeSecretInputString(process.env.MSTEAMS_AUTHORITY);

return { appId, appPassword, tenantId, authority };
```

#### 5. 修改 `runtime.ts`

找到 Graph API 令牌请求，修改为中国区端点：

```diff
- const token = await tokenProvider.getAccessToken("https://graph.microsoft.com");
+ const token = await tokenProvider.getAccessToken("https://microsoftgraph.chinacloudapi.cn");
```

#### 6. 修改 `attachments/shared.ts`

```diff
- const GRAPH_ROOT = "https://graph.microsoft.com/v1.0";
+ const GRAPH_ROOT = "https://microsoftgraph.chinacloudapi.cn/v1.0";

const DEFAULT_MEDIA_HOST_ALLOWLIST = [
-  "graph.microsoft.com",
+  "microsoftgraph.chinacloudapi.cn",
  // ...
];

const DEFAULT_MEDIA_AUTH_HOST_ALLOWLIST = [
-  "api.botframework.com",
+  "api.botframework.azure.cn",
+  "botframework.azure.cn",
  // ...
];
```

#### 7. 修改 `monitor.ts`

```diff
- import { authorizeJWT } from "@microsoft/agents-hosting";
+ import { createCustomJwtMiddleware } from "./auth.js";

// 在 Express 应用中
- app.use(authorizeJWT(authConfig));
+ app.use(createCustomJwtMiddleware(authConfig, log));
```

#### 8. 修改 `messenger.ts`

```diff
- import { CustomMSTeamsAdapter } from "./...";
+ import { CloudAdapter } from "@microsoft/agents-hosting";

// 更新类型引用
- adapter: CustomMSTeamsAdapter;
+ adapter: CloudAdapter;
```

#### 9. 修改 `index.ts`

```diff
+ export {
+   loadMSTeamsSdk,
+   buildMSTeamsAuthConfig,
+   createMSTeamsAdapter,
+ } from "./sdk.js";
```

### 第四步：验证检查清单

完成适配后，确认以下项目：

- [ ] 所有 `login.microsoftonline.com` 替换为 `login.partner.microsoftonline.cn`
- [ ] 所有 `graph.microsoft.com` 替换为 `microsoftgraph.chinacloudapi.cn`
- [ ] 所有 `api.botframework.com` 替换为 `api.botframework.azure.cn`
- [ ] JWT 验证使用中国区 JWKS URI
- [ ] 媒体下载白名单包含中国区域名
- [ ] 环境变量支持 `MSTEAMS_AUTHORITY`

---

## 源码差异报告 (srcV0 → srcV2)

### 文件结构差异

| 版本 | 文件数 | 结构特点 |
|------|--------|----------|
| srcV0 | 80 文件 | 所有文件在根目录 |
| srcV2 | 160 文件 | 根目录 + src/ 子目录双重结构 |
| srcV3 | 161 文件 | 同 srcV2，增加 AGENTS.md |

### 核心修改文件清单

#### 🆕 新增文件

| 文件 | 用途 |
|------|------|
| `src/auth.ts` | 自定义 JWT 验证逻辑，支持中国区 JWKS 端点 |
| `src/cloud-adapter.ts` | 补丁 CloudAdapter，强制使用中国区 Scope |

#### 🔧 修改文件摘要

| 文件 | 修改内容 |
|------|----------|
| `sdk.ts` | 添加中国区认证配置 (authority, issuers, scope) |
| `runtime.ts` | 简化运行时实现，移除 createPluginRuntimeStore |
| `token.ts` | 添加 `authority` 字段支持 |
| `attachments/shared.ts` | 修改 GRAPH_ROOT 和媒体白名单 |
| `monitor.ts` | 使用自定义 JWT 中间件，adapter 改为 await |
| `messenger.ts` | 类型引用改为 CloudAdapter |
| `index.ts` | 导出 SDK 加载函数 |

### 端点变更汇总

| 组件 | 全球版端点 | 中国区端点 |
|------|-----------|-----------|
| Azure AD Authority | `login.microsoftonline.com` | `login.partner.microsoftonline.cn` |
| Graph API | `graph.microsoft.com` | `microsoftgraph.chinacloudapi.cn` |
| Bot Framework Scope | `api.botframework.com` | `api.botframework.azure.cn` |
| JWT Issuer | `api.botframework.com` | `api.botframework.azure.cn`, `sts.chinacloudapi.cn` |
| JWKS URI | `login.botframework.com` | `login.botframework.azure.cn` |
| Graph Token Scope | `https://graph.microsoft.com` | `https://microsoftgraph.chinacloudapi.cn` |

### 修改类型统计

| 修改类型 | 数量 |
|----------|------|
| 新增文件 | 2 |
| 修改文件 | 9 |
| 端点变更 | 6 |
| 类型变更 | 3 |

### 适配步骤总结

1. **创建适配层**: 新增 `auth.ts` 和 `cloud-adapter.ts`
2. **修改认证配置**: 在 `sdk.ts` 中添加中国区端点
3. **修改 Graph 端点**: 在 `runtime.ts` 和 `attachments/shared.ts` 中替换
4. **扩展凭证类型**: 在 `token.ts` 中添加 `authority` 字段
5. **替换中间件**: 在 `monitor.ts` 中使用自定义 JWT 验证
6. **调整类型引用**: 在 `messenger.ts` 中使用标准 CloudAdapter

### 验证命令

```bash
# 检查是否还有全球版端点残留
grep -r "login.microsoftonline.com" src/
grep -r "graph.microsoft.com" src/ --exclude-dir=node_modules
grep -r "api.botframework.com" src/
```

---

## 环境变量配置

```bash
# 中国区配置
MSTEAMS_AUTHORITY=https://login.partner.microsoftonline.cn
MSTEAMS_TENANT_ID=<your-tenant-id>
MSTEAMS_APP_ID=<your-app-id>
MSTEAMS_APP_PASSWORD=<your-app-password>
```

## 相关文件结构

```
src/
├── index.ts              # 入口点，导出 SDK 加载函数
├── sdk.ts                # 认证配置构建
├── cloud-adapter.ts      # 适配器补丁
├── auth.ts               # JWT 验证
├── token.ts              # 凭证类型
├── runtime.ts            # 运行时配置
├── monitor.ts            # 监控中间件
├── messenger.ts          # 消息处理
└── attachments/
    └── shared.ts         # Graph 端点和白名单
```

## 输出

适配完成后，应输出：
1. 修改文件列表
2. 新增文件列表
3. 验证通过的测试用例
4. 可供其他项目复用的适配模式文档

---

## 故障排除

### `adapter.process is not a function`

**错误现象:**
```
TypeError: adapter.process is not a function
    at messageHandler (src/monitor.ts:287:5)
```

**原因:**
1. `createMSTeamsAdapter` 是异步函数但调用处没有 `await`
2. `CloudAdapter` 的 `process` 方法在子类中未显式暴露

**修复步骤:**

#### 1. 修改 `sdk.ts` - 添加 await 并返回正确类型

```typescript
export async function createMSTeamsAdapter(
  authConfig: MSTeamsAuthConfig,
  sdk: MSTeamsSdk,
): Promise<MSTeamsAdapter> {
  const { createPatchedAdapter } = await import("./cloud-adapter.js");
  const adapter = await createPatchedAdapter(authConfig, sdk);
  return adapter as unknown as MSTeamsAdapter;
}
```

#### 2. 修改 `monitor.ts` - 使用 await

```typescript
// ❌ 错误
const adapter = createMSTeamsAdapter(authConfig, sdk);

// ✅ 正确
const adapter = await createMSTeamsAdapter(authConfig, sdk);
```

#### 3. 修改 `cloud-adapter.ts` - 显式暴露 process 方法

```typescript
class PatchedCloudAdapter extends CloudAdapterCtor {
  // ... 其他方法 ...

  // 显式暴露 process 方法
  public process = async (req: any, res: any, logic: (context: any) => Promise<void>) => {
    return super.process(req, res, logic);
  };
}
```
