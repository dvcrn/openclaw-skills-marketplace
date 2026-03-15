# Clawshier

OpenClaw skill that processes receipt/invoice photos from any chat channel, extracts expense data via OpenAI Vision, and logs it to a Google Spreadsheet.

## Prerequisites

- Node.js 18+
- OpenAI API key
- Google Cloud service account with Sheets API enabled

## Install

```bash
git clone https://github.com/YOUR_USER/clawshier.git
cd clawshier
npm install
cp .env.example .env
```

Fill in `.env` with your credentials (see `.env.example`).

### Google Sheets setup

1. Create a Google Cloud service account and download the JSON key file
2. Enable the Google Sheets API in your project
3. Create a spreadsheet and share it with the service account email
4. Add the spreadsheet ID and key file path to `.env`

### OpenClaw usage

Copy `SKILL.md` into your OpenClaw skills directory or install via ClawHub.

## License

MIT
