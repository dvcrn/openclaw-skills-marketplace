// src/skill-handler.ts
import {
  Scanner,
  SastEngine,
  ScaEngine,
  ToolAnalyzerEngine,
  MalwareDetectorEngine,
  PermissionCheckerEngine,
  DastEngine,
  BehaviorMonitorEngine,
  loadGlobalConfig,
  RiskLevel,
  validateScanPath
} from "@asvs/core";
import { ReportGenerator } from "@asvs/reporter";
import { existsSync } from "fs";
import { resolve } from "path";
import { createHmac } from "crypto";
var SkillHandler = class {
  scanner;
  reporter;
  apiBase;
  constructor() {
    this.scanner = new Scanner();
    this.reporter = new ReportGenerator();
    this.apiBase = process.env["ASVS_API_URL"] ?? "https://vs-api.aiclude.com";
    this.scanner.registerEngine(new SastEngine());
    this.scanner.registerEngine(new ScaEngine());
    this.scanner.registerEngine(new ToolAnalyzerEngine());
    this.scanner.registerEngine(new MalwareDetectorEngine());
    this.scanner.registerEngine(new PermissionCheckerEngine());
    this.scanner.registerEngine(new DastEngine());
    this.scanner.registerEngine(new BehaviorMonitorEngine());
  }
  /** API 호출에 사용할 인증 헤더 생성 */
  createAuthHeaders(name) {
    const secret = process.env["ASVS_SIGNING_SECRET"] ?? "asvs-default-signing-key-2026";
    const timestamp = String(Date.now());
    const payload = `skill:${name}:${timestamp}`;
    const signature = createHmac("sha256", secret).update(payload).digest("hex");
    return {
      "Content-Type": "application/json",
      "X-ASVS-Source": "skill",
      "X-ASVS-Timestamp": timestamp,
      "X-ASVS-Signature": signature
    };
  }
  /**
   * API 기반 보안 스캔 조회/요청
   * 기존 스캔 결과를 검색하고, 없으면 등록 후 스캔을 요청
   */
  async lookup(invocation) {
    const apiUrl = `${this.apiBase}/api/v1/scan/lookup`;
    const lookupRes = await fetch(apiUrl, {
      method: "POST",
      headers: this.createAuthHeaders(invocation.name),
      body: JSON.stringify({
        name: invocation.name,
        type: invocation.type ?? "mcp-server",
        description: invocation.description ?? "",
        repositoryUrl: invocation.repositoryUrl ?? "",
        npmPackage: invocation.npmPackage ?? "",
        source: "skill"
      })
    });
    const lookupData = await lookupRes.json();
    if (lookupData["status"] === "found") {
      const report = lookupData["report"];
      const scan = lookupData["scan"];
      const target = lookupData["target"];
      if (report) {
        return this.formatApiReport(report, target);
      }
      return this.formatScanSummary(target, scan);
    }
    if (lookupData["status"] === "scanning" || lookupData["status"] === "registered") {
      const jobId = lookupData["jobId"];
      const target = lookupData["target"];
      const maxWait = 12e4;
      const interval = 5e3;
      const startTime = Date.now();
      while (Date.now() - startTime < maxWait) {
        await new Promise((r) => setTimeout(r, interval));
        const statusRes = await fetch(`${this.apiBase}/api/v1/scan/status/${jobId}`, {
          headers: this.createAuthHeaders(invocation.name)
        });
        const statusData = await statusRes.json();
        if (statusData["status"] === "completed") {
          const report = statusData["report"];
          const scanResult = statusData["scan"];
          const completedTarget = statusData["target"];
          if (report) {
            return this.formatApiReport(report, completedTarget);
          }
          return this.formatScanSummary(completedTarget, scanResult);
        }
        if (statusData["status"] === "failed") {
          const job = statusData["job"];
          throw new Error(`\uC2A4\uCE94 \uC2E4\uD328: ${job?.["error"] ?? "\uC54C \uC218 \uC5C6\uB294 \uC624\uB958"}`);
        }
      }
      return [
        `# \uBCF4\uC548 \uC2A4\uCE94 \uC9C4\uD589 \uC911: ${invocation.name}`,
        "",
        `\uC2A4\uCE94\uC774 \uC544\uC9C1 \uC9C4\uD589 \uC911\uC785\uB2C8\uB2E4. \uC7A0\uC2DC \uD6C4 \uB2E4\uC2DC \uC2DC\uB3C4\uD558\uC138\uC694.`,
        `Job ID: ${jobId}`,
        `\uD0C0\uAC9F: ${target["canonicalName"] ?? invocation.name}`,
        "",
        `*\uC0C1\uC138 \uACB0\uACFC\uB294 https://vs.aiclude.com \uC5D0\uC11C \uD655\uC778\uD558\uC138\uC694*`
      ].join("\n");
    }
    return `API \uC751\uB2F5: ${JSON.stringify(lookupData, null, 2)}`;
  }
  /** Handle a /security-scan invocation (로컬 경로 스캔) */
  async handle(invocation) {
    const config = loadGlobalConfig();
    const scanConfig = {
      ...config.defaultScanConfig,
      ...invocation.profile && { sandboxProfile: invocation.profile },
      ...invocation.engines && { engines: invocation.engines }
    };
    if (!scanConfig.engines.includes("malware-detector")) {
      scanConfig.engines.push("malware-detector");
    }
    const targetPath = validateScanPath(invocation.targetPath);
    const targetType = invocation.type ?? this.detectTargetType(targetPath);
    const target = {
      type: targetType,
      name: targetPath.split("/").pop() ?? targetPath,
      path: targetPath
    };
    const scanResult = await this.scanner.scan(target, scanConfig);
    const format = invocation.format ?? "markdown";
    const report = this.reporter.generate(scanResult, format);
    return this.formatOutput(report, format, scanResult.engineResults.flatMap((r) => r.vulnerabilities));
  }
  /** Auto-detect whether target is an MCP server or skill */
  detectTargetType(targetPath) {
    if (existsSync(resolve(targetPath, "SKILL.md")) || targetPath.endsWith("SKILL.md") || targetPath.includes("/skill")) {
      return "skill";
    }
    return "mcp-server";
  }
  /** Format the report output with detailed findings */
  formatOutput(report, format, vulnerabilities) {
    if (format === "json") {
      return JSON.stringify(report, null, 2);
    }
    const lines = [];
    const { summary } = report.scanResult;
    const icon = summary.overallRiskLevel === RiskLevel.CRITICAL ? "[CRITICAL]" : summary.overallRiskLevel === RiskLevel.HIGH ? "[HIGH RISK]" : summary.overallRiskLevel === RiskLevel.MEDIUM ? "[MEDIUM RISK]" : summary.overallRiskLevel === RiskLevel.LOW ? "[LOW RISK]" : "[CLEAN]";
    lines.push(`# ${icon} Security Scan Report: ${report.title}`);
    lines.push("");
    lines.push(`| Metric | Value |`);
    lines.push(`|--------|-------|`);
    lines.push(`| Scan Date | ${report.generatedAt} |`);
    lines.push(`| Target | ${report.scanResult.target.path} |`);
    lines.push(`| Target Type | ${report.scanResult.target.type} |`);
    lines.push(`| Overall Risk | **${summary.overallRiskLevel}** |`);
    lines.push(`| Risk Score | **${summary.overallScore}/100** |`);
    lines.push(`| Total Findings | ${summary.totalVulnerabilities} |`);
    lines.push(`| Scan Duration | ${report.scanResult.duration}ms |`);
    lines.push("");
    lines.push("## Severity Breakdown");
    lines.push("");
    lines.push(`| Severity | Count |`);
    lines.push(`|----------|-------|`);
    for (const [level, count] of Object.entries(summary.bySeverity)) {
      if (count > 0) {
        lines.push(`| **${level}** | ${count} |`);
      }
    }
    lines.push("");
    if (vulnerabilities.length > 0) {
      lines.push("## Detailed Findings");
      lines.push("");
      const sorted = [...vulnerabilities].sort((a, b) => {
        const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, INFO: 4 };
        return (order[a.severity] ?? 5) - (order[b.severity] ?? 5);
      });
      const top = sorted.slice(0, 20);
      for (let i = 0; i < top.length; i++) {
        const v = top[i];
        lines.push(`### ${i + 1}. [${v.severity}] ${v.title}`);
        lines.push("");
        lines.push(`- **ID**: ${v.id}`);
        lines.push(`- **Category**: ${v.category}`);
        lines.push(`- **Confidence**: ${Math.round(v.confidence * 100)}%`);
        if (v.location) {
          lines.push(`- **Location**: \`${v.location.file}:${v.location.line}\``);
        }
        lines.push(`- **Description**: ${v.description}`);
        lines.push(`- **Remediation**: ${v.remediation}`);
        if (v.cveIds?.length) {
          lines.push(`- **CVE**: ${v.cveIds.join(", ")}`);
        }
        if (v.location?.snippet) {
          lines.push("");
          lines.push("```");
          lines.push(v.location.snippet.substring(0, 300));
          lines.push("```");
        }
        lines.push("");
      }
      if (sorted.length > 20) {
        lines.push(`> ... and ${sorted.length - 20} more findings. Use \`--format json\` for the complete list.`);
        lines.push("");
      }
    }
    if (report.risks.length > 0) {
      lines.push("## Risk Assessment");
      lines.push("");
      for (const risk of report.risks) {
        lines.push(`### [${risk.level}] ${risk.area}`);
        lines.push(`- **Impact**: ${risk.impact}`);
        lines.push(`- **Likelihood**: ${risk.likelihood}`);
        lines.push(`- **Remediation**: ${risk.remediation}`);
        lines.push("");
      }
    }
    if (report.precautions.length > 0) {
      lines.push("## Precautions & Warnings");
      lines.push("");
      for (const precaution of report.precautions) {
        lines.push(`- ${precaution}`);
      }
      lines.push("");
    }
    return lines.join("\n");
  }
  // -----------------------------------------------------------------------
  // API 리포트 포맷팅 헬퍼
  // -----------------------------------------------------------------------
  /** API에서 받은 상세 리포트를 마크다운으로 포맷 */
  formatApiReport(report, target) {
    const lines = [];
    const scanResult = report["scanResult"];
    const summary = scanResult?.["summary"];
    const engineResults = scanResult?.["engineResults"] ?? [];
    const risks = report["risks"] ?? [];
    const precautions = report["precautions"] ?? [];
    const riskLevel = summary?.["overallRiskLevel"] ?? target["riskLevel"] ?? "UNKNOWN";
    const score = summary?.["overallScore"] ?? target["lastScore"] ?? 0;
    const totalVulns = summary?.["totalVulnerabilities"] ?? 0;
    const bySeverity = summary?.["bySeverity"] ?? {};
    const targetName = target["canonicalName"] ?? target["displayName"] ?? "Unknown";
    const targetType = target["type"] ?? "mcp-server";
    const icon = riskLevel === "CRITICAL" ? "[CRITICAL]" : riskLevel === "HIGH" ? "[HIGH RISK]" : riskLevel === "MEDIUM" ? "[MEDIUM RISK]" : riskLevel === "LOW" ? "[LOW RISK]" : "[CLEAN]";
    lines.push(`# ${icon} Security Scan Report: ${targetName}`);
    lines.push("");
    lines.push(`| Metric | Value |`);
    lines.push(`|--------|-------|`);
    lines.push(`| Target | ${targetName} |`);
    lines.push(`| Type | ${targetType} |`);
    lines.push(`| Overall Risk | **${riskLevel}** |`);
    lines.push(`| Risk Score | **${score}/100** |`);
    lines.push(`| Total Findings | ${totalVulns} |`);
    lines.push(`| Scan Date | ${report["generatedAt"] ?? "N/A"} |`);
    lines.push("");
    lines.push("## Severity Breakdown");
    lines.push("");
    lines.push("| Severity | Count |");
    lines.push("|----------|-------|");
    for (const level of ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]) {
      const count = bySeverity[level] ?? 0;
      if (count > 0) {
        lines.push(`| **${level}** | ${count} |`);
      }
    }
    lines.push("");
    const allVulns = engineResults.flatMap(
      (r) => r["vulnerabilities"] ?? []
    );
    if (allVulns.length > 0) {
      lines.push("## Detailed Findings");
      lines.push("");
      const sorted = [...allVulns].sort((a, b) => {
        const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, INFO: 4 };
        return (order[a["severity"]] ?? 5) - (order[b["severity"]] ?? 5);
      });
      const top = sorted.slice(0, 20);
      for (let i = 0; i < top.length; i++) {
        const v = top[i];
        lines.push(`### ${i + 1}. [${v["severity"]}] ${v["title"]}`);
        lines.push("");
        lines.push(`- **Category**: ${v["category"]}`);
        lines.push(`- **Confidence**: ${Math.round(v["confidence"] * 100)}%`);
        const loc = v["location"];
        if (loc) {
          lines.push(`- **Location**: \`${loc["file"]}:${loc["line"]}\``);
        }
        lines.push(`- **Description**: ${v["description"]}`);
        lines.push(`- **Remediation**: ${v["remediation"]}`);
        lines.push("");
      }
      if (sorted.length > 20) {
        lines.push(`> ... and ${sorted.length - 20} more findings.`);
        lines.push("");
      }
    }
    if (risks.length > 0) {
      lines.push("## Risk Assessment");
      lines.push("");
      for (const risk of risks) {
        lines.push(`### [${risk["level"]}] ${risk["area"]}`);
        lines.push(`- **Impact**: ${risk["impact"]}`);
        lines.push(`- **Remediation**: ${risk["remediation"]}`);
        lines.push("");
      }
    }
    if (precautions.length > 0) {
      lines.push("## Precautions & Warnings");
      lines.push("");
      for (const p of precautions) {
        lines.push(`- ${p}`);
      }
      lines.push("");
    }
    lines.push("---");
    lines.push(`*Report ID: ${report["id"] ?? "N/A"}*`);
    lines.push(`*Web Dashboard: https://vs.aiclude.com/targets*`);
    return lines.join("\n");
  }
  /** 스캔 요약만 포맷 */
  formatScanSummary(target, scan) {
    const lines = [];
    const targetName = target["canonicalName"] ?? target["displayName"] ?? "Unknown";
    const riskLevel = scan["riskLevel"] ?? target["riskLevel"] ?? "UNKNOWN";
    const score = scan["score"] ?? target["lastScore"] ?? 0;
    lines.push(`# Security Scan Summary: ${targetName}`);
    lines.push("");
    lines.push(`| Metric | Value |`);
    lines.push(`|--------|-------|`);
    lines.push(`| Risk Level | **${riskLevel}** |`);
    lines.push(`| Risk Score | **${score}/100** |`);
    lines.push(`| Total Vulnerabilities | ${scan["totalVulnerabilities"] ?? 0} |`);
    lines.push(`| CRITICAL | ${scan["criticalCount"] ?? 0} |`);
    lines.push(`| HIGH | ${scan["highCount"] ?? 0} |`);
    lines.push(`| MEDIUM | ${scan["mediumCount"] ?? 0} |`);
    lines.push(`| LOW | ${scan["lowCount"] ?? 0} |`);
    lines.push(`| INFO | ${scan["infoCount"] ?? 0} |`);
    lines.push(`| Scanned At | ${scan["scannedAt"] ?? "N/A"} |`);
    lines.push("");
    lines.push(`*\uC0C1\uC138 \uB9AC\uD3EC\uD2B8\uB294 https://vs.aiclude.com \uC5D0\uC11C \uD655\uC778\uD558\uC138\uC694*`);
    return lines.join("\n");
  }
};
export {
  SkillHandler
};
