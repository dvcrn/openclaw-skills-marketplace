import { clampFiniteInt } from './utils/integers.js';
const env = process.env;
export function loadConfig() {
    const user = env.THETA_INFERENCE_AUTH_USER;
    const pass = env.THETA_INFERENCE_AUTH_PASS;
    const token = env.THETA_INFERENCE_AUTH_TOKEN;
    return {
        dryRun: env.THETA_DRY_RUN === '1',
        edgecloudApiKey: env.THETA_EC_API_KEY,
        edgecloudProjectId: env.THETA_EC_PROJECT_ID,
        edgecloudOrgId: env.THETA_ORG_ID,
        videoSaId: env.THETA_VIDEO_SA_ID,
        videoSaSecret: env.THETA_VIDEO_SA_SECRET,
        inferenceEndpoint: env.THETA_INFERENCE_ENDPOINT,
        inferenceAuth: token ? { token } : user && pass ? { user, pass } : undefined,
        onDemandApiToken: env.THETA_ONDEMAND_API_TOKEN ?? env.THETA_ONDEMAND_API_KEY,
        httpTimeoutMs: clampFiniteInt(env.THETA_HTTP_TIMEOUT_MS, 20000, 1000, 120000),
        httpMaxRetries: clampFiniteInt(env.THETA_HTTP_MAX_RETRIES, 2, 0, 6),
        httpRetryBackoffMs: clampFiniteInt(env.THETA_HTTP_RETRY_BACKOFF_MS, 250, 25, 10000)
    };
}
