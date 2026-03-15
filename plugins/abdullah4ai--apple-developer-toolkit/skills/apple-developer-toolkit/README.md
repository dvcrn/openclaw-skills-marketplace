# Apple Developer Toolkit

All-in-one Apple developer CLI: documentation search, WWDC videos, App Store Connect management, autonomous app builder, and lifecycle hooks with Telegram notifications. Ships as a **single unified binary** (`appledev`).

## Install

```bash
brew install Abdullah4AI/tap/appledev
```

```bash
clawhub install apple-developer-toolkit
```

## Quick Start

```bash
appledev build                    # Build an iOS app from a description
appledev store apps               # List your App Store Connect apps
appledev hooks init               # Set up lifecycle hooks
appledev notify telegram --message "Hello"
node cli.js search "NavigationStack"
```

## What's Inside

| Tool | Command | Description |
|------|---------|-------------|
| **Docs** | `node cli.js` | Apple docs + 1,267 WWDC sessions (2014-2025) |
| **Store** | `appledev store` | 120+ App Store Connect commands |
| **Builder** | `appledev build` | AI-powered iOS/macOS/watchOS/tvOS/visionOS app generation |
| **Hooks** | `appledev hooks` | 31 lifecycle events with Telegram/Slack notifications |

## Lifecycle Hooks

Hooks fire automatically when you build, upload, submit, or release. Get notified on Telegram, auto-distribute to TestFlight, git-tag releases, and chain operations into pipelines.

### Setup

```bash
appledev hooks init --template indie
```

### 31 Events

| Category | Events |
|----------|--------|
| **Build** | `build.start`, `build.compile.success/failure`, `build.fix.start/done`, `build.run.success`, `build.done` |
| **Store** | `store.upload.start/done/failure`, `store.processing.done`, `store.testflight.distribute`, `store.submit.start/done/failure`, `store.review.approved/rejected`, `store.release.done`, `store.validate.pass/fail` |
| **Pipeline** | `pipeline.start`, `pipeline.step.done`, `pipeline.done`, `pipeline.failure` |

### Config Example

```yaml
version: 1
notifiers:
  telegram:
    enabled: true
    bot_token_keychain: "my-bot-token"
    chat_id: "123456"

hooks:
  build.done:
    - name: notify-build
      notify: telegram
      template: "{{if eq .STATUS \"success\"}}✅{{else}}❌{{end}} {{.APP_NAME}} build {{.STATUS}}"

  store.review.approved:
    - name: tag-release
      run: "git tag v{{.VERSION}} && git push origin v{{.VERSION}}"
    - name: notify
      notify: telegram
      template: "🎉 {{.APP_NAME}} v{{.VERSION}} approved"
```

### Templates

```bash
appledev hooks init --template indie    # Telegram + auto TestFlight
appledev hooks init --template team     # Slack + Telegram + git tagging
appledev hooks init --template ci       # Logging + test running (CI/CD)
```

### Hook Commands

```bash
appledev hooks list [--event "store.*"]
appledev hooks fire <event> [KEY=VALUE...]
appledev hooks fire --dry-run build.done STATUS=success
appledev hooks validate
appledev notify telegram --message "Deploy done"
appledev notify slack --webhook $URL --message "Build ready"
```

### Config Locations

- **Global**: `~/.appledev/hooks.yaml` (applies to all projects)
- **Project**: `.appledev/hooks.yaml` (extends/overrides global)

## Documentation Search

Search Apple docs and 1,267 WWDC sessions locally. No API key needed.

```bash
node cli.js search "NavigationStack"
node cli.js symbols "UIView"
node cli.js doc "/documentation/swiftui/view"
node cli.js wwdc-search "concurrency"
node cli.js wwdc-year 2025
node cli.js wwdc-topic "swiftui-ui-frameworks"
```

## App Store Connect

120+ commands covering the entire App Store Connect API.

```bash
# Auth
appledev store auth login --name "MyApp" --key-id "KEY" --issuer-id "ISS" --private-key ./Key.p8

# TestFlight
appledev store publish testflight --app "APP_ID" --ipa app.ipa --group "Beta" --wait

# App Store submission
appledev store publish appstore --app "APP_ID" --ipa app.ipa --submit --confirm --wait

# Validation
appledev store validate --app "APP_ID" --version-id "VER_ID" --strict

# Analytics
appledev store insights weekly --app "APP_ID"

# Workflow automation
appledev store workflow run beta BUILD_ID:123 GROUP_ID:abc
```

| Category | Commands |
|----------|----------|
| Getting Started | auth, doctor, init, docs |
| Apps | apps, app-setup, app-tags, app-info, versions, localizations, screenshots, video-previews |
| TestFlight | testflight, builds, sandbox, feedback, crashes |
| Review & Release | review, reviews, submit, validate, publish, status |
| Signing | signing, bundle-ids, certificates, profiles, notarization |
| Monetization | iap, subscriptions, offer-codes, win-back-offers, promoted-purchases, pricing |
| Analytics | analytics, insights, finance, performance |
| Automation | xcode-cloud, webhooks, hooks, notify, workflow, metadata, diff, migrate |

## iOS App Builder

Build complete multi-platform Apple apps from natural language.

```bash
appledev build              # Describe your app and build it
appledev build chat         # Edit interactively
appledev build fix          # Auto-fix compilation errors
appledev build run          # Build and launch in simulator
appledev build open         # Open in Xcode
```

Supports: iOS, iPadOS, macOS, watchOS, tvOS, visionOS

### How It Works

```
describe → analyze → plan → build → fix → run
```

## Reference Files

52 reference files for AI agents:

| Reference | Count | Content |
|-----------|-------|---------|
| `references/ios-rules/` | 38 | iOS development rules |
| `references/swiftui-guides/` | 12 | SwiftUI best practices (Liquid Glass, navigation, state, etc.) |
| `references/app-store-connect.md` | 1 | Complete CLI reference |
| `references/hooks-reference.md` | 1 | All 31 hook events with context variables |

## Requirements

| Feature | Requires |
|---------|----------|
| Documentation search | Node.js 18+ |
| App Store Connect | API key (.p8 file) |
| iOS app builder | Xcode + LLM API key |
| Hooks | Nothing (works out of the box) |

## License

MIT
