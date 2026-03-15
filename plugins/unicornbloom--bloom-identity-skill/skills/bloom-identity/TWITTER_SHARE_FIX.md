# Twitter Share Fix - 顯示卡片圖片

## 問題
當前分享到 X/Twitter 時，只顯示連結文字，沒有卡片圖片預覽。

**原因**：`/api/og/agent/{agentUserId}` endpoint 不存在（返回 404）

---

## 解決方案

### Step 1: 創建 Agent OG Image Generator

在 frontend 創建新文件：

**路徑**：`src/app/api/og/agent/[agentUserId]/route.tsx`

```tsx
import { ImageResponse } from 'next/og';
import { NextRequest } from 'next/server';

export const runtime = 'edge';

// Personality config
const PERSONALITY_CONFIG: Record<string, { gradient: string; emoji: string }> = {
  'visionary': {
    gradient: 'linear-gradient(135deg, #9333ea, #7c3aed)',
    emoji: '💜',
  },
  'explorer': {
    gradient: 'linear-gradient(135deg, #10b981, #059669)',
    emoji: '💚',
  },
  'cultivator': {
    gradient: 'linear-gradient(135deg, #06b6d4, #0891b2)',
    emoji: '🩵',
  },
  'optimizer': {
    gradient: 'linear-gradient(135deg, #f97316, #ea580c)',
    emoji: '🧡',
  },
  'innovator': {
    gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)',
    emoji: '💙',
  },
};

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ agentUserId: string }> }
) {
  const { agentUserId } = await params;

  try {
    // Fetch agent data from backend
    const BACKEND_API_URL = process.env.BACKEND_API_URL || 'https://api.bloomprotocol.ai';
    const response = await fetch(`${BACKEND_API_URL}/x402/agent/${agentUserId}`, {
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error('Failed to fetch agent data');
    }

    const result = await response.json();
    const agentData = result.data;

    // Extract data
    const personalityType = agentData.identityData.personalityType; // e.g., "The Visionary"
    const tagline = agentData.identityData.tagline;
    const mainCategories = agentData.identityData.mainCategories || [];
    const dimensions = agentData.identityData.dimensions;

    // Get personality key
    const personalityKey = personalityType.toLowerCase().replace('the ', '');
    const config = PERSONALITY_CONFIG[personalityKey] || PERSONALITY_CONFIG.visionary;

    // Format member since
    const memberSince = new Date(agentData.createdAt).toLocaleDateString('en-US', {
      month: 'long',
      year: 'numeric'
    });

    const cardId = `A-${agentData.agentUserId.toString().padStart(6, '0')}`;

    return new ImageResponse(
      (
        <div
          style={{
            width: '1200',
            height: '630',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%)',
          }}
        >
          {/* Card with 3D effect */}
          <div
            style={{
              width: '500',
              display: 'flex',
              flexDirection: 'column',
              padding: '40px',
              borderRadius: '32px',
              background: 'linear-gradient(145deg, rgba(255,255,255,0.98) 0%, rgba(240,235,255,0.95) 50%, rgba(255,245,250,0.98) 100%)',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            }}
          >
            {/* Header */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '20px',
              }}
            >
              <div
                style={{
                  fontSize: '12px',
                  fontWeight: 'bold',
                  color: '#9ca3af',
                  letterSpacing: '0.2em',
                }}
              >
                BLOOM IDENTITY
              </div>
              <div
                style={{
                  fontSize: '12px',
                  color: '#9ca3af',
                  fontFamily: 'monospace',
                }}
              >
                {cardId}
              </div>
            </div>

            {/* Divider */}
            <div
              style={{
                width: '100%',
                height: '1px',
                background: 'linear-gradient(90deg, #e5e7eb, #d1d5db, #e5e7eb)',
                marginBottom: '30px',
              }}
            />

            {/* Emoji Icon */}
            <div
              style={{
                fontSize: '72px',
                marginBottom: '16px',
                textAlign: 'center',
                display: 'flex',
                justifyContent: 'center',
              }}
            >
              {config.emoji}
            </div>

            {/* Personality Type */}
            <div
              style={{
                fontSize: '36px',
                fontWeight: 'bold',
                color: '#1f2937',
                marginBottom: '12px',
                textAlign: 'center',
                display: 'flex',
                justifyContent: 'center',
              }}
            >
              {personalityType}
            </div>

            {/* Tagline */}
            <div
              style={{
                fontSize: '18px',
                color: '#6b7280',
                marginBottom: '24px',
                textAlign: 'center',
                display: 'flex',
                justifyContent: 'center',
                fontStyle: 'italic',
              }}
            >
              "{tagline}"
            </div>

            {/* 2x2 Dimensions */}
            <div
              style={{
                display: 'flex',
                gap: '16px',
                marginBottom: '24px',
                justifyContent: 'center',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  padding: '12px 20px',
                  background: 'rgba(147, 51, 234, 0.1)',
                  borderRadius: '12px',
                }}
              >
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#7c3aed' }}>
                  {dimensions.conviction}
                </div>
                <div style={{ fontSize: '12px', color: '#6b7280' }}>Conviction</div>
              </div>
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  padding: '12px 20px',
                  background: 'rgba(59, 130, 246, 0.1)',
                  borderRadius: '12px',
                }}
              >
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3b82f6' }}>
                  {dimensions.intuition}
                </div>
                <div style={{ fontSize: '12px', color: '#6b7280' }}>Intuition</div>
              </div>
            </div>

            {/* Categories */}
            {mainCategories.length > 0 && (
              <div
                style={{
                  display: 'flex',
                  gap: '10px',
                  marginBottom: '20px',
                  flexWrap: 'wrap',
                  justifyContent: 'center',
                }}
              >
                {mainCategories.slice(0, 3).map((cat: string, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      padding: '8px 16px',
                      borderRadius: '999px',
                      background: 'rgba(243, 244, 246, 0.9)',
                      fontSize: '14px',
                      color: '#374151',
                      fontWeight: '500',
                    }}
                  >
                    {cat}
                  </div>
                ))}
              </div>
            )}

            {/* Member since */}
            <div
              style={{
                fontSize: '13px',
                color: '#9ca3af',
                marginBottom: '20px',
                textAlign: 'center',
                display: 'flex',
                justifyContent: 'center',
              }}
            >
              Member since {memberSince}
            </div>

            {/* Divider */}
            <div
              style={{
                width: '100%',
                height: '1px',
                background: 'linear-gradient(90deg, transparent, rgba(209,213,219,0.5), transparent)',
                marginBottom: '16px',
              }}
            />

            {/* Branding */}
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
              }}
            >
              <div
                style={{
                  fontSize: '16px',
                  color: '#4b5563',
                  fontWeight: '600',
                  letterSpacing: '0.02em',
                }}
              >
                bloomprotocol.ai
              </div>
              <div
                style={{
                  fontSize: '12px',
                  color: '#9ca3af',
                  marginTop: '4px',
                }}
              >
                Discover. Support. Bloom.
              </div>
            </div>
          </div>
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );
  } catch (error) {
    console.error('Failed to generate OG image:', error);

    // Fallback OG image
    return new ImageResponse(
      (
        <div
          style={{
            width: '1200',
            height: '630',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #9333ea, #7c3aed)',
            color: 'white',
            fontSize: '48px',
            fontWeight: 'bold',
          }}
        >
          Bloom Identity Card
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );
  }
}
```

---

### Step 2: 測試 OG Image

**本地測試**：
```bash
# 1. 啟動 dev server
cd bloom-protocol-fe
npm run dev

# 2. 訪問 OG image URL
# http://localhost:3000/api/og/agent/123
```

**部署後測試**：
```
https://preflight.bloomprotocol.ai/api/og/agent/123
```

應該會看到一個 1200x630 的卡片圖片。

---

### Step 3: 驗證 Twitter Card

使用 **Twitter Card Validator**：
1. 訪問：https://cards-dev.twitter.com/validator
2. 輸入你的 agent URL：`https://preflight.bloomprotocol.ai/agents/123`
3. 檢查預覽：
   - ✅ 應該顯示卡片圖片
   - ✅ 標題：`{personalityType} | Bloom Identity`
   - ✅ 描述：tagline

---

## 進階：優化分享體驗

### Option 1: 在 Share 按鈕中包含預設文案

```tsx
const handleShareOnX = () => {
  if (!agentData) return;

  const shareText = `I just discovered my Bloom Identity: ${agentData.personalityType}! 🌸

"${agentData.tagline}"

Top categories: ${agentData.mainCategories.slice(0, 2).join(', ')}

Check out my personalized skill recommendations 👇`;

  const shareUrl = window.location.href;

  const twitterUrl = `https://twitter.com/intent/tweet?${new URLSearchParams({
    text: shareText,
    url: shareUrl,
  })}`;

  window.open(twitterUrl, '_blank', 'width=550,height=420');
};
```

**結果**：
- ✅ 包含個性化文案
- ✅ 包含 tagline
- ✅ 包含 top categories
- ✅ OG image 會自動附加（Twitter 會抓取）

---

### Option 2: 提供複製連結功能

除了 "Share on X" 按鈕，加上 "Copy Link" 按鈕：

```tsx
const [copied, setCopied] = useState(false);

const handleCopyLink = () => {
  navigator.clipboard.writeText(window.location.href);
  setCopied(true);
  setTimeout(() => setCopied(false), 2000);
};

// 在 UI 中：
<button onClick={handleCopyLink}>
  {copied ? '✅ Copied!' : '📋 Copy Link'}
</button>
```

---

## 部署 Checklist

- [ ] 創建 `/api/og/agent/[agentUserId]/route.tsx`
- [ ] 確認 `BACKEND_API_URL` 環境變數正確
- [ ] 本地測試 OG image generation
- [ ] Deploy 到 Railway/Vercel
- [ ] 使用 Twitter Card Validator 驗證
- [ ] 測試實際分享到 Twitter
- [ ] （Optional）優化分享文案
- [ ] （Optional）加上 Copy Link 功能

---

## 注意事項

1. **Edge Runtime**：OG image generation 使用 Edge runtime，確保只使用支援的 API
2. **Cache**：Twitter 會快取 OG image，測試時可能需要加上 `?v=2` 等參數強制重新抓取
3. **Fallback**：如果 backend API 失敗，提供 fallback OG image
4. **Size**：圖片大小固定為 1200x630（Twitter 推薦尺寸）

---

## 效果預期

**分享到 Twitter 後，會顯示**：
```
[用戶的分享文案]

┌─────────────────────────────────┐
│  💜                              │
│  The Visionary                   │
│  "See beyond the hype"           │
│                                  │
│  🎯 50    💡 75                  │
│  Conviction  Intuition           │
│                                  │
│  🏷️ Crypto · AI Tools            │
│                                  │
│  bloomprotocol.ai                │
└─────────────────────────────────┘

bloomprotocol.ai/agents/123
```

這樣用戶的朋友在 Twitter 看到分享時，會立即看到漂亮的卡片圖片，而不只是純文字連結！
