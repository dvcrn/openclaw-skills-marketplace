"use strict";
/**
 * Pyre Kit Actions
 *
 * Thin wrappers that call torchsdk functions and map params/results
 * into game-semantic Pyre types. No new on-chain logic.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.createEphemeralAgent = void 0;
exports.blacklistMints = blacklistMints;
exports.isBlacklistedMint = isBlacklistedMint;
exports.getBlacklistedMints = getBlacklistedMints;
exports.getFactions = getFactions;
exports.getFaction = getFaction;
exports.getMembers = getMembers;
exports.getComms = getComms;
exports.getJoinQuote = getJoinQuote;
exports.getDefectQuote = getDefectQuote;
exports.getStronghold = getStronghold;
exports.getStrongholdForAgent = getStrongholdForAgent;
exports.getAgentLink = getAgentLink;
exports.getLinkedAgents = getLinkedAgents;
exports.getWarChest = getWarChest;
exports.getWarLoan = getWarLoan;
exports.getAllWarLoans = getAllWarLoans;
exports.getMaxWarLoan = getMaxWarLoan;
exports.launchFaction = launchFaction;
exports.joinFaction = joinFaction;
exports.directJoinFaction = directJoinFaction;
exports.defect = defect;
exports.messageFaction = messageFaction;
exports.fudFaction = fudFaction;
exports.rally = rally;
exports.requestWarLoan = requestWarLoan;
exports.repayWarLoan = repayWarLoan;
exports.tradeOnDex = tradeOnDex;
exports.claimSpoils = claimSpoils;
exports.createStronghold = createStronghold;
exports.fundStronghold = fundStronghold;
exports.withdrawFromStronghold = withdrawFromStronghold;
exports.recruitAgent = recruitAgent;
exports.exileAgent = exileAgent;
exports.coup = coup;
exports.withdrawAssets = withdrawAssets;
exports.siege = siege;
exports.ascend = ascend;
exports.raze = raze;
exports.tithe = tithe;
exports.convertTithe = convertTithe;
exports.verifyAgent = verifyAgent;
exports.confirmAction = confirmAction;
exports.getDexPool = getDexPool;
exports.getDexVaults = getDexVaults;
const web3_js_1 = require("@solana/web3.js");
const torchsdk_1 = require("torchsdk");
const mappers_1 = require("./mappers");
const vanity_1 = require("./vanity");
// ─── Blacklist ──────────────────────────────────────────────────────
// Mints from previous swarm runs. Agents should skip these and only
// interact with freshly launched factions.
const DEFAULT_BLACKLIST = [
    'E1SgYPW6JXhw5BabrvJkr6L2PyvfFenYaoCTePazyNpy', '6jWsyDC87RmfrZZRjuxSAxvUxE665HGZwZ2Z8j5z9epy',
    '6J8PLgFxHb98cNURP2Yt2SKwgnUeEXpN6Us2kxaMz1py', '5A297UyPQstxWpJyydDnFvn2zN8whCEYdqvnfB5bF9py',
    '8XdWfSKLJusAcRrYzK3bWJ7dy46AkbU8qxF3B55uSfpy', '7ZYrKcJbFFbG36keCYRvfc1j1HScQmJW1zRV3wVVD4py',
    'ERQPyG2oqx5bdyuY2Nnm5ZbZY2zcB46TfUxqpzYWH5py', 'JCvpK3kTnh2EdQG71mqE8ZXcvzLU5EJNG5vgGZme4wpy',
    '9RDFkGSjKpjHtXZ25uuug2MN5P7oSjzkLg16HcrKy3py', '2kWcX1ZetV4jUtBPbKKk265q4gS4nuut2kc1MbaZDfpy',
    '3r9FnQim6GToR7NkY5om8igUNu7gfpq5fk2qtv3bV5py', '2498F79s1Ghyj3J4VhV1qy5hhznnM53ZwzTXM9iscopy',
    '5VpotyDyc8QKKqLuzu8pfhtEa9gsRG1ww58DbqJUgTpy', 'GXi1opahTkavPfAqfUhkoUJRBjPoAmAMVW87kdbDwNpy',
    'GKFAokGiyhXGXxUPgwQEo8fE5nBjRdJcVX6LVj7SgPpy', 'EKFVwfNk1xzqhpyFJSMNw8KDcLRemvqxiGoSyfRtBspy',
    'GsZLHVt3mTwus5krUcifBWS52xMQSuXSy3RpPhEFtvpy', '9azKjXnt2w4RB5ykVcyaicWSssmxoapZ9SSQLMZc4Epy',
    'BaLwryyMrqhtsMrELkrTSdWF9UYuNdjW4413hrQqbtpy', '5p9ibszMVe79mm95M8uubS6WttXem2xZfh3mWmBdvUpy',
    'CTvoAmTggJcBTnbxcfy91Y1c6t6fU5xq3SRtYh3TgEpy', '2kqVCdQS9KSv2kxLiytGZfcLsx5xwKQT6rHTg4V18hpy',
    'zV7XZcvY8DVk4scKUiw7GGN4L3eBPSXuD7Q1NPxfspy', '3UhzKfdU1wgnEN2VCykRURw88qVVqeu3ejRkUnjmhRpy',
    'FRaS3dAdr1zo6u811XBVGUp9K2mSdQ2yG8qW4qP5hapy', '4NHzWVP7hzZhd9LhTrbyxzsSnT8EmNSYVP1DpAKXHYpy',
    'Yt2rdfp6uzS7L52df3LPmetLoy3GvKChYJ4Lmvk6gpy', '9Ejju29KHPWMpda4WpFsJ6ZDHVUqNWyMZHteEisgw9py',
    '2zPC4A7WR2cMNDfBzERp49fEbTBCyqXPKhcrgz3hWcpy', '7jBAriydb1qRy7Wg4WAz8woHP4pVxZJSnF7vw95tVQpy',
    'HvPWKuMFpG3zAdkPMbaadyo78VoJbAMtpXaBYMK1Aqpy', 'GyNw9bkqz2rhR66Xx7P4p11PFBrjPi2r6XoCg5gPAdpy',
    '6HveNEes9xtkkchb76JgjWWQ61sbXjESy2vr3A7Maipy', '8E3GETvTkTTaCLpzkyHJTnuNMfmGvzUEgAYnurZuLZpy',
    'AeApaJqppwjW9S2KeZGPZpmg1kAdxZHkFRnXPZc8Kjpy', '8FfteyAMQm96upu4w6cJvE5T8RcMKRf5keJMdXbukXpy',
    'BrEj2Q9XE13WesRU1u8USiprv2DkpBcJfaqQeqQ6grpy', 'Dtki37mAB3DiTW1bp8LnZQyv54UuC68Yo5pGZkPdVSpy',
    '77UzTntZ7ThyXhN4hVvSx7m6tjit8uCw6U2LVQHPSqpy', 'ASV9kiC6vEpZy3X7xVExuyG257KHKd3Hutbji8AVRUpy',
    'Fc1V6KcxSriJkUNeDLqz8w5Sm4mp1s8gxornZVLcHEpy', 'FEizyHEUoYenqfpF87kqiGnq3w1R2TReodEfsnTrrfpy',
    'DmwgcVHoJxKeRiij5LtedY9LWDpqoqa3hGfUyVgBkgpy', 'GUGz1Em5KZ57aKFqEBSd4Y4Vb6WxBd3H2b16fPCC6upy',
    '6ZWY3Bau5zw1j7vMQQ1czSw4rjBJrExHQ8Renor2vLpy',
];
const BLACKLISTED_MINTS = new Set(DEFAULT_BLACKLIST);
/** Add mints to the blacklist (call at startup with old mints) */
function blacklistMints(mints) {
    for (const m of mints)
        BLACKLISTED_MINTS.add(m);
}
/** Check if a mint is blacklisted */
function isBlacklistedMint(mint) {
    return BLACKLISTED_MINTS.has(mint);
}
/** Get all blacklisted mints */
function getBlacklistedMints() {
    return Array.from(BLACKLISTED_MINTS);
}
// ─── Read Operations ───────────────────────────────────────────────
/** List all factions with optional filtering and sorting */
async function getFactions(connection, params) {
    const sdkParams = params ? {
        limit: params.limit,
        offset: params.offset,
        status: params.status ? (0, mappers_1.mapTokenStatusFilter)(params.status) : undefined,
        sort: params.sort,
    } : undefined;
    const result = await (0, torchsdk_1.getTokens)(connection, sdkParams);
    return (0, mappers_1.mapTokenListResult)(result);
}
/** Get detailed info for a single faction */
async function getFaction(connection, mint) {
    const detail = await (0, torchsdk_1.getToken)(connection, mint);
    return (0, mappers_1.mapTokenDetailToFaction)(detail);
}
/** Get faction members (top holders, excluding program-owned accounts) */
async function getMembers(connection, mint, limit) {
    const mintPk = new web3_js_1.PublicKey(mint);
    const [bondingCurve] = (0, vanity_1.getBondingCurvePda)(mintPk);
    const [treasury] = (0, vanity_1.getTokenTreasuryPda)(mintPk);
    const [treasuryLock] = (0, vanity_1.getTreasuryLockPda)(mintPk);
    const excluded = new Set([
        bondingCurve.toString(),
        treasury.toString(),
        treasuryLock.toString(),
    ]);
    // Fetch extra to compensate for filtered-out program accounts
    const result = await (0, torchsdk_1.getHolders)(connection, mint, (limit ?? 10) + 5);
    result.holders = result.holders.filter(h => !excluded.has(h.address));
    if (limit)
        result.holders = result.holders.slice(0, limit);
    return (0, mappers_1.mapHoldersResult)(result);
}
/** Get faction comms (trade-bundled messages, including post-ascension DEX messages) */
async function getComms(connection, mint, limit, status) {
    // Non-ascended: bonding curve only (1 RPC call)
    // Ascended: pool only (1 RPC call) — bonding curve is stale post-migration
    const source = status === 'ascended' ? 'pool' : status ? 'bonding' : 'all';
    const result = await (0, torchsdk_1.getMessages)(connection, mint, limit, { source });
    return (0, mappers_1.mapMessagesResult)(result);
}
/** Get a quote for joining a faction (buying tokens) */
async function getJoinQuote(connection, mint, amountSolLamports) {
    return (0, torchsdk_1.getBuyQuote)(connection, mint, amountSolLamports);
}
/** Get a quote for defecting from a faction (selling tokens) */
async function getDefectQuote(connection, mint, amountTokens) {
    return (0, torchsdk_1.getSellQuote)(connection, mint, amountTokens);
}
/** Get stronghold (vault) by creator */
async function getStronghold(connection, creator) {
    const vault = await (0, torchsdk_1.getVault)(connection, creator);
    return vault ? (0, mappers_1.mapVaultToStronghold)(vault) : null;
}
/** Get stronghold for a linked agent wallet */
async function getStrongholdForAgent(connection, wallet) {
    const vault = await (0, torchsdk_1.getVaultForWallet)(connection, wallet);
    return vault ? (0, mappers_1.mapVaultToStronghold)(vault) : null;
}
/** Get agent link info for a wallet */
async function getAgentLink(connection, wallet) {
    const link = await (0, torchsdk_1.getVaultWalletLink)(connection, wallet);
    return link ? (0, mappers_1.mapWalletLinkToAgentLink)(link) : null;
}
/** Get all linked agents for a vault (via getProgramAccounts) */
async function getLinkedAgents(connection, vaultAddress) {
    // VaultWalletLink account layout: 8-byte discriminator + 32-byte vault + 32-byte wallet + 8-byte linked_at + 1-byte bump
    const DISCRIMINATOR = Buffer.from([111, 59, 70, 89, 148, 117, 217, 156]); // sha256("account:VaultWalletLink")[0..8]
    const vaultPubkey = new web3_js_1.PublicKey(vaultAddress);
    const filters = [
        { dataSize: 81 }, // 8 + 32 + 32 + 8 + 1
        { memcmp: { offset: 8, bytes: vaultPubkey.toBase58() } },
    ];
    const accounts = await connection.getProgramAccounts(torchsdk_1.PROGRAM_ID, { filters });
    return accounts.map((acc) => {
        const data = acc.account.data;
        const wallet = new web3_js_1.PublicKey(data.subarray(40, 72)).toBase58();
        const linked_at = Number(data.readBigInt64LE(72));
        return {
            address: acc.pubkey.toBase58(),
            stronghold: vaultAddress,
            wallet,
            linked_at,
        };
    });
}
/** Get war chest (lending info) for a faction */
async function getWarChest(connection, mint) {
    const info = await (0, torchsdk_1.getLendingInfo)(connection, mint);
    return (0, mappers_1.mapLendingToWarChest)(info);
}
/** Get war loan position for a specific agent on a faction */
async function getWarLoan(connection, mint, wallet) {
    const pos = await (0, torchsdk_1.getLoanPosition)(connection, mint, wallet);
    return (0, mappers_1.mapLoanToWarLoan)(pos);
}
/** Get all war loans for a faction */
async function getAllWarLoans(connection, mint) {
    const result = await (0, torchsdk_1.getAllLoanPositions)(connection, mint);
    return (0, mappers_1.mapAllLoansResult)(result);
}
/** Compute max borrowable SOL for a given collateral amount */
async function getMaxWarLoan(connection, mint, collateralAmount) {
    return (0, torchsdk_1.getBorrowQuote)(connection, mint, collateralAmount);
}
// ─── Faction Operations (controller) ───────────────────────────────
/** Launch a new faction (create token) */
async function launchFaction(connection, params) {
    const result = await (0, vanity_1.buildCreateFactionTransaction)(connection, {
        creator: params.founder,
        name: params.name,
        symbol: params.symbol,
        metadata_uri: params.metadata_uri,
        sol_target: params.sol_target,
        community_token: params.community_faction,
    });
    return (0, mappers_1.mapCreateResult)(result);
}
/** Join a faction via stronghold (vault-funded buy) */
async function joinFaction(connection, params) {
    const result = await (0, torchsdk_1.buildBuyTransaction)(connection, {
        mint: params.mint,
        buyer: params.agent,
        amount_sol: params.amount_sol,
        slippage_bps: params.slippage_bps,
        vote: params.strategy ? (0, mappers_1.mapVote)(params.strategy) : undefined,
        message: params.message,
        vault: params.stronghold,
    });
    return (0, mappers_1.mapBuyResult)(result);
}
/** Join a faction directly (no vault) */
async function directJoinFaction(connection, params) {
    const result = await (0, torchsdk_1.buildDirectBuyTransaction)(connection, {
        mint: params.mint,
        buyer: params.agent,
        amount_sol: params.amount_sol,
        slippage_bps: params.slippage_bps,
        vote: params.strategy ? (0, mappers_1.mapVote)(params.strategy) : undefined,
        message: params.message,
    });
    return (0, mappers_1.mapBuyResult)(result);
}
/** Defect from a faction (sell tokens) */
async function defect(connection, params) {
    return (0, torchsdk_1.buildSellTransaction)(connection, {
        mint: params.mint,
        seller: params.agent,
        amount_tokens: params.amount_tokens,
        slippage_bps: params.slippage_bps,
        message: params.message,
        vault: params.stronghold,
    });
}
/** "Said in" — micro buy (0.001 SOL) + message. Routes through bonding curve or DEX automatically. */
async function messageFaction(connection, params) {
    const MICRO_BUY_LAMPORTS = 1_000_000; // 0.001 SOL
    if (params.ascended) {
        return (0, torchsdk_1.buildVaultSwapTransaction)(connection, {
            mint: params.mint,
            signer: params.agent,
            vault_creator: params.stronghold,
            amount_in: MICRO_BUY_LAMPORTS,
            minimum_amount_out: 1,
            is_buy: true,
            message: params.message,
        });
    }
    const result = await (0, torchsdk_1.buildBuyTransaction)(connection, {
        mint: params.mint,
        buyer: params.agent,
        amount_sol: MICRO_BUY_LAMPORTS,
        message: params.message,
        vault: params.stronghold,
        vote: params.first_buy ? (0, mappers_1.mapVote)(Math.random() > 0.5 ? 'fortify' : 'scorched_earth') : undefined,
    });
    return (0, mappers_1.mapBuyResult)(result);
}
/** "Argued in" — micro sell (100 tokens) + negative message. Routes through bonding curve or DEX automatically. */
async function fudFaction(connection, params) {
    const MICRO_SELL_TOKENS = 100;
    if (params.ascended) {
        return (0, torchsdk_1.buildVaultSwapTransaction)(connection, {
            mint: params.mint,
            signer: params.agent,
            vault_creator: params.stronghold,
            amount_in: MICRO_SELL_TOKENS,
            minimum_amount_out: 1,
            is_buy: false,
            message: params.message,
        });
    }
    return (0, torchsdk_1.buildSellTransaction)(connection, {
        mint: params.mint,
        seller: params.agent,
        amount_tokens: MICRO_SELL_TOKENS,
        message: params.message,
        vault: params.stronghold,
    });
}
/** Rally support for a faction (star) */
async function rally(connection, params) {
    return (0, torchsdk_1.buildStarTransaction)(connection, {
        mint: params.mint,
        user: params.agent,
        vault: params.stronghold,
    });
}
/** Request a war loan (borrow SOL against token collateral) */
async function requestWarLoan(connection, params) {
    return (0, torchsdk_1.buildBorrowTransaction)(connection, {
        mint: params.mint,
        borrower: params.borrower,
        collateral_amount: params.collateral_amount,
        sol_to_borrow: params.sol_to_borrow,
        vault: params.stronghold,
    });
}
/** Repay a war loan */
async function repayWarLoan(connection, params) {
    return (0, torchsdk_1.buildRepayTransaction)(connection, {
        mint: params.mint,
        borrower: params.borrower,
        sol_amount: params.sol_amount,
        vault: params.stronghold,
    });
}
/** Trade on DEX via stronghold (vault-routed Raydium swap) */
async function tradeOnDex(connection, params) {
    return (0, torchsdk_1.buildVaultSwapTransaction)(connection, {
        mint: params.mint,
        signer: params.signer,
        vault_creator: params.stronghold_creator,
        amount_in: params.amount_in,
        minimum_amount_out: params.minimum_amount_out,
        is_buy: params.is_buy,
        message: params.message,
    });
}
/** Claim spoils (protocol rewards) */
async function claimSpoils(connection, params) {
    return (0, torchsdk_1.buildClaimProtocolRewardsTransaction)(connection, {
        user: params.agent,
        vault: params.stronghold,
    });
}
// ─── Stronghold Operations (authority) ─────────────────────────────
/** Create a new stronghold (vault) */
async function createStronghold(connection, params) {
    return (0, torchsdk_1.buildCreateVaultTransaction)(connection, {
        creator: params.creator,
    });
}
/** Fund a stronghold with SOL */
async function fundStronghold(connection, params) {
    return (0, torchsdk_1.buildDepositVaultTransaction)(connection, {
        depositor: params.depositor,
        vault_creator: params.stronghold_creator,
        amount_sol: params.amount_sol,
    });
}
/** Withdraw SOL from a stronghold */
async function withdrawFromStronghold(connection, params) {
    return (0, torchsdk_1.buildWithdrawVaultTransaction)(connection, {
        authority: params.authority,
        vault_creator: params.stronghold_creator,
        amount_sol: params.amount_sol,
    });
}
/** Recruit an agent (link wallet to stronghold) */
async function recruitAgent(connection, params) {
    return (0, torchsdk_1.buildLinkWalletTransaction)(connection, {
        authority: params.authority,
        vault_creator: params.stronghold_creator,
        wallet_to_link: params.wallet_to_link,
    });
}
/** Exile an agent (unlink wallet from stronghold) */
async function exileAgent(connection, params) {
    return (0, torchsdk_1.buildUnlinkWalletTransaction)(connection, {
        authority: params.authority,
        vault_creator: params.stronghold_creator,
        wallet_to_unlink: params.wallet_to_unlink,
    });
}
/** Coup — transfer stronghold authority */
async function coup(connection, params) {
    return (0, torchsdk_1.buildTransferAuthorityTransaction)(connection, {
        authority: params.authority,
        vault_creator: params.stronghold_creator,
        new_authority: params.new_authority,
    });
}
/** Withdraw token assets from stronghold */
async function withdrawAssets(connection, params) {
    return (0, torchsdk_1.buildWithdrawTokensTransaction)(connection, {
        authority: params.authority,
        vault_creator: params.stronghold_creator,
        mint: params.mint,
        destination: params.destination,
        amount: params.amount,
    });
}
// ─── Permissionless Operations ─────────────────────────────────────
/** Siege — liquidate an undercollateralized war loan */
async function siege(connection, params) {
    return (0, torchsdk_1.buildLiquidateTransaction)(connection, {
        mint: params.mint,
        liquidator: params.liquidator,
        borrower: params.borrower,
        vault: params.stronghold,
    });
}
/** Ascend — migrate a completed faction to DEX */
async function ascend(connection, params) {
    return (0, torchsdk_1.buildMigrateTransaction)(connection, {
        mint: params.mint,
        payer: params.payer,
    });
}
/** Raze — reclaim a failed faction */
async function raze(connection, params) {
    return (0, torchsdk_1.buildReclaimFailedTokenTransaction)(connection, {
        payer: params.payer,
        mint: params.mint,
    });
}
/** Tithe — harvest transfer fees */
async function tithe(connection, params) {
    return (0, torchsdk_1.buildHarvestFeesTransaction)(connection, {
        mint: params.mint,
        payer: params.payer,
        sources: params.sources,
    });
}
/** Convert tithe — swap harvested fees to SOL */
async function convertTithe(connection, params) {
    return (0, torchsdk_1.buildSwapFeesToSolTransaction)(connection, {
        mint: params.mint,
        payer: params.payer,
        minimum_amount_out: params.minimum_amount_out,
        harvest: params.harvest,
        sources: params.sources,
    });
}
// ─── SAID Operations ───────────────────────────────────────────────
/** Verify an agent's SAID reputation */
async function verifyAgent(wallet) {
    return (0, torchsdk_1.verifySaid)(wallet);
}
/** Confirm a transaction on-chain */
async function confirmAction(connection, signature, wallet) {
    return (0, torchsdk_1.confirmTransaction)(connection, signature, wallet);
}
// ─── Utility ───────────────────────────────────────────────────────
/** Create an ephemeral agent keypair (memory-only, zero key management) */
var torchsdk_2 = require("torchsdk");
Object.defineProperty(exports, "createEphemeralAgent", { enumerable: true, get: function () { return torchsdk_2.createEphemeralAgent; } });
/** Get the Raydium pool state PDA for an ascended faction's DEX pool */
function getDexPool(mint) {
    const { poolState } = (0, torchsdk_1.getRaydiumMigrationAccounts)(new web3_js_1.PublicKey(mint));
    return poolState;
}
/** Get Raydium pool vault addresses for an ascended faction */
function getDexVaults(mint) {
    const accts = (0, torchsdk_1.getRaydiumMigrationAccounts)(new web3_js_1.PublicKey(mint));
    return {
        solVault: (accts.isWsolToken0 ? accts.token0Vault : accts.token1Vault).toString(),
        tokenVault: (accts.isWsolToken0 ? accts.token1Vault : accts.token0Vault).toString(),
    };
}
