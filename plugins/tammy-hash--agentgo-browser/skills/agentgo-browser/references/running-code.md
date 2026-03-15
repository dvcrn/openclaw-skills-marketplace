# Running Playwright Code on AgentGo

Equivalent of `playwright-cli` commands using `playwright@1.51.0` directly.

## Setup (reuse across examples)

```typescript
import { chromium, Page } from "playwright";

const opts = encodeURIComponent(JSON.stringify({ _apikey: process.env.AGENTGO_API_KEY }));
const browser = await chromium.connect(`wss://app.browsers.live?launch-options=${opts}`);
const page = await browser.newPage();
```

---

## Core

```typescript
// open + goto
await page.goto("https://example.com");

// type into focused element
await page.keyboard.type("search query");

// click by selector
await page.click("button#submit");
await page.click("text=Sign in");

// double click
await page.dblclick(".item");

// fill (clear + type)
await page.fill("input[name=email]", "user@example.com");

// hover
await page.hover(".menu-item");

// select dropdown
await page.selectOption("select#country", "US");

// check / uncheck
await page.check("input[type=checkbox]");
await page.uncheck("input[type=checkbox]");

// resize viewport
await page.setViewportSize({ width: 1920, height: 1080 });

// close page
await page.close();
// close browser (releases AgentGo session)
await browser.close();
```

---

## Navigation

```typescript
await page.goBack();
await page.goForward();
await page.reload();
```

---

## Keyboard

```typescript
await page.keyboard.press("Enter");
await page.keyboard.press("ArrowDown");
await page.keyboard.down("Shift");
await page.keyboard.up("Shift");
```

---

## Mouse

```typescript
await page.mouse.move(150, 300);
await page.mouse.down();
await page.mouse.up();
await page.mouse.wheel(0, 100);

// drag and drop
await page.dragAndDrop(".source", ".target");
```

---

## Screenshot & PDF

```typescript
// full page screenshot → Buffer
const buf = await page.screenshot({ fullPage: true });

// save to file
await page.screenshot({ path: "page.png" });

// element screenshot
const el = await page.$(".chart");
await el?.screenshot({ path: "chart.png" });

// PDF (Chromium only)
await page.pdf({ path: "page.pdf", format: "A4" });
```

---

## Tabs

```typescript
const context = browser.contexts()[0];

// list pages
const pages = context.pages();

// new tab
const newPage = await context.newPage();
await newPage.goto("https://example.com");

// close a tab
await pages[1].close();

// switch — just use the page reference directly
await pages[0].bringToFront();
```

---

## Storage

```typescript
// save full storage state (cookies + localStorage)
await context.storageState({ path: "auth.json" });

// load on next session
const context2 = await browser.newContext({ storageState: "auth.json" });

// cookies
const cookies = await context.cookies();
await context.addCookies([{ name: "session", value: "abc", domain: "example.com", path: "/" }]);
await context.clearCookies();

// localStorage via evaluate
await page.evaluate(() => localStorage.setItem("theme", "dark"));
const theme = await page.evaluate(() => localStorage.getItem("theme"));
await page.evaluate(() => localStorage.clear());
```

---

## Network mocking

```typescript
// mock a route
await page.route("**/*.jpg", route => route.fulfill({ status: 404 }));
await page.route("https://api.example.com/**", route =>
  route.fulfill({ body: JSON.stringify({ mock: true }), contentType: "application/json" })
);

// remove mock
await page.unroute("**/*.jpg");
```

---

## DevTools

```typescript
// collect console messages
const logs: string[] = [];
page.on("console", msg => logs.push(`[${msg.type()}] ${msg.text()}`));

// collect network requests
const requests: string[] = [];
page.on("request", req => requests.push(req.url()));

// tracing
await context.tracing.start({ screenshots: true, snapshots: true });
// ... actions ...
await context.tracing.stop({ path: "trace.zip" });

// video — configure on context creation
const ctxWithVideo = await browser.newContext({
  recordVideo: { dir: "videos/", size: { width: 1280, height: 720 } },
});
const videoPage = await ctxWithVideo.newPage();
// ... actions ...
await ctxWithVideo.close(); // video saved on close
```

---

## Dialogs

```typescript
// accept
page.once("dialog", dialog => dialog.accept("confirmation text"));

// dismiss
page.once("dialog", dialog => dialog.dismiss());
```

---

## Evaluate JS

```typescript
// on page
const title = await page.evaluate(() => document.title);

// on element
const text = await page.$eval("h1", el => el.textContent);

// multiple elements
const links = await page.$$eval("a", els => els.map(a => a.href));
```

---

## Sessions (named browsers)

```typescript
// open two independent browsers on AgentGo
const browserA = await chromium.connect(serverUrl);
const browserB = await chromium.connect(serverUrl);

const pageA = await browserA.newPage();
const pageB = await browserB.newPage();

await Promise.all([
  pageA.goto("https://site-a.com"),
  pageB.goto("https://site-b.com"),
]);

await browserA.close();
await browserB.close();
```
