import { deleteEmpty, getJson, postJson, putEmpty } from './http.js';
import { fromConfigError } from '../errors.js';
const BASE_CTRL = 'https://controller.thetaedgecloud.com';
const BASE_API = 'https://api.thetaedgecloud.com';
function apiKeyHeaders(cfg) {
    if (!cfg.edgecloudApiKey)
        throw fromConfigError('THETA_EC_API_KEY missing. In thetaedgecloud.com go to Account -> Projects -> select project -> Create API Key.', 'MISSING_THETA_EC_API_KEY');
    return { 'x-api-key': cfg.edgecloudApiKey };
}
function pathSegment(value, field, code) {
    if (value === undefined || value === null)
        throw fromConfigError(`${field} is required`, code);
    const raw = String(value).trim();
    if (!raw)
        throw fromConfigError(`${field} is required`, code);
    return encodeURIComponent(raw);
}
function buildUrl(base, path, params = {}) {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
        if (value === undefined || value === null)
            continue;
        if (Array.isArray(value)) {
            for (const entry of value) {
                if (entry !== undefined && entry !== null) {
                    query.append(key, String(entry));
                }
            }
            continue;
        }
        query.set(key, String(value));
    }
    const qs = query.toString();
    return `${base}${path}${qs ? `?${qs}` : ''}`;
}
function net(cfg, service, headers) {
    return {
        service,
        headers,
        timeoutMs: cfg.httpTimeoutMs,
        maxRetries: cfg.httpMaxRetries,
        retryBackoffMs: cfg.httpRetryBackoffMs
    };
}
export const edgecloudControllerClient = {
    listStandardTemplates: (cfg, category, page = 0, number = 50) => getJson(buildUrl(BASE_CTRL, '/deployment_template/list_standard_templates', { category, page, number }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg))),
    listCustomTemplates: (cfg, projectId) => getJson(buildUrl(BASE_CTRL, '/deployment_template/list_custom_templates', { project_id: projectId }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg))),
    listVmTypes: (cfg) => getJson(`${BASE_API}/resource/vm/list`, net(cfg, 'edgecloud-controller')),
    getBalance: (cfg, orgId) => {
        if (!orgId)
            throw fromConfigError('orgId is required (set THETA_ORG_ID or pass args.orgId)', 'MISSING_THETA_ORG_ID');
        return getJson(buildUrl(BASE_API, '/balance', { orgID: orgId }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg)));
    },
    createDeployment: (cfg, payload) => postJson(`${BASE_CTRL}/deployment`, payload, net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg))),
    listDeployments: (cfg, projectId) => getJson(buildUrl(BASE_CTRL, '/deployment/list', { project_id: projectId }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg))),
    listJupyterNotebooks: (cfg, projectId) => getJson(buildUrl(BASE_CTRL, '/deployment/list', { project_id: projectId, template_name: 'Jupyter Notebook' }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg))),
    listGpuNodes: (cfg, projectId) => getJson(buildUrl(BASE_CTRL, '/deployment/list', { project_id: projectId, template_name: 'GPU Node' }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg))),
    listDedicatedDeployments: (cfg, projectId) => getJson(buildUrl(BASE_CTRL, '/deployment/list', { project_id: projectId, not_template_name: ['Jupyter Notebook', 'GPU Node'] }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg))),
    listClusters: (cfg, projectId) => getJson(buildUrl(BASE_CTRL, '/cluster/list', { project_id: projectId }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg))),
    listStorageClaims: (cfg, projectId, page = 1, number = 20) => getJson(buildUrl(BASE_CTRL, '/volume/claim', { projectId, page, number }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg))),
    listChatbots: (cfg, projectId) => getJson(buildUrl(BASE_CTRL, '/chatbot/list', { project_id: projectId, number: 100 }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg))),
    stopDeployment: (cfg, projectId, shard, suffix) => putEmpty(buildUrl(BASE_CTRL, `/deployment/${pathSegment(shard, 'shard', 'INVALID_SHARD')}/${pathSegment(suffix, 'suffix', 'INVALID_SUFFIX')}/stop`, { project_id: projectId }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg))),
    deleteDeployment: (cfg, projectId, shard, suffix) => deleteEmpty(buildUrl(BASE_CTRL, `/deployment/${pathSegment(shard, 'shard', 'INVALID_SHARD')}/${pathSegment(suffix, 'suffix', 'INVALID_SUFFIX')}`, { project_id: projectId }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg))),
    deleteDeploymentBase: (cfg, projectId, deploymentId) => deleteEmpty(buildUrl(BASE_CTRL, `/deployment/base/${pathSegment(deploymentId, 'deploymentId', 'INVALID_DEPLOYMENT_ID')}`, { project_id: projectId }), net(cfg, 'edgecloud-controller', apiKeyHeaders(cfg)))
};
