import { getJson, postJson } from './http.js';
import { fromConfigError } from '../errors.js';
const ALLOWED_INFERENCE_DOMAIN_SUFFIXES = ['.thetaedgecloud.com'];
function isLoopbackOrPrivateHost(hostname) {
    const host = hostname.toLowerCase();
    if (host === 'localhost' || host === '::1' || host === '0.0.0.0' || host === '::ffff:127.0.0.1')
        return true;
    if (/^\d{1,3}(\.\d{1,3}){3}$/.test(host)) {
        const parts = host.split('.').map((p) => Number.parseInt(p, 10));
        if (parts.some((p) => !Number.isInteger(p) || p < 0 || p > 255))
            return true;
        if (parts[0] === 10 || parts[0] === 127)
            return true;
        if (parts[0] === 169 && parts[1] === 254)
            return true;
        if (parts[0] === 192 && parts[1] === 168)
            return true;
        if (parts[0] === 172 && parts[1] >= 16 && parts[1] <= 31)
            return true;
    }
    if (host.startsWith('fe80:') || host.startsWith('fc') || host.startsWith('fd')) {
        return true;
    }
    return false;
}
function parseEndpoint(raw, code) {
    try {
        const parsed = new URL(String(raw).trim());
        if (parsed.protocol !== 'https:') {
            throw fromConfigError('Inference endpoint must use https://', code);
        }
        if (parsed.username || parsed.password) {
            throw fromConfigError('Inference endpoint must not include embedded credentials', code);
        }
        if (!parsed.hostname || isLoopbackOrPrivateHost(parsed.hostname)) {
            throw fromConfigError('Inference endpoint host is unsafe (private/loopback not allowed)', code);
        }
        return parsed;
    }
    catch (error) {
        if (error && typeof error === 'object' && 'code' in error) {
            throw error;
        }
        throw fromConfigError('Inference endpoint must be an absolute https URL', code);
    }
}
function isAllowedHost(hostname, baselineHost) {
    const host = hostname.toLowerCase();
    if (baselineHost && host === baselineHost.toLowerCase()) {
        return true;
    }
    return ALLOWED_INFERENCE_DOMAIN_SUFFIXES.some((suffix) => host === suffix.slice(1) || host.endsWith(suffix));
}
function endpoint(cfg, e) {
    const base = cfg.inferenceEndpoint;
    if (!base)
        throw fromConfigError('THETA_INFERENCE_ENDPOINT missing', 'MISSING_THETA_INFERENCE_ENDPOINT');
    const baseline = parseEndpoint(base, 'INVALID_THETA_INFERENCE_ENDPOINT');
    const target = parseEndpoint(e ?? base, 'INVALID_THETA_INFERENCE_ENDPOINT_OVERRIDE');
    if (!isAllowedHost(target.hostname, baseline.hostname)) {
        throw fromConfigError('Inference endpoint override host is not allowed. Use THETA_INFERENCE_ENDPOINT host or a thetaedgecloud.com host.', 'UNSAFE_THETA_INFERENCE_ENDPOINT_OVERRIDE');
    }
    return target.href.replace(/\/$/, '');
}
function auth(cfg, a) {
    return a ?? cfg.inferenceAuth;
}
function net(cfg, service, authOverride) {
    return {
        service,
        auth: authOverride,
        timeoutMs: cfg.httpTimeoutMs,
        maxRetries: cfg.httpMaxRetries,
        retryBackoffMs: cfg.httpRetryBackoffMs
    };
}
export const edgecloudInferenceClient = {
    listModels: (cfg, e, a) => getJson(`${endpoint(cfg, e)}/v1/models`, net(cfg, 'edgecloud-inference', auth(cfg, a))),
    chat: (cfg, body, e, a) => postJson(`${endpoint(cfg, e)}/v1/chat/completions`, body, net(cfg, 'edgecloud-inference', auth(cfg, a)))
};
