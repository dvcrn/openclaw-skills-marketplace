# GuavaSuite — STATUS

## ステータス: 🔨 W6 ClawHub公開準備中

## ファネル上の位置: ④ REVENUE（$GUAVAトークンゲート）

## 概要
でぃー＆グアバ固有のAIアイデンティティ保護・管理プラットフォーム。
$GUAVA保有量で認証。超越者メンバーには$GUAVAを配布。

## 認証モデル
- **超越者**（¥100,000/月）→ $GUAVA配布 → Suite利用可
- **Founders Pass**（1 POL / 10個限定）→ 90M $GUAVA付与 → Suite利用可
- **一般** → QuickSwapで$GUAVA購入 → 閾値以上保有で利用可

## 含む機能
- ✅ SuiteGate middleware（fail-closed gate + grace period）
- ✅ License API（challenge/verify/health endpoints）
- ✅ TokenBalanceChecker（Polygon RPC、ゼロ依存）
- ✅ SignatureVerifier（EIP-712、ethers optional）
- ✅ SuiteBridge（SuiteGate → guard-scanner mode switch）
- ✅ CLI Activation（activate.js — 1コマンドアクティベーション）
- ✅ Setup Script（setup.sh — 依存インストール + 配置）
- ✅ plugin.ts JWT検出（GuavaSuite JWT → auto strict mode）
- ✅ Zettel Memory Integration（zettel-memory-integrationから吸収）
- ✅ SoulRegistry V2（contracts/SoulRegistryV2.sol）

## テストカバレッジ

- Unit Tests: 21（suite-integration.test.js）— ✅ ALL PASS
- E2E Tests: 6（e2e-activation.test.js）— ✅ ALL PASS
- **合計: 27テスト、0失敗**

## 技術進捗
- [x] W1 Contracts（Hardhat 5本 PASS）
- [x] W2 License API（28本 PASS）
- [x] W3 Runtime Gate GREEN（SuiteGate middleware）
- [x] W3 REFACTOR（CLI + クラス分離）
- [x] W4 E2E（27テスト全パス）
- [x] W5 コード分離（OSS/Private境界確定）
- [ ] W6 ClawHub公開（GitHub Private配布）

## 吸収元
- `guava-guard-onchain` → SoulRegistry統合
- `founders-pass` → NFTライセンス統合
- `guava-protocol` → tanhスコアリング統合

## 次のアクション
→ GitHub Private リポ作成 → push → 配布テスト
