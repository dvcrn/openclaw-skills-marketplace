# General Tips: Bypassing Anti-Bot Detection

Many websites employ fingerprinting, behavioral analysis, and rate limiting to block automated traffic. The techniques below significantly improve success rates on AgentGo cloud browsers.

## Mobile Device Emulation

Emulating a real mobile device (e.g. iPhone) is one of the most effective anti-detection strategies. Mobile fingerprints are simpler and harder for sites to distinguish from real users.

```typescript
const context = await browser.newContext({
  userAgent:
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) " +
    "AppleWebKit/605.1.15 (KHTML, like Gecko) " +
    "Version/17.4 Mobile/15E148 Safari/604.1",
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3,
  isMobile: true,
  hasTouch: true,
});
```

Key parameters:
- **User-Agent** — match a recent iOS version (update periodically).
- **Viewport** — use a real device resolution (390x844 = iPhone 13/14).
- **deviceScaleFactor** — `3` for Retina displays.
- **isMobile / hasTouch** — must both be `true` for consistent fingerprint.

## Human-Like Typing

Use `keyboard.type()` with a random per-character delay instead of `page.fill()`. Many sites detect instant input and silently discard it.

```typescript
// Simulates human typing rhythm (80-150ms per character)
async function humanType(page: Page, selector: string, text: string) {
  await page.click(selector);
  for (const char of text) {
    await page.keyboard.type(char, {
      delay: 80 + Math.floor(Math.random() * 70),
    });
  }
}
```

## Simulated Scrolling and Reading

Scroll the page before interacting with elements. Sites track viewport engagement and flag sessions with zero scroll activity.

```typescript
async function simulateReading(page: Page, scrolls = 2) {
  for (let i = 0; i < scrolls; i++) {
    await page.mouse.wheel(0, 300 + Math.floor(Math.random() * 200));
    await page.waitForTimeout(1000 + Math.floor(Math.random() * 1000));
  }
}
```

## Cookie-Based Authentication

For sites where you already have valid session credentials, inject cookies directly instead of automating the login flow. This avoids triggering login-page anti-bot checks entirely.

```typescript
await context.addCookies([
  { name: "session_token", value: "...", domain: ".example.com", path: "/" },
  { name: "csrf_token", value: "...", domain: ".example.com", path: "/" },
]);
```

## Navigate Naturally

- **Do not** jump directly to deep links or API-style URLs. Navigate to the main page first, then click through to the target.
- Wait for `networkidle` or key selectors rather than fixed timeouts.
- Add small random delays between actions (500-2000ms).

## Post-Action Verification

After performing a critical action (form submit, post, etc.), reload the page and confirm the result is visible:

```typescript
await page.reload({ waitUntil: "networkidle" });
const success = await page.$("text=Your post was published");
if (!success) throw new Error("Action verification failed");
```

## Always Close Sessions

Cloud browsers consume credits while open. Always wrap work in `try/finally`:

```typescript
const browser = await connectAgentGo();
try {
  // ... work ...
} finally {
  await browser.close();
}
```
