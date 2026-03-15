"use strict";
/**
 * Quote calculations
 *
 * Get expected output for buy/sell operations.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.getBorrowQuote = exports.getSellQuote = exports.getBuyQuote = void 0;
const web3_js_1 = require("@solana/web3.js");
const program_1 = require("./program");
const constants_1 = require("./constants");
const tokens_1 = require("./tokens");
/**
 * Get a buy quote: how many tokens for a given SOL amount.
 */
const getBuyQuote = async (connection, mintStr, amountSolLamports) => {
    const mint = new web3_js_1.PublicKey(mintStr);
    const tokenData = await (0, tokens_1.fetchTokenRaw)(connection, mint);
    if (!tokenData) {
        throw new Error(`Token not found: ${mintStr}`);
    }
    const { bondingCurve } = tokenData;
    if (bondingCurve.bonding_complete) {
        throw new Error('Bonding curve complete, trade on DEX');
    }
    const virtualSol = BigInt(bondingCurve.virtual_sol_reserves.toString());
    const virtualTokens = BigInt(bondingCurve.virtual_token_reserves.toString());
    const realSol = BigInt(bondingCurve.real_sol_reserves.toString());
    const bondingTarget = BigInt(bondingCurve.bonding_target.toString());
    const amountSol = BigInt(amountSolLamports);
    const result = (0, program_1.calculateTokensOut)(amountSol, virtualSol, virtualTokens, realSol, 100, 100, bondingTarget);
    const priceBefore = (0, program_1.calculatePrice)(virtualSol, virtualTokens);
    const priceAfter = (0, program_1.calculatePrice)(virtualSol + result.solToCurve, virtualTokens - result.tokensOut);
    const priceImpact = ((priceAfter - priceBefore) / priceBefore) * 100;
    const minOutput = (result.tokensToUser * BigInt(99)) / BigInt(100);
    return {
        input_sol: Number(amountSol),
        output_tokens: Number(result.tokensOut),
        tokens_to_user: Number(result.tokensToUser),
        tokens_to_treasury: Number(result.tokensToCommunity),
        protocol_fee_sol: Number(result.protocolFee),
        price_per_token_sol: (priceBefore * constants_1.TOKEN_MULTIPLIER) / constants_1.LAMPORTS_PER_SOL,
        price_impact_percent: priceImpact,
        min_output_tokens: Number(minOutput),
    };
};
exports.getBuyQuote = getBuyQuote;
/**
 * Get a sell quote: how much SOL for a given token amount.
 */
const getSellQuote = async (connection, mintStr, amountTokens) => {
    const mint = new web3_js_1.PublicKey(mintStr);
    const tokenData = await (0, tokens_1.fetchTokenRaw)(connection, mint);
    if (!tokenData) {
        throw new Error(`Token not found: ${mintStr}`);
    }
    const { bondingCurve } = tokenData;
    if (bondingCurve.bonding_complete) {
        throw new Error('Bonding curve complete, trade on DEX');
    }
    const virtualSol = BigInt(bondingCurve.virtual_sol_reserves.toString());
    const virtualTokens = BigInt(bondingCurve.virtual_token_reserves.toString());
    const tokenAmount = BigInt(amountTokens);
    const result = (0, program_1.calculateSolOut)(tokenAmount, virtualSol, virtualTokens);
    const priceBefore = (0, program_1.calculatePrice)(virtualSol, virtualTokens);
    const priceAfter = (0, program_1.calculatePrice)(virtualSol - result.solOut, virtualTokens + tokenAmount);
    const priceImpact = ((priceBefore - priceAfter) / priceBefore) * 100;
    const minOutput = (result.solToUser * BigInt(99)) / BigInt(100);
    return {
        input_tokens: Number(tokenAmount),
        output_sol: Number(result.solToUser),
        protocol_fee_sol: 0,
        price_per_token_sol: (priceBefore * constants_1.TOKEN_MULTIPLIER) / constants_1.LAMPORTS_PER_SOL,
        price_impact_percent: priceImpact,
        min_output_sol: Number(minOutput),
    };
};
exports.getSellQuote = getSellQuote;
/**
 * Get a borrow quote: maximum borrowable SOL for a given collateral amount on a migrated token.
 *
 * @param collateralAmount - Collateral in token base units (with 6 decimals)
 */
const getBorrowQuote = async (connection, mintStr, collateralAmount) => {
    const TRANSFER_FEE_BPS = 4;
    const [lending, detail] = await Promise.all([
        (0, tokens_1.getLendingInfo)(connection, mintStr),
        (0, tokens_1.getToken)(connection, mintStr),
    ]);
    const pricePerToken = detail.price_sol;
    const collateralDisplayTokens = collateralAmount / constants_1.TOKEN_MULTIPLIER;
    const collateralValueSol = collateralDisplayTokens * pricePerToken * constants_1.LAMPORTS_PER_SOL;
    // 1. LTV cap
    const ltvMaxSol = collateralValueSol * (lending.max_ltv_bps / 10000);
    // 2. Pool available
    const treasurySol = detail.treasury_sol_balance * constants_1.LAMPORTS_PER_SOL;
    const maxLendableSol = treasurySol * lending.utilization_cap_bps / 10000;
    const totalLent = lending.total_sol_lent ?? 0;
    const poolAvailableSol = Math.max(0, maxLendableSol - totalLent);
    // 3. Per-user cap (accounts for transfer fee reducing net collateral)
    const netCollateral = collateralAmount * (1 - TRANSFER_FEE_BPS / 10000);
    const borrowMultiplier = lending.borrow_share_multiplier || 3;
    const perUserCapSol = maxLendableSol * netCollateral * borrowMultiplier / Number(constants_1.TOTAL_SUPPLY);
    const maxBorrowSol = Math.max(0, Math.min(ltvMaxSol, poolAvailableSol, perUserCapSol));
    return {
        max_borrow_sol: Math.floor(maxBorrowSol),
        collateral_value_sol: Math.floor(collateralValueSol),
        ltv_max_sol: Math.floor(ltvMaxSol),
        pool_available_sol: Math.floor(poolAvailableSol),
        per_user_cap_sol: Math.floor(perUserCapSol),
        interest_rate_bps: lending.interest_rate_bps,
        liquidation_threshold_bps: lending.liquidation_threshold_bps,
    };
};
exports.getBorrowQuote = getBorrowQuote;
//# sourceMappingURL=quotes.js.map