import { onDemandApiClient } from '../clients/ondemandApi.js';
import { sleep } from '../clients/http.js';
import { isStructuredError, summarizeError } from '../errors.js';
import { clampFiniteInt } from '../utils/integers.js';
import { listOnDemandServices, ONDEMAND_SERVICE_CATALOG } from './ondemandCatalog.js';
function getFirstInferRequest(payload) {
    if (!payload || typeof payload !== 'object')
        return undefined;
    const body = payload.body;
    if (!body?.infer_requests?.length)
        return undefined;
    return body.infer_requests[0];
}
function isTerminal(state) {
    return state === 'success' || state === 'error' || state === 'failed' || state === 'cancelled';
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
function resolveVideoLikeInput(inferRequest) {
    const input = inferRequest?.input;
    if (!input || typeof input !== 'object')
        return undefined;
    return input;
}
function deriveAdaptivePollTimeoutMs(inferRequest) {
    const input = resolveVideoLikeInput(inferRequest);
    const frames = readPositiveInt(input?.frames);
    if (!frames)
        return undefined;
    const fps = readPositiveInt(input?.fps) ?? 10;
    const renderSeconds = Math.max(1, Math.ceil(frames / Math.max(1, fps)));
    const queueAndVarianceBufferMs = 240000;
    const frameScaledMs = frames * 4000;
    const durationScaledMs = renderSeconds * 60000;
    const derivedMs = queueAndVarianceBufferMs + Math.max(frameScaledMs, durationScaledMs);
    const roundedMs = roundUpMs(derivedMs, 30000);
    return Math.min(1800000, Math.max(360000, roundedMs));
}
function withCatalogFallback(reason, warning) {
    return listOnDemandServices().map((s) => ({
        ...s,
        source: 'catalog',
        fallbackReason: reason,
        warning
    }));
}
export const ondemand = {
    catalog: ONDEMAND_SERVICE_CATALOG,
    listServices: async (cfg) => {
        try {
            const payload = await onDemandApiClient.listServices(cfg);
            const services = payload?.body?.services;
            if (Array.isArray(services) && services.length > 0) {
                return services
                    .map((s) => ({
                    name: s?.name ?? s?.alias ?? 'unknown',
                    service: s?.alias ?? s?.name ?? 'unknown',
                    templateId: s?.template_id,
                    workloadType: s?.workload_type,
                    rank: s?.rank,
                    source: 'live'
                }))
                    .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0));
            }
            return withCatalogFallback('live-empty', 'Live on-demand catalog returned no services; using embedded catalog fallback.');
        }
        catch (error) {
            const reason = isStructuredError(error) && error.code.startsWith('HTTP_')
                ? 'live-http-error'
                : 'network-or-parse-error';
            return withCatalogFallback(reason, `Live on-demand catalog unavailable; using embedded catalog fallback (${summarizeError(error)}).`);
        }
    },
    infer: (cfg, service, payload) => cfg.dryRun ? { dryRun: true, service, payload } : onDemandApiClient.createInferRequest(cfg, service, payload),
    status: (cfg, requestId) => onDemandApiClient.getInferRequest(cfg, requestId),
    inputPresignedUrls: (cfg, service) => cfg.dryRun ? { dryRun: true, service } : onDemandApiClient.createInputPresignedUrls(cfg, service),
    pollUntilDone: async (cfg, requestId, opts = {}) => {
        if (!requestId)
            throw new Error('requestId is required');
        const intervalMs = clampFiniteInt(opts.intervalMs, 3000, 100, 60000);
        const explicitTimeoutMs = opts.timeoutMs === undefined
            ? undefined
            : clampFiniteInt(opts.timeoutMs, 120000, 1000, 3600000);
        let timeoutMs = explicitTimeoutMs ?? 120000;
        const maxAttempts = clampFiniteInt(opts.maxAttempts, 1000, 1, 20000);
        const startedAt = Date.now();
        let attempts = 0;
        let lastResult;
        while (attempts < maxAttempts) {
            const elapsedBeforeRequest = Date.now() - startedAt;
            if (elapsedBeforeRequest >= timeoutMs) {
                return {
                    attempts,
                    elapsedMs: elapsedBeforeRequest,
                    terminalState: 'timeout',
                    result: lastResult
                };
            }
            attempts += 1;
            const result = await onDemandApiClient.getInferRequest(cfg, requestId);
            lastResult = result;
            const inferRequest = getFirstInferRequest(result);
            if (explicitTimeoutMs === undefined) {
                const adaptiveTimeoutMs = deriveAdaptivePollTimeoutMs(inferRequest);
                if (adaptiveTimeoutMs !== undefined) {
                    timeoutMs = adaptiveTimeoutMs;
                }
            }
            if (isTerminal(inferRequest?.state)) {
                return {
                    attempts,
                    elapsedMs: Date.now() - startedAt,
                    terminalState: inferRequest?.state,
                    result
                };
            }
            const elapsedAfterRequest = Date.now() - startedAt;
            if (elapsedAfterRequest >= timeoutMs) {
                return {
                    attempts,
                    elapsedMs: elapsedAfterRequest,
                    terminalState: 'timeout',
                    result
                };
            }
            const sleepMs = Math.min(intervalMs, Math.max(0, timeoutMs - elapsedAfterRequest));
            if (sleepMs > 0) {
                await sleep(sleepMs);
            }
        }
        return {
            attempts,
            elapsedMs: Date.now() - startedAt,
            terminalState: 'max-attempts',
            result: lastResult
        };
    }
};
