"use strict";
// ─────────────────────────────────────────────────────────────────────────────
// LobsterGuard Auto-Fix Tool
// Guided remediation for security issues via the fix_engine.py backend
// ─────────────────────────────────────────────────────────────────────────────
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerFixTool = registerFixTool;
const child_process_1 = require("child_process");
const path_1 = require("path");
/**
 * Register the security_fix tool with the OpenClaw plugin API.
 *
 * @param api - The plugin API to register the tool with
 * @param scriptsDir - Path to the LobsterGuard scripts directory
 * @param logger - Logging function
 */
function registerFixTool(api, scriptsDir, logger) {
    const FIX_ENGINE = (0, path_1.join)(scriptsDir, "fix_engine.py");
    function runFixEngine(args) {
        try {
            const output = (0, child_process_1.execSync)(`python3 "${FIX_ENGINE}" ${args}`, {
                encoding: "utf-8",
                timeout: 120000, // 2 minutes max per step
                maxBuffer: 1024 * 1024,
            });
            return JSON.parse(output);
        }
        catch (err) {
            const error = err;
            // Try to parse stdout even on non-zero exit (fix_engine uses output() which calls sys.exit(0))
            if (error.stdout) {
                try {
                    return JSON.parse(error.stdout);
                }
                catch {
                    // Not JSON
                }
            }
            logger("error", `fix_engine error: ${error.stderr || error.message || "unknown"}`);
            return null;
        }
    }
    api.registerTool({
        name: "security_fix",
        description: "Guided auto-fix for security issues detected by LobsterGuard. " +
            "Use action='plan' to detect the environment and generate a fix plan. " +
            "Use action='execute' to run a specific step (requires step_id). " +
            "Use action='rollback' to undo changes if something fails. " +
            "Use action='verify' to confirm the fix worked. " +
            "Use action='list' to see all available auto-fixes. " +
            "IMPORTANT: Always show the plan to the user and get confirmation before executing steps.",
        parameters: [
            {
                name: "action",
                type: "string",
                description: "Action to perform: plan, execute, rollback, verify, list",
                required: true,
                enum: ["plan", "execute", "rollback", "verify", "list"],
            },
            {
                name: "check_id",
                type: "string",
                description: "ID of the check to fix (e.g., 'openclaw_user' for check #11). " +
                    "Required for plan, execute, rollback, verify.",
                required: false,
                default: "",
            },
            {
                name: "step_id",
                type: "number",
                description: "Step number to execute (required for action='execute')",
                required: false,
                default: 0,
            },
            {
                name: "target_user",
                type: "string",
                description: "Target user for the fix (e.g., 'openclaw'). " +
                    "If not specified, auto-detected from current user.",
                required: false,
                default: "",
            },
            {
                name: "language",
                type: "string",
                description: "Preferred language: es (Spanish) or en (English)",
                required: false,
                default: "es",
                enum: ["es", "en"],
            },
        ],
        async execute(args) {
            const action = args.action;
            const checkId = args.check_id || "";
            const stepId = args.step_id || 0;
            const targetUser = args.target_user || "";
            const lang = args.language || "es";
            logger("info", `security_fix called: action=${action}, check=${checkId}, step=${stepId}`);
            switch (action) {
                case "list": {
                    const result = runFixEngine("list");
                    if (!result) {
                        return { success: false, error: "Failed to list available fixes" };
                    }
                    return { success: true, data: result, text: JSON.stringify(result, null, 2) };
                }
                case "plan": {
                    if (!checkId) {
                        return { success: false, error: "check_id is required for action='plan'" };
                    }
                    let cmd = `plan ${checkId} --lang ${lang}`;
                    if (targetUser)
                        cmd += ` --user ${targetUser}`;
                    const result = runFixEngine(cmd);
                    if (!result) {
                        return { success: false, error: "Failed to generate fix plan" };
                    }
                    if (!result.success) {
                        const errMsg = lang === "es"
                            ? result.error_es || "Error generando plan"
                            : result.error_en || "Error generating plan";
                        return { success: false, error: errMsg, data: result };
                    }
                    // Format plan summary for the agent to display
                    const title = lang === "es" ? result.title_es : result.title_en;
                    const desc = lang === "es" ? result.description_es : result.description_en;
                    const time = lang === "es" ? result.estimated_time_es : result.estimated_time_en;
                    const steps = result.steps;
                    const stepList = steps.map((s) => {
                        const sTitle = lang === "es" ? s.title_es : s.title_en;
                        return `  ${s.id}. ${sTitle}`;
                    }).join("\n");
                    const summary = [
                        `🛡️ ${title}`,
                        "",
                        desc,
                        "",
                        lang === "es" ? `⏱️ Tiempo estimado: ${time}` : `⏱️ Estimated time: ${time}`,
                        lang === "es" ? `🔧 Proceso detectado: ${result.process_manager}` : `🔧 Process detected: ${result.process_manager}`,
                        lang === "es" ? `👤 Usuario destino: ${result.target_user}` : `👤 Target user: ${result.target_user}`,
                        "",
                        lang === "es" ? "Pasos:" : "Steps:",
                        stepList,
                        "",
                        lang === "es"
                            ? "¿Quieres que proceda? Puedo revertir los cambios si algo falla."
                            : "Shall I proceed? I can roll back changes if anything fails.",
                    ].join("\n");
                    return { success: true, data: result, text: summary };
                }
                case "execute": {
                    if (!checkId) {
                        return { success: false, error: "check_id is required" };
                    }
                    if (!stepId || stepId < 1) {
                        return { success: false, error: "step_id is required and must be >= 1" };
                    }
                    const result = runFixEngine(`execute ${checkId} ${stepId}`);
                    if (!result) {
                        return { success: false, error: `Failed to execute step ${stepId}` };
                    }
                    if (!result.success) {
                        const errMsg = lang === "es"
                            ? result.error_es || `Error en paso ${stepId}`
                            : result.error_en || `Error in step ${stepId}`;
                        const failText = [
                            `❌ ${errMsg}`,
                            "",
                            lang === "es"
                                ? "¿Quieres que revierta los cambios?"
                                : "Do you want me to roll back the changes?",
                        ].join("\n");
                        return { success: false, error: errMsg, data: result, text: failText };
                    }
                    const stepTitle = lang === "es" ? result.title_es : result.title_en;
                    const total = result.total_steps;
                    const emoji = result.is_last_step ? "🎉" : "✅";
                    const progress = `${result.step_id}/${total}`;
                    let statusText = `${emoji} Paso ${progress}: ${stepTitle}`;
                    if (lang === "en") {
                        statusText = `${emoji} Step ${progress}: ${stepTitle}`;
                    }
                    if (result.is_last_step) {
                        statusText += "\n\n" + (lang === "es"
                            ? "✅ ¡Todos los pasos completados! Verificando..."
                            : "✅ All steps completed! Verifying...");
                    }
                    return { success: true, data: result, text: statusText };
                }
                case "rollback": {
                    if (!checkId) {
                        return { success: false, error: "check_id is required" };
                    }
                    const result = runFixEngine(`rollback ${checkId}`);
                    if (!result) {
                        return { success: false, error: "Failed to rollback" };
                    }
                    const msg = lang === "es"
                        ? result.message_es || "Rollback completado"
                        : result.message_en || "Rollback completed";
                    return { success: true, data: result, text: `↩️ ${msg}` };
                }
                case "verify": {
                    if (!checkId) {
                        return { success: false, error: "check_id is required" };
                    }
                    const result = runFixEngine(`verify ${checkId}`);
                    if (!result) {
                        return { success: false, error: "Failed to verify fix" };
                    }
                    const msg = lang === "es"
                        ? result.message_es || ""
                        : result.message_en || "";
                    return {
                        success: true,
                        data: result,
                        text: msg || (result.fixed ? "✅ Fix verified!" : "⚠️ Fix not verified"),
                    };
                }
                default:
                    return { success: false, error: `Unknown action: ${action}` };
            }
        },
    });
    logger("info", "security_fix tool registered — guided auto-remediation available");
}
//# sourceMappingURL=fix_tool.js.map