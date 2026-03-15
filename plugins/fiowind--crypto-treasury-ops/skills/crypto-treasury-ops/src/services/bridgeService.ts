import { URL } from "node:url";
import { getAddress, type Address, type Hex } from "viem";
import { getNativeToken } from "../chains/index.js";
import { appConfig } from "../config.js";
import type { BridgeQuote, BridgeStatus, ChainName, FeeQuote, GasSuggestion, TokenInfo } from "../types.js";
import { WalletService } from "./walletService.js";
import { TokenService } from "./tokenService.js";

interface BridgeRequest {
  sourceChain: ChainName;
  destinationChain: ChainName;
  sourceToken: TokenInfo;
  destinationToken: TokenInfo;
  amount: bigint;
  fromAddress: Address;
  toAddress: Address;
  slippageBps?: number;
}

interface BridgeProvider {
  quote(request: BridgeRequest): Promise<BridgeQuote>;
  execute(quote: BridgeQuote): Promise<{
    sourceTxHash: Hex;
    approvalTxHash?: Hex;
  }>;
  waitForCompletion(quote: BridgeQuote, sourceTxHash: Hex): Promise<BridgeStatus>;
}

function normaliseBaseUrl(baseUrl: string): string {
  return baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
}

function parseFeeQuotes(rawFees: unknown): FeeQuote[] {
  if (!Array.isArray(rawFees)) {
    return [];
  }

  return rawFees.map((fee) => {
    const feeRecord = fee as Record<string, unknown>;
    return {
      name: String(feeRecord.name ?? "unknown"),
      amount: String(feeRecord.amount ?? "0"),
      amountUsd: feeRecord.amountUSD ? String(feeRecord.amountUSD) : undefined,
      tokenSymbol:
        typeof feeRecord.token === "object" && feeRecord.token
          ? String((feeRecord.token as Record<string, unknown>).symbol ?? "")
          : undefined,
      percentageBps: feeRecord.percentage ? Math.round(Number(feeRecord.percentage) * 100) : undefined,
      included: typeof feeRecord.included === "boolean" ? feeRecord.included : undefined
    };
  });
}

class LifiBridgeProvider implements BridgeProvider {
  public constructor(
    private readonly walletService: WalletService,
    private readonly tokenService: TokenService
  ) {}

  public async quote(request: BridgeRequest): Promise<BridgeQuote> {
    const endpoint = new URL(`${normaliseBaseUrl(appConfig.bridge.lifiApiUrl)}/quote`);
    endpoint.searchParams.set("fromChain", String(request.sourceToken.chain === "ethereum" ? 1 : undefined));
    endpoint.searchParams.delete("fromChain");
    endpoint.searchParams.set("fromChain", this.toChainId(request.sourceChain));
    endpoint.searchParams.set("toChain", this.toChainId(request.destinationChain));
    endpoint.searchParams.set("fromToken", request.sourceToken.address!);
    endpoint.searchParams.set("toToken", request.destinationToken.address!);
    endpoint.searchParams.set("fromAmount", request.amount.toString());
    endpoint.searchParams.set("fromAddress", request.fromAddress);
    endpoint.searchParams.set("toAddress", request.toAddress);
    if (!request.sourceToken.isNative && !request.destinationToken.isNative) {
      endpoint.searchParams.set("preset", "stablecoin");
    }
    endpoint.searchParams.set("integrator", appConfig.bridge.integrator);
    endpoint.searchParams.set(
      "slippage",
      String((request.slippageBps ?? appConfig.safety.maxSlippageBps) / 10_000)
    );

    const response = await fetch(endpoint, {
      headers: appConfig.bridge.lifiApiKey
        ? {
            "x-lifi-api-key": appConfig.bridge.lifiApiKey
          }
        : undefined
    });

    if (!response.ok) {
      const body = await response.text();
      throw new Error(`LI.FI quote failed: ${response.status} ${body}`);
    }

    const payload = (await response.json()) as Record<string, unknown>;
    const estimate = (payload.estimate ?? {}) as Record<string, unknown>;
    const transactionRequest = (payload.transactionRequest ?? {}) as Record<string, unknown>;

    return {
      provider: "lifi",
      routeId: typeof payload.id === "string" ? payload.id : undefined,
      tool: typeof payload.tool === "string" ? payload.tool : undefined,
      sourceChain: request.sourceChain,
      destinationChain: request.destinationChain,
      sourceToken: request.sourceToken,
      destinationToken: request.destinationToken,
      fromAmountRaw: request.amount,
      toAmountRaw: BigInt(String(estimate.toAmount ?? "0")),
      minReceivedRaw: estimate.toAmountMin ? BigInt(String(estimate.toAmountMin)) : undefined,
      approvalAddress: estimate.approvalAddress ? getAddress(String(estimate.approvalAddress)) : undefined,
      transactionRequest: {
        to: transactionRequest.to ? getAddress(String(transactionRequest.to)) : undefined,
        data: transactionRequest.data ? (String(transactionRequest.data) as Hex) : undefined,
        value: transactionRequest.value ? String(transactionRequest.value) : undefined,
        gasLimit: transactionRequest.gasLimit ? String(transactionRequest.gasLimit) : undefined,
        gasPrice: transactionRequest.gasPrice ? String(transactionRequest.gasPrice) : undefined
      },
      feeQuotes: parseFeeQuotes(estimate.feeCosts),
      raw: payload
    };
  }

  public async execute(quote: BridgeQuote): Promise<{ sourceTxHash: Hex; approvalTxHash?: Hex }> {
    const sourceToken = quote.sourceToken;
    const sender = this.walletService.getTreasuryAddress();

    let approvalTxHash: Hex | undefined;
    if (quote.approvalAddress) {
      approvalTxHash = await this.tokenService.ensureAllowance(
        quote.sourceChain,
        sourceToken,
        sender,
        quote.approvalAddress,
        quote.fromAmountRaw
      );
    }

    const txRequest = quote.transactionRequest;
    if (!txRequest?.to) {
      throw new Error("Bridge quote did not include transaction request data.");
    }

    const sourceTxHash = await this.walletService.sendTransaction(quote.sourceChain, {
      to: txRequest.to,
      data: txRequest.data,
      value: txRequest.value ? BigInt(txRequest.value) : 0n,
      gas: txRequest.gasLimit ? BigInt(txRequest.gasLimit) : undefined
    });

    await this.walletService.waitForReceipt(quote.sourceChain, sourceTxHash);
    return { sourceTxHash, approvalTxHash };
  }

  public async waitForCompletion(quote: BridgeQuote, sourceTxHash: Hex): Promise<BridgeStatus> {
    const startedAt = Date.now();

    while (Date.now() - startedAt < appConfig.bridge.statusTimeoutMs) {
      const endpoint = new URL(`${normaliseBaseUrl(appConfig.bridge.lifiApiUrl)}/status`);
      endpoint.searchParams.set("txHash", sourceTxHash);
      endpoint.searchParams.set("fromChain", this.toChainId(quote.sourceChain));
      endpoint.searchParams.set("toChain", this.toChainId(quote.destinationChain));
      if (quote.tool) {
        endpoint.searchParams.set("bridge", quote.tool);
      }

      const response = await fetch(endpoint, {
        headers: appConfig.bridge.lifiApiKey
          ? {
              "x-lifi-api-key": appConfig.bridge.lifiApiKey
            }
          : undefined
      });

      if (!response.ok) {
        const body = await response.text();
        throw new Error(`LI.FI status lookup failed: ${response.status} ${body}`);
      }

      const payload = (await response.json()) as Record<string, unknown>;
      const status = String(payload.status ?? "NOT_FOUND") as BridgeStatus["status"];

      if (status === "DONE" || status === "FAILED" || status === "INVALID") {
        const receiving = (payload.receiving ?? {}) as Record<string, unknown>;
        return {
          provider: "lifi",
          status,
          substatus: payload.substatus ? String(payload.substatus) : undefined,
          substatusMessage: payload.substatusMessage ? String(payload.substatusMessage) : undefined,
          tool: payload.tool ? String(payload.tool) : quote.tool,
          txHash: sourceTxHash,
          explorerUrl: payload.lifiExplorerLink ? String(payload.lifiExplorerLink) : undefined,
          receivingTxHash: receiving.txHash ? (String(receiving.txHash) as Hex) : undefined,
          receivedAmountRaw: receiving.amount ? BigInt(String(receiving.amount)) : undefined,
          raw: payload
        };
      }

      await new Promise((resolve) => setTimeout(resolve, appConfig.bridge.statusPollMs));
    }

    return {
      provider: "lifi",
      status: "PENDING",
      txHash: sourceTxHash,
      tool: quote.tool,
      raw: {
        timeoutMs: appConfig.bridge.statusTimeoutMs
      }
    };
  }

  private toChainId(chain: ChainName): string {
    switch (chain) {
      case "ethereum":
        return "1";
      case "polygon":
        return "137";
      case "arbitrum":
        return "42161";
      case "base":
        return "8453";
    }
  }
}

class AcrossBridgeProvider implements BridgeProvider {
  public async quote(): Promise<BridgeQuote> {
    // TODO: integrate Across quote and execution APIs when provider selection is switched to "across".
    throw new Error("Across bridge provider is not implemented yet.");
  }

  public async execute(): Promise<{ sourceTxHash: Hex; approvalTxHash?: Hex }> {
    throw new Error("Across bridge provider is not implemented yet.");
  }

  public async waitForCompletion(): Promise<BridgeStatus> {
    throw new Error("Across bridge provider is not implemented yet.");
  }
}

class RelayBridgeProvider implements BridgeProvider {
  public async quote(): Promise<BridgeQuote> {
    // TODO: integrate Relay API credentials and response parsing when provider selection is switched to "relay".
    throw new Error("Relay bridge provider is not implemented yet.");
  }

  public async execute(): Promise<{ sourceTxHash: Hex; approvalTxHash?: Hex }> {
    throw new Error("Relay bridge provider is not implemented yet.");
  }

  public async waitForCompletion(): Promise<BridgeStatus> {
    throw new Error("Relay bridge provider is not implemented yet.");
  }
}

export class BridgeService {
  private readonly provider: BridgeProvider;

  public constructor(
    walletService: WalletService,
    tokenService: TokenService
  ) {
    switch (appConfig.bridge.provider) {
      case "lifi":
        this.provider = new LifiBridgeProvider(walletService, tokenService);
        break;
      case "across":
        this.provider = new AcrossBridgeProvider();
        break;
      case "relay":
        this.provider = new RelayBridgeProvider();
        break;
      default:
        throw new Error(`Unsupported bridge provider "${appConfig.bridge.provider}".`);
    }
  }

  public quoteTransfer(request: BridgeRequest): Promise<BridgeQuote> {
    return this.provider.quote(request);
  }

  public executeBridge(quote: BridgeQuote): Promise<{ sourceTxHash: Hex; approvalTxHash?: Hex }> {
    return this.provider.execute(quote);
  }

  public waitForBridgeCompletion(quote: BridgeQuote, sourceTxHash: Hex): Promise<BridgeStatus> {
    return this.provider.waitForCompletion(quote, sourceTxHash);
  }

  public async getGasSuggestion(
    destinationChain: ChainName,
    sourceChain: ChainName,
    sourceToken: TokenInfo
  ): Promise<GasSuggestion | undefined> {
    const endpoint = new URL(`${normaliseBaseUrl(appConfig.bridge.lifiApiUrl)}/gas/suggestion/${this.toChainId(destinationChain)}`);
    endpoint.searchParams.set("fromChain", this.toChainId(sourceChain));
    endpoint.searchParams.set("fromToken", sourceToken.address ?? sourceToken.symbol);

    const response = await fetch(endpoint, {
      headers: appConfig.bridge.lifiApiKey
        ? {
            "x-lifi-api-key": appConfig.bridge.lifiApiKey
          }
        : undefined
    });

    if (!response.ok) {
      return undefined;
    }

    const payload = (await response.json()) as Record<string, unknown>;
    const recommended = (payload.recommended ?? {}) as Record<string, unknown>;
    if (!recommended.amount || !payload.fromAmount) {
      return undefined;
    }

    return {
      destinationChain,
      destinationToken: getNativeToken(destinationChain),
      recommendedDestinationAmountRaw: BigInt(String(recommended.amount)),
      sourceToken,
      requiredSourceAmountRaw: BigInt(String(payload.fromAmount)),
      raw: payload
    };
  }

  private toChainId(chain: ChainName): string {
    switch (chain) {
      case "ethereum":
        return "1";
      case "polygon":
        return "137";
      case "arbitrum":
        return "42161";
      case "base":
        return "8453";
    }
  }
}
