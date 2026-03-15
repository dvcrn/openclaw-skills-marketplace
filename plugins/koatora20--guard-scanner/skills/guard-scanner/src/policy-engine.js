class PolicyEngine {
    constructor(config = { mode: 'enforce' }) {
        this.mode = config.mode;
    }

    evaluate(toolName, args) {
        if (this.mode === 'monitor') {
            return { action: 'allow', reason: 'monitor mode' };
        }

        const argsStr = JSON.stringify(args).toLowerCase();

        // Destructive FS operations
        if (toolName === 'run_shell_command' && (argsStr.includes('rm -rf') || argsStr.includes('mkfs'))) {
            return { action: 'block', reason: 'destructive fs operation' };
        }

        // Credential access
        if (toolName === 'read_file' && (argsStr.includes('.env') || argsStr.includes('secret') || argsStr.includes('.aws'))) {
            return { action: 'block', reason: 'credential read operation' };
        }

        // Unrestricted network
        if (toolName === 'run_shell_command' && (argsStr.includes('curl') || argsStr.includes('wget')) && argsStr.includes('| bash')) {
            return { action: 'block', reason: 'unrestricted network execution (curl|bash)' };
        }

        return { action: 'allow', reason: 'safe operation' };
    }
}

module.exports = { PolicyEngine };
