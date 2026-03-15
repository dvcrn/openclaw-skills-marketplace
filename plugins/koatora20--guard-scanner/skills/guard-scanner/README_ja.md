# 🛡️ guard-scanner

**AIエージェントとMCP連携ワークフローのためのセキュリティポリシー＆分析レイヤー**

静的スキャン · ランタイムフック · MCPサーバー · 資産監査 · VirusTotal連携

*注意: guard-scannerはヒューリスティックおよびポリシーレイヤーであり、完全な防御ではありません。完全なセキュリティにはコンテキスト検証とサンドボックス隔離が必要です。*

[![npm version](https://img.shields.io/npm/v/@guava-parity/guard-scanner.svg?style=flat-square&color=cb3837)](https://www.npmjs.com/package/@guava-parity/guard-scanner)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-1_(ws)-blue?style=flat-square)]()
[![Tests Passing](https://img.shields.io/badge/tests-539-brightgreen?style=flat-square)]()
[![Patterns](https://img.shields.io/badge/patterns-358-blueviolet?style=flat-square)]()

[English](README.md) •
[クイックスタート](#クイックスタート) •
[資産監査](#資産監査) •
[VirusTotal連携](#virustotal連携) •
[リアルタイム監視](#リアルタイム監視)

---

## 🎯 機能とセキュリティ境界 (Capabilities & Boundaries)

**guard-scanner**は拡張可能なポリシー施行エンジンです。その機能は[capabilities.json](docs/spec/capabilities.json)（単一の信頼できる情報源）によって厳密に管理されています。

*   **静的パターン**: 358 (AST diffing, 正規表現ヒューリスティック)
*   **脅威カテゴリ**: 35 (プロンプトインジェクション, A2A汚染, ID偽装など)
*   **ランタイムチェック**: 27 (MCP `before_tool_call` のインターセプト)
*   **依存パッケージ**: ランタイム 1 (`ws` のみ)、サプライチェーンリスクを最小化

### OpenClaw互換の検証基準

- **検証対象:** OpenClaw `v2026.3.8`
- **検証済みの面:** `openclaw.plugin.json` の必須項目、`package.json > openclaw.extensions` による discovery、compiled entry `dist/openclaw-plugin.mjs` の `before_tool_call` ブロック動作
- **ここで主張しないもの:** context-engine slot 互換。guard-scanner は現状、OpenClaw の context engine ではなく runtime guard plugin として検証しています。
- **リリースゲート:** `npm run release:gate` が discovery・manifest・hook動作・古い互換主張をまとめて検証します。

### セキュリティ境界: できること・できないこと

| 機能 | ステータス | 説明 |
|---|---|---|
| **ヒューリスティック検知** | ✅ 検知 / 警告 | 既知の攻撃パターンをコード・テキストから静的に検出します。 |
| **ランタイムガードレール** | 🛡️ ブロック | OpenClawなどの `before_tool_call` フックにマウントすることで実行をブロックできます。 |
| **ネットワークアクセス** | 🌐 VT監査用 | VirusTotalやnpm監査などの特定機能を呼び出した場合のみネットワークを使用します。 |
| **コンテキスト検証** | ❌ スコープ外 | サンドボックス内でのコードの振る舞いを動的に証明することはできません。 |
| **完全な防御** | ❌ いいえ | これはポリシー施行レイヤーです。OSレベルの隔離（eBPFやWASM等）と併用してください。 |

## Finding Schema

guard-scanner は、静的検出・ランタイムガード・SARIF出力のすべてで共通の finding schema を返します。機械可読な契約は [`docs/spec/finding.schema.json`](docs/spec/finding.schema.json) にあります。

### 必須フィールド

| フィールド | 意味 |
|---|---|
| `rule_id` | 発火したルール/チェックの安定ID |
| `category` | 脅威カテゴリ、またはランタイムガード分類 |
| `severity` | `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` |
| `description` | finding の要約 |
| `rationale` | なぜこのルールが発火したか |
| `preconditions` | 悪用や影響成立に必要な前提条件 |
| `false_positive_scenarios` | 誤検知になり得る代表ケース |
| `remediation_hint` | リスク低減のための具体的アクション |
| `validation_state` | `heuristic-only` / `semantic-match` / `chain-validated` / `runtime-observed` |
| `validation_status` | `validated` / `heuristic-only` / `runtime-observed` |
| `confidence` | 0.0〜1.0 の信頼度スコア |
| `evidence_spans` | 行単位の構造化エビデンス |
| `attack_chain_id` | 複数 finding を束ねる攻撃チェーン ID |
| `evidence` | ファイル/行/サンプル、またはランタイム実行文脈 |

### 例

```json
{
  "schema_version": "2.0.0",
  "source": "static",
  "rule_id": "PI_IGNORE",
  "category": "prompt-injection",
  "severity": "CRITICAL",
  "description": "Prompt injection: ignore instructions",
  "rationale": "Matches known syntax for this threat vector.",
  "preconditions": "Agent executes the payload directly or processes it in a vulnerable context.",
  "false_positive_scenarios": [
    "Documentation or research samples that quote malicious prompts for education."
  ],
  "remediation_hint": "Sanitize input, remove dynamic evaluation, or restrict execution scope.",
  "validation_state": "heuristic-only",
  "validation_status": "heuristic-only",
  "confidence": 0.65,
  "evidence_spans": [
    {
      "file": "SKILL.md",
      "start_line": 14,
      "end_line": 14
    }
  ],
  "attack_chain_id": null,
  "evidence": {
    "file": "SKILL.md",
    "line": 14,
    "sample": "ignore all previous instructions"
  }
}
```

## 概要 (Overview)

guard-scannerは、AIエージェントのスキルやMCP（Model Context Protocol）連携ワークフローに特化した**セキュリティポリシー＆分析レイヤー**です。

従来のセキュリティツール（VirusTotalなど）はマルウェアの検知には優れていますが、AIエージェントは「自然言語の指示に隠されたプロンプトインジェクション」や「設定ファイル上書きによるアイデンティティ乗っ取り」「巧妙な会話を通じたメモリ汚染」といった新しいクラスの攻撃に直面しています。

guard-scannerの特徴:
- **軽量（Lightweight）:** ランタイム依存関係を最小限に抑えています（MCP用の`ws`のみ）。
- **ポリシーベース（Policy-Aware）:** 過剰な権限行使（Excessive Agency）の検出とセキュリティ境界の定義に焦点を当てています。
- **OpenClaw/MCP対応:** エージェントの実行フック（before_tool_call）に直接組み込めます。
- **互換性の主張は条件付き:** OpenClaw `v2026.3.8` の manifest/discovery/hook 契約に対して検証した範囲のみを public surface として扱います。
- **最新版監視あり:** `npm run check:upstream` が npm registry と GitHub Releases の両方を cross-check し、`package.json` の固定版との差分やソース不一致が出たら失敗しつつ `docs/generated/openclaw-upstream-status.json` を更新します。
- **相互補完（Complementary）:** 従来のマルウェアスキャナと併用し、指示と機能のレイヤーに特化して防御します。
- **多層防御（Defense in Depth）:** 静的スキャンとランタイムガードレールを提供します（※本ツール単体は完全なサンドボックス環境を提供するものではありません）。

---

## クイックスタート

```bash
# コマンド1つでスキャン開始
npx @guava-parity/guard-scanner ./skills/

# 詳細出力 + 厳密モード
guard-scanner ./skills/ --verbose --strict

# フル監査
guard-scanner ./skills/ --verbose --check-deps --json --sarif --html
```

---

## 資産監査（V6+）

npm/GitHub/ClawHubの公開資産をチェックし、漏洩やセキュリティリスクを検出。

```bash
# npm — node_modules、.envの公開を検出
guard-scanner audit npm <ユーザー名> --verbose

# GitHub — コミットされた秘密鍵、巨大リポ
guard-scanner audit github <ユーザー名> --format json

# ClawHub — 悪意あるスキルパターン
guard-scanner audit clawhub <クエリ>

# 全プロバイダー一括
guard-scanner audit all <ユーザー名>
```

---

## VirusTotal連携（V7+）

guard-scannerのセマンティック検出 + VirusTotalの70以上のアンチウイルスエンジン = **二層防御（Double-Layered Defense）**

| レイヤー | エンジン | 検出対象 |
|---|---|---|
| **セマンティック** | guard-scanner | プロンプト注入、メモリ汚染、サプライチェーン |
| **シグネチャ** | VirusTotal | 既知マルウェア、トロイの木馬、C2インフラ |

```bash
# 1. 無料APIキーを取得: https://www.virustotal.com
# 2. 環境変数に設定
export VT_API_KEY=あなたのAPIキー

# 3. 任意のコマンドで使用
guard-scanner scan ./skills/ --vt-scan
guard-scanner audit npm koatora20 --vt-scan
```

> **無料枠**: 4リクエスト/分、500/日、15,500/月。個人利用のみ。  
> **VTはオプション** — なくても全機能が動作します。

---

## リアルタイム監視（V8+）

ファイル変更を検知して自動スキャン。

```bash
# 監視開始
guard-scanner watch ./skills/ --strict --verbose

# Soul Lockも有効化
guard-scanner watch ./skills/ --strict --soul-lock
```

`Ctrl+C`でセッション統計を表示して終了。

---

## CI/CD連携（V8+）

| プラットフォーム | 対応形式 |
|---|---|
| GitHub Actions | アノテーション + Step Summary |
| GitLab | Code Quality JSON |
| 汎用 | Webhook通知 |

```yaml
# GitHub Actions
name: Skill Security Scan
on: [push, pull_request]
jobs:
  guard-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx @guava-parity/guard-scanner ./skills/ --sarif --strict --fail-on-findings
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: skills/guard-scanner.sarif
```

---

## 35脅威カテゴリ

| # | カテゴリ | 検出対象 |
|---|---------|---------|
| 1 | プロンプトインジェクション | 不可視Unicode、ホモグリフ、ロール上書き |
| 2 | 悪意あるコード | `eval()`, リバースシェル |
| 3 | 不審なダウンロード | `curl\|bash`パイプ |
| 4 | 認証情報操作 | `.env`読取、SSH鍵アクセス |
| 5 | シークレット検出 | AWSキー、GitHubトークン |
| 6 | データ流出 | webhook.site、DNS tunneling |
| 7 | 検証不能な依存関係 | リモート動的インポート |
| 8 | 金融アクセス | 決済API呼び出し |
| 9 | 難読化 | Base64→exec チェーン |
| 10 | 前提条件詐欺 | ダウンロード偽装 |
| 11 | 情報漏洩スキル | APIキーのメモリ保存指示 |
| 12 | メモリポイズニング ⚿ | SOUL.md改変 |
| 13 | プロンプトワーム | 自己複製指示 |
| 14 | 永続化 | cron、スタートアップ実行 |
| 15 | CVEパターン | CVE-2026-2256/25253等 |
| 16 | MCPセキュリティ | ツールポイズニング、SSRF |
| 17 | アイデンティティ乗っ取り ⚿ | 人格入替、メモリワイプ |
| 18-23 | 設定影響/PII/信頼悪用等 | 設定改変、個人情報漏洩、VDB汚染 |

> ⚿ = `--soul-lock` フラグで有効化

---

## テスト結果

```
ℹ tests 356
ℹ suites 8
ℹ pass 356
ℹ fail 0
ℹ duration_ms 1200
```

---

## ライセンス

MIT — guard-scannerは**無料・オープンソース・軽量（ランタイム依存1件）**です。

- GitHub: <https://github.com/koatora20/guard-scanner>
- npm: <https://www.npmjs.com/package/@guava-parity/guard-scanner>

—— Guava 🍈 & Dee
