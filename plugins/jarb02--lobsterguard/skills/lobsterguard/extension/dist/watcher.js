"use strict";
// ─────────────────────────────────────────────────────────────────────────────
// LobsterGuard Shield — Continuous File & Agent Watcher
// Phase 3: Real-time monitoring of filesystem and agent behavior
//
// Monitors:
//   1. OpenClaw config/skills/plugins directories for changes
//   2. System security files (SSH, sudoers, etc.)
//   3. Agent behavior patterns (rapid external requests, etc.)
//   4. Triggers monitor.sh on-demand when suspicious activity detected
// ─────────────────────────────────────────────────────────────────────────────
Object.defineProperty(exports, "__esModule", { value: true });
exports.FileWatcher = void 0;
const fs_1 = require("fs");
const path_1 = require("path");
const child_process_1 = require("child_process");
const DEFAULT_WATCHER_CONFIG = {
    enabled: true,
    check_interval_ms: 30000, // 30 seconds
    max_external_requests_per_min: 10,
    max_sensitive_reads_per_min: 5,
    auto_trigger_monitor: true,
    monitor_script_path: "",
    max_event_history: 200,
};
function getWatchTargets(openclawHome) {
    return [
        // OpenClaw configuration
        {
            path: (0, path_1.join)(openclawHome, "config"),
            category: "config",
            severity_on_change: "HIGH",
            description_es: "Configuración de OpenClaw modificada",
            description_en: "OpenClaw configuration modified",
        },
        {
            path: (0, path_1.join)(openclawHome, "gateway"),
            category: "config",
            severity_on_change: "HIGH",
            description_es: "Configuración del gateway modificada",
            description_en: "Gateway configuration modified",
        },
        // Skills directory
        {
            path: (0, path_1.join)(openclawHome, "skills"),
            category: "skill",
            severity_on_change: "MEDIUM",
            description_es: "Skill instalada o modificada",
            description_en: "Skill installed or modified",
        },
        // Plugins directory
        {
            path: (0, path_1.join)(openclawHome, "plugins"),
            category: "plugin",
            severity_on_change: "MEDIUM",
            description_es: "Plugin instalado o modificado",
            description_en: "Plugin installed or modified",
        },
        // System security files
        {
            path: "/etc/ssh",
            category: "system",
            severity_on_change: "CRITICAL",
            description_es: "Configuración SSH modificada",
            description_en: "SSH configuration modified",
        },
        {
            path: "/etc/sudoers",
            category: "system",
            severity_on_change: "CRITICAL",
            description_es: "Archivo sudoers modificado",
            description_en: "Sudoers file modified",
        },
        {
            path: "/etc/crontab",
            category: "system",
            severity_on_change: "HIGH",
            description_es: "Crontab del sistema modificado",
            description_en: "System crontab modified",
        },
        {
            path: "/etc/passwd",
            category: "system",
            severity_on_change: "CRITICAL",
            description_es: "Archivo de usuarios del sistema modificado",
            description_en: "System users file modified",
        },
    ];
}
// ─── Watcher Class ───────────────────────────────────────────────────────────
class FileWatcher {
    constructor(openclawHome, dataDir, config = {}, logFn) {
        this.watchers = [];
        this.events = [];
        this.anomalyInterval = null;
        this.running = false;
        /** Snapshot of file mtimes for polling-based change detection */
        this.fileSnapshots = new Map();
        this.pollInterval = null;
        this.openclawHome = openclawHome;
        this.dataDir = dataDir;
        this.config = { ...DEFAULT_WATCHER_CONFIG, ...config };
        this.eventsFile = (0, path_1.join)(dataDir, "watcher-events.json");
        this.logFn = logFn || (() => { });
        this.behavior = {
            external_requests: [],
            sensitive_reads: [],
            install_events: [],
            rapid_actions: 0,
            window_start: Date.now(),
        };
        // Load previous events
        this.events = this.loadEvents();
    }
    // ─── Lifecycle ─────────────────────────────────────────────────────────────
    /**
     * Start watching all configured paths.
     */
    start() {
        if (this.running)
            return;
        this.running = true;
        const targets = getWatchTargets(this.openclawHome);
        let watchCount = 0;
        for (const target of targets) {
            if (!(0, fs_1.existsSync)(target.path))
                continue;
            try {
                // Use native fs.watch for directories
                const watcher = (0, fs_1.watch)(target.path, { recursive: false }, (eventType, filename) => {
                    if (!filename)
                        return;
                    const fullPath = (0, path_1.join)(target.path, filename);
                    this.handleFileEvent(eventType, fullPath, target);
                });
                this.watchers.push(watcher);
                watchCount++;
            }
            catch {
                // Some paths may not be watchable (permissions, etc.)
                this.logFn("warn", `Cannot watch: ${target.path}`);
            }
        }
        // Start polling for files that don't support fs.watch well
        this.startPolling(targets);
        // Start anomaly detection interval
        this.anomalyInterval = setInterval(() => {
            this.checkBehaviorAnomalies();
        }, this.config.check_interval_ms);
        this.logFn("info", `Watcher started: monitoring ${watchCount} paths + polling`);
    }
    /**
     * Stop all watchers and intervals.
     */
    stop() {
        this.running = false;
        for (const w of this.watchers) {
            try {
                w.close();
            }
            catch { /* ignore */ }
        }
        this.watchers = [];
        if (this.anomalyInterval) {
            clearInterval(this.anomalyInterval);
            this.anomalyInterval = null;
        }
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
        this.saveEvents();
        this.logFn("info", "Watcher stopped");
    }
    /**
     * Check if the watcher is running.
     */
    isRunning() {
        return this.running;
    }
    // ─── Event Handling ────────────────────────────────────────────────────────
    handleFileEvent(eventType, filePath, target) {
        const fileName = (0, path_1.basename)(filePath);
        // Ignore temp files and our own data
        if (fileName.startsWith(".") || fileName.endsWith(".swp") || fileName.endsWith(".tmp"))
            return;
        if (filePath.includes("lobsterguard/data"))
            return;
        // Determine event type
        let type = "file_change";
        if (eventType === "rename") {
            type = (0, fs_1.existsSync)(filePath) ? "new_file" : "file_deleted";
        }
        // Elevate severity for specific dangerous changes
        let severity = target.severity_on_change;
        let descEs = target.description_es;
        let descEn = target.description_en;
        // Special cases
        if (fileName === "SKILL.md" && type === "new_file") {
            descEs = `Nueva skill detectada: ${fileName}`;
            descEn = `New skill detected: ${fileName}`;
            severity = "HIGH";
        }
        else if (filePath.includes("lobsterguard") && type === "file_deleted") {
            descEs = "⚠️ Archivo de LobsterGuard eliminado";
            descEn = "⚠️ LobsterGuard file deleted";
            severity = "CRITICAL";
        }
        else if (fileName === "sshd_config") {
            severity = "CRITICAL";
            descEs = "Configuración SSH (sshd_config) modificada";
            descEn = "SSH configuration (sshd_config) modified";
        }
        else if (fileName === "authorized_keys") {
            severity = "CRITICAL";
            descEs = "Claves SSH autorizadas modificadas";
            descEn = "SSH authorized keys modified";
        }
        const event = {
            timestamp: new Date().toISOString(),
            type,
            path: filePath,
            category: target.category,
            severity,
            description_es: `${descEs} — ${filePath}`,
            description_en: `${descEn} — ${filePath}`,
            alerted: false,
        };
        this.addEvent(event);
        // Auto-trigger monitor.sh for critical events
        if (severity === "CRITICAL" && this.config.auto_trigger_monitor) {
            this.triggerMonitor(event);
        }
    }
    // ─── Polling-based Detection ───────────────────────────────────────────────
    startPolling(targets) {
        // Take initial snapshot
        this.takeSnapshot(targets);
        this.pollInterval = setInterval(() => {
            this.pollForChanges(targets);
        }, this.config.check_interval_ms);
    }
    takeSnapshot(targets) {
        for (const target of targets) {
            if (!(0, fs_1.existsSync)(target.path))
                continue;
            try {
                const stat = (0, fs_1.statSync)(target.path);
                if (stat.isFile()) {
                    this.fileSnapshots.set(target.path, stat.mtimeMs);
                }
                else if (stat.isDirectory()) {
                    // Snapshot directory contents
                    const files = (0, fs_1.readdirSync)(target.path);
                    for (const f of files) {
                        const fp = (0, path_1.join)(target.path, f);
                        try {
                            const fStat = (0, fs_1.statSync)(fp);
                            this.fileSnapshots.set(fp, fStat.mtimeMs);
                        }
                        catch { /* skip */ }
                    }
                }
            }
            catch { /* skip */ }
        }
    }
    pollForChanges(targets) {
        for (const target of targets) {
            if (!(0, fs_1.existsSync)(target.path))
                continue;
            try {
                const stat = (0, fs_1.statSync)(target.path);
                if (stat.isFile()) {
                    const prev = this.fileSnapshots.get(target.path);
                    if (prev && stat.mtimeMs > prev) {
                        this.handleFileEvent("change", target.path, target);
                    }
                    this.fileSnapshots.set(target.path, stat.mtimeMs);
                }
                else if (stat.isDirectory()) {
                    const files = (0, fs_1.readdirSync)(target.path);
                    for (const f of files) {
                        const fp = (0, path_1.join)(target.path, f);
                        try {
                            const fStat = (0, fs_1.statSync)(fp);
                            const prev = this.fileSnapshots.get(fp);
                            if (!prev) {
                                // New file
                                this.handleFileEvent("rename", fp, target);
                            }
                            else if (fStat.mtimeMs > prev) {
                                // Modified file
                                this.handleFileEvent("change", fp, target);
                            }
                            this.fileSnapshots.set(fp, fStat.mtimeMs);
                        }
                        catch { /* skip */ }
                    }
                    // Check for deleted files
                    for (const [path] of this.fileSnapshots) {
                        if (path.startsWith(target.path) && !(0, fs_1.existsSync)(path)) {
                            this.handleFileEvent("rename", path, target);
                            this.fileSnapshots.delete(path);
                        }
                    }
                }
            }
            catch { /* skip */ }
        }
    }
    // ─── Behavior Tracking (called from interceptor/tools) ────────────────────
    /**
     * Track an external network request made by the agent.
     */
    trackExternalRequest(url) {
        this.behavior.external_requests.push(Date.now());
        this.cleanOldTimestamps();
    }
    /**
     * Track a sensitive file read by the agent.
     */
    trackSensitiveRead(path) {
        this.behavior.sensitive_reads.push(Date.now());
        this.cleanOldTimestamps();
    }
    /**
     * Track a skill/plugin install event.
     */
    trackInstallEvent(name) {
        this.behavior.install_events.push(Date.now());
        const event = {
            timestamp: new Date().toISOString(),
            type: "new_file",
            path: name,
            category: "agent_behavior",
            severity: "MEDIUM",
            description_es: `Skill/plugin instalado: ${name}`,
            description_en: `Skill/plugin installed: ${name}`,
            alerted: false,
        };
        this.addEvent(event);
    }
    // ─── Anomaly Detection ─────────────────────────────────────────────────────
    checkBehaviorAnomalies() {
        this.cleanOldTimestamps();
        const now = Date.now();
        const oneMinAgo = now - 60000;
        // Check external request rate
        const recentExternal = this.behavior.external_requests.filter((t) => t > oneMinAgo).length;
        if (recentExternal > this.config.max_external_requests_per_min) {
            const event = {
                timestamp: new Date().toISOString(),
                type: "behavior_anomaly",
                path: `${recentExternal} requests/min`,
                category: "agent_behavior",
                severity: "HIGH",
                description_es: `Anomalía: ${recentExternal} solicitudes externas en el último minuto (límite: ${this.config.max_external_requests_per_min})`,
                description_en: `Anomaly: ${recentExternal} external requests in last minute (limit: ${this.config.max_external_requests_per_min})`,
                alerted: false,
            };
            this.addEvent(event);
            if (this.config.auto_trigger_monitor) {
                this.triggerMonitor(event);
            }
        }
        // Check sensitive file access rate
        const recentSensitive = this.behavior.sensitive_reads.filter((t) => t > oneMinAgo).length;
        if (recentSensitive > this.config.max_sensitive_reads_per_min) {
            const event = {
                timestamp: new Date().toISOString(),
                type: "behavior_anomaly",
                path: `${recentSensitive} sensitive reads/min`,
                category: "agent_behavior",
                severity: "HIGH",
                description_es: `Anomalía: ${recentSensitive} lecturas de archivos sensibles en el último minuto`,
                description_en: `Anomaly: ${recentSensitive} sensitive file reads in last minute`,
                alerted: false,
            };
            this.addEvent(event);
        }
        // Check for rapid installs (3+ in 5 minutes = suspicious)
        const fiveMinAgo = now - 300000;
        const recentInstalls = this.behavior.install_events.filter((t) => t > fiveMinAgo).length;
        if (recentInstalls >= 3) {
            const event = {
                timestamp: new Date().toISOString(),
                type: "behavior_anomaly",
                path: `${recentInstalls} installs in 5min`,
                category: "agent_behavior",
                severity: "HIGH",
                description_es: `Anomalía: ${recentInstalls} instalaciones en 5 minutos — posible ataque de supply chain`,
                description_en: `Anomaly: ${recentInstalls} installs in 5 minutes — possible supply chain attack`,
                alerted: false,
            };
            this.addEvent(event);
            if (this.config.auto_trigger_monitor) {
                this.triggerMonitor(event);
            }
        }
    }
    cleanOldTimestamps() {
        const fiveMinAgo = Date.now() - 300000;
        this.behavior.external_requests = this.behavior.external_requests.filter((t) => t > fiveMinAgo);
        this.behavior.sensitive_reads = this.behavior.sensitive_reads.filter((t) => t > fiveMinAgo);
        this.behavior.install_events = this.behavior.install_events.filter((t) => t > fiveMinAgo);
    }
    // ─── Monitor Integration ───────────────────────────────────────────────────
    triggerMonitor(event) {
        if (!this.config.monitor_script_path || !(0, fs_1.existsSync)(this.config.monitor_script_path)) {
            this.logFn("warn", "Monitor script not found — cannot trigger alert");
            return;
        }
        try {
            this.logFn("warn", `Triggering monitor due to: ${event.description_en}`);
            (0, child_process_1.execSync)(`bash "${this.config.monitor_script_path}" 2>&1`, {
                encoding: "utf-8",
                timeout: 60000,
            });
            event.alerted = true;
            this.saveEvents();
        }
        catch (err) {
            const error = err;
            this.logFn("error", `Monitor trigger failed: ${error.message}`);
        }
    }
    // ─── Event Management ──────────────────────────────────────────────────────
    addEvent(event) {
        // Deduplicate: skip if same path+type within last 60 seconds
        const recentDuplicate = this.events.find((e) => e.path === event.path &&
            e.type === event.type &&
            new Date(event.timestamp).getTime() - new Date(e.timestamp).getTime() < 60000);
        if (recentDuplicate)
            return;
        this.events.push(event);
        // Trim to max
        if (this.events.length > this.config.max_event_history) {
            this.events = this.events.slice(-this.config.max_event_history);
        }
        this.saveEvents();
        this.logFn(event.severity === "CRITICAL" || event.severity === "HIGH" ? "warn" : "info", `[${event.severity}] ${event.description_en}`);
    }
    // ─── Reporting ─────────────────────────────────────────────────────────────
    /**
     * Get formatted report of recent events.
     */
    getReport(limit = 20) {
        const recent = this.events.slice(-limit);
        if (recent.length === 0) {
            return "🛡️ LobsterGuard Watcher — Sin eventos / No events\n\nEl sistema está tranquilo. / System is quiet.";
        }
        const lines = [
            "🛡️ LobsterGuard Watcher — Eventos Recientes / Recent Events",
            "─".repeat(60),
        ];
        for (const event of recent.reverse()) {
            const emoji = this.severityEmoji(event.severity);
            const time = new Date(event.timestamp).toLocaleString();
            const alertTag = event.alerted ? " [📲 alertado]" : "";
            lines.push(`${emoji} [${event.severity}] ${time}${alertTag}`);
            lines.push(`   ${event.description_es}`);
            lines.push(`   Tipo: ${event.type} | Categoría: ${event.category}`);
            lines.push("");
        }
        lines.push("─".repeat(60));
        // Summary
        const bySeverity = {};
        const byCategory = {};
        for (const e of this.events) {
            bySeverity[e.severity] = (bySeverity[e.severity] || 0) + 1;
            byCategory[e.category] = (byCategory[e.category] || 0) + 1;
        }
        lines.push(`Total eventos: ${this.events.length}`);
        const sevParts = [];
        for (const s of ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]) {
            if (bySeverity[s])
                sevParts.push(`${s}: ${bySeverity[s]}`);
        }
        if (sevParts.length > 0)
            lines.push(`Por severidad: ${sevParts.join(" | ")}`);
        const catParts = [];
        for (const [cat, count] of Object.entries(byCategory)) {
            catParts.push(`${cat}: ${count}`);
        }
        if (catParts.length > 0)
            lines.push(`Por categoría: ${catParts.join(" | ")}`);
        return lines.join("\n");
    }
    /**
     * Get stats for status display.
     */
    getStats() {
        const oneMinAgo = Date.now() - 60000;
        return {
            total_events: this.events.length,
            critical_events: this.events.filter((e) => e.severity === "CRITICAL").length,
            alerts_triggered: this.events.filter((e) => e.alerted).length,
            watching_paths: this.watchers.length,
            is_running: this.running,
            behavior: {
                external_req_rate: this.behavior.external_requests.filter((t) => t > oneMinAgo).length,
                sensitive_read_rate: this.behavior.sensitive_reads.filter((t) => t > oneMinAgo).length,
            },
        };
    }
    /**
     * Clear all events.
     */
    clearEvents() {
        this.events = [];
        this.saveEvents();
    }
    // ─── Persistence ───────────────────────────────────────────────────────────
    loadEvents() {
        try {
            if ((0, fs_1.existsSync)(this.eventsFile)) {
                const data = JSON.parse((0, fs_1.readFileSync)(this.eventsFile, "utf-8"));
                return Array.isArray(data) ? data : [];
            }
        }
        catch { /* start fresh */ }
        return [];
    }
    saveEvents() {
        try {
            (0, fs_1.writeFileSync)(this.eventsFile, JSON.stringify(this.events, null, 2), "utf-8");
        }
        catch { /* non-critical */ }
    }
    // ─── Utility ───────────────────────────────────────────────────────────────
    severityEmoji(severity) {
        switch (severity) {
            case "CRITICAL": return "🔴";
            case "HIGH": return "🟠";
            case "MEDIUM": return "🟡";
            case "LOW": return "🟢";
            default: return "⚪";
        }
    }
}
exports.FileWatcher = FileWatcher;
//# sourceMappingURL=watcher.js.map