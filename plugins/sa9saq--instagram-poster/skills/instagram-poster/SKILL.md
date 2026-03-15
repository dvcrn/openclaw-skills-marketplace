---
name: instagram-poster
description: "Instagram automation via local Puppeteer browser. Posts, Reels, Stories, carousel without Cloudflare dependency."
---

# Instagram Poster（ローカル版）

InstagramブラウザA自動化。Puppeteerでローカル実行、Cloudflare不要。

## 前提条件

```bash
npm install puppeteer
```

## 機能

### 投稿タイプ
- **フィード投稿**: 画像/動画 + キャプション
- **カルーセル**: 複数画像スライド
- **リール**: 短尺動画
- **ストーリー**: 24時間限定コンテンツ

### 自動化機能
- スケジュール投稿
- ハッシュタグ最適化
- キャプション生成
- エンゲージメント分析

## 使用方法

### 基本投稿
```
「Instagramに画像を投稿して」
「[画像URL]をInstagramに投稿、キャプション: [text]」
```

### リール投稿
```
「Instagramリールを投稿
 動画: [video_url]
 キャプション: [text]
 音楽: [optional]」
```

### カルーセル投稿
```
「Instagramカルーセル投稿
 画像1: [url1]
 画像2: [url2]
 画像3: [url3]
 キャプション: [text]」
```

## Puppeteer実装

```javascript
const puppeteer = require('puppeteer');
const fs = require('fs');

async function loginToInstagram(client) {
  await client.executeSequence([
    { type: 'navigate', url: 'https://www.instagram.com' },
    { type: 'waitForSelector', selector: '[name="username"]' },
    { type: 'type', selector: '[name="username"]', text: process.env.INSTAGRAM_USERNAME },
    { type: 'type', selector: '[name="password"]', text: process.env.INSTAGRAM_PASSWORD },
    { type: 'click', selector: '[type="submit"]' },
    { type: 'wait', ms: 5000 },
    { type: 'screenshot' }
  ]);

  // Cookieを保存
  const cookies = await client.getCookies();
  fs.writeFileSync('instagram-cookies.json', JSON.stringify(cookies));
}

async function postToInstagram(client, imagePath, caption) {
  // ファイルアップロードにはPuppeteerのpage.uploadFile()を使用
  const fileInput = await client.page.$('input[type="file"]');

  await client.executeSequence([
    { type: 'click', selector: '[aria-label="New post"]' },
    { type: 'wait', ms: 1000 }
  ]);

  // ファイルアップロード
  await fileInput.uploadFile(imagePath);

  await client.executeSequence([
    { type: 'wait', ms: 2000 },
    { type: 'click', selector: 'button:has-text("Next")' },
    { type: 'wait', ms: 1000 },
    { type: 'click', selector: 'button:has-text("Next")' },
    { type: 'waitForSelector', selector: '[aria-label="Write a caption..."]' },
    { type: 'type', selector: '[aria-label="Write a caption..."]', text: caption },
    { type: 'click', selector: 'button:has-text("Share")' },
    { type: 'wait', ms: 5000 },
    { type: 'screenshot' }
  ]);
}

// 使用例
async function main() {
  const client = await createClient({ headless: true });

  // Cookie復元（あれば）
  if (fs.existsSync('instagram-cookies.json')) {
    const cookies = JSON.parse(fs.readFileSync('instagram-cookies.json'));
    await client.setCookies(cookies);
  } else {
    await loginToInstagram(client);
  }

  await postToInstagram(client, '/path/to/image.jpg', 'キャプション #hashtag');
  await client.close();
}
```

## ハッシュタグ戦略

### 配分（30個まで）
```
人気タグ (100万+): 3-5個
中規模タグ (10万-100万): 10-15個
ニッチタグ (1万-10万): 10-15個
ブランドタグ: 1-2個
```

### カテゴリ別推奨

**テクノロジー**
```
#tech #technology #ai #artificialintelligence #coding #developer
#startup #innovation #futuretech #techlife
```

**ライフスタイル**
```
#lifestyle #dailylife #minimalism #productivity #wellness
#selfcare #mindfulness #healthylifestyle
```

**ビジネス**
```
#entrepreneur #business #success #motivation #hustle
#startup #smallbusiness #businesstips
```

## 最適な投稿時間

| 曜日 | 最適時間 (JST) |
|------|---------------|
| 月 | 11:00, 14:00, 19:00 |
| 火 | 10:00, 14:00, 19:00 |
| 水 | 11:00, 15:00, 19:00 |
| 木 | 10:00, 14:00, 19:00 |
| 金 | 10:00, 14:00, 16:00 |
| 土 | 10:00, 11:00, 15:00 |
| 日 | 10:00, 11:00, 19:00 |

## キャプション構造

```
[フック（最初の1行で注目を引く）]

[本文（価値提供・ストーリー）]

[CTA（行動喚起）]

・
・
・

[ハッシュタグ群]
```

## 注意事項

### レート制限
- 1時間に最大30アクション
- 1日に最大100アクション
- 投稿間隔: 最低30分

### アカウント保護
- 急激なアクティビティ増加を避ける
- 自然なパターンを維持
- 2FAを有効化
