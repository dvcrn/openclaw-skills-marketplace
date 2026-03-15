import { edgecloudInferenceClient } from '../clients/edgecloudInference.js';
import { isStructuredError, thetaError } from '../errors.js';
function annotateEndpointReadinessError(error) {
    if (isStructuredError(error) && (error.status === 404 || error.status === 502 || error.status === 503)) {
        throw thetaError({
            ...error,
            code: 'THETA_DEDICATED_ENDPOINT_UPSTREAM_UNREADY',
            retriable: true,
            message: `Dedicated inference endpoint is not ready upstream (HTTP ${error.status}). ` +
                'Fresh deployments can briefly return authenticated 404/502/503 during warm-up before the model service is fully ready. ' +
                'Retry with readiness backoff or verify endpoint health from Theta dashboard logs.'
        });
    }
    throw error;
}
export const inference = {
    models: async (cfg, endpoint) => {
        try {
            return await edgecloudInferenceClient.listModels(cfg, endpoint);
        }
        catch (error) {
            annotateEndpointReadinessError(error);
        }
    },
    chat: async (cfg, body, endpoint) => {
        if (cfg.dryRun)
            return { dryRun: true, endpoint: endpoint ?? cfg.inferenceEndpoint, body };
        try {
            return await edgecloudInferenceClient.chat(cfg, body, endpoint);
        }
        catch (error) {
            annotateEndpointReadinessError(error);
        }
    }
};
