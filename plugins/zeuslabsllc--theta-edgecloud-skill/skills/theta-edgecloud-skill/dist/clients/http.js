import { fromHttpError, fromTransportError, isStructuredError } from '../errors.js';
import { clampFiniteInt } from '../utils/integers.js';
const RETRIABLE_STATUS = new Set([408, 425, 429, 500, 502, 503, 504]);
function withAuth(headers = {}, auth) {
    if (!auth)
        return headers;
    if (auth.token)
        return { ...headers, Authorization: `Bearer ${auth.token}` };
    if (auth.user && auth.pass) {
        const basic = Buffer.from(`${auth.user}:${auth.pass}`).toString('base64');
        return { ...headers, Authorization: `Basic ${basic}` };
    }
    return headers;
}
function backoffDelayMs(attempt, baseMs) {
    return baseMs * Math.max(1, 2 ** (attempt - 1));
}
export const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
async function request(url, method, body, opts) {
    const timeoutMs = clampFiniteInt(opts?.timeoutMs, 20000, 1000, 120000);
    const maxRetries = clampFiniteInt(opts?.maxRetries, 2, 0, 6);
    const retryBackoffMs = clampFiniteInt(opts?.retryBackoffMs, 250, 25, 10000);
    for (let attempt = 0; attempt <= maxRetries; attempt += 1) {
        const canRetry = attempt < maxRetries;
        try {
            const signal = AbortSignal.timeout(timeoutMs);
            const res = await fetch(url, {
                method,
                headers: withAuth(opts?.headers, opts?.auth),
                body,
                signal
            });
            if (res.ok)
                return res;
            const errorBody = await res.text();
            if (canRetry && RETRIABLE_STATUS.has(res.status)) {
                await sleep(backoffDelayMs(attempt + 1, retryBackoffMs));
                continue;
            }
            throw fromHttpError(opts?.service ?? 'unknown', url, res.status, errorBody);
        }
        catch (error) {
            if (isStructuredError(error)) {
                throw error;
            }
            if (canRetry) {
                await sleep(backoffDelayMs(attempt + 1, retryBackoffMs));
                continue;
            }
            throw fromTransportError(opts?.service ?? 'unknown', url, error);
        }
    }
    throw fromTransportError(opts?.service ?? 'unknown', url, new Error('HTTP request failed after retries'));
}
export async function getJson(url, opts) {
    const res = await request(url, 'GET', undefined, opts);
    return res.json();
}
export async function postJson(url, body, opts) {
    const res = await request(url, 'POST', JSON.stringify(body), {
        ...opts,
        headers: { 'content-type': 'application/json', ...(opts?.headers ?? {}) }
    });
    return res.json();
}
async function parseResponseBody(res) {
    const contentType = res.headers.get('content-type') ?? '';
    if (contentType.includes('application/json')) {
        return res.json();
    }
    const text = await res.text();
    if (!text)
        return { status: 'success' };
    return { status: 'success', raw: text };
}
export async function putEmpty(url, opts) {
    const res = await request(url, 'PUT', undefined, opts);
    return parseResponseBody(res);
}
export async function putJson(url, body, opts) {
    const res = await request(url, 'PUT', JSON.stringify(body), {
        ...opts,
        headers: { 'content-type': 'application/json', ...(opts?.headers ?? {}) }
    });
    return res.json();
}
export async function deleteEmpty(url, opts) {
    const res = await request(url, 'DELETE', undefined, opts);
    return parseResponseBody(res);
}
