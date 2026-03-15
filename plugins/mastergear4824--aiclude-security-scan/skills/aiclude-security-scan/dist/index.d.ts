import { ReportFormat, ScanEngineId } from '@asvs/core';

/**
 * Skill Handler
 * Processes /security-scan skill invocations from Claude Code
 * 로컬 경로 스캔 + 이름 기반 API 검색 모두 지원
 */

interface SkillInvocation {
    targetPath: string;
    type?: "mcp-server" | "skill";
    profile?: "strict" | "standard" | "permissive";
    format?: ReportFormat;
    engines?: ScanEngineId[];
}
/** API 기반 조회 요청 */
interface SkillLookupInvocation {
    name: string;
    type?: "mcp-server" | "skill";
    description?: string;
    repositoryUrl?: string;
    npmPackage?: string;
}
declare class SkillHandler {
    private scanner;
    private reporter;
    private apiBase;
    constructor();
    /** API 호출에 사용할 인증 헤더 생성 */
    private createAuthHeaders;
    /**
     * API 기반 보안 스캔 조회/요청
     * 기존 스캔 결과를 검색하고, 없으면 등록 후 스캔을 요청
     */
    lookup(invocation: SkillLookupInvocation): Promise<string>;
    /** Handle a /security-scan invocation (로컬 경로 스캔) */
    handle(invocation: SkillInvocation): Promise<string>;
    /** Auto-detect whether target is an MCP server or skill */
    private detectTargetType;
    /** Format the report output with detailed findings */
    private formatOutput;
    /** API에서 받은 상세 리포트를 마크다운으로 포맷 */
    private formatApiReport;
    /** 스캔 요약만 포맷 */
    private formatScanSummary;
}

export { SkillHandler, type SkillInvocation, type SkillLookupInvocation };
