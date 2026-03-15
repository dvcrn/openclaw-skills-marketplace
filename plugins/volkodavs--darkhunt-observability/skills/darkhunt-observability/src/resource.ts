import os from 'node:os';
import { Resource } from '@opentelemetry/resources';
import { INSTRUMENTATION_LIBRARY } from './types.js';

export function buildResource(
  serviceVersion?: string,
  processOwner?: string,
  deploymentEnv?: string,
  workspaceId?: string,
  applicationId?: string,
): Resource {
  const attrs: Record<string, string> = {
    'service.name': 'openclaw',
    'host.name': os.type(),
    'host.arch': os.arch(),
    'process.owner': processOwner ?? os.userInfo().username,
  };

  // Use OpenClaw version if available, fall back to plugin version
  attrs['service.version'] = serviceVersion || INSTRUMENTATION_LIBRARY.version;

  const runtime = typeof process !== 'undefined' && (process as NodeJS.Process).versions?.bun
    ? 'bun'
    : 'node';
  attrs['process.runtime.name'] = runtime;
  attrs['process.runtime.version'] = process.version ?? '';

  if (deploymentEnv) {
    attrs['deployment.environment'] = deploymentEnv;
  }
  if (workspaceId) {
    attrs['openclaw.workspace.id'] = workspaceId;
  }
  if (applicationId) {
    attrs['openclaw.application.id'] = applicationId;
  }

  return new Resource(attrs);
}
