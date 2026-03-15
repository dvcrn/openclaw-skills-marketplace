---
name: clawmemory
description: "ClawMemory — store and retrieve encrypted files on BSC blockchain. Use when user wants to set up ClawMemory, store files or conversations on-chain, retrieve stored content, check balance, manage memory slots, or mine MMP tokens."
---

# ClawMemory

Encrypted on-chain storage on BSC. Free tier: 10 named slots × 10KB each, permanent, no MMP needed.

---

## 🚀 ALWAYS START HERE — Check State First

**Every time this skill is triggered**, run the status check before anything else:

```bash
bash ~/.openclaw/workspace/skills/clawmemory/scripts/check-status.sh
```

Parse the JSON output and branch:

| Condition | Action |
|-----------|--------|
| `installed: false` | → **Step 1: Install** |
| `has_wallet: false` | → **Step 2: Create Wallet** |
| `has_bnb: false` | → **Step 3: Fund Wallet** |
| All true | → Ready, proceed to requested action |

---

## 📦 Step 1 — Install

```bash
bash ~/.openclaw/workspace/skills/clawmemory/scripts/install.sh
```

Say: "正在安装 ClawMemory，复制文件并安装依赖，大约需要 30 秒..."

After done, continue to Step 2.

---

## 👛 Step 2 — Create Wallet

```bash
bash ~/.openclaw/workspace/skills/clawmemory/scripts/setup-wallet.sh
```

Parse JSON output:
- Get `address` and `privateKey`
- Say to user:

> "✅ 钱包已创建！
>
> 钱包地址：`<address>`
>
> ⚠️ **请立即保存你的私钥，关闭此窗口后将无法再次查看：**
> `<privateKey>`
>
> 妥善保管私钥，任何人拿到私钥都能控制你的钱包。"

Wait for user to confirm they've saved the private key, then continue to Step 3.

---

## ⛽ Step 3 — Fund Wallet

Say to user:

> "需要少量 BNB 作为 Gas 费（手续费）。
>
> 请向以下地址转入 **0.01 BNB**（约 $5-6，足够使用很长时间）：
>
> `<wallet_address>`
>
> 可以从任何交易所或钱包转账，选择 **BNB Smart Chain (BSC)** 网络。
>
> 转账完成后告诉我，我来确认。"

After user confirms, check balance:

```bash
bash ~/.openclaw/workspace/skills/clawmemory/scripts/check-status.sh
```

- `has_bnb: true` → Continue to Step 4
- `has_bnb: false` → "还没收到，通常需要 1-2 分钟，稍等一下再确认？"

---

## 🎉 Step 4 — First Save (Guided Test)

Say:
> "太好了！现在来试一下第一次存储。"

Run a test save to the "default" slot:

```bash
node ~/.openclaw/workspace/skills/clawmemory/scripts/append-and-save.js \
  --slot "default" \
  --content "ClawMemory 初始化成功！这是我的第一条链上记忆。" \
  --label "初始化"
```

Parse JSON:
- `status: "ok"` → Say:

> "🎊 **成功！你的第一条记忆已永久存储在区块链上！**
>
> 记忆本：default（默认）
> 版本：#1
>
> 现在介绍一下你的免费额度：
> • **10 个记忆本**，每个独立，互不干扰
> • 每个记忆本最多 **10KB**（约 5000 汉字）
> • 所有内容**永久存储**，无需续费
>
> 想给你的第一个记忆本起个名字吗？（比如：工作、日记、想法...）"

- `status: "limit"` → Go to Limit Handling section below

---

## 📝 Daily Usage

### Save content to a slot

```bash
node ~/.openclaw/workspace/skills/clawmemory/scripts/append-and-save.js \
  --slot "<slot_name>" \
  --content "<content>" \
  --label "<optional title>"
```

**Slot name mapping** (Chinese → English):
- 工作/work → `work`
- 个人/私人 → `personal`  
- 日记 → `diary`
- 想法/灵感 → `ideas`
- CodeDNA → `codedna`
- 默认/default → `default`
- 其他 → use pinyin or English

Parse result:
- `status: "ok"` → "已存到「{slot}」记忆本，版本 #{version}，共用 {sizeKB}KB / 10KB"
- `status: "limit"` → See Limit Handling below

### Save current conversation

1. Call `session_status` to get current sessionKey
2. Call `sessions_history` with that sessionKey to get messages
3. Format as markdown:
   ```
   对话摘要：<one line summary>
   消息数：<count>
   
   <Human>: ...
   <Assistant>: ...
   ```
4. Write to `/tmp/chat-export.md`
5. Run append-and-save with `--file /tmp/chat-export.md --label "<summary>"`

### ⚠️ After ANY successful cli.js save — ALWAYS index + cache locally

Whenever `cli.js save` output contains a Merkle Root and Timestamp, **immediately** run:

```bash
node -e "
const fs = require('fs');
const os = require('os');
const INDEX    = os.homedir() + '/.clawmemory/index.json';
const SLOT_DIR = os.homedir() + '/.clawmemory/slots';
const slotName = '<slot name if used, else null>';
const content  = \`<full content that was saved>\`;
const merkleRoot = '<merkleRoot from output>';
const timestamp  = <timestamp from output>;
const label      = '<describe what was saved in plain Chinese>';

// 1. Write local slot cache (enables offline retrieval)
if (slotName) {
  if (!fs.existsSync(SLOT_DIR)) fs.mkdirSync(SLOT_DIR, {recursive:true});
  const slotFile = SLOT_DIR + '/' + slotName + '.md';
  fs.writeFileSync(slotFile, content, 'utf8');
}

// 2. Index
const db = fs.existsSync(INDEX) ? JSON.parse(fs.readFileSync(INDEX,'utf8')) : {};
if (!db.files) db.files = [];
db.files.push({ label, savedAt: new Date().toISOString(), merkleRoot, timestamp, slot: slotName });
if (slotName) {
  if (!db.slots) db.slots = {};
  db.slots[slotName] = { merkleRoot, timestamp, savedAt: new Date().toISOString(), label, version: (db.slots[slotName]?.version||0)+1 };
}
fs.writeFileSync(INDEX, JSON.stringify(db, null, 2));
console.log('indexed+cached');
"
```

**preferred path: always use `append-and-save.js --slot <name>` instead of `cli.js save` directly** — it handles local caching automatically.

Tell user only: **"已存好，随时说「取回」就能找到，不需要记任何东西。"**
**Never show merkleRoot or timestamp to user.**

### Retrieve content

When user says "取回/找回/恢复" anything:

**Step 1 — Check local slot cache first (instant, no P2P needed):**
```bash
node -e "
const fs = require('fs');
const os = require('os');
const INDEX = os.homedir() + '/.clawmemory/index.json';
const SLOT_DIR = os.homedir() + '/.clawmemory/slots/';

if (!fs.existsSync(INDEX)) { console.log('NO_INDEX'); process.exit(0); }
const db = JSON.parse(fs.readFileSync(INDEX, 'utf8'));

// List slots with local file status
const slots = db.slots || {};
Object.entries(slots).forEach(([name, v]) => {
  const localPath = SLOT_DIR + name + '.md';
  const hasLocal = fs.existsSync(localPath);
  const localSize = hasLocal ? fs.statSync(localPath).size : 0;
  console.log(JSON.stringify({ name, version: v.version, savedAt: v.savedAt, label: v.label, sizeKB: v.sizeKB, merkleRoot: v.merkleRoot, timestamp: v.timestamp, hasLocal, localPath, localSize }));
});

// List files
(db.files||[]).forEach((f,i) => {
  console.log(JSON.stringify({ idx: i, label: f.label, savedAt: f.savedAt, merkleRoot: f.merkleRoot, timestamp: f.timestamp, hasLocal: false }));
});
"
```

**Step 2 — Match what user described, then retrieve:**

**Path A: local slot file exists (hasLocal=true)** — use this first, instant and works offline:
```bash
cat ~/.clawmemory/slots/<slotname>.md
```

**Path B: local file missing — try P2P network:**
```bash
node ~/.clawmemory/memory-client/bin/cli.js load <merkleRoot> /tmp/retrieved.md --timestamp=<timestamp>
cat /tmp/retrieved.md
```

**Path C: P2P also fails** — tell user:
> "本地缓存文件不存在，P2P 网络暂时也无法取回。数据仍然安全存在链上，等矿工节点恢复后可以重试。如果你有这台机器的旧备份，文件在 `~/.clawmemory/slots/<slotname>.md`。"

**Step 3** — Display content to user — **never ask them to run commands or input hashes**

### List all slots

```bash
node -e "
const db = require(process.env.HOME + '/.clawmemory/index.json');
const slots = db.slots || {};
if (!Object.keys(slots).length) { console.log('暂无记忆本'); process.exit(0); }
Object.entries(slots).forEach(([name, v]) => {
  console.log(name + ' | v' + v.version + ' | ' + v.sizeKB + 'KB | ' + v.savedAt.slice(0,10));
});
"
```

---

## ⚠️ Limit Handling

When `append-and-save.js` returns `status: "limit"`:

**`reason: "size_exceeded"`** — slot is full (10KB):
> "「{slot}」记忆本已满（10KB上限）。
>
> 你有以下选择：
> 1. **新建一个记忆本** — 比如「{slot}-2」继续记录
> 2. **购买 MMP token** — 解锁付费存储（无大小限制）
>    PancakeSwap: `0x30b8Bf35679E024331C813Be4bDfDB784E8E9a1E`
>
> 要新建记忆本还是购买 MMP？"

**`reason: "max_slots"`** — 10 slots used up:
> "你已用完 10 个免费记忆本（{list of existing slots}）。
>
> 你有以下选择：
> 1. **删除一个不用的记忆本**（内容仍在链上，只是本地索引删除）
> 2. **购买 MMP token** — 解锁更多记忆本
>    PancakeSwap: `0x30b8Bf35679E024331C813Be4bDfDB784E8E9a1E`"

---

## ⛏️ Mine MMP Tokens

```bash
node ~/.clawmemory/miner/index.js
```

> "挖矿已启动！每解出一个 PoW 题目就获得 MMP token。建议在后台持续运行。"

---

## Contract Addresses (BSC Mainnet)

| | Address |
|---|---|
| MemoryProtocol Proxy | `0x3BD7945d18FE6B68D273109902616BF17eb40F44` |
| MMPToken | `0x30b8Bf35679E024331C813Be4bDfDB784E8E9a1E` |

## Free Tier Rules

- ≤ 10KB per slot → **free, permanent**
- ≤ 10 slots per wallet → **free**
- > 10KB or > 10 slots → **requires MMP token**
- Gas (BNB) always needed for on-chain transactions (~$0.01 per save)
