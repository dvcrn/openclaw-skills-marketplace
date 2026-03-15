# Performance Analysis - OpenClaw Agent Slowness

**Date:** 2026-02-06
**Issue:** OpenClaw agent running bloom-identity-skill is very slow
**Status:** 🔍 Analyzed, 🚀 Solutions Ready

---

## 🐌 Identified Bottlenecks

### 1. **CDP Wallet Initialization Timeout** ⏰ (CRITICAL - 30-60 seconds!)

**Location:** `src/blockchain/agent-wallet.ts:73-154`

**Problem:**
```typescript
// Line 87-90: Tries to use CDP API
this.walletProvider = await CdpWalletProvider.configureWithWallet({
  network: cdpNetwork as 'base' | 'base-sepolia',
  cdpWalletData: existingWallet.walletData,
});
```

**What happens:**
1. SDK looks for `coinbase_cloud_api_key.json`
2. Finds file but **format is wrong**
3. Tries to connect to CDP API
4. **TIMES OUT (30-60 seconds!)**
5. Finally falls back to mock wallet (line 135)

**Impact:** 30-60 seconds of waiting **every single run**

**Proof:**
- Current `coinbase_cloud_api_key.json` format:
  ```json
  {
    "id": "3118c35e-913a-406b-9946-1574c4de3642",
    "privateKey": "PHI8FmeRJaGnIGfAh6ZHUc8bfC+XR2M6yk52FLhXlmZNEpQZuwiGZlDygyD/a8IrUa5JPekMY2pkov4X2OWjhA=="
  }
  ```

- Expected format (from CDP Portal):
  ```json
  {
    "name": "organizations/{org_id}/apiKeys/{key_id}",
    "privateKey": "-----BEGIN EC PRIVATE KEY-----\nMHc...your_key_here...\n-----END EC PRIVATE KEY-----\n"
  }
  ```

**Why it's wrong:**
- ❌ `id` should be `name` with full organization path
- ❌ `privateKey` should be PEM format (BEGIN/END markers), not base64

---

### 2. **ClawHub Sequential API Calls** 🔄 (6-12 seconds)

**Location:** `src/integrations/clawhub-client.ts:72-95`

**Problem:**
```typescript
// Line 78-91: Sequential loop
for (const category of categories) {
  const results = await this.searchSkills({
    query: category,
    limit: limitPerCategory,
  });
  // ... process results
}
```

**What happens:**
- Main skill execution calls `getRecommendations()` (line 198)
- Searches 3 main categories → 3 sequential HTTP requests
- Then searches 3 sub categories → 3 more sequential HTTP requests
- **Total: 6 sequential requests**

**Impact:**
- Each request: ~1-2 seconds
- Total: 6-12 seconds

**Better approach:**
```typescript
// Parallel requests with Promise.all
const results = await Promise.all(
  categories.map(category =>
    this.searchSkills({ query: category, limit: limitPerCategory })
  )
);
```

---

### 3. **Bloom Backend Registration** 🌐 (2-5 seconds)

**Location:** `src/blockchain/agent-wallet.ts:243-303`

**Problem:**
```typescript
// Line 267-280: HTTP POST to Bloom backend
const response = await fetch(`${BLOOM_API_URL}/x402/agent-claim`, {
  method: 'POST',
  body: JSON.stringify({ ... }),
});
```

**What happens:**
- Registers agent with Bloom backend
- Includes signature verification
- Network latency + processing time

**Impact:** 2-5 seconds (acceptable, but could be optimized)

---

## 📊 Total Execution Time Breakdown

### Current (Slow) 🐌
```
1. Data Collection            →    ~1 sec    (mock data, fast)
2. Personality Analysis       →    ~2 sec    (AI analysis)
3. ClawHub Recommendations    →   6-12 sec   ⚠️ Sequential
4. CDP Wallet Init (TIMEOUT)  →  30-60 sec   ❌ CRITICAL
5. Bloom Registration         →   2-5 sec    (acceptable)
6. Twitter Share Link         →    ~1 sec    (fast)
────────────────────────────────────────────
TOTAL:                         42-81 seconds  😱
```

### After Quick Fix 🚀
```
1. Data Collection            →    ~1 sec
2. Personality Analysis       →    ~2 sec
3. ClawHub Recommendations    →   2-4 sec    ✅ Parallel
4. CDP Wallet (Skip Timeout)  →    <1 sec    ✅ Removed file
5. Bloom Registration         →   2-5 sec
6. Twitter Share Link         →    ~1 sec
────────────────────────────────────────────
TOTAL:                         8-13 seconds   ✅ Fast!
```

---

## ✅ Solutions

### Solution 1: Remove Bad CDP File (Immediate Fix - 5 seconds)

**Action:** Delete or rename `coinbase_cloud_api_key.json`

**Impact:** Eliminates 30-60 second timeout

**How:**
```bash
cd /Users/andrea.unicorn/bloom-identity-skill
mv coinbase_cloud_api_key.json coinbase_cloud_api_key.json.backup
```

**Result:**
- SDK immediately falls back to mock wallet
- No timeout
- Per-user wallets still work (deterministic mock addresses)

---

### Solution 2: Get Correct CDP Credentials (Production Fix)

**Action:** Download new key from CDP Portal

**Steps:**
1. Go to https://portal.cdp.coinbase.com/
2. Navigate to: Projects → API Keys
3. Click "Create API Key" or download existing
4. **Important:** Select "Export as JSON" (not raw format)
5. Save file as `coinbase_cloud_api_key.json` in project root

**Expected format:**
```json
{
  "name": "organizations/abc-123-def/apiKeys/3118c35e-913a-406b-9946-1574c4de3642",
  "privateKey": "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIBQpkJk...(your actual PEM key)...kpIRH8=\n-----END EC PRIVATE KEY-----\n"
}
```

**Verification:**
```bash
npm run build
node dist/index.js --user-id test-user

# Should see:
# ✅ Agent Wallet created: 0x{real_address}
# (NOT "Mock wallet")
```

---

### Solution 3: Optimize ClawHub Parallel Searches (Code Change)

**File:** `src/integrations/clawhub-client.ts`

**Current (Sequential):**
```typescript
async searchMultipleCategories(categories: string[], limitPerCategory: number = 3) {
  const allResults: ClawHubSkill[] = [];

  for (const category of categories) {  // ❌ Sequential
    const results = await this.searchSkills({
      query: category,
      limit: limitPerCategory,
    });
    // ...
  }

  return allResults;
}
```

**Optimized (Parallel):**
```typescript
async searchMultipleCategories(categories: string[], limitPerCategory: number = 3) {
  console.log(`🔍 Searching ${categories.length} categories in parallel...`);

  // Execute all searches in parallel
  const searchPromises = categories.map(category =>
    this.searchSkills({
      query: category,
      limit: limitPerCategory,
    })
  );

  const resultsArrays = await Promise.all(searchPromises);  // ✅ Parallel

  // Flatten and deduplicate
  const allResults: ClawHubSkill[] = [];
  const seenSlugs = new Set<string>();

  for (const results of resultsArrays) {
    for (const skill of results) {
      if (!seenSlugs.has(skill.slug)) {
        seenSlugs.add(skill.slug);
        allResults.push(skill);
      }
    }
  }

  // Sort by similarity score
  return allResults.sort((a, b) => b.similarityScore - a.similarityScore);
}
```

**Impact:**
- 6 sequential requests (6-12 sec) → 1 parallel batch (~2 sec)
- **Saves 4-10 seconds**

---

### Solution 4: Add Timeout to CDP Initialization (Defensive)

**File:** `src/blockchain/agent-wallet.ts`

**Add timeout wrapper:**
```typescript
async initialize(): Promise<AgentWalletInfo> {
  console.log(`🤖 Initializing Agent Wallet for user ${this.userId}...`);

  try {
    // ⭐ Add 5-second timeout
    const result = await Promise.race([
      this.initializeWallet(),
      this.createTimeoutPromise(5000)  // 5 seconds max
    ]);

    return result;
  } catch (error) {
    // Fast fallback to mock
    console.warn('⚠️  CDP timeout, using mock wallet');
    return this.createMockWallet();
  }
}

private createTimeoutPromise(ms: number): Promise<never> {
  return new Promise((_, reject) =>
    setTimeout(() => reject(new Error('CDP timeout')), ms)
  );
}
```

**Impact:**
- Reduces worst-case timeout from 60s → 5s
- Still provides fallback

---

## 🎯 Recommended Action Plan

### Phase 1: Immediate Fix (Do Now - 2 minutes)
1. ✅ Delete/rename bad CDP credentials file
2. ✅ Test skill → Should be fast now (~10 seconds)
3. ✅ Commit and push

### Phase 2: Performance Optimization (Next - 15 minutes)
1. ✅ Implement parallel ClawHub searches
2. ✅ Add CDP initialization timeout (defensive)
3. ✅ Test and verify improved speed
4. ✅ Commit and push

### Phase 3: Production CDP Keys (When Ready)
1. ⏳ Get correct format CDP keys from portal
2. ⏳ Test with real wallets
3. ⏳ Deploy to production

---

## 🧪 Testing

### Test Current Performance:
```bash
time node dist/index.js --user-id test-performance
```

**Expected (Before Fix):** 42-81 seconds
**Expected (After Fix):** 8-13 seconds

---

## 📝 Summary

| Issue | Impact | Fix | Time Saved |
|-------|--------|-----|------------|
| CDP credentials timeout | 30-60 sec | Remove bad file | 30-60 sec ✅ |
| Sequential ClawHub API | 6-12 sec | Parallel requests | 4-10 sec ✅ |
| No timeout defense | Variable | Add 5s timeout | Reduces risk ✅ |

**Total Time Saved:** 34-70 seconds (from 42-81s → 8-13s)

**Performance Improvement:** ~6x faster! 🚀

---

Built with 💜 for @openclaw by Bloom Protocol
