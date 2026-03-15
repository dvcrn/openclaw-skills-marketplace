#!/usr/bin/env node

const cmd = process.argv[2] || 'help';

function out(s='') { console.log(s); }

switch (cmd) {
  case 'help':
    out('waimai');
    out('');
    out('Browser assistant for manual Eleme browsing and order preparation.');
    out('');
    out('Commands:');
    out('  waimai help      Show this help');
    out('  waimai about     Show skill boundaries');
    break;
  case 'about':
    out('This skill is for manual browser-assisted Eleme browsing.');
    out('Login stays manual. Payment stays manual.');
    out('It does not store passwords or complete payment.');
    break;
  default:
    out(`Unknown command: ${cmd}`);
    process.exitCode = 1;
}
