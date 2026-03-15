import { loadConfig } from '../config.js';
import { deployments } from '../commands/deployments.js';
import { healthCheck } from '../commands/health.js';
import { inference } from '../commands/inference.js';
import { ondemand } from '../commands/ondemand.js';
import { video } from '../commands/video.js';
import { fromConfigError, summarizeError } from '../errors.js';
import { redactObject } from '../redaction.js';
import { clampFiniteInt } from '../utils/integers.js';
import { resolveThetaInferenceAuth, resolveThetaOnDemandToken } from './secretResolver.js';
const IDENTIFIER_PATTERN = /^[A-Za-z0-9._:-]+$/;
const PROJECT_ID_PATTERN = /^prj_[A-Za-z0-9_]+$/;
function coerceBool(value, fallback) {
    if (value === undefined)
        return fallback;
    const normalized = value.trim().toLowerCase();
    if (['1', 'true', 'yes', 'on'].includes(normalized))
        return true;
    if (['0', 'false', 'no', 'off'].includes(normalized))
        return false;
    return fallback;
}
function requireObject(value, field, code = 'INVALID_FIELD_TYPE') {
    if (!value || typeof value !== 'object' || Array.isArray(value)) {
        throw fromConfigError(`${field} must be an object`, code);
    }
    return value;
}
function requireText(value, field, code = 'INVALID_FIELD') {
    if (value === undefined || value === null) {
        throw fromConfigError(`${field} is required`, code);
    }
    const text = String(value).trim();
    if (!text) {
        throw fromConfigError(`${field} is required`, code);
    }
    return text;
}
function requireIdentifier(value, field, code = 'INVALID_IDENTIFIER') {
    const text = requireText(value, field, code);
    if (!IDENTIFIER_PATTERN.test(text)) {
        throw fromConfigError(`${field} must contain only letters, numbers, dot, underscore, colon, and hyphen`, code);
    }
    return text;
}
function requireProjectId(value) {
    const projectId = requireText(value, 'projectId', 'MISSING_THETA_EC_PROJECT_ID');
    if (!PROJECT_ID_PATTERN.test(projectId)) {
        throw fromConfigError('projectId must match prj_* format from thetaedgecloud.com', 'INVALID_THETA_EC_PROJECT_ID');
    }
    return projectId;
}
function requireNonNegativeInt(value, field, code = 'INVALID_INTEGER') {
    const parsed = Number(value);
    if (!Number.isInteger(parsed) || parsed < 0) {
        throw fromConfigError(`${field} must be a non-negative integer`, code);
    }
    return parsed;
}
function requirePositiveInt(value, field, code = 'INVALID_INTEGER') {
    const parsed = Number(value);
    if (!Number.isInteger(parsed) || parsed <= 0) {
        throw fromConfigError(`${field} must be a positive integer`, code);
    }
    return parsed;
}
function rejectEndpointOverride(args) {
    if (args?.endpoint !== undefined && String(args.endpoint).trim() !== '') {
        throw fromConfigError('args.endpoint override is disabled for security. Set THETA_INFERENCE_ENDPOINT instead.', 'INFERENCE_ENDPOINT_OVERRIDE_DISABLED');
    }
}
async function buildRuntimeConfig(ctx) {
    const base = loadConfig();
    const env = ctx.env ?? {};
    const onDemandApiToken = await resolveThetaOnDemandToken(ctx, base.onDemandApiToken);
    const inferenceAuth = await resolveThetaInferenceAuth(ctx, base.inferenceAuth);
    return {
        ...base,
        dryRun: coerceBool(env.THETA_DRY_RUN, base.dryRun),
        edgecloudApiKey: env.THETA_EC_API_KEY ?? base.edgecloudApiKey,
        edgecloudProjectId: env.THETA_EC_PROJECT_ID ?? base.edgecloudProjectId,
        edgecloudOrgId: env.THETA_ORG_ID ?? base.edgecloudOrgId,
        videoSaId: env.THETA_VIDEO_SA_ID ?? base.videoSaId,
        videoSaSecret: env.THETA_VIDEO_SA_SECRET ?? base.videoSaSecret,
        inferenceEndpoint: env.THETA_INFERENCE_ENDPOINT ?? base.inferenceEndpoint,
        inferenceAuth,
        onDemandApiToken,
        httpTimeoutMs: clampFiniteInt(env.THETA_HTTP_TIMEOUT_MS, base.httpTimeoutMs, 1000, 120000),
        httpMaxRetries: clampFiniteInt(env.THETA_HTTP_MAX_RETRIES, base.httpMaxRetries, 0, 6),
        httpRetryBackoffMs: clampFiniteInt(env.THETA_HTTP_RETRY_BACKOFF_MS, base.httpRetryBackoffMs, 25, 10000)
    };
}
function requireFields(args, fields) {
    if (!args || typeof args !== 'object') {
        throw fromConfigError('Command args must be an object', 'INVALID_COMMAND_ARGS');
    }
    for (const field of fields) {
        if (!(field in args) || args[field] === undefined || args[field] === null || args[field] === '') {
            throw fromConfigError(`Missing required field: ${field}`, 'MISSING_REQUIRED_FIELD');
        }
    }
}
function resolveProjectId(cfg, args) {
    const projectId = args?.projectId ?? cfg.edgecloudProjectId;
    if (!projectId)
        throw fromConfigError('projectId missing. Set THETA_EC_PROJECT_ID or pass args.projectId. Find it in thetaedgecloud.com -> Account -> Projects (prj_...).', 'MISSING_THETA_EC_PROJECT_ID');
    return requireProjectId(projectId);
}
function resolveDeleteTarget(args) {
    if (args?.deploymentId)
        return { deploymentId: requireIdentifier(args.deploymentId, 'deploymentId', 'INVALID_DEPLOYMENT_ID') };
    if (args?.shard !== undefined && args?.suffix !== undefined) {
        return {
            shard: requireNonNegativeInt(args.shard, 'shard', 'INVALID_SHARD'),
            suffix: requireIdentifier(args.suffix, 'suffix', 'INVALID_SUFFIX')
        };
    }
    throw fromConfigError('For theta.deployments.delete pass deploymentId OR shard + suffix.', 'MISSING_DEPLOYMENT_DELETE_TARGET');
}
async function probeCapability(name, probe, required, notes = undefined) {
    try {
        const result = await probe();
        return { name, configured: true, verified: true, required, notes, sample: result ? { keys: Object.keys(result).slice(0, 8) } : undefined };
    }
    catch (error) {
        return { name, configured: true, verified: false, required, notes, error: summarizeError(error) };
    }
}
async function authCapabilities(cfg, args = {}) {
    rejectEndpointOverride(args);
    const overrideOrgId = args.orgId ? requireIdentifier(args.orgId, 'orgId', 'INVALID_THETA_ORG_ID') : undefined;
    const caps = [];
    const controllerConfigured = Boolean(cfg.edgecloudApiKey && cfg.edgecloudProjectId);
    if (!controllerConfigured) {
        caps.push({
            name: 'controller.project',
            configured: false,
            verified: false,
            required: ['THETA_EC_API_KEY', 'THETA_EC_PROJECT_ID'],
            notes: 'Project-scoped controller APIs (deployments/templates/cluster/storage/chatbot listings).'
        });
    }
    else {
        caps.push(await probeCapability('controller.project', () => deployments.list(cfg, cfg.edgecloudProjectId), ['THETA_EC_API_KEY', 'THETA_EC_PROJECT_ID'], 'Project-scoped controller APIs.'));
    }
    const balanceOrgId = overrideOrgId ?? cfg.edgecloudOrgId;
    if (!controllerConfigured || !balanceOrgId) {
        caps.push({
            name: 'billing.balance',
            configured: false,
            verified: false,
            required: ['THETA_EC_API_KEY', 'THETA_ORG_ID'],
            notes: 'Org credit balance lookup.'
        });
    }
    else {
        caps.push(await probeCapability('billing.balance', () => deployments.balance(cfg, balanceOrgId), ['THETA_EC_API_KEY', 'THETA_ORG_ID'], 'Org credit balance lookup.'));
    }
    caps.push(await probeCapability('ondemand.catalog', () => ondemand.listServices(cfg), [], 'Public on-demand model catalog.'));
    if (!cfg.onDemandApiToken) {
        caps.push({
            name: 'ondemand.inference',
            configured: false,
            verified: false,
            required: ['THETA_ONDEMAND_API_TOKEN or THETA_ONDEMAND_API_KEY'],
            notes: 'On-demand infer/status/poll commands.'
        });
    }
    else {
        try {
            await ondemand.inputPresignedUrls(cfg, 'flux');
            caps.push({
                name: 'ondemand.inference',
                configured: true,
                verified: true,
                required: ['THETA_ONDEMAND_API_TOKEN or THETA_ONDEMAND_API_KEY'],
                notes: 'On-demand infer/status/poll commands.'
            });
        }
        catch (error) {
            caps.push({
                name: 'ondemand.inference',
                configured: true,
                verified: false,
                required: ['THETA_ONDEMAND_API_TOKEN or THETA_ONDEMAND_API_KEY'],
                notes: 'Auth probe uses input presigned URL endpoint; success verifies token scope.',
                error: summarizeError(error)
            });
        }
    }
    const infEndpoint = cfg.inferenceEndpoint;
    if (!infEndpoint) {
        caps.push({
            name: 'inference.endpoint',
            configured: false,
            verified: false,
            required: ['THETA_INFERENCE_ENDPOINT', 'THETA_INFERENCE_AUTH_TOKEN or THETA_INFERENCE_AUTH_USER/PASS'],
            notes: 'Dedicated endpoint model/chat commands.'
        });
    }
    else {
        caps.push(await probeCapability('inference.endpoint', () => inference.models(cfg), ['THETA_INFERENCE_ENDPOINT', 'THETA_INFERENCE_AUTH_TOKEN or THETA_INFERENCE_AUTH_USER/PASS'], 'Dedicated endpoint model/chat commands.'));
    }
    if (!cfg.videoSaId || !cfg.videoSaSecret) {
        caps.push({
            name: 'video.api',
            configured: false,
            verified: false,
            required: ['THETA_VIDEO_SA_ID', 'THETA_VIDEO_SA_SECRET'],
            notes: 'Video service commands.'
        });
    }
    else {
        caps.push(await probeCapability('video.api', () => video.videoList(cfg, cfg.videoSaId, 1, 1), ['THETA_VIDEO_SA_ID', 'THETA_VIDEO_SA_SECRET'], 'Video service commands.'));
    }
    return {
        mode: 'api-key-first',
        dryRun: cfg.dryRun,
        timestamp: new Date().toISOString(),
        capabilities: caps,
        summary: {
            configured: caps.filter((c) => c.configured).length,
            verified: caps.filter((c) => c.verified).length,
            total: caps.length
        }
    };
}
const commandRegistry = {
    'theta.health': {
        schema: { command: 'theta.health', description: 'EdgeCloud health check via controller VM listing', required: [] },
        handler: (cfg) => healthCheck(cfg)
    },
    'theta.auth.capabilities': {
        schema: { command: 'theta.auth.capabilities', description: 'Return command-family capabilities for current credential set', required: [] },
        handler: (cfg, args) => authCapabilities(cfg, args)
    },
    'theta.setup': {
        schema: { command: 'theta.setup', description: 'Show first-run setup checklist and where to create Theta API keys', required: [] },
        handler: () => ({
            mode: 'api-key-first',
            checklist: [
                'Log in at https://www.thetaedgecloud.com/',
                'Go to Account -> Projects and select your project.',
                'Click Create API Key and copy the project API key.',
                'Set THETA_EC_API_KEY and THETA_EC_PROJECT_ID in OpenClaw.',
                'Recommended: for on-demand image/video infer, create On-demand API key/token and set THETA_ONDEMAND_API_KEY (or THETA_ONDEMAND_API_TOKEN).',
                'Run theta.auth.capabilities to verify configured command families.'
            ],
            env: {
                baselineRequired: ['THETA_EC_API_KEY', 'THETA_EC_PROJECT_ID'],
                optionalByFeature: {
                    billing: ['THETA_ORG_ID'],
                    ondemand: ['THETA_ONDEMAND_API_KEY or THETA_ONDEMAND_API_TOKEN'],
                    dedicatedInference: ['THETA_INFERENCE_ENDPOINT', 'THETA_INFERENCE_AUTH_TOKEN or THETA_INFERENCE_AUTH_USER/PASS'],
                    video: ['THETA_VIDEO_SA_ID', 'THETA_VIDEO_SA_SECRET']
                }
            },
            links: {
                thetaDashboard: 'https://www.thetaedgecloud.com/',
                apiKeyDoc: 'https://docs.thetatoken.org/docs/edgecloud-api-keys'
            }
        })
    },
    'theta.inference.models': {
        schema: { command: 'theta.inference.models', description: 'List models from dedicated inference endpoint', required: [] },
        handler: (cfg, args) => {
            rejectEndpointOverride(args);
            return inference.models(cfg);
        }
    },
    'theta.inference.chat': {
        schema: { command: 'theta.inference.chat', description: 'Run chat completion on dedicated inference endpoint', required: ['body'] },
        handler: (cfg, args) => {
            rejectEndpointOverride(args);
            const body = requireObject(args.body, 'body', 'INVALID_CHAT_BODY');
            return inference.chat(cfg, body);
        }
    },
    'theta.ondemand.listServices': {
        schema: { command: 'theta.ondemand.listServices', description: 'List supported on-demand services', required: [] },
        handler: (cfg) => ondemand.listServices(cfg)
    },
    'theta.ondemand.infer': {
        schema: { command: 'theta.ondemand.infer', description: 'Create on-demand infer request', required: ['service', 'payload'] },
        handler: (cfg, args) => ondemand.infer(cfg, requireIdentifier(args.service, 'service', 'INVALID_ONDEMAND_SERVICE'), args.payload)
    },
    'theta.ondemand.status': {
        schema: { command: 'theta.ondemand.status', description: 'Get on-demand infer request status', required: ['requestId'] },
        handler: (cfg, args) => ondemand.status(cfg, requireIdentifier(args.requestId, 'requestId', 'INVALID_ONDEMAND_REQUEST_ID'))
    },
    'theta.ondemand.inputPresignedUrls': {
        schema: { command: 'theta.ondemand.inputPresignedUrls', description: 'Create presigned URLs for on-demand inputs', required: ['service'] },
        handler: (cfg, args) => ondemand.inputPresignedUrls(cfg, requireIdentifier(args.service, 'service', 'INVALID_ONDEMAND_SERVICE'))
    },
    'theta.ondemand.pollUntilDone': {
        schema: { command: 'theta.ondemand.pollUntilDone', description: 'Poll on-demand request until terminal state', required: ['requestId'] },
        handler: (cfg, args) => ondemand.pollUntilDone(cfg, requireIdentifier(args.requestId, 'requestId', 'INVALID_ONDEMAND_REQUEST_ID'), args.options ? requireObject(args.options, 'options', 'INVALID_POLL_OPTIONS') : undefined)
    },
    'theta.deployments.list': {
        schema: { command: 'theta.deployments.list', description: 'List deployments for project', required: [] },
        handler: (cfg, args) => deployments.list(cfg, resolveProjectId(cfg, args))
    },
    'theta.deployments.create': {
        schema: { command: 'theta.deployments.create', description: 'Create deployment in project', required: ['payload'] },
        handler: (cfg, args) => {
            const payload = requireObject(args.payload, 'payload', 'INVALID_DEPLOYMENT_PAYLOAD');
            return deployments.create(cfg, {
                ...payload,
                project_id: payload.project_id ? requireProjectId(payload.project_id) : resolveProjectId(cfg, args)
            });
        }
    },
    'theta.deployments.stop': {
        schema: { command: 'theta.deployments.stop', description: 'Stop deployment by shard/suffix', required: ['shard', 'suffix'] },
        handler: (cfg, args) => deployments.stop(cfg, resolveProjectId(cfg, args), requireNonNegativeInt(args.shard, 'shard', 'INVALID_SHARD'), requireIdentifier(args.suffix, 'suffix', 'INVALID_SUFFIX'))
    },
    'theta.deployments.delete': {
        schema: { command: 'theta.deployments.delete', description: 'Delete deployment by deploymentId OR shard/suffix', required: [] },
        handler: (cfg, args) => {
            const projectId = resolveProjectId(cfg, args);
            const target = resolveDeleteTarget(args);
            return deployments.delete(cfg, projectId, target.shard, target.suffix, target.deploymentId);
        }
    },
    'theta.deployments.listVm': {
        schema: { command: 'theta.deployments.listVm', description: 'List EdgeCloud VM types', required: [] },
        handler: (cfg) => deployments.listVm(cfg)
    },
    'theta.billing.balance': {
        schema: { command: 'theta.billing.balance', description: 'Get org credit balance (API key scoped)', required: [] },
        handler: (cfg, args) => deployments.balance(cfg, args.orgId ? requireIdentifier(args.orgId, 'orgId', 'INVALID_THETA_ORG_ID') : undefined)
    },
    'theta.deployments.listStandard': {
        schema: { command: 'theta.deployments.listStandard', description: 'List standard deployment templates by category', required: ['category'] },
        handler: (cfg, args) => deployments.listStandard(cfg, requireIdentifier(args.category, 'category', 'INVALID_TEMPLATE_CATEGORY'), args.page === undefined ? 0 : requireNonNegativeInt(args.page, 'page', 'INVALID_PAGE'), args.number === undefined ? 50 : requirePositiveInt(args.number, 'number', 'INVALID_PAGE_SIZE'))
    },
    'theta.deployments.listCustom': {
        schema: { command: 'theta.deployments.listCustom', description: 'List custom templates for project', required: [] },
        handler: (cfg, args) => deployments.listCustom(cfg, resolveProjectId(cfg, args))
    },
    'theta.ai.dedicatedDeployments.list': {
        schema: { command: 'theta.ai.dedicatedDeployments.list', description: 'List dedicated deployments for project', required: [] },
        handler: (cfg, args) => deployments.listDedicated(cfg, resolveProjectId(cfg, args))
    },
    'theta.ai.jupyter.list': {
        schema: { command: 'theta.ai.jupyter.list', description: 'List Jupyter notebook deployments', required: [] },
        handler: (cfg, args) => deployments.listJupyter(cfg, resolveProjectId(cfg, args))
    },
    'theta.ai.gpuNode.list': {
        schema: { command: 'theta.ai.gpuNode.list', description: 'List GPU node deployments', required: [] },
        handler: (cfg, args) => deployments.listGpuNodes(cfg, resolveProjectId(cfg, args))
    },
    'theta.ai.gpuCluster.list': {
        schema: { command: 'theta.ai.gpuCluster.list', description: 'List GPU clusters', required: [] },
        handler: (cfg, args) => deployments.listClusters(cfg, resolveProjectId(cfg, args))
    },
    'theta.ai.storage.list': {
        schema: { command: 'theta.ai.storage.list', description: 'List persistent storage claims', required: [] },
        handler: (cfg, args) => deployments.listStorageClaims(cfg, resolveProjectId(cfg, args), args.page === undefined ? 1 : requirePositiveInt(args.page, 'page', 'INVALID_PAGE'), args.number === undefined ? 20 : requirePositiveInt(args.number, 'number', 'INVALID_PAGE_SIZE'))
    },
    'theta.ai.agent.list': {
        schema: { command: 'theta.ai.agent.list', description: 'List AI agent (RAG chatbot) resources', required: [] },
        handler: (cfg, args) => deployments.listChatbots(cfg, resolveProjectId(cfg, args))
    },
    'theta.video.list': {
        schema: { command: 'theta.video.list', description: 'List videos for service account (defaults to THETA_VIDEO_SA_ID when omitted)', required: [] },
        handler: (cfg, args) => {
            const serviceAccountId = args.serviceAccountId ?? cfg.videoSaId;
            if (!serviceAccountId) {
                throw fromConfigError('serviceAccountId missing. Pass args.serviceAccountId or set THETA_VIDEO_SA_ID.', 'MISSING_THETA_VIDEO_SA_ID');
            }
            return video.videoList(cfg, requireIdentifier(serviceAccountId, 'serviceAccountId', 'INVALID_SERVICE_ACCOUNT_ID'), args.page === undefined ? 1 : requirePositiveInt(args.page, 'page', 'INVALID_PAGE'), args.number === undefined ? 10 : requirePositiveInt(args.number, 'number', 'INVALID_PAGE_SIZE'));
        }
    },
    'theta.video.uploadCreate': {
        schema: { command: 'theta.video.uploadCreate', description: 'Create Theta Video upload session', required: [] },
        handler: (cfg) => video.uploadCreate(cfg)
    },
    'theta.video.videoCreate': {
        schema: { command: 'theta.video.videoCreate', description: 'Create Theta Video transcoding job', required: ['payload'] },
        handler: (cfg, args) => video.videoCreate(cfg, requireObject(args.payload, 'payload', 'INVALID_VIDEO_PAYLOAD'))
    },
    'theta.video.videoGet': {
        schema: { command: 'theta.video.videoGet', description: 'Get Theta Video job by videoId', required: ['videoId'] },
        handler: (cfg, args) => video.videoGet(cfg, requireIdentifier(args.videoId, 'videoId', 'INVALID_VIDEO_ID'))
    },
    'theta.video.streamCreate': {
        schema: { command: 'theta.video.streamCreate', description: 'Create Theta Video livestream', required: ['payload'] },
        handler: (cfg, args) => video.streamCreate(cfg, requireObject(args.payload, 'payload', 'INVALID_STREAM_PAYLOAD'))
    },
    'theta.video.streamGet': {
        schema: { command: 'theta.video.streamGet', description: 'Get Theta Video stream by streamId', required: ['streamId'] },
        handler: (cfg, args) => video.streamGet(cfg, requireIdentifier(args.streamId, 'streamId', 'INVALID_STREAM_ID'))
    },
    'theta.video.ingestor.list': {
        schema: { command: 'theta.video.ingestor.list', description: 'List available Theta Video ingestors', required: [] },
        handler: (cfg) => video.ingestorList(cfg)
    },
    'theta.video.ingestor.select': {
        schema: { command: 'theta.video.ingestor.select', description: 'Select Theta Video ingestor', required: ['ingestorId'] },
        handler: (cfg, args) => video.ingestorSelect(cfg, requireIdentifier(args.ingestorId, 'ingestorId', 'INVALID_INGESTOR_ID'), args.body ? requireObject(args.body, 'body', 'INVALID_INGESTOR_BODY') : {})
    },
};
const onDemandTokenCommands = new Set([
    'theta.ondemand.infer',
    'theta.ondemand.status',
    'theta.ondemand.inputPresignedUrls',
    'theta.ondemand.pollUntilDone'
]);
export const thetaRuntimeCommandSchemas = Object.fromEntries(Object.entries(commandRegistry).map(([cmd, reg]) => [cmd, reg.schema]));
export function listThetaRuntimeCommands() {
    return Object.keys(commandRegistry).sort();
}
export async function executeThetaRuntimeCommand(args, ctx = {}) {
    if (!args || typeof args !== 'object') {
        throw new Error('Command args must be an object');
    }
    const registration = commandRegistry[args.command];
    if (!registration) {
        throw new Error(`Unsupported theta runtime command: ${args.command}`);
    }
    requireFields(args, registration.schema.required);
    const cfg = await buildRuntimeConfig(ctx);
    if (onDemandTokenCommands.has(args.command) && !cfg.dryRun && !cfg.onDemandApiToken) {
        throw fromConfigError('On-demand API key/token missing. Set THETA_ONDEMAND_API_KEY (or THETA_ONDEMAND_API_TOKEN). You can create it from Theta dashboard under On-demand Model APIs -> API Key.', 'MISSING_THETA_ONDEMAND_API_TOKEN');
    }
    const result = await registration.handler(cfg, args);
    return redactObject(result);
}
