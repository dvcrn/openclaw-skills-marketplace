import { getJson, postJson } from './http.js';
import { fromConfigError } from '../errors.js';
const BASE = 'https://ondemand.thetaedgecloud.com';
function onDemandBearerHeaders(cfg) {
    if (!cfg.onDemandApiToken)
        throw fromConfigError('THETA_ONDEMAND_API_TOKEN missing', 'MISSING_THETA_ONDEMAND_API_TOKEN');
    return {
        Authorization: `Bearer ${cfg.onDemandApiToken}`
    };
}
function segment(value, field, code) {
    if (value === undefined || value === null)
        throw fromConfigError(`${field} is required`, code);
    const raw = String(value).trim();
    if (!raw)
        throw fromConfigError(`${field} is required`, code);
    return encodeURIComponent(raw);
}
function roundUpMs(value, bucketMs) {
    return Math.ceil(value / bucketMs) * bucketMs;
}
function readPositiveInt(value) {
    const parsed = Number(value);
    if (!Number.isInteger(parsed) || parsed <= 0)
        return undefined;
    return parsed;
}
function resolveStepVideoFrames(payload) {
    const input = payload && typeof payload === 'object' && payload.input && typeof payload.input === 'object'
        ? payload.input
        : payload;
    if (!input || typeof input !== 'object')
        return undefined;
    return readPositiveInt(input.frames);
}
function resolveCreateInferTimeoutMs(cfg, service, payload) {
    if (String(service).trim().toLowerCase() !== 'step_video')
        return cfg.httpTimeoutMs;
    const frames = resolveStepVideoFrames(payload) ?? 30;
    const derivedMs = 120000 + (frames * 500);
    return Math.min(300000, Math.max(cfg.httpTimeoutMs, roundUpMs(derivedMs, 5000)));
}
function net(cfg, timeoutMs = cfg.httpTimeoutMs) {
    return {
        headers: onDemandBearerHeaders(cfg),
        service: 'theta-ondemand-api',
        timeoutMs,
        maxRetries: cfg.httpMaxRetries,
        retryBackoffMs: cfg.httpRetryBackoffMs
    };
}
export const onDemandApiClient = {
    listServices: (cfg) => getJson(`${BASE}/service/list?expand=template_id`, {
        service: 'theta-ondemand-api',
        timeoutMs: cfg?.httpTimeoutMs ?? 20000,
        maxRetries: cfg?.httpMaxRetries ?? 2,
        retryBackoffMs: cfg?.httpRetryBackoffMs ?? 250
    }),
    createInferRequest: (cfg, service, payload) => {
        const body = payload && typeof payload === 'object' && Object.prototype.hasOwnProperty.call(payload, 'input')
            ? payload
            : { input: payload };
        if (body?.input && typeof body.input === 'object' && body.input !== null && !Object.prototype.hasOwnProperty.call(body.input, 'stream') && Array.isArray(body.input.messages)) {
            body.input = { ...body.input, stream: false };
        }
        const timeoutMs = resolveCreateInferTimeoutMs(cfg, service, body);
        return postJson(`${BASE}/infer_request/${segment(service, 'service', 'INVALID_ONDEMAND_SERVICE')}`, body, net(cfg, timeoutMs));
    },
    getInferRequest: (cfg, requestId) => getJson(`${BASE}/infer_request/${segment(requestId, 'requestId', 'INVALID_ONDEMAND_REQUEST_ID')}`, net(cfg)),
    createInputPresignedUrls: (cfg, service) => postJson(`${BASE}/infer_request/${segment(service, 'service', 'INVALID_ONDEMAND_SERVICE')}/input_presigned_urls`, {}, net(cfg))
};
