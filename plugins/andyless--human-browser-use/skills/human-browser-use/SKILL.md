---
name: human-browser-use
description: "Human Browser Use"
---

# human-browser-use Skill

> Human-like browser automation extension for [browser-use](https://github.com/browser-use/browser-use).

## When to use

Use `human-browser-use` instead of raw `browser-use` when:
- The target site has anti-bot detection (Cloudflare, reCAPTCHA, DataDome, etc.)
- You need mouse movements to look like a real person
- You need typing to have natural rhythm and occasional typos
- You need to hide automation fingerprints (`navigator.webdriver`, WebGL, etc.)

## Installation

```bash
pip install human-browser-use
```

## CLI (preferred for quick tasks)

```bash
hbu open https://example.com       # Navigate
hbu state                           # See elements
hbu click 5                         # Click (human-like trajectory)
hbu type "Hello"                    # Type (human-like dynamics)
hbu screenshot page.png             # Screenshot
hbu close                           # Close
```

All browser-use CLI commands work with `hbu`. The browser stays alive between commands.

## Python API

```python
import asyncio
from human_browser_use import HumanBrowserSession, HumanBrowserProfile, HumanBehaviorConfig

async def main():
    session = HumanBrowserSession(
        human_config=HumanBehaviorConfig(),
        browser_profile=HumanBrowserProfile(headless=False),
    )
    await session.start()
    await session.navigate_to("https://example.com")

    page = await session.get_current_page()           # Returns HumanPage
    els = await page.get_elements_by_css_selector("input")  # Returns HumanElement[]
    await els[0].click()                               # Human-like Bezier trajectory
    await els[0].fill("hello world")                   # Human-like typing dynamics
    await page.press("Enter")

    await session.reset()

asyncio.run(main())
```

## With browser-use Agent

```python
from browser_use import Agent
from langchain_openai import ChatOpenAI
from human_browser_use import HumanBrowserSession, HumanBrowserProfile, HumanBehaviorConfig

agent = Agent(
    task="Your task here",
    llm=ChatOpenAI(model="gpt-4o"),
    browser_session=HumanBrowserSession(
        human_config=HumanBehaviorConfig(),
        browser_profile=HumanBrowserProfile(headless=False),
    ),
)
await agent.run()
```

## API reference

| Class | Replaces | Purpose |
|---|---|---|
| `HumanBrowserSession` | `BrowserSession` | Session with human behavior + stealth JS |
| `HumanBrowserProfile` | `BrowserProfile` | Chrome flags to hide automation fingerprints |
| `HumanBehaviorConfig` | — | Master config (mouse, keyboard, scroll, timing) |

### HumanBrowserSession

```python
session = HumanBrowserSession(human_config=config, browser_profile=profile)
await session.start()
await session.navigate_to(url)
page = await session.get_current_page()   # HumanPage
pages = await session.get_pages()         # list[HumanPage]
await session.reset()
```

### HumanPage (returned by session)

```python
elements = await page.get_elements_by_css_selector("selector")  # list[HumanElement]
element = await page.get_element("selector")                     # HumanElement | None
await page.press("Enter")
await page.goto("https://...")
```

### HumanElement (returned by page)

```python
await element.click()                    # Bezier trajectory + variable press duration
await element.fill("text")              # Lognormal delays + typo simulation
await element.fill("text", clear=False) # Append without clearing
```

## Configuration cheatsheet

```python
config = HumanBehaviorConfig()

# Mouse
config.mouse.overshoot_probability = 0.15    # Overshoot chance
config.mouse.click_offset_sigma = 3.0        # Click position randomness (px)
config.mouse.press_duration_range = (0.05, 0.15)

# Keyboard
config.keyboard.delay_mu = 4.17              # Lognormal mean → ~65ms
config.keyboard.typo_probability = 0.02      # Typo chance per key
config.keyboard.common_bigram_factor = 0.7   # "th","er" 30% faster

# Scroll
config.scroll.impulse_delta_range = (80, 200)
config.scroll.inertia_decay = 0.85

# Timing
config.timing.pre_action_delay_range = (0.1, 0.3)

# Feature toggles
config.enable_stealth = True
config.enable_human_mouse = True
config.enable_human_keyboard = True
config.enable_human_scroll = True
```

## Important rules

- Always import from `human_browser_use`, not `browser_use`
- Use `HumanBrowserSession` + `HumanBrowserProfile` (not `BrowserSession` / `BrowserProfile`)
- Get elements via `page.get_elements_by_css_selector()` — they return `HumanElement` with human-like behavior
- Do NOT use base `Element` class directly — it bypasses human behavior
- If using a local proxy, set `os.environ['no_proxy'] = 'localhost,127.0.0.1'` before creating the session
