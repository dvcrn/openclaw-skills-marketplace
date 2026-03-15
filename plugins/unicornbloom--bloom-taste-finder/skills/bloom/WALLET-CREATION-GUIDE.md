# 🔐 Wallet Creation Guide

Bloom Identity Skill uses a **3-Tier Hybrid Approach** for wallet creation, providing flexibility for different users.

## 📊 Comparison

| Tier | Method | For | Setup | Cost | Control |
|------|--------|-----|-------|------|---------|
| 1️⃣ | Backend API | Bloom authenticated users | ✅ None | 🟢 Bloom pays | 🟡 Bloom manages |
| 2️⃣ | User CDP Credentials | Third-party power users | ⚙️ CDP account needed | 🟢 User pays | 🟢 Full control |
| 3️⃣ | Mock Wallet | Testing/development | ✅ None | 🟢 Free | 🔴 Test only |

---

## 🎯 How It Works

The skill automatically tries each tier in order:

```
🔍 Tier 1: Backend API
   ↓ (if unavailable)
🔍 Tier 2: User CDP Credentials
   ↓ (if unavailable)
🔍 Tier 3: Mock Wallet (testing)
```

### Tier 1: Backend API (Recommended for Bloom Users)

**Best for**: Bloom Protocol users who want the easiest experience

**How it works**:
1. Skill calls `https://api.bloomprotocol.ai/x402/wallet/create`
2. Backend creates wallet using Bloom's CDP credentials
3. Returns wallet info to skill

**Advantages**:
- ✅ Zero setup required
- ✅ Best user experience
- ✅ Cost controlled by Bloom
- ✅ Centralized wallet management

**Requirements**:
- None! Just run the skill

**Example**:
```bash
npx tsx src/index.ts --user-id your-user-id
# Automatically uses Backend API if available
```

---

### Tier 2: User CDP Credentials (Power Users)

**Best for**: Third-party developers who want full control

**How it works**:
1. User registers at https://portal.cdp.coinbase.com/
2. User sets CDP credentials in `.env`
3. Skill creates wallet using user's credentials

**Advantages**:
- ✅ Full control over wallets
- ✅ User owns the CDP account
- ✅ No dependency on Bloom backend
- ✅ Can export/manage wallets directly

**Requirements**:
1. Register at https://portal.cdp.coinbase.com/
2. Create API keys
3. Set environment variables:

```bash
# .env
CDP_API_KEY_ID=your_api_key_id
CDP_API_KEY_SECRET=your_api_key_secret
CDP_WALLET_SECRET=your_wallet_secret
CDP_RPC_URL=https://sepolia.base.org  # Optional
```

**Example**:
```bash
# Set credentials in .env, then run:
npx tsx src/index.ts --user-id your-user-id
# Will use your CDP credentials
```

---

### Tier 3: Mock Wallet (Testing Only)

**Best for**: Testing the skill without any setup

**How it works**:
1. Generates deterministic wallet address based on userId
2. Creates viem signing account for testing
3. Works locally but **cannot do real transactions**

**Advantages**:
- ✅ Zero setup required
- ✅ Perfect for testing/development
- ✅ Free
- ✅ Deterministic (same userId = same address)

**Limitations**:
- ❌ **Not a real wallet** - cannot receive/send funds
- ❌ **Test only** - do not use in production
- ⚠️ **No real balance** - just for testing flow

**Requirements**:
- None! Just run the skill without any credentials

**Example**:
```bash
# No .env setup needed
npx tsx src/index.ts --user-id test-user
# Will create mock wallet: 0x...
```

---

## 🚀 Quick Start

### Option A: Use Bloom Backend (Easiest)
```bash
# 1. Clone the repo
git clone https://github.com/unicornbloom/bloom-identity-skill.git
cd bloom-identity-skill

# 2. Install dependencies
npm install

# 3. Set required env vars
cp .env.example .env
# Edit .env: Set JWT_SECRET, DASHBOARD_URL, BLOOM_API_URL

# 4. Run!
npx tsx src/index.ts --user-id your-user-id

# ✅ Backend API creates real wallet automatically
```

### Option B: Use Your Own CDP (Power Users)
```bash
# 1-3. Same as Option A

# 4. Add CDP credentials to .env
CDP_API_KEY_ID=xxx
CDP_API_KEY_SECRET=xxx
CDP_WALLET_SECRET=xxx

# 5. Run!
npx tsx src/index.ts --user-id your-user-id

# ✅ Creates wallet with YOUR CDP credentials
```

### Option C: Test Mode (Developers)
```bash
# 1-3. Same as Option A

# 4. Run without any CDP setup!
npx tsx src/index.ts --user-id test-user

# ✅ Creates mock wallet for testing
```

---

## 🔍 How to Check Which Tier Was Used

Look for these log messages:

**Tier 1 (Backend API)**:
```
✅ Wallet created via Backend API (Bloom managed)
```

**Tier 2 (User CDP)**:
```
✅ Wallet created with user CDP credentials
```

**Tier 3 (Mock)**:
```
🧪 Mock wallet for test-user: 0x...
📝 To use real wallets: Set CDP credentials or authenticate with Bloom
```

---

## ⚠️ Important Notes

### Mock Wallets
- **DO NOT** send real funds to mock wallet addresses
- Mock wallets are **deterministic** - same userId always generates same address
- Great for testing identity card generation
- Cannot do real blockchain transactions

### Backend API Wallets
- Managed by Bloom Protocol
- Subject to rate limits
- Ideal for Bloom ecosystem users
- Contact Bloom team for wallet export if needed

### User CDP Wallets
- Full control and ownership
- You pay CDP costs
- Export/backup available through CDP dashboard
- Recommended for production third-party integrations

---

## 📚 Further Reading

- [Coinbase CDP Documentation](https://docs.cdp.coinbase.com/)
- [AgentKit Documentation](https://docs.cdp.coinbase.com/agent-kit/welcome)
- [X402 Protocol](https://docs.cdp.coinbase.com/x402/welcome)
- [Bloom Protocol Docs](https://docs.bloomprotocol.ai)

---

## 🆘 Troubleshooting

### "Backend wallet creation not available"
→ Backend API endpoint not yet deployed. Falls back to Tier 2 or 3.

### "CDP wallet initialization timed out"
→ CDP credentials invalid or network issue. Falls back to Tier 3.

### "Agent wallet not initialized"
→ All tiers failed. Check logs and environment variables.

---

**Questions?** Open an issue on GitHub or join our Discord!
