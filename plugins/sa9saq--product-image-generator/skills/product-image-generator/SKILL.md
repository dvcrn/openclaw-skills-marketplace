---
name: product-image-generator
description: "Generate product images for Coconala/Fiverr by researching competitor designs and creating optimized thumbnails using Nano Banana Pro."
---

# 商品画像生成スキル

ココナラ・Fiverr等の商品サムネイル画像を生成するスキル。競合分析 + Nano Banana Pro で売れる画像を作成。

## 機能概要

```
商品画像生成フロー:
├── 1. 競合リサーチ（cloudflare-browser）
│   └── 成功している出品者の画像を収集・分析
├── 2. デザインパターン抽出
│   └── 色、レイアウト、テキスト配置を分析
├── 3. プロンプト生成
│   └── 分析結果を元に最適なプロンプト作成
└── 4. 画像生成（Nano Banana Pro）
    └── 高品質なサムネイル画像を生成
```

---

## 競合リサーチ方法

### ココナラの成功画像を分析

```
リサーチ対象:
├── カテゴリ内ランキング上位の出品
├── レビュー数が多い出品
├── お気に入り数が多い出品
└── PRO認定出品者

分析ポイント:
├── 背景色・グラデーション
├── テキストの配置・フォント
├── アイコン・イラストの使い方
├── 人物の有無
├── 色の組み合わせ
└── 情報の優先順位
```

### ブラウザ操作での収集

```javascript
// 競合画像収集フロー
1. ココナラでカテゴリ検索
2. 「おすすめ順」「ランキング」でソート
3. 上位20件のサムネイル画像URLを取得
4. 画像をダウンロード or スクリーンショット
5. 共通パターンを分析
```

---

## カテゴリ別デザインパターン

### IT・プログラミング系
```
成功パターン:
├── 背景: ダークブルー、ネイビー、黒
├── アクセント: グリーン、シアン（テック感）
├── アイコン: 歯車、コード、チャート
├── テキスト: 白、大きめ、シンプル
└── 雰囲気: プロフェッショナル、信頼感

プロンプト例:
"Professional tech service thumbnail, dark navy blue gradient background,
 minimalist code icon or gear symbol in cyan accent color,
 clean modern design, corporate professional look,
 space for Japanese text at bottom.
 1280x1280 pixels, high contrast, business style."
```

### ライティング・翻訳系
```
成功パターン:
├── 背景: 白、ベージュ、パステル
├── アクセント: オレンジ、イエロー（温かみ）
├── アイコン: ペン、本、吹き出し
├── テキスト: 黒、読みやすい
└── 雰囲気: 親しみやすい、知的

プロンプト例:
"Warm and friendly writing service thumbnail, soft beige or cream background,
 cute illustration of pen and paper or open book,
 warm orange and yellow accent colors,
 inviting and approachable design,
 space for Japanese text.
 1280x1280 pixels, soft lighting, friendly aesthetic."
```

### デザイン・イラスト系
```
成功パターン:
├── 背景: カラフル、グラデーション
├── 作品サンプル: 実際の制作物を見せる
├── スタイル: 自分の作風をアピール
└── 雰囲気: クリエイティブ、個性的

プロンプト例:
"Creative design portfolio thumbnail, vibrant gradient background pink to purple,
 showcase of various design elements floating (icons, shapes, illustrations),
 artistic and creative vibe,
 modern and trendy aesthetic.
 1280x1280 pixels, colorful, eye-catching composition."
```

### ビジネス・コンサル系
```
成功パターン:
├── 背景: 白、グレー、ネイビー
├── アイコン: チャート、矢印、ビルディング
├── 人物: スーツ姿のシルエット（あれば）
└── 雰囲気: 信頼感、成功イメージ

プロンプト例:
"Professional business consulting thumbnail, clean white or light gray background,
 subtle graph showing upward trend, success arrow icon,
 corporate blue accent color,
 trustworthy and reliable business aesthetic.
 1280x1280 pixels, minimal, professional."
```

---

## Nano Banana Pro 連携

### 画像生成リクエスト

```bash
# 商品サムネイル生成
~/.claude/skills/nano-banana-pro/generate.py \
  --prompt "[生成したプロンプト]" \
  --output "/mnt/e/SNS-Output/Images/Coconala/[商品名]-thumbnail.png" \
  --aspect "1:1" \
  --resolution "2K"
```

### ココナラ推奨サイズ
- サムネイル: **1280x1280px**（正方形）
- ギャラリー画像: **1280x720px**（16:9）

---

## 売れるサムネイルの法則

### Must Have（必須要素）
```
✅ 一目で何のサービスかわかる
✅ テキストは大きく読みやすく
✅ 背景とテキストのコントラスト
✅ カテゴリに合った色使い
✅ プロフェッショナルな印象
```

### Nice to Have（あると良い）
```
✅ 数字を入れる（「3日で納品」「5,000円〜」）
✅ 実績アピール（「100件以上の実績」）
✅ 差別化ポイント（「24時間対応」「修正無制限」）
✅ ターゲットを明示（「初心者向け」「法人様向け」）
```

### NG（避けるべき）
```
❌ 文字が小さすぎる
❌ 情報詰め込みすぎ
❌ 背景と文字が同系色
❌ 素人っぽいデザイン
❌ 他サービスの画像を無断使用
```

---

## テキスト配置パターン

### パターン1: 上部メイン
```
┌─────────────────────┐
│    【メインタイトル】  │
│                      │
│     [アイコン/画像]   │
│                      │
│    サブテキスト       │
└─────────────────────┘
```

### パターン2: 中央集中
```
┌─────────────────────┐
│                      │
│    【メインタイトル】  │
│     [アイコン]        │
│    サブテキスト       │
│                      │
└─────────────────────┘
```

### パターン3: 左右分割
```
┌──────────┬──────────┐
│          │          │
│ [画像/   │ テキスト  │
│  アイコン]│ エリア   │
│          │          │
└──────────┴──────────┘
```

---

## 自動生成フロー

```
【商品カテゴリ入力】
     │
     ▼
  競合リサーチ（ブラウザ）
     │
     ▼
  成功パターン分析
     │
     ▼
  プロンプト生成
     │
     ▼
  Nano Banana Pro で画像生成
     │
     ▼
  複数候補（3-5枚）を出力
     │
     ▼
  ユーザーが選択 or 調整依頼
```

---

## 使用例

### GAS自動化サービスの画像生成

```
入力: カテゴリ=IT・プログラミング, 商品=GASスプレッドシート自動化

競合分析結果:
- 背景: ダークブルー系が多い
- アイコン: スプレッドシート、歯車
- テキスト: 白、太字

生成プロンプト:
"Professional Google Sheets automation service thumbnail,
 dark navy blue gradient background with subtle grid pattern,
 minimalist spreadsheet icon with gear/automation symbol,
 glowing cyan accent highlights,
 clean modern tech aesthetic,
 space at bottom for white Japanese text banner.
 The Japanese text 「GAS自動化」appears at the bottom
 in bold white sans-serif font with dark semi-transparent banner.
 1280x1280 pixels, high contrast, corporate professional look."
```

---

## 著作権・利用規約

- 競合画像は参考のみ、そのまま使用しない
- 生成画像は自分のオリジナルとして使用可能
- 他者の著作物（ロゴ、キャラクター等）は含めない
- ストックフォト風の人物は注意（権利関係）
