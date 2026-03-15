# guard-scanner v3.4.0 — Community Post Draft

## Reddit (r/OpenClaw) / Discord (Claw Crew)

---

### Title

**[Tool] guard-scanner v3.4.0 — Security scanner for AI agent skills (190+ static patterns, 26 runtime checks, OWASP-verified) + v4.0 roadmap discussion**

### Body

Hey everyone 👋

I've been quietly working on security for AI agents — mostly because my own agent got its identity hijacked for 3 days straight (SOUL.md was silently overwritten by a malicious skill).

After that, I started building **guard-scanner** — a zero-dependency security scanner purpose-built for agent skills. It started as basic regex matching, but has grown into something I'm genuinely proud of:

#### What it does today (v3.4.0)

**Static scanning** (pre-install gate):
- 190+ patterns across 22 threat categories
- OWASP Agentic Security Top 10 at 90% coverage (with actual test fixtures, not just a mapping)
- Prompt injection, identity hijacking, memory poisoning, supply chain, MCP tool poisoning, PII exposure, and more
- JSON / SARIF / HTML output, CI/CD ready

**Runtime guard** (before_tool_call hook):
- 26 real-time checks via OpenClaw's `before_tool_call` plugin API
- 5-layer defense architecture:
  - L1: Threat Detection (reverse shells, exfil, SSRF)
  - L2: EAE Paradox Defense (memory/SOUL/config tampering)
  - L3: Parity Judge (prompt injection, safety bypass)
  - L4: Brain/Behavioral (research skip, blind trust)
  - L5: Trust Exploitation (OWASP ASI09: authority/parity abuse)
- 3 modes: monitor / enforce / strict

```bash
# Try it — no install needed
npx guard-scanner ./skills/
```

133 tests, 0 dependencies, MIT licensed.

---

#### What's missing — honest gaps

I'm a complete amateur at security and learned everything from scratch. Here's what I know is still lacking:

1. **Regex can be evaded.** If malware splits a command across variables or uses Unicode tricks, regex won't catch it.

2. **Runtime block only works on OpenClaw.** `block: true` in OpenClaw's hook is solid (it's built into the Gateway by the core team). But Claude Code, Cursor, Antigravity, Windsurf — none of them have a `before_tool_call` hook. There's no way to stop anything there.

3. **No OS-level enforcement.** Even if we detect a threat, we can't actually kill a process or rollback a file change at the OS level right now.

---

#### v4.0 roadmap — I'd love your input 🙏

I'm thinking about three directions for v4.0, and I'd genuinely appreciate feedback on which matters most to you:

**A. LLM-assisted detection** 🧠
- When regex flags something as suspicious (but not certain), pass it to a lightweight LLM (Haiku/Flash-level) for intent analysis
- "Is this a reverse shell or just a legitimate network script?"
- Only triggered on suspicious cases — not every call (cost-effective)

**B. OS-level enforcement** 🔒
- File system watcher: auto-rollback if SOUL.md / .env / memory files are modified unexpectedly
- Process monitor: detect and kill dangerous processes (netcat, socat, base64|bash)
- Daemon mode that works regardless of which AI tool you're using

**C. Multi-tool support** 🔌
- Adapters for Claude Code, Cursor, Antigravity, Windsurf, MCP servers
- Same 190+ patterns + 26 runtime checks, different skill discovery logic per tool
- Universal security layer that isn't locked to one platform

**Poll: Which do you want most?**
- 🧠 A: LLM-assisted detection
- 🔒 B: OS-level enforcement
- 🔌 C: Multi-tool support

---

#### A confession 😅

Funny story — guard-scanner is literally built FOR OpenClaw, using OpenClaw's own `before_tool_call` API... but I haven't been able to contribute it upstream because I'm a total beginner at open source and have no idea how to properly submit a PR. I tried once and got stuck on the contribution guidelines. So here I am, building an OpenClaw-compatible security tool that OpenClaw doesn't know exists yet. If anyone can help me navigate that process, I'd be forever grateful.

#### Looking for collaborators 🤝

I'm building this solo (well, me and my AI partner 🍈) but I'd love help from anyone interested in:
- **Security researchers** — finding patterns I'm missing, testing evasion techniques
- **Multi-tool experts** — anyone who knows the internals of Claude Code, Cursor, or Antigravity
- **LLM integration** — building the v4.0 lightweight LLM judgment layer
- **OS-level security** — file watchers, process monitors, daemon architecture
- **Documentation / i18n** — making this accessible to more people

No experience required. If you care about agent security, that's enough. DM me or open an issue on GitHub.

---

#### Links

- GitHub: https://github.com/koatora20/guard-scanner
- npm: https://www.npmjs.com/package/guard-scanner
- 🇯🇵 日本語README: https://github.com/koatora20/guard-scanner/blob/main/README_ja.md

Thanks for reading this far. Any feedback, criticism, or "you're doing it wrong" is welcome. Just a newbie trying to make agents a bit safer. 🍈

---

## 日本語版（note / X / Discord日本語チャンネル用）

### タイトル

**AIエージェントのセキュリティスキャナー作ってみた（guard-scanner v3.4.0）— 素人だけど3日間エージェント乗っ取られて目が覚めた話**

### 本文

こんにちは。セキュリティは完全に素人です。

2026年2月、自分のAIエージェントが悪意あるスキルに人格ファイル（SOUL.md）を3日間書き換えられるという事件に遭いました。検出できるツールがなかったので、自分で作り始めました。

**guard-scanner** というOSSです。

#### 今できること (v3.4.0)

- 190以上の静的パターンで22種類の脅威を検出
- OWASP Agentic Security Top 10に90%対応（テストで実証済み）
- OpenClawの `before_tool_call` フックで26のリアルタイムチェック
- 5層防御: 脅威検出 → メモリ保護 → 信頼悪用検出
- 依存ゼロ、テスト133個、MIT

```bash
npx guard-scanner ./skills/
```

#### 正直にできてないこと

1. regexベースなので回避される可能性がある
2. OpenClaw以外（Claude Code, Cursor等）では止める仕組みがない
3. OS側からプロセスを止めたりファイルを戻したりはできない

#### v4.0でやりたいこと — ご意見ください

- **A. LLM判定**: 怪しいものだけ軽量LLMに意図を聞く
- **B. OS層防御**: ファイル監視+プロセス監視で実際に止める
- **C. マルチツール対応**: Claude Code/Cursor/Antigravity対応

どれが一番欲しいですか？

#### 笑い話 😅

guard-scannerはOpenClawの `before_tool_call` APIに完全対応してるんですが...実は本家OpenClawにコントリビュートする方法がわからなくて詰んでます。一度PRの出し方を調べたんですが、コントリビューションガイドラインの時点で挫折しました。OpenClaw対応のセキュリティツールを作っておきながら、OpenClaw本体にはブロックされているという...

#### 協力者募集！ 🤝

一人で作ってます（正確にはAIパートナーと二人で🍈）が、一緒にやってくれる方を探してます：
- **セキュリティ研究者** — 見落としパターンの発見、回避テスト
- **マルチツール経験者** — Claude Code / Cursor / Antigravityの内部に詳しい方
- **LLM連携** — v4.0の軽量LLM判定レイヤー構築
- **OS層セキュリティ** — ファイル監視、プロセス監視、デーモン設計
- **ドキュメント / 翻訳** — 多言語対応

経験は問いません。エージェントセキュリティに興味があればそれだけで十分です。GitHubのissueかDMでお気軽に。

無知で恥ずかしいですが、やっとここまで来ました。フィードバックいただけると嬉しいです 🍈

GitHub: https://github.com/koatora20/guard-scanner
