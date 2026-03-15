"use strict";
// ─────────────────────────────────────────────────────────────────────────────
// LobsterGuard Shield — Action Interceptor
// Phase 2: Real-time blocking of dangerous commands
//
// This module intercepts tool calls and shell commands before execution,
// matching them against a configurable set of threat patterns.
// ─────────────────────────────────────────────────────────────────────────────
Object.defineProperty(exports, "__esModule", { value: true });
exports.PATTERN_CATEGORIES = exports.BUILTIN_PATTERN_COUNT = exports.ActionInterceptor = void 0;
const fs_1 = require("fs");
const path_1 = require("path");
// ─── Built-in Threat Patterns ────────────────────────────────────────────────
const BUILTIN_PATTERNS = [
    // ──── DESTRUCTION ────
    {
        id: "DEST-001",
        pattern: "rm\\s+(-[a-zA-Z]*f[a-zA-Z]*\\s+)?(/$|\\$HOME|~/|/root|/etc|/var(?!/log/lobsterguard)|/usr)",
        description_es: "Eliminación destructiva de directorios del sistema",
        description_en: "Destructive deletion of system directories",
        severity: "CRITICAL",
        action: "block",
        category: "destruction",
        enabled: true,
    },
    {
        id: "DEST-002",
        pattern: "rm\\s+-[a-zA-Z]*r[a-zA-Z]*f|rm\\s+-[a-zA-Z]*f[a-zA-Z]*r",
        description_es: "Comando rm con flags recursivo y forzado",
        description_en: "rm command with recursive and force flags",
        severity: "HIGH",
        action: "warn",
        category: "destruction",
        enabled: true,
    },
    {
        id: "DEST-003",
        pattern: "mkfs\\.|dd\\s+if=.*of=/dev/[a-z]",
        description_es: "Formateo o sobreescritura de disco/partición",
        description_en: "Disk/partition formatting or overwrite",
        severity: "CRITICAL",
        action: "block",
        category: "destruction",
        enabled: true,
    },
    {
        id: "DEST-004",
        pattern: ":(){ :|:& };:|fork\\s*bomb",
        description_es: "Fork bomb — colapsa el sistema",
        description_en: "Fork bomb — crashes the system",
        severity: "CRITICAL",
        action: "block",
        category: "destruction",
        enabled: true,
    },
    {
        id: "DEST-005",
        pattern: "\\>\\s*/dev/sd[a-z]|\\>\\s*/dev/nvme",
        description_es: "Escritura directa a dispositivo de bloque",
        description_en: "Direct write to block device",
        severity: "CRITICAL",
        action: "block",
        category: "destruction",
        enabled: true,
    },
    // ──── EXFILTRATION ────
    {
        id: "EXFIL-001",
        pattern: "curl.*(-d|--data|--upload-file|--form|-F|-T).*\\.(env|key|pem|crt|secret|password|token|credentials)",
        description_es: "Envío de archivos sensibles a servidor externo",
        description_en: "Sending sensitive files to external server",
        severity: "CRITICAL",
        action: "block",
        category: "exfiltration",
        enabled: true,
    },
    {
        id: "EXFIL-002",
        pattern: "cat.*\\.(env|key|pem|secret|password|token).*\\|\\s*(curl|wget|nc|ncat)",
        description_es: "Lectura de secretos con pipe a red",
        description_en: "Reading secrets piped to network tool",
        severity: "CRITICAL",
        action: "block",
        category: "exfiltration",
        enabled: true,
    },
    {
        id: "EXFIL-003",
        pattern: "(curl|wget|nc)\\s+.*(webhook\\.site|requestbin|hookbin|pipedream|ngrok|burp)",
        description_es: "Comunicación con servicios de exfiltración conocidos",
        description_en: "Communication with known exfiltration services",
        severity: "HIGH",
        action: "block",
        category: "exfiltration",
        enabled: true,
    },
    {
        id: "EXFIL-004",
        pattern: "tar\\s+.*\\|\\s*(curl|wget|nc|ssh)|zip.*\\|\\s*(curl|wget|nc)",
        description_es: "Compresión con envío directo a red",
        description_en: "Compression piped directly to network",
        severity: "HIGH",
        action: "warn",
        category: "exfiltration",
        enabled: true,
    },
    {
        id: "EXFIL-005",
        pattern: "scp\\s+.*\\.(env|key|pem|secret|config|json)\\s+[^@]*@",
        description_es: "SCP de archivos sensibles a host remoto",
        description_en: "SCP of sensitive files to remote host",
        severity: "HIGH",
        action: "warn",
        category: "exfiltration",
        enabled: true,
    },
    // ──── CONFIG TAMPERING ────
    {
        id: "CONF-001",
        pattern: "(sed|echo|cat|tee|>).*\\.openclaw/(config|gateway|agents)",
        description_es: "Modificación directa de configuración de OpenClaw",
        description_en: "Direct modification of OpenClaw configuration",
        severity: "HIGH",
        action: "warn",
        category: "config_tampering",
        enabled: true,
    },
    {
        id: "CONF-002",
        pattern: "(mv|rm|cp).*\\.openclaw/skills/.*/SKILL\\.md",
        description_es: "Manipulación de archivos SKILL.md",
        description_en: "Manipulation of SKILL.md files",
        severity: "HIGH",
        action: "warn",
        category: "config_tampering",
        enabled: true,
    },
    {
        id: "CONF-003",
        pattern: "chmod\\s+777|chmod\\s+-R\\s+777",
        description_es: "Permisos excesivos (777)",
        description_en: "Excessive permissions (777)",
        severity: "MEDIUM",
        action: "warn",
        category: "config_tampering",
        enabled: true,
    },
    {
        id: "CONF-004",
        pattern: "(echo|cat|sed).*(/etc/ssh/sshd_config|/etc/sudoers)",
        description_es: "Modificación de SSH o sudoers",
        description_en: "Modification of SSH or sudoers config",
        severity: "HIGH",
        action: "warn",
        category: "config_tampering",
        enabled: true,
    },
    {
        id: "CONF-005",
        pattern: "ufw\\s+(disable|delete|reset)|iptables\\s+-F|iptables\\s+-X",
        description_es: "Desactivación o flush del firewall",
        description_en: "Firewall disable or flush",
        severity: "CRITICAL",
        action: "block",
        category: "config_tampering",
        enabled: true,
    },
    // ──── CREDENTIAL THEFT ────
    {
        id: "CRED-001",
        pattern: "(cat|head|tail|less|more|strings)\\s+.*(shadow|passwd|master\\.key|credentials|vault)",
        description_es: "Lectura de archivos de credenciales del sistema",
        description_en: "Reading system credential files",
        severity: "HIGH",
        action: "warn",
        category: "credential_theft",
        enabled: true,
    },
    {
        id: "CRED-002",
        pattern: "grep\\s+(-r|--recursive).*(-i|--ignore-case)?\\s*.*(password|secret|api.?key|token|bearer)",
        description_es: "Búsqueda recursiva de credenciales",
        description_en: "Recursive search for credentials",
        severity: "MEDIUM",
        action: "warn",
        category: "credential_theft",
        enabled: true,
    },
    {
        id: "CRED-003",
        pattern: "find\\s+.*-name\\s+['\"]?\\*\\.(env|key|pem|p12|pfx|jks)",
        description_es: "Búsqueda de archivos de claves/certificados",
        description_en: "Searching for key/certificate files",
        severity: "MEDIUM",
        action: "warn",
        category: "credential_theft",
        enabled: true,
    },
    {
        id: "CRED-004",
        pattern: "printenv|env\\s*$|set\\s*$|export\\s+-p",
        description_es: "Dump de variables de entorno (pueden contener secrets)",
        description_en: "Environment variable dump (may contain secrets)",
        severity: "MEDIUM",
        action: "warn",
        category: "credential_theft",
        enabled: true,
    },
    // ──── PRIVILEGE ESCALATION ────
    {
        id: "PRIV-001",
        pattern: "chmod\\s+[u+]*s|chmod\\s+[0-7]*[4-7][0-7]{2}",
        description_es: "Establecer bit SUID/SGID en ejecutable",
        description_en: "Setting SUID/SGID bit on executable",
        severity: "HIGH",
        action: "warn",
        category: "privilege_escalation",
        enabled: true,
    },
    {
        id: "PRIV-002",
        pattern: "echo.*NOPASSWD.*>>?\\s*/etc/sudoers|visudo",
        description_es: "Modificación de sudoers para acceso sin contraseña",
        description_en: "Modifying sudoers for passwordless access",
        severity: "CRITICAL",
        action: "block",
        category: "privilege_escalation",
        enabled: true,
    },
    {
        id: "PRIV-003",
        pattern: "usermod\\s+.*-aG\\s+(sudo|root|wheel|admin)",
        description_es: "Agregar usuario a grupo privilegiado",
        description_en: "Adding user to privileged group",
        severity: "HIGH",
        action: "warn",
        category: "privilege_escalation",
        enabled: true,
    },
    // ──── MALWARE ────
    {
        id: "MAL-001",
        pattern: "curl\\s+.*\\|\\s*(bash|sh|python|perl|ruby)|wget\\s+.*-O-\\s*\\|\\s*(bash|sh)",
        description_es: "Descarga y ejecución directa de script remoto",
        description_en: "Download and direct execution of remote script",
        severity: "CRITICAL",
        action: "block",
        category: "malware",
        enabled: true,
    },
    {
        id: "MAL-002",
        pattern: "eval\\s*\\$\\(.*curl|eval\\s*\\$\\(.*wget|eval\\s+['\"`].*base64",
        description_es: "Eval de contenido remoto o codificado",
        description_en: "Eval of remote or encoded content",
        severity: "CRITICAL",
        action: "block",
        category: "malware",
        enabled: true,
    },
    {
        id: "MAL-003",
        pattern: "crontab.*curl|crontab.*wget|(echo|cat).*\\*.*\\*.*\\*.*\\|\\s*crontab",
        description_es: "Instalación de cron malicioso",
        description_en: "Malicious cron installation",
        severity: "HIGH",
        action: "warn",
        category: "malware",
        enabled: true,
    },
    {
        id: "MAL-004",
        pattern: "python3?\\s+-c\\s+['\"].*import\\s+(socket|subprocess|os).*connect",
        description_es: "Reverse shell via Python inline",
        description_en: "Python inline reverse shell",
        severity: "CRITICAL",
        action: "block",
        category: "malware",
        enabled: true,
    },
    {
        id: "MAL-005",
        pattern: "bash\\s+-i\\s+>\\s*/dev/tcp|nc\\s+-[a-zA-Z]*e\\s+/bin/(ba)?sh",
        description_es: "Reverse shell directo",
        description_en: "Direct reverse shell",
        severity: "CRITICAL",
        action: "block",
        category: "malware",
        enabled: true,
    },
    // ──── EVASION ────
    {
        id: "EVAS-001",
        pattern: "(mv|rm|cp).*\\.openclaw/(skills|plugins)/lobsterguard",
        description_es: "Intento de desactivar LobsterGuard",
        description_en: "Attempt to disable LobsterGuard",
        severity: "CRITICAL",
        action: "block",
        category: "evasion",
        enabled: true,
    },
    {
        id: "EVAS-002",
        pattern: "openclaw\\s+(plugins?\\s+)?(disable|remove|uninstall)\\s+lobsterguard",
        description_es: "Intento de desinstalar LobsterGuard via CLI",
        description_en: "Attempt to uninstall LobsterGuard via CLI",
        severity: "CRITICAL",
        action: "block",
        category: "evasion",
        enabled: true,
    },
    {
        id: "EVAS-003",
        pattern: "pkill.*lobsterguard|kill.*lobsterguard|killall.*lobsterguard",
        description_es: "Intento de matar proceso LobsterGuard",
        description_en: "Attempt to kill LobsterGuard process",
        severity: "HIGH",
        action: "block",
        category: "evasion",
        enabled: true,
    },
    {
        id: "EVAS-004",
        pattern: "history\\s+-c|unset\\s+HISTFILE|export\\s+HISTSIZE=0",
        description_es: "Limpieza de historial (ocultar evidencia)",
        description_en: "History cleanup (hiding evidence)",
        severity: "MEDIUM",
        action: "warn",
        category: "evasion",
        enabled: true,
    },
];
// ─── Interceptor Class ───────────────────────────────────────────────────────
class ActionInterceptor {
    constructor(dataDir, config = {}, logFn) {
        this.stateFile = (0, path_1.join)(dataDir, "shield-state.json");
        this.rulesFile = (0, path_1.join)(dataDir, "shield-rules.json");
        this.shieldLevel = config.shield_level || "standard";
        this.logFn = logFn || (() => { });
        // Ensure data directory exists
        if (!(0, fs_1.existsSync)(dataDir)) {
            (0, fs_1.mkdirSync)(dataDir, { recursive: true });
        }
        // Load patterns: builtin + custom + saved rules
        this.patterns = [...BUILTIN_PATTERNS];
        // Load custom rules from file if exists
        const savedRules = this.loadCustomRules();
        if (savedRules.length > 0) {
            this.patterns.push(...savedRules);
        }
        // Add any runtime custom patterns
        if (config.custom_patterns) {
            this.patterns.push(...config.custom_patterns);
        }
        // Compile whitelist
        this.whitelist = (config.whitelist || []).map((w) => new RegExp(w, "i"));
        // Apply shield level filtering
        this.applyShieldLevel();
        this.logFn("info", `Interceptor initialized: ${this.getActivePatternCount()} patterns active (level: ${this.shieldLevel})`);
    }
    /**
     * Main entry point: check if a command/action should be allowed.
     */
    intercept(command, context) {
        // Empty commands are always allowed
        if (!command || command.trim().length === 0) {
            return { allowed: true, risk_score: 0 };
        }
        // Check whitelist first
        for (const wl of this.whitelist) {
            if (wl.test(command)) {
                return { allowed: true, risk_score: 0 };
            }
        }
        // Check against all active patterns
        let highestSeverityMatch = null;
        let highestRiskScore = 0;
        for (const pattern of this.patterns) {
            if (!pattern.enabled)
                continue;
            try {
                const regex = new RegExp(pattern.pattern, "i");
                if (regex.test(command)) {
                    const riskScore = this.severityToScore(pattern.severity);
                    if (riskScore > highestRiskScore) {
                        highestRiskScore = riskScore;
                        highestSeverityMatch = pattern;
                    }
                }
            }
            catch {
                // Invalid regex in pattern — skip it
                this.logFn("warn", `Invalid regex in pattern ${pattern.id}: ${pattern.pattern}`);
            }
        }
        // No match — allowed
        if (!highestSeverityMatch) {
            return { allowed: true, risk_score: 0 };
        }
        // Match found — record it
        const blocked = highestSeverityMatch.action === "block";
        this.recordAction(command, highestSeverityMatch, blocked);
        this.logFn(blocked ? "error" : "warn", `${blocked ? "BLOCKED" : "WARNING"} [${highestSeverityMatch.id}] ${command.substring(0, 80)}...`);
        return {
            allowed: !blocked,
            matched_pattern: highestSeverityMatch,
            reason_es: blocked
                ? `🚫 BLOQUEADO: ${highestSeverityMatch.description_es}`
                : `⚠️ ADVERTENCIA: ${highestSeverityMatch.description_es}`,
            reason_en: blocked
                ? `🚫 BLOCKED: ${highestSeverityMatch.description_en}`
                : `⚠️ WARNING: ${highestSeverityMatch.description_en}`,
            risk_score: highestRiskScore,
        };
    }
    /**
     * Get a formatted summary of recent blocked/warned actions.
     */
    getRecentActivity(limit = 10) {
        const state = this.loadState();
        const recent = state.blocked_actions.slice(-limit);
        if (recent.length === 0) {
            return "No hay actividad reciente / No recent activity";
        }
        const lines = [
            "🛡️ LobsterGuard Shield — Actividad Reciente / Recent Activity",
            "─".repeat(55),
        ];
        for (const action of recent) {
            const emoji = action.action_taken === "blocked" ? "🚫" : "⚠️";
            const time = new Date(action.timestamp).toLocaleString();
            lines.push(`${emoji} [${action.severity}] ${time}`);
            lines.push(`   ${action.pattern}`);
            lines.push(`   Comando: ${action.command.substring(0, 60)}${action.command.length > 60 ? "..." : ""}`);
            lines.push("");
        }
        lines.push("─".repeat(55));
        lines.push(`Total: ${state.blocked_actions.length} acciones registradas`);
        return lines.join("\n");
    }
    /**
     * Get threat statistics.
     */
    getStats() {
        const state = this.loadState();
        const actions = state.blocked_actions;
        const stats = {
            total_intercepted: actions.length,
            total_blocked: actions.filter((a) => a.action_taken === "blocked").length,
            total_warned: actions.filter((a) => a.action_taken === "warned").length,
            by_category: {},
            by_severity: {},
        };
        for (const action of actions) {
            // Find matching pattern to get category
            const pattern = this.patterns.find((p) => p.id === action.pattern);
            if (pattern) {
                stats.by_category[pattern.category] = (stats.by_category[pattern.category] || 0) + 1;
            }
            stats.by_severity[action.severity] = (stats.by_severity[action.severity] || 0) + 1;
        }
        return stats;
    }
    /**
     * Add a custom rule at runtime.
     */
    addCustomRule(pattern) {
        this.patterns.push(pattern);
        this.saveCustomRule(pattern);
        this.logFn("info", `Custom rule added: ${pattern.id}`);
    }
    /**
     * List all active patterns.
     */
    listPatterns() {
        return this.patterns.filter((p) => p.enabled);
    }
    /**
     * Update shield level at runtime.
     */
    setShieldLevel(level) {
        this.shieldLevel = level;
        // Reset to builtin patterns + custom
        const customRules = this.loadCustomRules();
        this.patterns = [...BUILTIN_PATTERNS, ...customRules];
        this.applyShieldLevel();
        this.logFn("info", `Shield level changed to: ${level} (${this.getActivePatternCount()} patterns active)`);
    }
    // ─── Private Methods ───────────────────────────────────────────────────────
    applyShieldLevel() {
        switch (this.shieldLevel) {
            case "relaxed":
                // Only CRITICAL patterns with "block" action
                for (const p of this.patterns) {
                    if (p.severity !== "CRITICAL" || p.action !== "block") {
                        p.enabled = false;
                    }
                }
                break;
            case "standard":
                // CRITICAL + HIGH patterns, all actions
                for (const p of this.patterns) {
                    if (p.severity === "LOW") {
                        p.enabled = false;
                    }
                }
                break;
            case "paranoid":
                // Everything enabled, and all "warn" become "block" for CRITICAL/HIGH
                for (const p of this.patterns) {
                    p.enabled = true;
                    if ((p.severity === "CRITICAL" || p.severity === "HIGH") && p.action === "warn") {
                        p.action = "block";
                    }
                }
                break;
        }
    }
    severityToScore(severity) {
        switch (severity) {
            case "CRITICAL": return 95;
            case "HIGH": return 75;
            case "MEDIUM": return 50;
            case "LOW": return 25;
            default: return 10;
        }
    }
    getActivePatternCount() {
        return this.patterns.filter((p) => p.enabled).length;
    }
    loadState() {
        try {
            if ((0, fs_1.existsSync)(this.stateFile)) {
                return JSON.parse((0, fs_1.readFileSync)(this.stateFile, "utf-8"));
            }
        }
        catch { /* start fresh */ }
        return {
            last_scan_time: "",
            last_score: -1,
            scan_count: 0,
            alerts_sent: 0,
            shield_active: true,
            blocked_actions: [],
        };
    }
    saveState(state) {
        try {
            (0, fs_1.writeFileSync)(this.stateFile, JSON.stringify(state, null, 2), "utf-8");
        }
        catch { /* non-critical */ }
    }
    recordAction(command, pattern, blocked) {
        const state = this.loadState();
        state.blocked_actions.push({
            timestamp: new Date().toISOString(),
            pattern: pattern.id,
            command: command.substring(0, 200), // Truncate for storage
            severity: pattern.severity,
            action_taken: blocked ? "blocked" : "warned",
        });
        // Keep only last 500 actions to avoid unbounded growth
        if (state.blocked_actions.length > 500) {
            state.blocked_actions = state.blocked_actions.slice(-500);
        }
        this.saveState(state);
    }
    loadCustomRules() {
        try {
            if ((0, fs_1.existsSync)(this.rulesFile)) {
                const data = JSON.parse((0, fs_1.readFileSync)(this.rulesFile, "utf-8"));
                return Array.isArray(data) ? data : [];
            }
        }
        catch { /* no custom rules */ }
        return [];
    }
    saveCustomRule(pattern) {
        const rules = this.loadCustomRules();
        rules.push(pattern);
        try {
            (0, fs_1.writeFileSync)(this.rulesFile, JSON.stringify(rules, null, 2), "utf-8");
        }
        catch { /* non-critical */ }
    }
}
exports.ActionInterceptor = ActionInterceptor;
// ─── Exported pattern count for display ──────────────────────────────────────
exports.BUILTIN_PATTERN_COUNT = BUILTIN_PATTERNS.length;
exports.PATTERN_CATEGORIES = [
    "destruction",
    "exfiltration",
    "config_tampering",
    "credential_theft",
    "privilege_escalation",
    "malware",
    "evasion",
];
//# sourceMappingURL=interceptor.js.map