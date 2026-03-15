"use strict";
/**
 * Pyre Kit Intel
 *
 * Game-specific utility functions that compose torchsdk reads into
 * strategic intelligence. Agents use these to reason about the world.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.getFactionPower = getFactionPower;
exports.getFactionLeaderboard = getFactionLeaderboard;
exports.detectAlliances = detectAlliances;
exports.getFactionRivals = getFactionRivals;
exports.getAgentProfile = getAgentProfile;
exports.getAgentFactions = getAgentFactions;
exports.getWorldFeed = getWorldFeed;
exports.getWorldStats = getWorldStats;
exports.getAgentSolLamports = getAgentSolLamports;
exports.startVaultPnlTracker = startVaultPnlTracker;
const web3_js_1 = require("@solana/web3.js");
const torchsdk_1 = require("torchsdk");
const mappers_1 = require("./mappers");
const vanity_1 = require("./vanity");
// ─── Faction Power & Rankings ──────────────────────────────────────
/**
 * Calculate a faction's power score.
 *
 * Score = (market_cap_sol * 0.4) + (members * 0.2) + (war_chest_sol * 0.2)
 *       + (rallies * 0.1) + (progress * 0.1)
 *
 * Normalized to make comparison easy. Higher = stronger.
 */
async function getFactionPower(connection, mint) {
    const t = await (0, torchsdk_1.getToken)(connection, mint);
    const score = computePowerScore(t);
    return {
        mint: t.mint,
        name: t.name,
        symbol: t.symbol,
        score,
        market_cap_sol: t.market_cap_sol,
        members: t.holders ?? 0,
        war_chest_sol: t.treasury_sol_balance,
        rallies: t.stars,
        progress_percent: t.progress_percent,
        status: (0, mappers_1.mapFactionStatus)(t.status),
    };
}
/**
 * Ranked leaderboard of all factions by power score.
 */
async function getFactionLeaderboard(connection, opts) {
    // Fetch all tokens (up to 1000)
    const statusMap = {
        rising: 'bonding',
        ready: 'complete',
        ascended: 'migrated',
        razed: 'reclaimed',
    };
    const sdkStatus = opts?.status ? statusMap[opts.status] : 'all';
    // Fetch more than requested to account for non-pyre tokens being filtered out
    const fetchLimit = Math.min((opts?.limit ?? 20) * 3, 100);
    const result = await (0, torchsdk_1.getTokens)(connection, { limit: fetchLimit, status: sdkStatus });
    const pyreFactions = result.tokens.filter(t => (0, vanity_1.isPyreMint)(t.mint));
    const powers = pyreFactions.map((t) => ({
        mint: t.mint,
        name: t.name,
        symbol: t.symbol,
        score: computePowerScoreFromSummary(t),
        market_cap_sol: t.market_cap_sol,
        members: t.holders ?? 0,
        war_chest_sol: 0, // Not available in summary
        rallies: 0, // Not available in summary
        progress_percent: t.progress_percent,
        status: (0, mappers_1.mapFactionStatus)(t.status),
    }));
    powers.sort((a, b) => b.score - a.score);
    return powers;
}
// ─── Alliance & Rivalry Detection ──────────────────────────────────
/**
 * Detect alliances: factions with shared members.
 *
 * Given a set of faction mints, finds wallets holding multiple faction tokens.
 * Returns alliance clusters showing which factions share members.
 */
async function detectAlliances(connection, mints, holderLimit = 50) {
    // Fetch holders for each faction in parallel
    const holdersPerFaction = await Promise.all(mints.map(async (mint) => {
        const result = await getPyreHolders(connection, mint, holderLimit);
        return { mint, holders: new Set(result.holders.map(h => h.address)) };
    }));
    // Find overlapping holders between faction pairs
    const clusters = [];
    for (let i = 0; i < holdersPerFaction.length; i++) {
        for (let j = i + 1; j < holdersPerFaction.length; j++) {
            const a = holdersPerFaction[i];
            const b = holdersPerFaction[j];
            const shared = [...a.holders].filter(h => b.holders.has(h));
            if (shared.length > 0) {
                const minSize = Math.min(a.holders.size, b.holders.size);
                clusters.push({
                    factions: [a.mint, b.mint],
                    shared_members: shared.length,
                    overlap_percent: minSize > 0 ? (shared.length / minSize) * 100 : 0,
                });
            }
        }
    }
    clusters.sort((a, b) => b.shared_members - a.shared_members);
    return clusters;
}
/**
 * Find rival factions based on recent defection activity.
 *
 * Looks at recent sell messages to detect agents who have defected
 * from or to this faction.
 */
async function getFactionRivals(connection, mint, limit = 50) {
    // Get recent messages (sells include defection messages)
    const msgs = await (0, torchsdk_1.getMessages)(connection, mint, limit);
    const defectors = new Set(msgs.messages.map(m => m.sender));
    // For each defector, check what other factions they hold
    // This is a heuristic — we look at the messages to find patterns
    // In practice, agents would track this over time
    const rivalCounts = new Map();
    // Get all factions to cross-reference
    const allFactions = await (0, torchsdk_1.getTokens)(connection, { limit: 20, sort: 'volume' });
    for (const faction of allFactions.tokens.filter(t => (0, vanity_1.isPyreMint)(t.mint))) {
        if (faction.mint === mint)
            continue;
        const holders = await getPyreHolders(connection, faction.mint, 50);
        const holderAddrs = new Set(holders.holders.map(h => h.address));
        const overlap = [...defectors].filter(d => holderAddrs.has(d)).length;
        if (overlap > 0) {
            rivalCounts.set(faction.mint, {
                in: overlap, // Agents from this faction who also hold rival
                out: overlap,
                ...(rivalCounts.get(faction.mint) ?? {}),
            });
        }
    }
    const rivals = [];
    for (const [rivalMint, counts] of rivalCounts) {
        const faction = allFactions.tokens.find(t => t.mint === rivalMint);
        if (faction) {
            rivals.push({
                mint: rivalMint,
                name: faction.name,
                symbol: faction.symbol,
                defections_in: counts.in,
                defections_out: counts.out,
            });
        }
    }
    rivals.sort((a, b) => (b.defections_in + b.defections_out) - (a.defections_in + a.defections_out));
    return rivals;
}
// ─── Agent Intelligence ────────────────────────────────────────────
/**
 * Build an aggregate profile for an agent wallet.
 */
async function getAgentProfile(connection, wallet) {
    // Fetch stronghold and SAID verification in parallel
    const [vault, said] = await Promise.all([
        (0, torchsdk_1.getVaultForWallet)(connection, wallet).catch(() => null),
        (0, torchsdk_1.verifySaid)(wallet).catch(() => null),
    ]);
    // Get factions this agent holds — requires scanning
    // For now, check top factions for this holder
    const factions = await getAgentFactions(connection, wallet);
    // Find factions this wallet created
    const allFactions = await (0, torchsdk_1.getTokens)(connection, { limit: 100 });
    const founded = allFactions.tokens.filter(t => (0, vanity_1.isPyreMint)(t.mint))
        .filter(t => t.mint) // TokenSummary doesn't have creator, so we skip for now
        .map(t => t.mint);
    const totalValue = factions.reduce((sum, f) => sum + f.value_sol, 0);
    return {
        wallet,
        stronghold: vault ? {
            address: vault.address,
            creator: vault.creator,
            authority: vault.authority,
            sol_balance: vault.sol_balance,
            total_deposited: vault.total_deposited,
            total_withdrawn: vault.total_withdrawn,
            total_spent: vault.total_spent,
            total_received: vault.total_received,
            linked_agents: vault.linked_wallets,
            created_at: vault.created_at,
        } : null,
        factions_joined: factions,
        factions_founded: [], // Would need per-token creator lookup
        said_verification: said,
        total_value_sol: totalValue + (vault?.sol_balance ?? 0),
    };
}
/**
 * List all factions an agent holds tokens in.
 *
 * Scans both the wallet's and vault's Token-2022 accounts, merging balances.
 * Agents may hold tokens directly (no vault) or via stronghold (vault).
 */
async function getAgentFactions(connection, wallet, factionLimit = 50) {
    const { TOKEN_2022_PROGRAM_ID } = await Promise.resolve().then(() => __importStar(require('@solana/spl-token')));
    const walletPk = new web3_js_1.PublicKey(wallet);
    // Scan wallet token accounts
    const walletAccounts = await connection.getParsedTokenAccountsByOwner(walletPk, {
        programId: TOKEN_2022_PROGRAM_ID,
    });
    // Scan vault token accounts if a vault exists
    let vaultAccounts = { context: walletAccounts.context, value: [] };
    try {
        const vault = await (0, torchsdk_1.getVaultForWallet)(connection, wallet);
        if (!vault)
            throw new Error('no vault');
        const vaultPk = new web3_js_1.PublicKey(vault.address);
        vaultAccounts = await connection.getParsedTokenAccountsByOwner(vaultPk, {
            programId: TOKEN_2022_PROGRAM_ID,
        });
    }
    catch { }
    // Merge balances from both sources (wallet + vault)
    const balanceMap = new Map();
    for (const a of [...walletAccounts.value, ...vaultAccounts.value]) {
        const mint = a.account.data.parsed.info.mint;
        const balance = Number(a.account.data.parsed.info.tokenAmount.uiAmount ?? 0);
        if (balance > 0 && (0, vanity_1.isPyreMint)(mint)) {
            balanceMap.set(mint, (balanceMap.get(mint) ?? 0) + balance);
        }
    }
    if (balanceMap.size === 0)
        return [];
    // Fetch faction metadata for held mints
    const allFactions = await (0, torchsdk_1.getTokens)(connection, { limit: factionLimit });
    const factionMap = new Map(allFactions.tokens.filter(t => (0, vanity_1.isPyreMint)(t.mint)).map(t => [t.mint, t]));
    const positions = [];
    for (const [mint, balance] of balanceMap) {
        const faction = factionMap.get(mint);
        if (!faction)
            continue;
        // balance / 1B total supply
        const percentage = (balance / 1_000_000_000) * 100;
        positions.push({
            mint,
            name: faction.name,
            symbol: faction.symbol,
            balance,
            percentage,
            value_sol: balance * faction.price_sol,
        });
    }
    positions.sort((a, b) => b.value_sol - a.value_sol);
    return positions;
}
// ─── World State ───────────────────────────────────────────────────
/**
 * Aggregated recent activity across ALL factions.
 *
 * The "Bloomberg terminal" feed — launches, joins, defections, rallies.
 */
async function getWorldFeed(connection, opts) {
    const factionLimit = opts?.factionLimit ?? 20;
    const msgLimit = opts?.limit ?? 5;
    const allFactions = await (0, torchsdk_1.getTokens)(connection, { limit: factionLimit, sort: 'newest' });
    const events = [];
    // Add launch events for each faction
    for (const faction of allFactions.tokens.filter(t => (0, vanity_1.isPyreMint)(t.mint))) {
        events.push({
            type: 'launch',
            faction_mint: faction.mint,
            faction_name: faction.name,
            timestamp: faction.created_at,
        });
        // Map status to events
        if (faction.status === 'migrated') {
            events.push({
                type: 'ascend',
                faction_mint: faction.mint,
                faction_name: faction.name,
                timestamp: faction.last_activity_at,
            });
        }
        else if (faction.status === 'reclaimed') {
            events.push({
                type: 'raze',
                faction_mint: faction.mint,
                faction_name: faction.name,
                timestamp: faction.last_activity_at,
            });
        }
    }
    // Get recent messages from top factions (messages = trade activity)
    const topFactions = allFactions.tokens.slice(0, 10);
    await Promise.all(topFactions.map(async (faction) => {
        try {
            const msgs = await (0, torchsdk_1.getMessages)(connection, faction.mint, msgLimit);
            for (const msg of msgs.messages) {
                events.push({
                    type: 'join', // Messages are trade-bundled, most are buys
                    faction_mint: faction.mint,
                    faction_name: faction.name,
                    agent: msg.sender,
                    timestamp: msg.timestamp,
                    signature: msg.signature,
                    message: msg.memo,
                });
            }
        }
        catch {
            // Skip factions with no messages
        }
    }));
    events.sort((a, b) => b.timestamp - a.timestamp);
    return events.slice(0, opts?.limit ?? 100);
}
/**
 * Global stats: total factions, total agents, total SOL locked.
 */
async function getWorldStats(connection) {
    const all = await (0, torchsdk_1.getTokens)(connection, { limit: 200, status: 'all' });
    const pyreAll = all.tokens.filter(t => (0, vanity_1.isPyreMint)(t.mint));
    const pyreRising = pyreAll.filter(t => t.status === 'bonding');
    const pyreAscended = pyreAll.filter(t => t.status === 'migrated');
    const allFactions = [...pyreRising, ...pyreAscended];
    const totalSolLocked = allFactions.reduce((sum, t) => sum + t.market_cap_sol, 0);
    // Find most powerful
    let mostPowerful = null;
    let maxScore = 0;
    for (const t of allFactions) {
        const score = computePowerScoreFromSummary(t);
        if (score > maxScore) {
            maxScore = score;
            mostPowerful = {
                mint: t.mint,
                name: t.name,
                symbol: t.symbol,
                score,
                market_cap_sol: t.market_cap_sol,
                members: t.holders ?? 0,
                war_chest_sol: 0,
                rallies: 0,
                progress_percent: t.progress_percent,
                status: (0, mappers_1.mapFactionStatus)(t.status),
            };
        }
    }
    return {
        total_factions: pyreAll.length,
        rising_factions: pyreRising.length,
        ascended_factions: pyreAscended.length,
        total_sol_locked: totalSolLocked,
        most_powerful: mostPowerful,
    };
}
/** Fetch holders excluding program-owned accounts (bonding curve, treasury, treasury lock) */
async function getPyreHolders(connection, mint, limit) {
    const mintPk = new web3_js_1.PublicKey(mint);
    const [bondingCurve] = (0, vanity_1.getBondingCurvePda)(mintPk);
    const [treasury] = (0, vanity_1.getTokenTreasuryPda)(mintPk);
    const [treasuryLock] = (0, vanity_1.getTreasuryLockPda)(mintPk);
    const excluded = new Set([bondingCurve.toString(), treasury.toString(), treasuryLock.toString()]);
    const result = await (0, torchsdk_1.getHolders)(connection, mint, limit + 5);
    result.holders = result.holders.filter(h => !excluded.has(h.address)).slice(0, limit);
    return result;
}
// ─── Vault P&L ────────────────────────────────────────────────────
/**
 * Get total SOL balance in lamports for an agent: vault + wallet.
 * Checks vault first (where most SOL flows), falls back to wallet if no vault.
 * Returns the combined balance so P&L captures all SOL movement.
 */
async function getAgentSolLamports(connection, wallet) {
    const walletPk = new web3_js_1.PublicKey(wallet);
    let total = 0;
    try {
        total += await connection.getBalance(walletPk);
    }
    catch { }
    try {
        const vault = await (0, torchsdk_1.getVaultForWallet)(connection, wallet);
        if (vault)
            total += Math.round(vault.sol_balance * 1e9);
    }
    catch { }
    return total;
}
/**
 * Start tracking P&L for a single action/tick.
 *
 * Snapshots wallet + vault SOL before the action. Call `finish()` after
 * to get the diff. Covers both vault and wallet flows so no SOL is missed.
 *
 * Usage:
 *   const pnl = await startVaultPnlTracker(connection, wallet)
 *   // ... do action ...
 *   const { spent, received } = await pnl.finish()
 */
async function startVaultPnlTracker(connection, wallet) {
    const before = await getAgentSolLamports(connection, wallet);
    return {
        async finish() {
            const after = await getAgentSolLamports(connection, wallet);
            const diff = after - before;
            return {
                spent: diff < 0 ? Math.abs(diff) : 0,
                received: diff > 0 ? diff : 0,
            };
        },
    };
}
// ─── Internal Helpers ──────────────────────────────────────────────
function computePowerScore(t) {
    const mcWeight = 0.4;
    const memberWeight = 0.2;
    const chestWeight = 0.2;
    const rallyWeight = 0.1;
    const progressWeight = 0.1;
    return ((t.market_cap_sol * mcWeight) +
        ((t.holders ?? 0) * memberWeight) +
        (t.treasury_sol_balance * chestWeight) +
        (t.stars * rallyWeight) +
        (t.progress_percent * progressWeight));
}
function computePowerScoreFromSummary(t) {
    const mcWeight = 0.4;
    const memberWeight = 0.2;
    const progressWeight = 0.1;
    return ((t.market_cap_sol * mcWeight) +
        ((t.holders ?? 0) * memberWeight) +
        (t.progress_percent * progressWeight));
}
