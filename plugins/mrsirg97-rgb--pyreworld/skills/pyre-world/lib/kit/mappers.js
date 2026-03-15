"use strict";
/**
 * Pyre Kit Mappers
 *
 * Internal mapping functions between Torch SDK types and Pyre game types.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.mapFactionStatus = mapFactionStatus;
exports.mapTokenStatus = mapTokenStatus;
exports.mapTokenStatusFilter = mapTokenStatusFilter;
exports.mapFactionTier = mapFactionTier;
exports.mapFactionTierFromSol = mapFactionTierFromSol;
exports.mapStrategy = mapStrategy;
exports.mapVote = mapVote;
exports.mapTokenSummaryToFaction = mapTokenSummaryToFaction;
exports.mapTokenDetailToFaction = mapTokenDetailToFaction;
exports.mapVaultToStronghold = mapVaultToStronghold;
exports.mapWalletLinkToAgentLink = mapWalletLinkToAgentLink;
exports.mapTokenMessageToComms = mapTokenMessageToComms;
exports.mapLendingToWarChest = mapLendingToWarChest;
exports.mapLoanToWarLoan = mapLoanToWarLoan;
exports.mapLoanWithKeyToWarLoan = mapLoanWithKeyToWarLoan;
exports.mapHolderToMember = mapHolderToMember;
exports.mapTokenListResult = mapTokenListResult;
exports.mapHoldersResult = mapHoldersResult;
exports.mapMessagesResult = mapMessagesResult;
exports.mapAllLoansResult = mapAllLoansResult;
exports.mapBuyResult = mapBuyResult;
exports.mapCreateResult = mapCreateResult;
// ─── Status Mapping ────────────────────────────────────────────────
const STATUS_MAP = {
    bonding: 'rising',
    complete: 'ready',
    migrated: 'ascended',
    reclaimed: 'razed',
};
const STATUS_REVERSE = {
    rising: 'bonding',
    ready: 'complete',
    ascended: 'migrated',
    razed: 'reclaimed',
};
const STATUS_FILTER_REVERSE = {
    rising: 'bonding',
    ready: 'complete',
    ascended: 'migrated',
    razed: 'reclaimed',
    all: 'all',
};
function mapFactionStatus(status) {
    return STATUS_MAP[status];
}
function mapTokenStatus(status) {
    return STATUS_REVERSE[status];
}
function mapTokenStatusFilter(status) {
    return STATUS_FILTER_REVERSE[status];
}
// ─── Tier Mapping ──────────────────────────────────────────────────
/** Map SOL target to faction tier */
function mapFactionTier(sol_target) {
    // Torch tiers: spark (≤50 SOL), flame (≤100 SOL), torch (200 SOL default)
    if (sol_target <= 50_000_000_000)
        return 'ember'; // ≤50 SOL in lamports
    if (sol_target <= 100_000_000_000)
        return 'blaze'; // ≤100 SOL
    return 'inferno'; // 200 SOL (default)
}
/** Infer tier from sol_target in SOL (not lamports) */
function mapFactionTierFromSol(sol_target) {
    if (sol_target <= 50)
        return 'ember';
    if (sol_target <= 100)
        return 'blaze';
    return 'inferno';
}
// ─── Strategy Mapping ──────────────────────────────────────────────
function mapStrategy(vote) {
    return vote === 'burn' ? 'scorched_earth' : 'fortify';
}
function mapVote(strategy) {
    return strategy === 'scorched_earth' ? 'burn' : 'return';
}
// ─── Core Type Mappers ─────────────────────────────────────────────
function mapTokenSummaryToFaction(t) {
    return {
        mint: t.mint,
        name: t.name,
        symbol: t.symbol,
        status: mapFactionStatus(t.status),
        tier: mapFactionTierFromSol(t.market_cap_sol > 0 ? 200 : 200), // default tier from target
        price_sol: t.price_sol,
        market_cap_sol: t.market_cap_sol,
        progress_percent: t.progress_percent,
        members: t.holders,
        created_at: t.created_at,
        last_activity_at: t.last_activity_at,
    };
}
function mapTokenDetailToFaction(t) {
    return {
        mint: t.mint,
        name: t.name,
        symbol: t.symbol,
        description: t.description,
        image: t.image,
        status: mapFactionStatus(t.status),
        tier: mapFactionTierFromSol(t.sol_target),
        price_sol: t.price_sol,
        price_usd: t.price_usd,
        market_cap_sol: t.market_cap_sol,
        market_cap_usd: t.market_cap_usd,
        progress_percent: t.progress_percent,
        sol_raised: t.sol_raised,
        sol_target: t.sol_target,
        total_supply: t.total_supply,
        circulating_supply: t.circulating_supply,
        tokens_in_curve: t.tokens_in_curve,
        tokens_in_vote_vault: t.tokens_in_vote_vault,
        tokens_burned: t.tokens_burned,
        war_chest_sol: t.treasury_sol_balance,
        war_chest_tokens: t.treasury_token_balance,
        total_bought_back: t.total_bought_back,
        buyback_count: t.buyback_count,
        votes_scorched_earth: t.votes_burn,
        votes_fortify: t.votes_return,
        founder: t.creator,
        members: t.holders,
        rallies: t.stars,
        created_at: t.created_at,
        last_activity_at: t.last_activity_at,
        twitter: t.twitter,
        telegram: t.telegram,
        website: t.website,
        founder_verified: t.creator_verified,
        founder_trust_tier: t.creator_trust_tier,
        founder_said_name: t.creator_said_name,
        founder_badge_url: t.creator_badge_url,
        warnings: t.warnings,
    };
}
function mapVaultToStronghold(v) {
    return {
        address: v.address,
        creator: v.creator,
        authority: v.authority,
        sol_balance: v.sol_balance,
        total_deposited: v.total_deposited,
        total_withdrawn: v.total_withdrawn,
        total_spent: v.total_spent,
        total_received: v.total_received,
        linked_agents: v.linked_wallets,
        created_at: v.created_at,
    };
}
function mapWalletLinkToAgentLink(l) {
    return {
        address: l.address,
        stronghold: l.vault,
        wallet: l.wallet,
        linked_at: l.linked_at,
    };
}
function mapTokenMessageToComms(m) {
    return {
        signature: m.signature,
        memo: m.memo,
        sender: m.sender,
        timestamp: m.timestamp,
        sender_verified: m.sender_verified,
        sender_trust_tier: m.sender_trust_tier,
        sender_said_name: m.sender_said_name,
        sender_badge_url: m.sender_badge_url,
    };
}
function mapLendingToWarChest(l) {
    return {
        interest_rate_bps: l.interest_rate_bps,
        max_ltv_bps: l.max_ltv_bps,
        liquidation_threshold_bps: l.liquidation_threshold_bps,
        liquidation_bonus_bps: l.liquidation_bonus_bps,
        utilization_cap_bps: l.utilization_cap_bps,
        borrow_share_multiplier: l.borrow_share_multiplier,
        total_sol_lent: l.total_sol_lent,
        active_loans: l.active_loans,
        war_chest_sol_available: l.treasury_sol_available,
        warnings: l.warnings,
    };
}
function mapLoanToWarLoan(l) {
    return {
        collateral_amount: l.collateral_amount,
        borrowed_amount: l.borrowed_amount,
        accrued_interest: l.accrued_interest,
        total_owed: l.total_owed,
        collateral_value_sol: l.collateral_value_sol,
        current_ltv_bps: l.current_ltv_bps,
        health: l.health,
        warnings: l.warnings,
    };
}
function mapLoanWithKeyToWarLoan(l) {
    return {
        ...mapLoanToWarLoan(l),
        borrower: l.borrower,
    };
}
function mapHolderToMember(h) {
    return {
        address: h.address,
        balance: h.balance,
        percentage: h.percentage,
    };
}
// ─── Result Mappers ────────────────────────────────────────────────
function mapTokenListResult(r) {
    return {
        factions: r.tokens.map(mapTokenSummaryToFaction),
        total: r.total,
        limit: r.limit,
        offset: r.offset,
    };
}
function mapHoldersResult(r) {
    return {
        members: r.holders.map(mapHolderToMember),
        total_members: r.total_holders,
    };
}
function mapMessagesResult(r) {
    return {
        comms: r.messages.map(mapTokenMessageToComms),
        total: r.total,
    };
}
function mapAllLoansResult(r) {
    return {
        positions: r.positions.map(mapLoanWithKeyToWarLoan),
        pool_price_sol: r.pool_price_sol,
    };
}
function mapBuyResult(r) {
    return {
        transaction: r.transaction,
        additionalTransactions: r.additionalTransactions,
        message: r.message,
        migrationTransaction: r.migrationTransaction,
    };
}
function mapCreateResult(r) {
    return {
        transaction: r.transaction,
        additionalTransactions: r.additionalTransactions,
        message: r.message,
        mint: r.mint,
        mintKeypair: r.mintKeypair,
    };
}
