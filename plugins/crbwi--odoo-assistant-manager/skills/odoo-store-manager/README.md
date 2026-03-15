# Odoo Store Manager for OpenClaw

An OpenClaw skill to seamlessly interact with your Odoo ERP point of sale, sales, and inventory directly from the terminal or via natural language chat.

Query Odoo data including physical store sales, pending web orders, and inventory levels. It also includes an automated Odoo Discuss bot that replies to natural language queries.

## 🚀 Features

- **Store Dashboard:** Check today's Point of Sale (POS) revenue and pending Web Orders.
- **Inventory Check:** Quickly find the physical and forecasted stock of any product by barcode or name.
- **Stock Updates:** Manually adjust physical inventory right from OpenClaw.
- **Odoo Chat Bot:** Launch the `odoo_listener.py` to get an AI assistant right inside your Odoo Discuss channels.

## 📋 Security & Requirements

This skill handles live store data. 
- **Read-only by default:** Reporting commands are safe.
- **Stock adjustments are destructive:** The `update_stock` command modifies live inventory. Use carefully!

### Dependencies
No extra packages are needed if your Python environment already has standard libraries (`xmlrpc.client`, `ssl`).

## ⚙️ Installation & Setup

1. Copy the `odoo_store_manager` folder into your OpenClaw `skills` directory.
2. In the `odoo_store_manager` folder, duplicate `.env.example` and rename it to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit the `.env` file with your Odoo connection details:

| Variable | Description | Secret |
| :--- | :--- | :--- |
| `ODOO_URL` | Your Odoo URL (e.g., https://my-odoo.com) | No |
| `ODOO_DB` | Database name | No |
| `ODOO_USER` | Login email / username | No |
| `ODOO_PASSWORD` | Odoo Password or External API Key | Yes |
| `ODOO_BOT_ID` | Partner ID for the chat bot to reply from | No |

## 🎮 Usage Examples (Chat)

Once installed, just ask OpenClaw naturally:

* "How are the sales doing today?"
* "Do we have any pending web orders to ship?"
* "Check if we have Catan in stock"
* "Set the stock of product 84123456789 to 10 units"

### 🧠 OpenClaw Memory Integration

For OpenClaw to truly understand how to use this skill, ask your agent to initialize it right after copying the files:

> "Hey OpenClaw, I just installed the Odoo Store Manager skill. Please read its SKILL.md and integrate the tool commands into your `TOOLS.md` cheat sheet so you don't forget how to use them."

## 🤖 Starting the Odoo Discuss Bot

If you want the agent to answer questions inside your Odoo team chat:
1. Make sure you have exported your `.env` variables or loaded them in the terminal.
2. Run the listener script in the background:
```bash
python3 src/odoo_listener.py
```
From Odoo chat, you can type "ventas", "caja", or "stock de Catan" and the bot will fetch the real-time data from the ERP.
