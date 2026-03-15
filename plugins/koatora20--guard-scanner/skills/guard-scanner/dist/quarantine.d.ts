/**
 * QuarantineNode - Dual-Brain Architecture
 * Evaluates inputs in an isolated context to prevent Zero-Click prompt injections (EchoLeak) and API leaks.
 */
export interface QuarantineResult {
    clean: boolean;
    threatDetected?: string;
    sanitizedText: string;
}
export declare class QuarantineNode {
    readonly isIsolated: boolean;
    constructor();
    /**
     * Sanitizes untrusted text by removing known zero-click exploits and API secrets.
     */
    sanitize(input: string): Promise<QuarantineResult>;
}
//# sourceMappingURL=quarantine.d.ts.map