import { redact } from './redaction.js';
const MAX_MESSAGE_LEN = 280;
const MAX_SUMMARY_LEN = 220;
export function thetaError(input) {
    return input;
}
export function sanitizeHttpErrorMessage(message) {
    if (!message)
        return 'HTTP request failed';
    let out = message
        .replace(/\s+/g, ' ')
        .replace(/\b(Bearer|Basic)\s+([A-Za-z0-9\-._~+/]+=*)/gi, (_m, scheme, token) => `${scheme} ${redact(token)}`)
        .replace(/\b(x-api-key|x-tva-sa-id|x-tva-sa-secret|authorization|api[-_]?key|apikey|token|secret|password|credential)\s*=\s*([^\s&]+)/gi, (_m, key, value) => `${key}=${redact(value)}`)
        .replace(/\b(x-api-key|x-tva-sa-id|x-tva-sa-secret|authorization|api[-_]?key|apikey|token|secret|password|credential)\s*:\s*([^\s,;]+)/gi, (_m, key, value) => `${key}: ${redact(value)}`)
        .trim();
    if (out.length > MAX_MESSAGE_LEN) {
        out = `${out.slice(0, MAX_MESSAGE_LEN - 3)}...`;
    }
    return out || 'HTTP request failed';
}
export function fromHttpError(service, endpoint, status, message) {
    return {
        code: `HTTP_${status}`,
        message: sanitizeHttpErrorMessage(message),
        retriable: status >= 500 || status === 429 || status === 408,
        service,
        endpoint,
        status
    };
}
export function isStructuredError(value) {
    if (!value || typeof value !== 'object')
        return false;
    const candidate = value;
    return typeof candidate.code === 'string' && typeof candidate.message === 'string' && typeof candidate.retriable === 'boolean';
}
export function fromTransportError(service, endpoint, error) {
    const asAny = error;
    const isTimeout = asAny?.name === 'AbortError';
    const message = sanitizeHttpErrorMessage(asAny?.message ?? String(error ?? 'Network request failed'));
    return {
        code: isTimeout ? 'HTTP_408' : 'NETWORK_ERROR',
        message,
        retriable: true,
        service,
        endpoint,
        status: isTimeout ? 408 : undefined
    };
}
export function fromConfigError(message, code = 'CONFIG_ERROR') {
    return {
        code,
        message: sanitizeHttpErrorMessage(message),
        retriable: false,
        service: 'theta-runtime',
        endpoint: 'config'
    };
}
export function summarizeError(error, maxLen = MAX_SUMMARY_LEN) {
    let message;
    if (!error) {
        message = 'unknown error';
    }
    else if (typeof error === 'string') {
        message = error;
    }
    else if (error instanceof Error) {
        message = error.message;
    }
    else if (typeof error === 'object') {
        const asObj = error;
        try {
            message = asObj.message ? String(asObj.message) : JSON.stringify(asObj);
        }
        catch {
            message = String(asObj);
        }
    }
    else {
        message = String(error);
    }
    const sanitized = sanitizeHttpErrorMessage(message);
    if (sanitized.length > maxLen) {
        return `${sanitized.slice(0, maxLen - 3)}...`;
    }
    return sanitized;
}
