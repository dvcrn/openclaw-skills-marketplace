# Example: Block Reward Analysis

## User Prompt

```
Who produced block #68000000 and how much TRX was burned?
```

## Expected Workflow

1. **Fetch Block** → `getBlockByNum(68000000)` → Block header with witness address
2. **Block Stats** → `getBlockStatistics(68000000)` → Fee stats, energy/net usage
3. **Transaction Info** → `getTransactionInfoByBlockNum(68000000)` → All transaction receipts
4. **SR Lookup** → `listWitnesses()` → Match witness address to SR name
5. **SR Brokerage** → `getBrokerage(witnessAddress)` → Reward split
6. **Block Balance** → `getBlockBalance(hash, number)` → All balance changes

## Expected Output (Sample)

```
## Block #68,000,000 Report

### Block Overview
- Block Number: #68,000,000
- Timestamp: 2025-07-15 14:22:33 UTC

### Producer
- SR Address: TGj1Ej1qRzL9feLT...
- SR Name: Poloniex
- Brokerage: 20%

### Economics
- Block Reward: 16 TRX
- Transaction Fees: 28.3 TRX
- TRX Burned: 25.1 TRX
- SR Revenue: 16 + (28.3 - 25.1) = 19.2 TRX
  - SR keeps (20%): 3.84 TRX
  - Voter reward pool (80%): 15.36 TRX

### Transactions
- Total: 150 transactions
- Smart Contract Calls: 98 (65.3%)
- TRX Transfers: 30 (20.0%)
- Other: 22 (14.7%)

### Resource Consumption
- Total Energy Used: 9,800,000
- Total Bandwidth Used: 150,000
```

## MCP Tools Used

| Tool | Call Count | Purpose |
|------|-----------|---------|
| `getBlockByNum` | 1 | Block header data |
| `getBlockStatistics` | 1 | Block fee statistics |
| `getTransactionInfoByBlockNum` | 1 | Transaction receipts |
| `listWitnesses` | 1 | SR name lookup |
| `getBrokerage` | 1 | Reward distribution |
| `getBlockBalance` | 1 | Balance changes |
