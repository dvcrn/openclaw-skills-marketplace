export function clampFiniteInt(value, fallback, min = Number.MIN_SAFE_INTEGER, max = Number.MAX_SAFE_INTEGER) {
    if (value === undefined || value === null || value === '') {
        return fallback;
    }
    const parsed = typeof value === 'number' ? Math.trunc(value) : Number.parseInt(String(value), 10);
    if (!Number.isFinite(parsed)) {
        return fallback;
    }
    return Math.min(Math.max(parsed, min), max);
}
