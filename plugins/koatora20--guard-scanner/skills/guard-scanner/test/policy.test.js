const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { PolicyEngine } = require('../src/policy-engine.js');

describe('P1: Runtime Guard Policy Engine', () => {
    it('Should evaluate tool calls against strict sensitivity profiles', () => {
        const engine = new PolicyEngine({ mode: 'strict' });
        
        const decision1 = engine.evaluate('run_shell_command', { command: 'rm -rf /' });
        assert.equal(decision1.action, 'block', 'Should block destructive FS ops in strict mode');
        
        const decision2 = engine.evaluate('read_file', { file_path: '.env' });
        assert.equal(decision2.action, 'block', 'Should block credential reads in strict mode');
        
        const decision3 = engine.evaluate('read_file', { file_path: 'README.md' });
        assert.equal(decision3.action, 'allow', 'Should allow normal reads');
    });
});
