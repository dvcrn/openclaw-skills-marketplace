import { calculateRebalancing, executeRebalancing } from '@31third/sdk';
import { Contract, JsonRpcProvider, Wallet, isAddress } from 'ethers';
import { aggregatorV3Abi, assetUniversePolicyAbi, erc20Abi, executorModuleAbi, slippagePolicyAbi, staticAllocationPolicyAbi, tokenFeedRegistryAbi } from './src/contracts.js';
const ZERO_ADDRESS = '0x0000000000000000000000000000000000000000';
function required(name) {
    const value = process.env[name];
    if (!value) {
        throw new Error(`Missing ${name}`);
    }
    return value;
}
function readPositiveNumber(name, fallback) {
    const raw = process.env[name];
    if (!raw)
        return fallback;
    const parsed = Number(raw);
    if (!Number.isFinite(parsed) || parsed <= 0) {
        throw new Error(`Invalid ${name}`);
    }
    return parsed;
}
export function readConfigFromEnv() {
    const safeAddress = required('SAFE_ADDRESS');
    const executorModuleAddress = required('EXECUTOR_MODULE_ADDRESS');
    const rpcUrl = process.env.RPC_URL ?? 'https://mainnet.base.org';
    const apiKey = required('TOT_API_KEY');
    const executorWalletPrivateKey = required('EXECUTOR_WALLET_PRIVATE_KEY');
    const chainId = Number(process.env.CHAIN_ID ?? '8453');
    if (!Number.isInteger(chainId) || chainId <= 0) {
        throw new Error('Invalid CHAIN_ID');
    }
    if (!isAddress(safeAddress)) {
        throw new Error('Invalid SAFE_ADDRESS');
    }
    if (!isAddress(executorModuleAddress)) {
        throw new Error('Invalid EXECUTOR_MODULE_ADDRESS');
    }
    return {
        safeAddress,
        executorModuleAddress,
        executorWalletPrivateKey,
        apiKey,
        rpcUrl,
        chainId,
        apiBaseUrl: process.env.API_BASE_URL ?? 'https://api.31third.com/1.3',
        maxSlippage: readPositiveNumber('MAX_SLIPPAGE', 0.01),
        maxPriceImpact: readPositiveNumber('MAX_PRICE_IMPACT', 0.05),
        minTradeValue: readPositiveNumber('MIN_TRADE_VALUE', 0.1),
        skipBalanceValidation: (process.env.SKIP_BALANCE_VALIDATION ?? 'false').toLowerCase() === 'true'
    };
}
function normalizePolicyState(entry) {
    const policy = entry?.policy ?? (Array.isArray(entry) ? entry[0] : undefined);
    const policyType = entry?.policyType ?? (Array.isArray(entry) ? entry[1] : undefined);
    return {
        policy: typeof policy === 'string' ? policy : '',
        policyType: typeof policyType === 'string' ? policyType : ''
    };
}
function readPolicyAddresses(policies) {
    const find = (name) => policies.find((p) => p.policyType.toLowerCase() === name)?.policy;
    return {
        assetUniverseAddress: find('assetuniverse'),
        staticAllocationAddress: find('staticallocation'),
        slippageAddress: find('slippage')
    };
}
async function defaultLoadPlanInputs(config, provider, manualTargetEntries) {
    const executor = new Contract(config.executorModuleAddress, executorModuleAbi, provider);
    const [scheduler, registry] = await Promise.all([
        executor.scheduler(),
        executor.registry()
    ]);
    const policiesRaw = await executor.getPoliciesWithTypes();
    const policies = policiesRaw.map(normalizePolicyState);
    const policyAddresses = readPolicyAddresses(policies);
    const notes = [];
    let baseEntries = [];
    if (policyAddresses.assetUniverseAddress) {
        const assetUniverse = new Contract(policyAddresses.assetUniverseAddress, assetUniversePolicyAbi, provider);
        const assetUniverseTokens = await assetUniverse.getTokens();
        const balances = await Promise.all(assetUniverseTokens.map(async (tokenAddress) => {
            const token = new Contract(tokenAddress, erc20Abi, provider);
            const amount = await token.balanceOf(config.safeAddress);
            return { tokenAddress, amount };
        }));
        baseEntries = balances
            .filter((entry) => entry.amount > 0n)
            .map((entry) => ({ tokenAddress: entry.tokenAddress, amount: entry.amount.toString() }));
    }
    else {
        notes.push('AssetUniverse policy not deployed; baseEntries defaulted to empty array.');
    }
    let targetEntries = [];
    let driftThresholdBps;
    let feedRegistry;
    if (policyAddresses.staticAllocationAddress) {
        const staticAllocation = new Contract(policyAddresses.staticAllocationAddress, staticAllocationPolicyAbi, provider);
        const [rawTargets, rawDriftThresholdBps, staticFeedRegistry] = await Promise.all([
            staticAllocation.getAllTargets(),
            staticAllocation.driftThresholdBps(),
            staticAllocation.feedRegistry()
        ]);
        targetEntries = rawTargets.map((target) => {
            const tokenAddress = target?.token ?? (Array.isArray(target) ? target[0] : undefined);
            const bps = target?.bps ?? (Array.isArray(target) ? target[1] : undefined);
            if (typeof tokenAddress !== 'string' || typeof bps === 'undefined') {
                throw new Error('Invalid target entry on StaticAllocation policy.');
            }
            return {
                tokenAddress,
                allocation: Number(bps) / 10_000
            };
        });
        driftThresholdBps = Number(rawDriftThresholdBps);
        feedRegistry = staticFeedRegistry;
    }
    else if (manualTargetEntries && manualTargetEntries.length > 0) {
        targetEntries = manualTargetEntries;
        notes.push('StaticAllocation policy not deployed; using manually provided target entries.');
    }
    else {
        throw new Error('Missing StaticAllocation policy on ExecutorModule. Cannot auto fetch target allocation. Please pass targetEntries manually.');
    }
    let effectiveMaxSlippage = config.maxSlippage;
    let effectiveMaxPriceImpact = config.maxPriceImpact;
    if (policyAddresses.slippageAddress) {
        const slippagePolicy = new Contract(policyAddresses.slippageAddress, slippagePolicyAbi, provider);
        const bps = Number(await slippagePolicy.maxSlippageBps());
        const adjusted = Math.max(0, bps / 10_000 - 0.001);
        effectiveMaxSlippage = adjusted;
        effectiveMaxPriceImpact = adjusted;
    }
    else {
        notes.push('Slippage policy not deployed; using configured/default maxSlippage/maxPriceImpact.');
    }
    return {
        scheduler,
        registry,
        baseEntries,
        targetEntries,
        driftThresholdBps,
        feedRegistry,
        effectiveMaxSlippage,
        effectiveMaxPriceImpact,
        notes
    };
}
function tenPow(exp) {
    const e = BigInt(exp);
    if (e <= 0n)
        return 1n;
    return 10n ** e;
}
function abs(n) {
    return n >= 0n ? n : -n;
}
async function defaultCheckDrift(config, provider, targetEntries, driftThresholdBps, feedRegistry) {
    if (!targetEntries.length || !feedRegistry || !isAddress(feedRegistry)) {
        return {
            computable: false,
            maxDriftBps: 0,
            thresholdBps: driftThresholdBps,
            shouldRebalance: true,
            reason: 'Drift precheck skipped: missing target entries or feed registry.'
        };
    }
    const registry = new Contract(feedRegistry, tokenFeedRegistryAbi, provider);
    const values = await Promise.all(targetEntries.map(async (target) => {
        const token = new Contract(target.tokenAddress, erc20Abi, provider);
        const [balance, tokenDecimalsRaw, feedAddress] = await Promise.all([
            token.balanceOf(config.safeAddress),
            token.decimals(),
            registry.getFeed(target.tokenAddress)
        ]);
        const tokenDecimals = Number(tokenDecimalsRaw);
        if (!feedAddress || feedAddress.toLowerCase() === ZERO_ADDRESS) {
            return { target, usd18: null };
        }
        const feed = new Contract(feedAddress, aggregatorV3Abi, provider);
        const [feedDecimalsRaw, latestRoundData] = await Promise.all([
            feed.decimals(),
            feed.latestRoundData()
        ]);
        const feedDecimals = Number(feedDecimalsRaw);
        const price = latestRoundData[1];
        if (price <= 0n) {
            return { target, usd18: null };
        }
        let usd18 = (balance * price) / tenPow(tokenDecimals);
        if (feedDecimals < 18) {
            usd18 *= tenPow(18 - feedDecimals);
        }
        else if (feedDecimals > 18) {
            usd18 /= tenPow(feedDecimals - 18);
        }
        return { target, usd18 };
    }));
    if (values.some((v) => v.usd18 === null)) {
        return {
            computable: false,
            maxDriftBps: 0,
            thresholdBps: driftThresholdBps,
            shouldRebalance: true,
            reason: 'Drift precheck skipped: one or more target tokens have missing/invalid feeds.'
        };
    }
    const totalUsd18 = values.reduce((acc, v) => acc + v.usd18, 0n);
    if (totalUsd18 <= 0n) {
        return {
            computable: false,
            maxDriftBps: 0,
            thresholdBps: driftThresholdBps,
            shouldRebalance: true,
            reason: 'Drift precheck skipped: portfolio value is zero.'
        };
    }
    let maxDriftBps = 0;
    for (const entry of values) {
        const currentWeightBps = Number((entry.usd18 * 10000n) / totalUsd18);
        const targetWeightBps = Math.round(entry.target.allocation * 10_000);
        const drift = Number(abs(BigInt(currentWeightBps - targetWeightBps)));
        if (drift > maxDriftBps) {
            maxDriftBps = drift;
        }
    }
    const shouldRebalance = maxDriftBps >= driftThresholdBps;
    return {
        computable: true,
        maxDriftBps,
        thresholdBps: driftThresholdBps,
        shouldRebalance,
        reason: shouldRebalance
            ? `Drift check passed for execution: max drift ${maxDriftBps} bps >= threshold ${driftThresholdBps} bps.`
            : `Skipped: max drift ${maxDriftBps} bps < threshold ${driftThresholdBps} bps.`
    };
}
export async function rebalance_now(params) {
    const config = params?.config ?? readConfigFromEnv();
    const deps = params?.deps ?? {};
    const calculateRebalancingFn = deps.calculateRebalancingFn ?? calculateRebalancing;
    const executeRebalancingFn = deps.executeRebalancingFn ?? executeRebalancing;
    const loadPlanInputsFn = deps.loadPlanInputsFn ?? defaultLoadPlanInputs;
    const createExecutorSignerFn = deps.createExecutorSignerFn ?? ((cfg, provider) => new Wallet(cfg.executorWalletPrivateKey, provider));
    const checkDriftFn = deps.checkDriftFn ?? defaultCheckDrift;
    const provider = new JsonRpcProvider(config.rpcUrl);
    const executorSigner = createExecutorSignerFn(config, provider);
    const executorWallet = await executorSigner.getAddress();
    const { scheduler, registry, baseEntries, targetEntries, driftThresholdBps, feedRegistry, effectiveMaxSlippage, effectiveMaxPriceImpact, notes } = await loadPlanInputsFn(config, provider, params?.targetEntries);
    if (scheduler.toLowerCase() !== registry.toLowerCase()) {
        throw new Error(`SCHEDULER_REGISTRY_MISMATCH: scheduler=${scheduler} registry=${registry}`);
    }
    if (executorWallet.toLowerCase() === ZERO_ADDRESS) {
        throw new Error('EXECUTOR_WALLET_ZERO_ADDRESS: executor wallet cannot be zero address.');
    }
    if (executorWallet.toLowerCase() !== registry.toLowerCase()) {
        throw new Error(`EXECUTOR_WALLET_NOT_REGISTRY: wallet=${executorWallet} registry=${registry}`);
    }
    let maxDriftBps;
    if (typeof driftThresholdBps === 'number' && targetEntries.length > 0 && feedRegistry) {
        const drift = await checkDriftFn(config, provider, targetEntries, driftThresholdBps, feedRegistry);
        if (drift.computable) {
            maxDriftBps = drift.maxDriftBps;
        }
        if (!drift.shouldRebalance) {
            return {
                executed: false,
                skipped: true,
                scheduler,
                registry,
                executorWallet,
                baseEntriesCount: baseEntries.length,
                targetEntriesCount: targetEntries.length,
                maxDriftBps,
                driftThresholdBps: drift.thresholdBps,
                effectiveMaxSlippage,
                effectiveMaxPriceImpact,
                message: drift.reason
            };
        }
        if (!drift.computable) {
            notes.push(drift.reason);
        }
    }
    const rebalancing = await calculateRebalancingFn({
        apiBaseUrl: config.apiBaseUrl,
        apiKey: config.apiKey,
        chainId: config.chainId,
        payload: {
            wallet: config.safeAddress,
            signer: config.safeAddress,
            chainId: config.chainId,
            baseEntries,
            targetEntries,
            maxSlippage: effectiveMaxSlippage,
            maxPriceImpact: effectiveMaxPriceImpact,
            minTradeValue: config.minTradeValue,
            skipBalanceValidation: config.skipBalanceValidation
        }
    });
    const tx = await executeRebalancingFn({
        signer: executorSigner,
        executorModule: config.executorModuleAddress,
        rebalancing: rebalancing
    });
    await tx.wait();
    return {
        executed: true,
        skipped: false,
        txHash: tx.hash,
        scheduler,
        registry,
        executorWallet,
        baseEntriesCount: baseEntries.length,
        targetEntriesCount: targetEntries.length,
        maxDriftBps,
        driftThresholdBps,
        effectiveMaxSlippage,
        effectiveMaxPriceImpact,
        message: [
            'Rebalance executed using deployed on-chain policies.',
            ...notes
        ].join(' ')
    };
}
export function help() {
    return {
        summary: 'Simple one-step Safe rebalance tool. Use rebalance_now by default.',
        requiredEnv: [
            'SAFE_ADDRESS',
            'EXECUTOR_MODULE_ADDRESS',
            'EXECUTOR_WALLET_PRIVATE_KEY',
            'TOT_API_KEY',
            'RPC_URL (optional, default https://mainnet.base.org)',
            'CHAIN_ID (optional, default 8453)',
            'MIN_TRADE_VALUE (optional, default 0.1)'
        ],
        setupSteps: [
            'Deploy module + policies using the 31Third policy wizard: https://app.31third.com/safe-policy-deployer',
            'Use two wallets: Safe owner wallet (never share key) and executor wallet (configured on ExecutorModule)',
            'Copy env vars from the wizard final step',
            'Request a 31Third API key via https://31third.com or dev@31third.com',
            'Run only one command for normal usage: npm run cli -- rebalance-now',
            'If StaticAllocation policy is not deployed, pass targetEntries manually to rebalance_now.'
        ]
    };
}
