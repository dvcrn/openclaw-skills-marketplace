/**
 * tradesman-verify — OpenCorporates business entity lookup
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Standalone function for querying the OpenCorporates API.
 * Used internally by verifyBusinessEntityTool and by external
 * MCP tool integrations (e.g. contractor-verifier).
 */

import type { BusinessEntityClaims } from './types.js';

// ── Public types ───────────────────────────────────────────────────────────────

export interface BusinessEntityResult {
  found: boolean;
  isActive: boolean;
  name?: string;
  companyNumber?: string;
  jurisdiction?: string;
  incorporationDate?: string;
  currentStatus?: string;
  companyType?: string;
  /** Pre-formatted claims ready to pass to issueCredential / selfAttest */
  claims?: BusinessEntityClaims;
}

export type BusinessEntityError =
  | { kind: 'not_found'; businessName: string; jurisdiction: string }
  | { kind: 'rate_limit' }
  | { kind: 'auth_failed' }
  | { kind: 'network'; message: string }
  | { kind: 'api_error'; status: number };

export type BusinessEntityLookupResult =
  | { ok: true; data: BusinessEntityResult }
  | { ok: false; error: BusinessEntityError };

// ── Core lookup ────────────────────────────────────────────────────────────────

/**
 * Look up a business entity by name and jurisdiction via the OpenCorporates API.
 *
 * Returns the first matching company. For higher precision, pass the most
 * specific jurisdiction code available (e.g. "us_tx" rather than "us").
 *
 * @param businessName  Legal business name, e.g. "ABC Roofing LLC"
 * @param jurisdiction  OpenCorporates jurisdiction code, e.g. "us_tx", "gb", "ca_on"
 * @param apiKey        Optional override; falls back to OPENCORPORATES_API_KEY env var
 */
export async function lookupBusinessEntity(
  businessName: string,
  jurisdiction: string,
  apiKey?: string,
): Promise<BusinessEntityLookupResult> {
  const key = apiKey ?? process.env['OPENCORPORATES_API_KEY'];
  if (!key) {
    return {
      ok: false,
      error: { kind: 'auth_failed' },
    };
  }

  const url = new URL('https://api.opencorporates.com/v0.4/companies/search');
  url.searchParams.set('q', businessName);
  url.searchParams.set('jurisdiction_code', jurisdiction);
  url.searchParams.set('api_token', key);

  let response: Response;
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15_000);
    try {
      response = await fetch(url.toString(), {
        headers: {
          Accept: 'application/json',
          'User-Agent': 'tradesman-verify/0.1.0',
        },
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeout);
    }
  } catch (err: unknown) {
    return {
      ok: false,
      error: {
        kind: 'network',
        message: err instanceof Error ? err.message : String(err),
      },
    };
  }

  if (!response.ok) {
    if (response.status === 429) return { ok: false, error: { kind: 'rate_limit' } };
    if (response.status === 401) return { ok: false, error: { kind: 'auth_failed' } };
    return { ok: false, error: { kind: 'api_error', status: response.status } };
  }

  const data = (await response.json()) as {
    results?: { companies?: Array<{ company: Record<string, unknown> }> };
  };

  const companies = data?.results?.companies ?? [];
  if (companies.length === 0) {
    return { ok: false, error: { kind: 'not_found', businessName, jurisdiction } };
  }

  const company = companies[0]!.company;
  const isActive =
    (company['current_status'] as string | undefined)?.toLowerCase() === 'active';
  const verifiedAt = new Date().toISOString();

  const claims: BusinessEntityClaims = {
    businessName: (company['name'] as string | undefined) ?? businessName,
    companyNumber: company['company_number'] as string | undefined,
    jurisdiction: (company['jurisdiction_code'] as string | undefined) ?? jurisdiction,
    businessStatus: (company['current_status'] as string | undefined) ?? 'unknown',
    incorporationDate: company['incorporation_date'] as string | undefined,
    companyType: company['company_type'] as string | undefined,
    verificationSource: 'OpenCorporates',
    verifiedAt,
  };

  return {
    ok: true,
    data: {
      found: true,
      isActive,
      name: claims.businessName,
      companyNumber: claims.companyNumber,
      jurisdiction: claims.jurisdiction,
      incorporationDate: claims.incorporationDate,
      currentStatus: claims.businessStatus,
      companyType: claims.companyType,
      claims,
    },
  };
}
