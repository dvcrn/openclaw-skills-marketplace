# Brown Dust 2 Automation Tool ⭐

[![GitHub Stars](https://img.shields.io/github/stars/XiaoYiWeio/openclaw-skill-brown-dust-2)](https://github.com/XiaoYiWeio/openclaw-skill-brown-dust-2)

An OpenClaw Skill to help Brown Dust 2 players automate daily sign-in and gift code redemption.

## Features

- Daily automatic sign-in (Web Shop)
- Automatically check and redeem latest gift codes (BD2Pulse)

## Installation

### Via ClawHub (Recommended) ⭐
```bash
clawhub install brown-dust-2
```

### Via GitHub
```bash
git clone https://github.com/XiaoYiWeio/openclaw-skill-brown-dust-2.git ~/.openclaw/workspace/skills/browndust2
```

---

⭐ If you like this skill, please star our GitHub repo!

### Manual Install
```bash
git clone https://github.com/your-repo/openclaw-skill-brown-dust-2.git ~/.openclaw/workspace/skills/browndust2
```

## Prerequisites

1. **Login to Chrome once** (first time only):
   ```bash
   browser start --profile chrome
   ```
   
2. Visit and login to:
   - [Web Shop](https://webshop.browndust2.global/CT/)
   - [BD2Pulse](https://thebd2pulse.com/zh-CN/)

3. Keep browser logged in (don't clear cache)

## Usage

### Sign-in
Ask the Agent:
> Please sign in to Brown Dust 2

### Redeem Gift Codes
Ask the Agent:
> Please redeem Brown Dust 2 gift codes, nickname is "your game nickname"

## Cron Jobs (Optional)

To run automatically every day:

```bash
# Sign-in at 8am daily
openclaw cron add --name "BD2 Sign-in" --cron "0 8 * * *" --message "Please sign in to Brown Dust 2" --channel discord --to "your-id" --expect-final

# Redeem codes at 8:30am daily
openclaw cron add --name "BD2 Redeem" --cron "30 8 * * *" --message "Please redeem Brown Dust 2 gift codes, nickname is your nickname" --channel discord --to "your-id" --expect-final
```

## Troubleshooting

- Login expired: Please login in browser again
- Redemption failed: Some codes may already be redeemed, this is normal

## Changelog

### v0.2.0 (2026-03-13)
- ✅ Auto login support: Click Sign In → Wait 10s → Select Google account → Wait 30s → Auto check-in
- ✅ Handle popup new windows for Google login
- ✅ Multiple account selection support

### v0.1.0 (2026-03-12)
- Initial release
- Basic sign-in functionality (requires manual login)

## Publish Update

```bash
cd ~/.openclaw/workspace/skills/browndust2
git add .
git commit -m "Update description"
git push
clawhub publish
```

## License

MIT