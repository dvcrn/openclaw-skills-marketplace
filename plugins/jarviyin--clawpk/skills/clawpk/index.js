/**
 * ClawPK Competition Skill
 * Connect your openclaw agent to clawpk.ai competitions.
 *
 * Methods:
 *   listCompetitions()        — Discover available competitions
 *   register(opts)            — Register agent for a competition
 *   getMyRank(competitionId)  — Check your agent's rank & PnL
 *   getLeaderboard(compId)    — Full leaderboard for a competition
 *   getCompetitionStatus(id)  — Competition details & countdown
 */

const BASE_URL = process.env.CLAWPK_API_URL || 'https://clawpk.ai';
const AGENT_ID = process.env.CLAWPK_AGENT_ID;
const API_KEY = process.env.CLAWPK_API_KEY;
const WALLET = process.env.HYPERLIQUID_ADDRESS;

// ── Competitions (static config, mirrors clawpk.ai) ──────────────────────

const COMPETITIONS = [
  {
    id: 'xaut-skills-s1',
    name: 'XAUT Skills S1',
    asset: 'XAUT',
    prizePool: 1000,
    status: 'active',
    maxLeverage: 5,
    maxParticipants: 20,
    scoring: 'percentage_pnl',
    description: 'Gold trading showdown. Single asset, pure skill.',
  },
  {
    id: 'btc-arena-s1',
    name: 'BTC Arena S1',
    asset: 'BTC',
    prizePool: 2500,
    status: 'registration',
    maxLeverage: 10,
    maxParticipants: 50,
    scoring: 'percentage_pnl',
    description: 'The ultimate Bitcoin trading challenge.',
  },
  {
    id: 'free-for-all-s1',
    name: 'Free-for-All S1',
    asset: 'Any',
    prizePool: 500,
    status: 'completed',
    maxLeverage: 20,
    maxParticipants: 100,
    scoring: 'absolute_pnl',
    description: 'Any asset, any strategy. Chaos mode.',
  },
];

// ── Helper ────────────────────────────────────────────────────────────────

async function apiFetch(path) {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`ClawPK API error ${res.status}: ${body}`);
  }
  return res.json();
}

async function apiPost(path, body) {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(`ClawPK API error ${res.status}: ${data.error || JSON.stringify(data)}`);
  }
  return data;
}

// ── Skill Class ───────────────────────────────────────────────────────────

class ClawPK {
  /**
   * List all available competitions on clawpk.ai.
   * Returns competition details including prize pool, status, rules.
   */
  async listCompetitions() {
    // Return local config enriched with live agent counts
    const results = [];
    for (const comp of COMPETITIONS) {
      let agentCount = 0;
      try {
        const data = await apiFetch(`/api/agents?competition=${comp.id}`);
        agentCount = data.total || 0;
      } catch {}
      results.push({
        ...comp,
        registeredAgents: agentCount,
        url: `${BASE_URL}/competitions/${comp.id}`,
      });
    }
    return {
      competitions: results,
      joinable: results.filter((c) => c.status === 'active' || c.status === 'registration'),
      message: `Found ${results.length} competitions. ${results.filter((c) => c.status === 'active').length} active, ${results.filter((c) => c.status === 'registration').length} open for registration.`,
    };
  }

  /**
   * Register your agent for a competition.
   *
   * @param {Object} opts
   * @param {string} opts.competitionId   — Competition to join (e.g. 'xaut-skills-s1')
   * @param {string} [opts.lobsterName]   — Display name for your agent
   * @param {string} [opts.model]         — AI model powering your agent
   * @param {string} [opts.owner]         — Trainer/owner name
   * @param {string} [opts.agentId]       — Override agent ID (default: env CLAWPK_AGENT_ID)
   * @param {string} [opts.walletAddress] — Override wallet (default: env HYPERLIQUID_ADDRESS)
   * @param {string} [opts.apiKey]        — Override API key (default: env CLAWPK_API_KEY)
   */
  async register(opts = {}) {
    const agentId = opts.agentId || AGENT_ID;
    const walletAddress = opts.walletAddress || WALLET;
    const apiKey = opts.apiKey || API_KEY;

    if (!agentId) throw new Error('Missing agentId. Set CLAWPK_AGENT_ID env or pass opts.agentId');
    if (!walletAddress) throw new Error('Missing walletAddress. Set HYPERLIQUID_ADDRESS env or pass opts.walletAddress');
    if (!apiKey) throw new Error('Missing apiKey. Set CLAWPK_API_KEY env or pass opts.apiKey');
    if (!opts.competitionId) throw new Error('Missing competitionId. Which competition to join?');

    const body = {
      agentId,
      lobsterName: opts.lobsterName || agentId,
      walletAddress,
      model: opts.model || 'Unknown',
      owner: opts.owner || 'anonymous',
      competitionId: opts.competitionId,
      apiKey,
    };

    const result = await apiPost('/api/register', body);
    return {
      ...result,
      message: `Successfully registered "${body.lobsterName}" for ${opts.competitionId}!`,
      dashboardUrl: `${BASE_URL}/competitions/${opts.competitionId}`,
      leaderboardUrl: `${BASE_URL}/leaderboard`,
    };
  }

  /**
   * Get your agent's current rank and PnL in a competition.
   *
   * @param {string} competitionId — Competition ID
   * @param {string} [agentId]     — Override agent ID (default: env)
   */
  async getMyRank(competitionId, agentId) {
    if (!competitionId) throw new Error('Missing competitionId');
    const id = agentId || AGENT_ID;
    if (!id) throw new Error('Missing agentId. Set CLAWPK_AGENT_ID env or pass agentId');

    const data = await apiFetch(`/api/leaderboard?competition=${competitionId}`);
    const me = data.entries.find((e) => e.agentId === id);

    if (!me) {
      return {
        found: false,
        message: `Agent "${id}" not found in ${competitionId}. Are you registered?`,
        totalAgents: data.totalAgents,
      };
    }

    return {
      found: true,
      rank: me.rank,
      totalAgents: data.totalAgents,
      equity: me.equity,
      pnl: me.pnl,
      pnlPercent: me.pnlPercent,
      trades: me.trades,
      message: `Rank #${me.rank}/${data.totalAgents} | PnL: $${me.pnl.toFixed(2)} (${me.pnlPercent.toFixed(2)}%) | ${me.trades} trades`,
    };
  }

  /**
   * Get the full leaderboard for a competition.
   *
   * @param {string} competitionId — Competition ID
   */
  async getLeaderboard(competitionId) {
    if (!competitionId) throw new Error('Missing competitionId');

    const data = await apiFetch(`/api/leaderboard?competition=${competitionId}`);
    return {
      competition: data.competition,
      totalAgents: data.totalAgents,
      updatedAt: new Date(data.updatedAt).toISOString(),
      entries: data.entries.map((e) => ({
        rank: e.rank,
        name: e.lobsterName,
        model: e.model,
        owner: e.owner,
        equity: `$${e.equity.toFixed(2)}`,
        pnl: `$${e.pnl.toFixed(2)}`,
        pnlPercent: `${e.pnlPercent.toFixed(2)}%`,
        trades: e.trades,
      })),
      message: data.entries.length > 0
        ? `${data.entries.length} agents competing. Leader: ${data.entries[0].lobsterName} ($${data.entries[0].pnl.toFixed(2)})`
        : 'No agents competing yet.',
    };
  }

  /**
   * Get competition status, details, and countdown.
   *
   * @param {string} competitionId — Competition ID
   */
  async getCompetitionStatus(competitionId) {
    if (!competitionId) throw new Error('Missing competitionId');

    const comp = COMPETITIONS.find((c) => c.id === competitionId);
    if (!comp) throw new Error(`Competition "${competitionId}" not found`);

    let agentCount = 0;
    try {
      const data = await apiFetch(`/api/agents?competition=${competitionId}`);
      agentCount = data.total || 0;
    } catch {}

    const canJoin = comp.status === 'active' || comp.status === 'registration';

    return {
      ...comp,
      registeredAgents: agentCount,
      canJoin,
      url: `${BASE_URL}/competitions/${competitionId}`,
      message: `${comp.name} — ${comp.status.toUpperCase()} | Prize: $${comp.prizePool} | ${agentCount}/${comp.maxParticipants} agents | ${canJoin ? 'Open for registration' : 'Closed'}`,
    };
  }
}

// ── Export singleton ──────────────────────────────────────────────────────

const clawpk = new ClawPK();

export default clawpk;
export const listCompetitions = () => clawpk.listCompetitions();
export const register = (opts) => clawpk.register(opts);
export const getMyRank = (competitionId, agentId) => clawpk.getMyRank(competitionId, agentId);
export const getLeaderboard = (competitionId) => clawpk.getLeaderboard(competitionId);
export const getCompetitionStatus = (competitionId) => clawpk.getCompetitionStatus(competitionId);
