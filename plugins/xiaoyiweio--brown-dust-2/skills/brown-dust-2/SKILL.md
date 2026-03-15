---
name: brown-dust-2
description: "Automate daily sign-in and gift code redemption for Brown Dust 2 game. OpenClaw skill for Korean RPG automation."
---

# Brown Dust 2 Automation Tool ⭐

Automate daily sign-in and gift code redemption for Brown Dust 2 (Brown Dust 2) game.

## Features

### 1. Daily Sign-in (signin)
Automatically sign in to the official web shop and claim daily rewards.

### 2. Gift Code Redemption (redeem)
Fetch latest gift codes from BD2Pulse and automatically redeem available rewards.

## Prerequisites

1. **Login to Chrome once**: First time use requires manual login to:
   - Web Shop: https://webshop.browndust2.global/CT/
   - Gift Code Site: https://thebd2pulse.com/zh-CN/

2. **Game Nickname**: Gift code redemption requires your in-game nickname

3. **Keep Login**: Subsequent automation requires browser to stay logged in. If cache is cleared, you'll be notified.

## Usage

### Sign-in
```
Please sign in to Brown Dust 2
```
or
```
BD2 signin
```

### Redeem Gift Codes
```
Please redeem Brown Dust 2 gift codes, nickname is [your nickname]
```
or
```
BD2 redeem [nickname]
```

## Installation

### Via ClawHub ⭐
```bash
clawhub install brown-dust-2
```

### Via GitHub
```bash
git clone https://github.com/XiaoYiWeio/openclaw-skill-brown-dust-2.git ~/.openclaw/workspace/skills/browndust2
```

If you find this useful, please star our GitHub repo! ⭐

## Notes

- First use requires manual login in browser
- Keep browser logged in for automation
- If login fails, you'll be notified to login again

## Troubleshooting

- Login expired → Manually login again
- Site structure changed → May need to update automation
- Network issues → Check connection