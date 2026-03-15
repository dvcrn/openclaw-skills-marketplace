import { getJson, postJson, putJson } from './http.js';
import { fromConfigError } from '../errors.js';
const BASE = 'https://api.thetavideoapi.com';
function videoAuthHeaders(cfg) {
    if (!cfg.videoSaId || !cfg.videoSaSecret)
        throw fromConfigError('THETA_VIDEO_SA_ID / THETA_VIDEO_SA_SECRET missing', 'MISSING_THETA_VIDEO_CREDENTIALS');
    return { 'x-tva-sa-id': cfg.videoSaId, 'x-tva-sa-secret': cfg.videoSaSecret };
}
function segment(value, field, code) {
    if (value === undefined || value === null)
        throw fromConfigError(`${field} is required`, code);
    const raw = String(value).trim();
    if (!raw)
        throw fromConfigError(`${field} is required`, code);
    return encodeURIComponent(raw);
}
function buildQuery(params = {}) {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
        if (value === undefined || value === null)
            continue;
        query.set(key, String(value));
    }
    const qs = query.toString();
    return qs ? `?${qs}` : '';
}
function net(cfg, headers) {
    return {
        headers,
        service: 'theta-video',
        timeoutMs: cfg.httpTimeoutMs,
        maxRetries: cfg.httpMaxRetries,
        retryBackoffMs: cfg.httpRetryBackoffMs
    };
}
export const thetaVideoClient = {
    createUploadSession: (cfg) => postJson(`${BASE}/upload`, {}, net(cfg, videoAuthHeaders(cfg))),
    createVideo: (cfg, payload) => postJson(`${BASE}/video`, payload, net(cfg, videoAuthHeaders(cfg))),
    getVideo: (cfg, videoId) => getJson(`${BASE}/video/${segment(videoId, 'videoId', 'INVALID_VIDEO_ID')}`, net(cfg, videoAuthHeaders(cfg))),
    listVideos: (cfg, serviceAccountId, page = 1, number = 10) => getJson(`${BASE}/video/${segment(serviceAccountId, 'serviceAccountId', 'INVALID_SERVICE_ACCOUNT_ID')}/list${buildQuery({ page, number })}`, net(cfg, videoAuthHeaders(cfg))),
    createStream: (cfg, payload) => postJson(`${BASE}/stream`, payload, net(cfg, videoAuthHeaders(cfg))),
    getStream: (cfg, streamId) => getJson(`${BASE}/stream/${segment(streamId, 'streamId', 'INVALID_STREAM_ID')}`, net(cfg, videoAuthHeaders(cfg))),
    listIngestors: (cfg) => getJson(`${BASE}/ingestor/filter`, net(cfg, videoAuthHeaders(cfg))),
    selectIngestor: (cfg, ingestorId, body) => putJson(`${BASE}/ingestor/${segment(ingestorId, 'ingestorId', 'INVALID_INGESTOR_ID')}/select`, body, net(cfg, videoAuthHeaders(cfg)))
};
