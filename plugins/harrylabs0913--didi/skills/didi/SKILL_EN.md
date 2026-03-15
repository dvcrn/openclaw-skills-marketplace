# Didi Ride-Hailing Assistant

CLI tool for Didi Chuxing ride-hailing service.

## Features

- **Price Estimation** - Query estimated prices for different car types
- **Call Ride** - Quickly request rides (Express, Select, Premier, Luxury)
- **Trip Status** - Real-time tracking of current trips
- **Order History** - View past ride records
- **Coupons** - Check available coupons and discounts
- **QR Login** - Login via Didi app QR code scanning

## Installation

```bash
cd ~/.openclaw/workspace/skills/didi
pip install -r requirements.txt
playwright install chromium
```

## Usage

### 1. Login
```bash
python didi.py login
```
Scan QR code with Didi app to authenticate and save session.

### 2. Price Estimation
```bash
python didi.py estimate "Guomao" "Tiananmen"
python didi.py estimate "Beijing South Station" "Capital Airport"
```

### 3. Call Ride
```bash
# Default (Express)
python didi.py call "Guomao" "Tiananmen"

# Specify car type
python didi.py call "Guomao" "Tiananmen" --type premier
```

Supported car types:
- `express` - Didi Express (default)
- `select` - Didi Select
- `premier` - Didi Premier
- `luxury` - Didi Luxury

### 4. Check Trip Status
```bash
python didi.py status
```
Display current trip, driver info, and ETA.

### 5. View Order History
```bash
python didi.py history
```

### 6. Check Coupons
```bash
python didi.py coupon
```

## Data Storage

- Config directory: `~/.didi/`
- Cookies: `~/.didi/cookies.json`
- Database: `~/.didi/didi.db`

## Technical Implementation

- Python + Playwright browser automation
- SQLite local data storage
- Anti-detection measures
- Supports Didi web version and mini-program

## Security

- All user data stored locally, no cloud upload
- Browser automation simulates normal user behavior
- Encrypted cookie storage
- No malicious code or backdoors

## Dependencies

- Python 3.8+
- Playwright >= 1.40.0
- Chromium browser

## Notes

1. Login required before first use
2. Ride calling opens browser window - keep it open
3. Estimated prices are reference only, actual may vary
4. Recommended to estimate price before calling
