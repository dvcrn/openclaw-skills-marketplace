#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Main handler
async function main(input) {
  const action = input.action || 'help';
  const chain = input.chain || '';

  try {
    if (action === 'monitor') {
      if (chain === 'BSC') {
        const { monitorBSC } = require('./index-bsc.js');
        return monitorBSC(input);
      } else if (chain === 'SOL') {
        const { monitorSOL } = require('./index-sol-safe.js');
        return monitorSOL(input);
      } else if (!chain || chain === 'BOTH') {
        const { monitorBSC } = require('./index-bsc.js');
        const { monitorSOL } = require('./index-sol-safe.js');
        
        const [bscResult, solResult] = await Promise.all([
          monitorBSC(input),
          monitorSOL(input)
        ]);
        
        return {
          success: true,
          action: 'monitor',
          chains: ['BSC', 'SOL'],
          results: {
            BSC: bscResult,
            SOL: solResult
          }
        };
      }
    } else if (action === 'help') {
      return {
        success: true,
        action: 'help',
        message: `
Unified Dev Monitor with Auto-Buy - Multi-chain Dev Wallet Monitor

Supported chains: BSC, SOL
Features: Real-time monitoring, auto-buy via PancakeSwap/PumpSwap, webhook notifications, historical records

Usage:
  { "action": "monitor", "chain": "BSC", "address": "...", "duration": 3600, "autoBuy": { "enabled": true, "amount": "10" } }
  { "action": "monitor", "chain": "SOL", "address": "...", "duration": 3600, "autoBuy": { "enabled": true, "amount": 0.1 } }
        `
      };
    } else {
      return {
        success: false,
        error: 'Unknown action',
        message: 'Available actions: monitor, help'
      };
    }
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

module.exports = { main };

if (require.main === module) {
  const input = process.argv[2] ? JSON.parse(process.argv[2]) : { action: 'help' };
  
  main(input).then(result => {
    console.log(JSON.stringify(result, null, 2));
  }).catch(error => {
    console.error('Error:', error);
    process.exit(1);
  });
}
