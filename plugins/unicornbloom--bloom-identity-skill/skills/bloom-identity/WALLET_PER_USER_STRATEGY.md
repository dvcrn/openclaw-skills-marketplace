# Per-User Wallet Strategy for Agent Kit

## ✅ YES - Coinbase Agent Kit Supports Multiple Wallets

Based on the `CdpWalletProvider` interface, Agent Kit provides three key capabilities:

### 1. **Export Wallet** (Line 216)
```typescript
exportWallet(): Promise<WalletData>
```

### 2. **Import with Wallet Data** (Line 44-46)
```typescript
interface ConfigureCdpAgentkitWithWalletOptions {
  cdpWalletData?: string;  // Import existing wallet
  mnemonicPhrase?: string;  // Import via mnemonic
}
```

### 3. **Create New Wallet**
```typescript
CdpWalletProvider.configureWithWallet({ network: 'base' })
// Creates new wallet if no cdpWalletData or mnemonicPhrase provided
```

---

## 🎯 Implementation Strategy

### **Recommended: Store Wallet Per User**

```typescript
interface UserWalletRecord {
  userId: string;
  walletData: string;  // Exported from CDP
  walletAddress: string;
  createdAt: Date;
  lastUsedAt: Date;
}
```

### **Flow:**

#### **First Time User:**
```typescript
async function getOrCreateWalletForUser(userId: string) {
  // 1. Check if user already has a wallet
  const existing = await db.wallets.findOne({ userId });

  if (existing) {
    // 2. Import existing wallet
    const walletProvider = await CdpWalletProvider.configureWithWallet({
      network: 'base',
      cdpWalletData: existing.walletData,  // ⭐ Import
    });

    return {
      address: walletProvider.getAddress(),
      isNew: false,
    };
  }

  // 3. Create new wallet for this user
  const walletProvider = await CdpWalletProvider.configureWithWallet({
    network: 'base',
    // No cdpWalletData = creates new wallet
  });

  // 4. Export and store wallet data
  const walletData = await walletProvider.exportWallet();
  const walletDataJson = JSON.stringify(walletData);

  await db.wallets.insert({
    userId,
    walletData: walletDataJson,  // ⭐ Store for next time
    walletAddress: walletProvider.getAddress(),
    createdAt: new Date(),
    lastUsedAt: new Date(),
  });

  return {
    address: walletProvider.getAddress(),
    isNew: true,
  };
}
```

---

## 🔐 Security Considerations

### **Storage:**
- ✅ Store `walletData` encrypted in database
- ✅ Use user-specific encryption keys
- ✅ CDP wallet data already contains encrypted private keys
- ⚠️ Never store plain-text mnemonics or private keys

### **Access Control:**
- ✅ Only user can access their own wallet
- ✅ Agent can only sign with user's permission
- ✅ Use JWT or session tokens to verify user identity

---

## 📊 Current Implementation vs. Ideal

### **Current (bloom-identity-skill):**
```typescript
// ❌ Creates same wallet every time
this.walletProvider = await CdpWalletProvider.configureWithWallet({
  network: cdpNetwork,
});
// No userId, no storage, no retrieval
```

**Problem:** Every user gets the SAME wallet address (or a new random one each time)

### **Ideal Implementation:**
```typescript
// ✅ Per-user wallet
this.walletProvider = await CdpWalletProvider.configureWithWallet({
  network: cdpNetwork,
  cdpWalletData: await getUserWalletData(userId),  // ⭐ User-specific
});
```

---

## 🛠️ Implementation in agent-wallet.ts

### **Updated Constructor:**
```typescript
export class AgentWallet {
  private userId: string;  // ⭐ NEW

  constructor(config: AgentWalletConfig & { userId: string }) {
    this.userId = config.userId;  // ⭐ Store userId
    this.network = config.network || 'base-mainnet';
  }
}
```

### **Updated initialize():**
```typescript
async initialize(): Promise<AgentWalletInfo> {
  console.log(`🤖 Initializing Agent Wallet for user ${this.userId}...`);

  try {
    // 1. Check if user has existing wallet
    const existingWallet = await this.getUserWallet(this.userId);

    if (existingWallet) {
      // Import existing wallet
      console.log(`📂 Loading existing wallet for ${this.userId}...`);

      this.walletProvider = await CdpWalletProvider.configureWithWallet({
        network: this.network === 'base-mainnet' ? 'base' : 'base-sepolia',
        cdpWalletData: existingWallet.walletData,  // ⭐ Import
      });

      this.walletAddress = this.walletProvider.getAddress();

      // Update last used
      await this.updateWalletLastUsed(this.userId);

    } else {
      // Create new wallet
      console.log(`🆕 Creating new wallet for ${this.userId}...`);

      this.walletProvider = await CdpWalletProvider.configureWithWallet({
        network: this.network === 'base-mainnet' ? 'base' : 'base-sepolia',
      });

      this.walletAddress = this.walletProvider.getAddress();

      // Export and store
      const walletData = await this.walletProvider.exportWallet();
      await this.saveUserWallet(this.userId, walletData);
    }

    console.log(`✅ Agent Wallet ready: ${this.walletAddress}`);

    return {
      address: this.walletAddress,
      network: this.network,
      x402Endpoint: this.getX402Endpoint(),
    };

  } catch (error) {
    // Error handling...
  }
}
```

### **Storage Methods:**
```typescript
private async getUserWallet(userId: string): Promise<UserWalletRecord | null> {
  // TODO: Implement database lookup
  // - MongoDB collection: user_wallets
  // - Find by userId
  return null;
}

private async saveUserWallet(userId: string, walletData: WalletData): Promise<void> {
  // TODO: Implement database storage
  // - Encrypt walletData
  // - Store with userId as key
  // - Include timestamp
}

private async updateWalletLastUsed(userId: string): Promise<void> {
  // TODO: Update lastUsedAt timestamp
}
```

---

## 🔄 Migration Path

### **Phase 1: Current (Testing)**
- ✅ One wallet for all users (or random each time)
- ✅ Good for testing basic flow
- ⚠️ Not production-ready

### **Phase 2: Per-User Wallets** ⭐ REQUIRED FOR PRODUCTION
- ✅ Each user gets unique persistent wallet
- ✅ Wallet survives across sessions
- ✅ User can receive payments at their X402 endpoint
- ✅ Production-ready

### **Phase 3: Advanced** (Future)
- Multiple wallets per user (different networks)
- Wallet recovery mechanisms
- Multi-sig wallets for teams
- Custodial + non-custodial options

---

## 📚 References

From `@coinbase/agentkit` package:

- **Export:** `CdpWalletProvider.exportWallet()` → `WalletData`
- **Import:** `CdpWalletProvider.configureWithWallet({ cdpWalletData })` → `CdpWalletProvider`
- **Mnemonic:** `CdpWalletProvider.configureWithWallet({ mnemonicPhrase })` → `CdpWalletProvider`

Official Documentation:
- [Wallet Management](https://docs.cdp.coinbase.com/agentkit/docs/wallet-management)
- [CDP Wallets](https://www.coinbase.com/developer-platform/products/wallets)
- [GitHub: coinbase/agentkit](https://github.com/coinbase/agentkit)

---

## ✅ Answer to Original Question

**Q: Does the Coinbase function give us the power to enable different users' agents to create a wallet?**

**A: YES! ✅**

**How:**
1. ✅ **Export wallet data** using `exportWallet()`
2. ✅ **Store wallet data** per user in database
3. ✅ **Import wallet data** using `configureWithWallet({ cdpWalletData })`
4. ✅ **Each user gets unique, persistent wallet**

**Current Status:**
- ⚠️ Current implementation doesn't do this yet (uses same wallet for all)
- ✅ Agent Kit API supports it completely
- 🔨 Implementation requires adding storage layer

**Next Steps:**
1. Add database storage for user wallets
2. Update `AgentWallet` class to accept `userId`
3. Implement `getUserWallet()` and `saveUserWallet()`
4. Test with multiple users

---

Built with insights from [Coinbase Agent Kit](https://github.com/coinbase/agentkit) 🚀
