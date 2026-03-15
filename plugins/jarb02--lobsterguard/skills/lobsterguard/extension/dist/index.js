"use strict";
// ─────────────────────────────────────────────────────────────────────────────
// LobsterGuard Shield v4.0.0
// Real-time security monitoring and protection plugin for OpenClaw
//
// Phase 1: Tool registration + CLI commands
// Phase 2: Action interceptor — blocks dangerous commands in real-time
// Phase 3: Continuous file & agent monitoring with anomaly detection
// ─────────────────────────────────────────────────────────────────────────────
Object.defineProperty(exports, "__esModule", { value: true });
const child_process_1 = require("child_process");
const fs_1 = require("fs");
const path_1 = require("path");
const interceptor_1 = require("./interceptor");
const watcher_1 = require("./watcher");
const fix_tool_1 = require("./fix_tool");
// ─── Default paths ───────────────────────────────────────────────────────────
const OPENCLAW_HOME = process.env.HOME
    ? (0, path_1.join)(process.env.HOME, ".openclaw")
    : "/root/.openclaw";
const LOBSTERGUARD_DIR = (0, path_1.join)(OPENCLAW_HOME, "skills", "lobsterguard");
const SCRIPTS_DIR = (0, path_1.join)(LOBSTERGUARD_DIR, "scripts");
const DATA_DIR = (0, path_1.join)(LOBSTERGUARD_DIR, "data");
const CHECK_SCRIPT = (0, path_1.join)(SCRIPTS_DIR, "check.py");
const FIX_SCRIPT = (0, path_1.join)(SCRIPTS_DIR, "fix_engine.py");
const CLEANUP_SCRIPT = (0, path_1.join)(SCRIPTS_DIR, "cleanup.py");

        // Auto-cleanup: runs cleanup.py after a delay to kill orphan processes
        function scheduleCleanup(delaySec) {
            setTimeout(() => {
                try {
                    (0, child_process_1.execSync)(`python3 -u -W ignore "${CLEANUP_SCRIPT}" --silent 2>/dev/null`, { encoding: "utf-8", timeout: 15000 });
                } catch (e) { /* silent */ }
            }, (delaySec || 5) * 1000);
        }
const REPORT_TEXT = (0, path_1.join)(DATA_DIR, "latest-report.txt");
const REPORT_JSON = (0, path_1.join)(DATA_DIR, "latest-report.json");
const SHIELD_STATE_FILE = (0, path_1.join)(DATA_DIR, "shield-state.json");
const MONITOR_SCRIPT = (0, path_1.join)(SCRIPTS_DIR, "monitor.sh");
// ─── Default config ──────────────────────────────────────────────────────────
const DEFAULT_CONFIG = {
    shield_level: "standard",
    auto_block: false,
    alert_channel: "",
    check_script_path: CHECK_SCRIPT,
    report_cache_path: REPORT_TEXT,
};
// ─── Helper functions ────────────────────────────────────────────────────────
function loadShieldState() {
    try {
        if ((0, fs_1.existsSync)(SHIELD_STATE_FILE)) {
            const raw = (0, fs_1.readFileSync)(SHIELD_STATE_FILE, "utf-8");
            return JSON.parse(raw);
        }
    }
    catch {
        // Corrupted state file — start fresh
    }
    return {
        last_scan_time: "",
        last_score: -1,
        scan_count: 0,
        alerts_sent: 0,
        shield_active: true,
        blocked_actions: [],
    };
}
function saveShieldState(state) {
    try {
        (0, fs_1.writeFileSync)(SHIELD_STATE_FILE, JSON.stringify(state, null, 2), "utf-8");
    }
    catch {
        // Non-critical — state will rebuild on next scan
    }
}
function isCacheRecent(maxAgeHours = 12) {
    try {
        if (!(0, fs_1.existsSync)(REPORT_JSON))
            return false;
        const stats = (0, fs_1.statSync)(REPORT_JSON);
        const ageMs = Date.now() - stats.mtimeMs;
        const ageHours = ageMs / (1000 * 60 * 60);
        return ageHours < maxAgeHours;
    }
    catch {
        return false;
    }
}
function runScan(format = "text", lang = "es") {
    const flag = (format === "json" ? " --json" : format === "compact" ? " --compact" : "") + (lang ? ` --lang ${lang}` : "");
    try {
        const output = (0, child_process_1.execSync)(`python3 "${CHECK_SCRIPT}"${flag}`, {
            encoding: "utf-8",
            timeout: 120000, // 2 minutes max
            maxBuffer: 1024 * 1024, // 1MB
        });
        return output;
    }
    catch (err) {
        const error = err;
        return `Error running scan: ${error.stderr || error.message || "Unknown error"}`;
    }
}
function getCachedReport(format = "text") {
    const file = format === "json" ? REPORT_JSON : REPORT_TEXT;
    try {
        if ((0, fs_1.existsSync)(file)) {
            return (0, fs_1.readFileSync)(file, "utf-8");
        }
    }
    catch {
        // Fall through
    }
    return null;
}
function getScoreEmoji(score) {
    if (score >= 80)
        return "🟢";
    if (score >= 60)
        return "🟡";
    if (score >= 40)
        return "🟠";
    return "🔴";
}
function getTimeAgo(date) {
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 60)
        return "just now";
    if (seconds < 3600)
        return `${Math.floor(seconds / 60)} min ago`;
    if (seconds < 86400)
        return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)} days ago`;
}
// ─── Plugin Definition ───────────────────────────────────────────────────────
const lobsterguardPlugin = {
    id: "lobsterguard-shield",
    name: "LobsterGuard Shield",
    description: "Real-time security monitoring, action interception, file watching, and agent " +
        "behavior analysis for OpenClaw. 70 checks across 6 categories, OWASP Agentic AI " +
        "Top 10 coverage. Blocks dangerous commands, monitors file changes, detects anomalies.",
    kind: "security",
    version: "3.0.0",
    configSchema: {
        shield_level: {
            type: "select",
            description: "Security level: relaxed (block only critical), standard (recommended), paranoid (block everything suspicious)",
            default: "standard",
            options: ["relaxed", "standard", "paranoid"],
        },
        auto_block: {
            type: "boolean",
            description: "Automatically block critical security threats without asking",
            default: false,
        },
        alert_channel: {
            type: "string",
            description: "Preferred alert channel (telegram, whatsapp, discord, etc). Empty = auto-detect",
            default: "",
        },
    },
    // ─── Registration ────────────────────────────────────────────────────────
    register(api) {
        const config = { ...DEFAULT_CONFIG };
        api.logger.info("LobsterGuard Shield v4.0.0 — initializing...");
        // ═══════════════════════════════════════════════════════════════════════
        // PHASE 2: Initialize Action Interceptor
        // ═══════════════════════════════════════════════════════════════════════
        const interceptor = new interceptor_1.ActionInterceptor(DATA_DIR, { shield_level: config.shield_level }, (level, msg) => (api.logger[level] || api.logger.info)(msg));
        api.logger.info(`Interceptor active: ${interceptor_1.BUILTIN_PATTERN_COUNT} threat patterns loaded`);
        // ═══════════════════════════════════════════════════════════════════════
        // PHASE 3: Initialize File & Agent Watcher
        // ═══════════════════════════════════════════════════════════════════════
        const watcher = new watcher_1.FileWatcher(OPENCLAW_HOME, DATA_DIR, {
            monitor_script_path: MONITOR_SCRIPT,
            auto_trigger_monitor: true,
        }, (level, msg) => (api.logger[level] || api.logger.info)(msg));
        // Auto-start the watcher
        try {
            watcher.start();
            api.logger.info("File watcher started — monitoring config, skills, plugins, system files");
        }
        catch (err) {
            const error = err;
            api.logger.warn(`File watcher could not start: ${error.message}`);
        }
        // ═══════════════════════════════════════════════════════════════════════
        // ACTION HOOK: Intercept tool calls before execution
        // This is the core Phase 2 feature. When the agent tries to execute
        // a shell command or tool call, this hook checks it against threat
        // patterns and blocks/warns as needed.
        // ═══════════════════════════════════════════════════════════════════════
        if (typeof api.registerActionHook === "function") {
            // OpenClaw supports action hooks — use the native API
            api.registerActionHook({
                name: "lobsterguard-shield",
                description: "LobsterGuard real-time threat detection — blocks dangerous commands",
                priority: 1, // High priority — run before other hooks
                intercept(action) {
                    // Extract the command string to analyze
                    let commandStr = "";
                    if (action.command) {
                        commandStr = action.command;
                    }
                    else if (action.args && typeof action.args.command === "string") {
                        commandStr = action.args.command;
                    }
                    else if (action.args && typeof action.args.input === "string") {
                        commandStr = action.args.input;
                    }
                    if (!commandStr) {
                        return { allowed: true };
                    }
                    const result = interceptor.intercept(commandStr, {
                        tool: action.tool,
                        source: action.type,
                    });
                    if (!result.allowed) {
                        return {
                            allowed: false,
                            reason: result.reason_es || result.reason_en || "Blocked by LobsterGuard Shield",
                        };
                    }
                    // If it's a warning (allowed but risky), log it
                    if (result.matched_pattern && result.risk_score > 0) {
                        api.logger.warn(`⚠️ ${result.reason_es || result.reason_en}`);
                    }
                    return { allowed: true };
                },
            });
            api.logger.info("Action hook registered — real-time protection active");
        }
        else {
            // OpenClaw doesn't support action hooks yet — use tool-based interception
            api.logger.info("Action hooks not available — using tool-based interception");
            // Register a guard tool that the agent should call before executing
            // dangerous operations
            api.registerTool({
                name: "security_check_command",
                description: "IMPORTANT: Before executing any shell command or system operation, " +
                    "check it through this security tool. It analyzes the command for " +
                    "potential threats like data exfiltration, destructive operations, " +
                    "or privilege escalation. Returns whether the command is safe to execute.",
                parameters: [
                    {
                        name: "command",
                        type: "string",
                        description: "The shell command or operation to verify before execution",
                        required: true,
                    },
                    {
                        name: "context",
                        type: "string",
                        description: "Why this command is being executed (helps reduce false positives)",
                        required: false,
                        default: "",
                    },
                ],
                async execute(args) {
                    const command = args.command;
                    const context = args.context || "";
                    if (!command) {
                        return { success: true, text: "✅ No command to check" };
                    }
                    const result = interceptor.intercept(command, { source: context });
                    if (!result.allowed) {
                        return {
                            success: false,
                            error: result.reason_es,
                            text: [
                                result.reason_es || "",
                                result.reason_en || "",
                                "",
                                `Patrón: ${result.matched_pattern?.id} — ${result.matched_pattern?.category}`,
                                `Severidad: ${result.matched_pattern?.severity}`,
                                `Riesgo: ${result.risk_score}/100`,
                                "",
                                "⛔ Este comando NO debe ejecutarse.",
                                "⛔ This command should NOT be executed.",
                            ].join("\n"),
                        };
                    }
                    if (result.matched_pattern) {
                        return {
                            success: true,
                            text: [
                                result.reason_es || "",
                                result.reason_en || "",
                                "",
                                `Riesgo: ${result.risk_score}/100`,
                                "",
                                "El comando puede ejecutarse con precaución.",
                                "The command may proceed with caution.",
                            ].join("\n"),
                        };
                    }
                    return {
                        success: true,
                        text: "✅ Comando seguro / Command is safe",
                    };
                },
            });
        }
        // ═══════════════════════════════════════════════════════════════════════
        // TOOL: security_scan (Phase 1 — unchanged)
        // ═══════════════════════════════════════════════════════════════════════
        api.registerTool({
            name: "security_scan",
            description: "Run a comprehensive security audit on this OpenClaw installation. " +
                "Returns a detailed report with 70 checks across 6 categories " +
                "(OpenClaw config, server hardening, advanced settings, agentic AI, " +
                "forensics, and advanced hardening). Use when the user asks about " +
                "security, safety, protection, or when suspicious activity is detected.",
            parameters: [
                {
                    name: "format",
                    type: "string",
                    description: 'Output format: "compact" (default, minimal — only failures + score, saves tokens), ' +
                        '"text" for full human-readable report, "json" for structured data',
                    required: false,
                    default: "compact",
                    enum: ["compact", "text", "json"],
                },
                {
                    name: "force_fresh",
                    type: "boolean",
                    description: "Force a fresh scan even if a recent cached report exists (default: false, uses cache if <12h old)",
                    required: false,
                    default: false,
                },
                {
                    name: "language",
                    type: "string",
                    description: 'Preferred language for the report: "es" (Spanish) or "en" (English)',
                    required: false,
                    default: "es",
                    enum: ["es", "en"],
                },
            ],
            async execute(args) {
                const format = args.format || "compact";
                const lang = args.language || "es";
                const forceFresh = args.force_fresh || false;
                const state = loadShieldState();
                api.logger.info(`security_scan called (format=${format}, force=${forceFresh})`);
                // For compact format, always run fresh (it's fast and --compact saves cache internally)
                if (format === "compact") {
                    api.logger.info("Running compact scan (only failures + score)...");
                    const output = runScan("compact", lang);
                    state.last_scan_time = new Date().toISOString();
                    state.scan_count++;
                    const scoreMatch = output.match(/Score:\s*(\d+)\/100/);
                    if (scoreMatch) {
                        state.last_score = parseInt(scoreMatch[1], 10);
                    }
                    saveShieldState(state);
                    return { success: true, text: output };
                }
                // Try cached report first (saves resources) for text/json
                if (!forceFresh && isCacheRecent(12)) {
                    const cached = getCachedReport(format);
                    if (cached) {
                        api.logger.info("Returning cached report (< 12h old)");
                        state.last_scan_time = new Date().toISOString();
                        state.scan_count++;
                        saveShieldState(state);
                        if (format === "json") {
                            try {
                                const report = JSON.parse(cached);
                                state.last_score = report.score;
                                saveShieldState(state);
                                return {
                                    success: true,
                                    data: report,
                                    text: `Cached report — Score: ${report.score}/100 | ${report.failure_summary.total_passed}/${report.failure_summary.total_checks} checks passed`,
                                };
                            }
                            catch { /* fall through */ }
                        }
                        return { success: true, text: cached };
                    }
                }
                // Run fresh scan
                api.logger.info("Running fresh security scan...");
                const output = runScan(format, lang);
                // Save results to cache
                try {
                    const textOutput = format === "text" ? output : runScan("text", lang);
                    const jsonOutput = format === "json" ? output : runScan("json", lang);
                    (0, fs_1.writeFileSync)(REPORT_TEXT, textOutput, "utf-8");
                    (0, fs_1.writeFileSync)(REPORT_JSON, jsonOutput, "utf-8");
                }
                catch {
                    api.logger.warn("Could not save report cache");
                }
                state.last_scan_time = new Date().toISOString();
                state.scan_count++;
                if (format === "json") {
                    try {
                        const report = JSON.parse(output);
                        state.last_score = report.score;
                        saveShieldState(state);
                        return {
                            success: true,
                            data: report,
                            text: `Fresh scan — Score: ${report.score}/100 | ${report.failure_summary.total_passed}/${report.failure_summary.total_checks} checks passed`,
                        };
                    }
                    catch { /* fall through */ }
                }
                const scoreMatch = output.match(/Score:\s*(\d+)\/100/);
                if (scoreMatch) {
                    state.last_score = parseInt(scoreMatch[1], 10);
                }
                saveShieldState(state);
                return { success: true, text: output };
            },
        });
        // ═══════════════════════════════════════════════════════════════════════
        // TOOL: shield_activity (Phase 2 — NEW)
        // Shows recent intercepted/blocked actions
        // ═══════════════════════════════════════════════════════════════════════
        api.registerTool({
            name: "shield_activity",
            description: "Show recent LobsterGuard Shield activity: blocked commands, warnings, " +
                "and threat statistics. Use when the user asks about blocked actions, " +
                "security incidents, or shield activity.",
            parameters: [
                {
                    name: "limit",
                    type: "number",
                    description: "Number of recent actions to show (default: 10)",
                    required: false,
                    default: 10,
                },
            ],
            async execute(args) {
                const limit = args.limit || 10;
                const activity = interceptor.getRecentActivity(limit);
                const stats = interceptor.getStats();
                const summary = [
                    activity,
                    "",
                    "📊 Estadísticas / Statistics:",
                    `   Total interceptados: ${stats.total_intercepted}`,
                    `   Bloqueados: ${stats.total_blocked}`,
                    `   Advertidos: ${stats.total_warned}`,
                ];
                if (Object.keys(stats.by_category).length > 0) {
                    summary.push("", "   Por categoría / By category:");
                    for (const [cat, count] of Object.entries(stats.by_category)) {
                        summary.push(`     ${cat}: ${count}`);
                    }
                }
                return { success: true, text: summary.join("\n") };
            },
        });
        // ═══════════════════════════════════════════════════════════════════════
        // TOOL: watcher_report (Phase 3 — NEW)
        // Shows filesystem and agent behavior monitoring events
        // ═══════════════════════════════════════════════════════════════════════
        api.registerTool({
            name: "watcher_report",
            description: "Show LobsterGuard file and agent monitoring events. Reports filesystem " +
                "changes to OpenClaw config/skills/plugins, system file modifications, " +
                "and agent behavior anomalies. Use when the user asks about file changes, " +
                "system modifications, or monitoring events.",
            parameters: [
                {
                    name: "limit",
                    type: "number",
                    description: "Number of recent events to show (default: 20)",
                    required: false,
                    default: 20,
                },
            ],
            async execute(args) {
                const limit = args.limit || 20;
                const report = watcher.getReport(limit);
                const stats = watcher.getStats();
                const summary = [
                    report,
                    "",
                    `🔭 Watcher: ${stats.is_running ? "Activo" : "Inactivo"} | Paths: ${stats.watching_paths}`,
                    `   Solicitudes externas/min: ${stats.behavior.external_req_rate}`,
                    `   Lecturas sensibles/min: ${stats.behavior.sensitive_read_rate}`,
                ];
                return { success: true, text: summary.join("\n") };
            },
        });
        // ═══════════════════════════════════════════════════════════════════════
        // TOOL: security_fix (Auto-Fix — Phase 4)
        // Guided remediation for security issues
        // ═══════════════════════════════════════════════════════════════════════
        (0, fix_tool_1.registerFixTool)(api, SCRIPTS_DIR, (level, msg) => (api.logger[level] || api.logger.info)(msg));
        // ═══════════════════════════════════════════════════════════════════════
        // CLI: openclaw lobsterguard
        // Subcommands: scan, status, monitor, shield, threats, watch
        // ═══════════════════════════════════════════════════════════════════════
        api.registerCli({
            command: "lobsterguard",
            description: "LobsterGuard security management commands",
            subcommands: [
                // ── openclaw lobsterguard scan ──────────────────────────────────────
                {
                    name: "scan",
                    description: "Run a full security audit (70 checks across 6 categories)",
                    options: [
                        { flag: "--json", description: "Output in JSON format", type: "boolean", default: false },
                        { flag: "--force", description: "Force fresh scan (ignore cache)", type: "boolean", default: false },
                    ],
                    async execute(args) {
                        const useJson = args["--json"] || false;
                        const force = args["--force"] || false;
                        const format = useJson ? "json" : "text";
                        console.log("🛡️  LobsterGuard Shield — Running security scan...\n");
                        if (!force && isCacheRecent(12)) {
                            const cached = getCachedReport(format);
                            if (cached) {
                                console.log("(Using cached report — less than 12h old)\n");
                                console.log(cached);
                                return;
                            }
                        }
                        console.log("(Running fresh scan — this may take a moment...)\n");
                        const output = runScan(format, lang);
                        console.log(output);
                        try {
                            if (format === "text") {
                                (0, fs_1.writeFileSync)(REPORT_TEXT, output, "utf-8");
                                const jsonOut = runScan("json");
                                (0, fs_1.writeFileSync)(REPORT_JSON, jsonOut, "utf-8");
                            }
                            else {
                                (0, fs_1.writeFileSync)(REPORT_JSON, output, "utf-8");
                                const textOut = runScan("text");
                                (0, fs_1.writeFileSync)(REPORT_TEXT, textOut, "utf-8");
                            }
                        }
                        catch {
                            console.error("Warning: could not save report cache");
                        }
                        const state = loadShieldState();
                        state.last_scan_time = new Date().toISOString();
                        state.scan_count++;
                        const scoreMatch = output.match(/Score:\s*(\d+)\/100/);
                        if (scoreMatch)
                            state.last_score = parseInt(scoreMatch[1], 10);
                        saveShieldState(state);
                    },
                },
                // ── openclaw lobsterguard status ────────────────────────────────────
                {
                    name: "status",
                    description: "Show current security status, shield info, and last scan results",
                    options: [],
                    async execute() {
                        const state = loadShieldState();
                        const stats = interceptor.getStats();
                        const watcherStats = watcher.getStats();
                        console.log("🛡️  LobsterGuard Shield v3.0 — Status\n");
                        console.log("─".repeat(50));
                        // Score
                        if (state.last_score >= 0) {
                            const emoji = getScoreEmoji(state.last_score);
                            console.log(`  ${emoji} Score:        ${state.last_score}/100`);
                        }
                        else {
                            console.log("  ⚪ Score:        No scan yet");
                        }
                        // Scans
                        console.log(`  🔍 Scans:        ${state.scan_count} total`);
                        // Last scan
                        if (state.last_scan_time) {
                            const ago = getTimeAgo(new Date(state.last_scan_time));
                            console.log(`  🕐 Last scan:    ${ago}`);
                        }
                        else {
                            console.log("  🕐 Last scan:    Never");
                        }
                        // Shield status
                        console.log(`  🛡️  Shield:       Active (${config.shield_level} mode)`);
                        console.log(`  📐 Patterns:     ${interceptor.listPatterns().length} active`);
                        // Interception stats
                        if (stats.total_intercepted > 0) {
                            console.log(`  🚫 Blocked:      ${stats.total_blocked} commands`);
                            console.log(`  ⚠️  Warned:       ${stats.total_warned} commands`);
                        }
                        else {
                            console.log("  ✅ Threats:      None detected");
                        }
                        // Alerts
                        console.log(`  📲 Alerts:       ${state.alerts_sent} sent`);
                        console.log("─".repeat(50));
                        // Cache age
                        if ((0, fs_1.existsSync)(REPORT_JSON)) {
                            const st = (0, fs_1.statSync)(REPORT_JSON);
                            const ageHours = Math.round((Date.now() - st.mtimeMs) / (1000 * 60 * 60) * 10) / 10;
                            console.log(`  📄 Cache:        ${ageHours}h old`);
                        }
                        // Watcher
                        console.log(`  🔭 Watcher:      ${watcherStats.is_running ? "Active" : "Inactive"} (${watcherStats.watching_paths} paths)`);
                        if (watcherStats.total_events > 0) {
                            console.log(`  📋 Events:       ${watcherStats.total_events} (${watcherStats.critical_events} critical)`);
                        }
                        // Cron
                        try {
                            const crontab = (0, child_process_1.execSync)("crontab -l 2>/dev/null", { encoding: "utf-8" });
                            console.log(crontab.includes("lobsterguard") ? "  ⏰ Cron:         Active (every 6h)" : "  ⏰ Cron:         Not configured");
                        }
                        catch {
                            console.log("  ⏰ Cron:         Not configured");
                        }
                        console.log("\nCommands:");
                        console.log("  openclaw lobsterguard scan       — Full audit");
                        console.log("  openclaw lobsterguard shield     — Shield details");
                        console.log("  openclaw lobsterguard threats     — Recent threats");
                        console.log("  openclaw lobsterguard watch      — Watcher events");
                    },
                },
                // ── openclaw lobsterguard monitor ───────────────────────────────────
                {
                    name: "monitor",
                    description: "Control automatic monitoring (start/stop the 6h cron job)",
                    options: [
                        { flag: "--action", description: "Action: start or stop", type: "string", default: "start" },
                    ],
                    async execute(args) {
                        const action = args["--action"] || "start";
                        if (action === "start") {
                            console.log("🛡️  LobsterGuard — Starting automatic monitoring...\n");
                            try {
                                const crontab = (0, child_process_1.execSync)("crontab -l 2>/dev/null", { encoding: "utf-8" });
                                if (crontab.includes("lobsterguard")) {
                                    console.log("✅ Monitoring is already active!");
                                    return;
                                }
                            }
                            catch { /* no crontab */ }
                            const cronLine = `0 */6 * * * ${MONITOR_SCRIPT} >> /var/log/lobsterguard-monitor.log 2>&1`;
                            try {
                                const existing = (() => { try {
                                    return (0, child_process_1.execSync)("crontab -l 2>/dev/null", { encoding: "utf-8" });
                                }
                                catch {
                                    return "";
                                } })();
                                (0, child_process_1.execSync)(`echo '${existing}${cronLine}\n' | crontab -`, { encoding: "utf-8" });
                                console.log("✅ Monitoring enabled (scan every 6h + alerts)");
                            }
                            catch (err) {
                                const error = err;
                                console.error(`❌ Could not set up cron: ${error.message}`);
                            }
                        }
                        else if (action === "stop") {
                            try {
                                (0, child_process_1.execSync)("crontab -l 2>/dev/null | grep -v lobsterguard | crontab -", { encoding: "utf-8" });
                                console.log("✅ Monitoring disabled.");
                            }
                            catch (err) {
                                const error = err;
                                console.error(`❌ Could not remove cron: ${error.message}`);
                            }
                        }
                        else {
                            console.log(`❌ Unknown action: ${action}`);
                        }
                    },
                },
                // ── openclaw lobsterguard shield (Phase 2 — NEW) ───────────────────
                {
                    name: "shield",
                    description: "Show shield configuration and active threat patterns",
                    options: [
                        { flag: "--level", description: "Change shield level: relaxed, standard, paranoid", type: "string" },
                    ],
                    async execute(args) {
                        const newLevel = args["--level"];
                        if (newLevel && ["relaxed", "standard", "paranoid"].includes(newLevel)) {
                            interceptor.setShieldLevel(newLevel);
                            console.log(`🛡️  Shield level changed to: ${newLevel}\n`);
                        }
                        const patterns = interceptor.listPatterns();
                        const byCategory = {};
                        const bySeverity = {};
                        const byAction = {};
                        for (const p of patterns) {
                            byCategory[p.category] = (byCategory[p.category] || 0) + 1;
                            bySeverity[p.severity] = (bySeverity[p.severity] || 0) + 1;
                            byAction[p.action] = (byAction[p.action] || 0) + 1;
                        }
                        console.log("🛡️  LobsterGuard Shield — Configuration\n");
                        console.log("─".repeat(50));
                        console.log(`  Level:    ${config.shield_level}`);
                        console.log(`  Patterns: ${patterns.length} active (${interceptor_1.BUILTIN_PATTERN_COUNT} built-in)`);
                        console.log("");
                        console.log("  By severity:");
                        for (const sev of ["CRITICAL", "HIGH", "MEDIUM", "LOW"]) {
                            if (bySeverity[sev])
                                console.log(`    ${sev}: ${bySeverity[sev]}`);
                        }
                        console.log("");
                        console.log("  By category:");
                        for (const [cat, count] of Object.entries(byCategory).sort((a, b) => b[1] - a[1])) {
                            console.log(`    ${cat}: ${count}`);
                        }
                        console.log("");
                        console.log("  Actions:");
                        console.log(`    Block: ${byAction["block"] || 0} patterns`);
                        console.log(`    Warn:  ${byAction["warn"] || 0} patterns`);
                        console.log("─".repeat(50));
                        console.log("\nChange level: openclaw lobsterguard shield --level paranoid");
                    },
                },
                // ── openclaw lobsterguard threats (Phase 2 — NEW) ──────────────────
                {
                    name: "threats",
                    description: "Show recent blocked/warned actions and threat statistics",
                    options: [
                        { flag: "--limit", description: "Number of recent actions (default: 10)", type: "string", default: "10" },
                    ],
                    async execute(args) {
                        const limit = parseInt(args["--limit"] || "10", 10);
                        console.log(interceptor.getRecentActivity(limit));
                        const stats = interceptor.getStats();
                        if (stats.total_intercepted > 0) {
                            console.log("\n📊 Summary:");
                            console.log(`   Blocked: ${stats.total_blocked} | Warned: ${stats.total_warned}`);
                            if (Object.keys(stats.by_category).length > 0) {
                                console.log("   Top categories:");
                                const sorted = Object.entries(stats.by_category).sort((a, b) => b[1] - a[1]);
                                for (const [cat, count] of sorted.slice(0, 5)) {
                                    console.log(`     ${cat}: ${count}`);
                                }
                            }
                        }
                    },
                },
                // ── openclaw lobsterguard watch (Phase 3 — NEW) ────────────────────
                {
                    name: "watch",
                    description: "Show file watcher events and control real-time monitoring",
                    options: [
                        { flag: "--action", description: "Action: events, start, stop, clear", type: "string", default: "events" },
                        { flag: "--limit", description: "Number of events to show (default: 20)", type: "string", default: "20" },
                    ],
                    async execute(args) {
                        const action = args["--action"] || "events";
                        const limit = parseInt(args["--limit"] || "20", 10);
                        switch (action) {
                            case "events":
                                console.log(watcher.getReport(limit));
                                break;
                            case "start":
                                if (watcher.isRunning()) {
                                    console.log("✅ Watcher is already running");
                                }
                                else {
                                    watcher.start();
                                    console.log("✅ Watcher started — monitoring files and agent behavior");
                                }
                                break;
                            case "stop":
                                watcher.stop();
                                console.log("✅ Watcher stopped");
                                break;
                            case "clear":
                                watcher.clearEvents();
                                console.log("✅ Watcher events cleared");
                                break;
                            default:
                                console.log(`❌ Unknown action: ${action}`);
                                console.log("   Use: events, start, stop, clear");
                        }
                    },
                },
            ],
        });

        // ═══════════════════════════════════════════════════════════════════════
        // SLASH COMMANDS (Telegram)
        // ═══════════════════════════════════════════════════════════════════════
        const SKILL_SCANNER = path_1.join(LOBSTERGUARD_DIR, "scripts", "skill_scanner.py");
        const SETUP_SCRIPT = path_1.join(LOBSTERGUARD_DIR, "scripts", "lgsetup.py");

        api.registerCommand({
            name: "scan",
            description: "Escaneo de seguridad completo",
            handler: async (ctx) => {
                try {
                    const scanResult = (0, child_process_1.execSync)(`python3 -W ignore "${CHECK_SCRIPT}" --compact`, { encoding: "utf-8", timeout: 300000 });
                    scheduleCleanup(3);
                    return { text: scanResult };
                } catch (err) {
                    return { text: "Error scan: " + (err.stdout || err.stderr || err.message || "unknown").substring(0, 500) };
                }
            },
        });

        api.registerCommand({
            name: "fixlist",
            description: "Lista de problemas detectados",
            handler: async (ctx) => {
                try {
                    return { text: (0, child_process_1.execSync)(`python3 -W ignore "${FIX_SCRIPT}" list --telegram`, { encoding: "utf-8", timeout: 60000 }) };
                } catch (err) {
                    return { text: "Error fixlist: " + (err.stdout || err.stderr || err.message || "unknown").substring(0, 500) };
                }
            },
        });

        const fixCmds = [
            { name: "fixfw", check: "firewall", desc: "Configurar firewall" },
            { name: "fixbackup", check: "backups", desc: "Configurar backups" },
            { name: "fixkernel", check: "kernel_hardening", desc: "Endurecer kernel" },
            { name: "fixcore", check: "core_dump_protection", desc: "Deshabilitar core dumps" },
            { name: "fixaudit", check: "auditd_logging", desc: "Configurar auditoria" },
            { name: "fixsandbox", check: "sandbox_mode", desc: "Configurar sandbox" },
            { name: "fixenv", check: "env_leakage", desc: "Proteger tokens" },
            { name: "fixtmp", check: "tmp_security", desc: "Proteger /tmp" },
            { name: "fixcode", check: "code_execution_sandbox", desc: "Verificar integridad" },
            { name: "fixsystemd", check: "systemd_hardening", desc: "Crear servicio systemd" },
            { name: "runuser", check: "openclaw_user", desc: "Migrar de root a usuario dedicado" },
        ];
        for (const fc of fixCmds) {
            api.registerCommand({
                name: fc.name,
                description: fc.desc,
                handler: async (ctx) => {
                    try {
                        const fixResult = (0, child_process_1.execSync)(`python3 -u -W ignore "${FIX_SCRIPT}" run ${fc.check} --telegram 2>&1`, { encoding: "utf-8", timeout: 120000 });
                        scheduleCleanup(3);
                        return { text: fixResult };
                    } catch (err) {
                        return { text: "Error " + fc.name + ": " + (err.stdout || err.stderr || err.message || "unknown").substring(0, 500) };
                    }
                },
            });
        }
        api.registerCommand({
            name: "checkskill",
            description: "Escanear seguridad de skills instaladas",
            handler: async (ctx) => {
                try {
                    const skillResult = (0, child_process_1.execSync)(`python3 -W ignore "${SKILL_SCANNER}" all --telegram 2>&1`, { encoding: "utf-8", timeout: 60000 });
                    scheduleCleanup(3);
                    return { text: skillResult };
                } catch (err) {
                    return { text: "Error checkskill: " + (err.stdout || err.stderr || err.message || "unknown").substring(0, 500) };
                }
            },
        });

        api.registerCommand({
            name: "lgsetup",
            description: "Verificar instalacion de LobsterGuard",
            handler: async (ctx) => {
                try {
                    return { text: (0, child_process_1.execSync)(`python3 -W ignore "${SETUP_SCRIPT}" --telegram 2>&1`, { encoding: "utf-8", timeout: 120000 }) };
                } catch (err) {
                    return { text: "Error lgsetup: " + (err.stdout || err.stderr || err.message || "unknown").substring(0, 500) };
                }
            },
        });

        api.registerCommand({
            name: "cleanup",
            description: "Eliminar procesos fantasma de OpenClaw",
            handler: async (ctx) => {
                try {
                    return { text: (0, child_process_1.execSync)(`python3 -u -W ignore "${CLEANUP_SCRIPT}" 2>&1`, { encoding: "utf-8", timeout: 30000 }) };
                } catch (err) {
                    return { text: "Error cleanup: " + (err.stdout || err.stderr || err.message || "unknown").substring(0, 500) };
                }
            },
        });

                api.logger.info(`LobsterGuard Shield v4.0.0 — registered: 4 tools + 23 slash commands + ${interceptor_1.BUILTIN_PATTERN_COUNT} threat patterns + file watcher + auto-fix`);
    },
};
// ─── Export ──────────────────────────────────────────────────────────────────
exports.default = lobsterguardPlugin;
//# sourceMappingURL=index.js.map