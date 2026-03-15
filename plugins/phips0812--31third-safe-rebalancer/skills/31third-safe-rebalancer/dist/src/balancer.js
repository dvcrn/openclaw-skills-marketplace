import { parseAbi } from 'viem';
import { calculateRebalancing } from '@31third/sdk';
import { tokenFeedRegistryAbi } from './contracts.js';
const erc20Abi = parseAbi([
    'function balanceOf(address account) view returns (uint256)',
    'function decimals() view returns (uint8)',
    'function symbol() view returns (string)'
]);
const chainlinkFeedAbi = parseAbi([
    'function decimals() view returns (uint8)',
    'function latestRoundData() view returns (uint80,int256,uint256,uint256,uint80)'
]);
function tenPow(decimals) {
    return 10n ** BigInt(decimals);
}
function absDiff(a, b) {
    return a > b ? a - b : b - a;
}
function toPercentageString(bps) {
    return (bps / 100).toFixed(2);
}
async function readTokenSymbol(publicClient, token) {
    try {
        return (await publicClient.readContract({
            address: token,
            abi: erc20Abi,
            functionName: 'symbol'
        }));
    }
    catch {
        return `${token.slice(0, 6)}...${token.slice(-4)}`;
    }
}
async function readTokenDecimals(publicClient, token) {
    const decimals = (await publicClient.readContract({
        address: token,
        abi: erc20Abi,
        functionName: 'decimals'
    }));
    return Number(decimals);
}
async function readTokenFeed(publicClient, tokenFeedRegistry, token) {
    return (await publicClient.readContract({
        address: tokenFeedRegistry,
        abi: tokenFeedRegistryAbi,
        functionName: 'getFeed',
        args: [token]
    }));
}
async function readPriceAndDecimals(publicClient, feed, oracleMaxAgeSeconds) {
    const decimals = (await publicClient.readContract({
        address: feed,
        abi: chainlinkFeedAbi,
        functionName: 'decimals'
    }));
    const latestRoundData = (await publicClient.readContract({
        address: feed,
        abi: chainlinkFeedAbi,
        functionName: 'latestRoundData'
    }));
    const roundId = latestRoundData[0];
    const answer = latestRoundData[1];
    const updatedAt = latestRoundData[3];
    const answeredInRound = latestRoundData[4];
    if (updatedAt === 0n) {
        return { price: 0n, decimals: Number(decimals), staleReason: 'oracle returned zero updatedAt timestamp' };
    }
    if (answeredInRound < roundId) {
        return {
            price: 0n,
            decimals: Number(decimals),
            staleReason: 'oracle round is incomplete (answeredInRound < roundId)'
        };
    }
    if (typeof oracleMaxAgeSeconds === 'number') {
        const nowSec = BigInt(Math.floor(Date.now() / 1000));
        const ageSeconds = nowSec > updatedAt ? nowSec - updatedAt : 0n;
        if (ageSeconds > BigInt(oracleMaxAgeSeconds)) {
            return {
                price: 0n,
                decimals: Number(decimals),
                staleReason: `oracle price is stale (age ${ageSeconds.toString()}s > ${oracleMaxAgeSeconds}s)`
            };
        }
    }
    if (answer <= 0n) {
        return { price: 0n, decimals: Number(decimals), staleReason: 'oracle answer is non-positive' };
    }
    return { price: answer, decimals: Number(decimals) };
}
function usdValueLikePolicy(amount, tokenDecimals, price, priceDecimals) {
    if (amount === 0n || price === 0n) {
        return 0n;
    }
    let value = (amount * price) / tenPow(tokenDecimals);
    if (priceDecimals > 18) {
        value = value / tenPow(priceDecimals - 18);
    }
    else if (priceDecimals < 18) {
        value = value * tenPow(18 - priceDecimals);
    }
    return value;
}
export async function checkDrift(params) {
    const { publicClient, safeAddress, tokenFeedRegistry, policies, oracleMaxAgeSeconds } = params;
    if (policies.targetAllocations.length === 0) {
        return {
            totalUsd18: 0n,
            thresholdBps: 0,
            exceedsThreshold: false,
            maxDriftBps: 0,
            tokens: [],
            explanation: 'No StaticAllocation policy detected. Drift checks require target allocations.'
        };
    }
    const thresholdBps = policies.driftThresholdBps ?? 0;
    const tokens = policies.targetAllocations.map((item) => item.token);
    const raw = await Promise.all(tokens.map(async (token) => {
        const [symbol, decimals, balance, feed] = await Promise.all([
            readTokenSymbol(publicClient, token),
            readTokenDecimals(publicClient, token),
            publicClient.readContract({
                address: token,
                abi: erc20Abi,
                functionName: 'balanceOf',
                args: [safeAddress]
            }),
            readTokenFeed(publicClient, tokenFeedRegistry, token)
        ]);
        const { price, decimals: priceDecimals, staleReason } = await readPriceAndDecimals(publicClient, feed, oracleMaxAgeSeconds);
        if (staleReason) {
            throw new Error(`Stale or invalid price for ${token}: ${staleReason}`);
        }
        const valueUsd18 = usdValueLikePolicy(balance, decimals, price, priceDecimals);
        return { token, symbol, balance, valueUsd18 };
    }));
    const totalUsd18 = raw.reduce((sum, item) => sum + item.valueUsd18, 0n);
    const driftTokens = raw.map((item) => {
        const target = policies.targetAllocations.find((entry) => entry.token.toLowerCase() === item.token.toLowerCase());
        const targetWeightBps = target ? Number(target.bps) : 0;
        const currentWeightBps = totalUsd18 === 0n ? 0 : Number((item.valueUsd18 * 10000n) / totalUsd18);
        const driftBps = absDiff(currentWeightBps, targetWeightBps);
        return {
            token: item.token,
            symbol: item.symbol,
            balance: item.balance,
            valueUsd18: item.valueUsd18,
            currentWeightBps,
            targetWeightBps,
            driftBps
        };
    });
    const maxDrift = driftTokens.reduce((max, item) => (item.driftBps > max ? item.driftBps : max), 0);
    const mostDrifted = driftTokens.find((item) => item.driftBps === maxDrift);
    const exceedsThreshold = maxDrift >= thresholdBps;
    const explanation = mostDrifted
        ? `${mostDrifted.symbol} is at ${toPercentageString(mostDrifted.currentWeightBps)}%, target ${toPercentageString(mostDrifted.targetWeightBps)}% (drift ${mostDrifted.driftBps} bps).`
        : 'No tracked assets found for drift calculation.';
    return {
        totalUsd18,
        thresholdBps,
        exceedsThreshold,
        maxDriftBps: maxDrift,
        tokens: driftTokens,
        explanation
    };
}
export async function validateTrade(params) {
    const { publicClient, tokenFeedRegistry, policies, trade, oracleMaxAgeSeconds } = params;
    if (policies.assetUniverseTokens.length > 0) {
        const normalized = new Set(policies.assetUniverseTokens.map((token) => token.toLowerCase()));
        if (!normalized.has(trade.from.toLowerCase())) {
            return { ok: false, reason: `Asset Universe violation: from token ${trade.from} is not allowed.` };
        }
        if (!normalized.has(trade.to.toLowerCase())) {
            return { ok: false, reason: `Asset Universe violation: to token ${trade.to} is not allowed.` };
        }
    }
    if (typeof policies.maxSlippageBps === 'number') {
        const [fromFeed, toFeed, fromTokenDecimals, toTokenDecimals] = await Promise.all([
            readTokenFeed(publicClient, tokenFeedRegistry, trade.from),
            readTokenFeed(publicClient, tokenFeedRegistry, trade.to),
            readTokenDecimals(publicClient, trade.from),
            readTokenDecimals(publicClient, trade.to)
        ]);
        const [fromPriceData, toPriceData] = await Promise.all([
            readPriceAndDecimals(publicClient, fromFeed, oracleMaxAgeSeconds),
            readPriceAndDecimals(publicClient, toFeed, oracleMaxAgeSeconds)
        ]);
        if (fromPriceData.staleReason || toPriceData.staleReason) {
            return {
                ok: false,
                reason: `Slippage validation failed: ${fromPriceData.staleReason ?? toPriceData.staleReason}`
            };
        }
        if (fromPriceData.price === 0n || toPriceData.price === 0n) {
            return {
                ok: false,
                reason: 'Slippage validation failed: missing valid price feed answer for one or more trade tokens.'
            };
        }
        const numerator = (trade.fromAmount * fromPriceData.price) / tenPow(fromTokenDecimals);
        let expectedTo = (numerator * tenPow(toTokenDecimals)) / toPriceData.price;
        if (fromPriceData.decimals > toPriceData.decimals) {
            expectedTo = expectedTo / tenPow(fromPriceData.decimals - toPriceData.decimals);
        }
        else if (toPriceData.decimals > fromPriceData.decimals) {
            expectedTo = expectedTo * tenPow(toPriceData.decimals - fromPriceData.decimals);
        }
        const minAllowed = (expectedTo * BigInt(10_000 - policies.maxSlippageBps)) / 10000n;
        if (trade.minToReceiveBeforeFees < minAllowed) {
            return {
                ok: false,
                reason: `Slippage violation: minToReceive ${trade.minToReceiveBeforeFees.toString()} below minimum ${minAllowed.toString()}.`,
                minAllowedToReceive: minAllowed
            };
        }
    }
    return { ok: true, reason: 'Trade validated against Asset Universe and Slippage boundaries.' };
}
export async function buildBaseEntriesFromAssetUniverse(params) {
    if (params.assetUniverseTokens.length === 0) {
        return [];
    }
    const balances = await Promise.all(params.assetUniverseTokens.map(async (token) => {
        const balance = (await params.publicClient.readContract({
            address: token,
            abi: erc20Abi,
            functionName: 'balanceOf',
            args: [params.safeAddress]
        }));
        return { tokenAddress: token, balance };
    }));
    return balances
        .filter((entry) => entry.balance > 0n)
        .map((entry) => ({
        tokenAddress: entry.tokenAddress,
        amount: entry.balance.toString()
    }));
}
export async function planRebalancingWithSdk(input) {
    return calculateRebalancing({
        apiBaseUrl: 'https://api.31third.com/1.3',
        apiKey: input.apiKey,
        chainId: input.chainId,
        payload: {
            wallet: input.safeAddress,
            signer: input.signerAddress,
            chainId: input.chainId,
            minTradeValue: input.minTradeValue,
            baseEntries: input.baseEntries ?? [],
            targetEntries: input.targetAllocations.map((target) => ({
                tokenAddress: target.token,
                allocation: target.bps / 10_000
            }))
        }
    });
}
