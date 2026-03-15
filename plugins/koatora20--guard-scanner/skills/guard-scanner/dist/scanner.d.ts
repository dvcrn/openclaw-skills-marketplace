/**
 * guard-scanner v3.0.0 — Core Scanner (TypeScript)
 *
 * Full TypeScript rewrite of guard-scanner v2.1.0 + hbg-scan features.
 * Adds: Compaction Persistence check, Signature hash matching, typed interfaces.
 *
 * Zero dependencies. MIT License.
 */
import type { SkillResult, ScannerOptions, ScanStats, Thresholds, JSONReport, SARIFReport } from './types.js';
export declare const VERSION = "4.0.1";
export declare class GuardScanner {
    readonly verbose: boolean;
    readonly selfExclude: boolean;
    readonly strict: boolean;
    readonly summaryOnly: boolean;
    /** Suppress all console.log output (v3.2.0: for --format stdout piping) */
    readonly quiet: boolean;
    readonly checkDeps: boolean;
    readonly thresholds: Thresholds;
    findings: SkillResult[];
    stats: ScanStats;
    private scannerDir;
    private ignoredSkills;
    private ignoredPatterns;
    private customRules;
    constructor(options?: ScannerOptions);
    loadPlugin(pluginPath: string): void;
    loadCustomRules(rulesFile: string): void;
    private loadIgnoreFile;
    scanDirectory(dir: string): SkillResult[];
    scanSkill(skillPath: string, skillName: string): void;
    private classifyFile;
    private checkIoCs;
    private checkPatterns;
    /** NEW: hbg-scan compatible signature matching (hash + pattern + domain) */
    private checkSignatures;
    /** NEW: Compaction Layer Persistence check (hbg-scan Check 5) */
    private checkCompactionPersistence;
    private checkHardcodedSecrets;
    private shannonEntropy;
    private checkStructure;
    private checkDependencies;
    private checkSkillManifest;
    private checkComplexity;
    private checkConfigImpact;
    private checkHiddenFiles;
    private checkJSDataFlow;
    private checkCrossFile;
    private calculateRisk;
    private getVerdict;
    private getFiles;
    printSummary(): void;
    toJSON(): JSONReport;
    toSARIF(scanDir: string): SARIFReport;
    toHTML(): string;
}
//# sourceMappingURL=scanner.d.ts.map