---
name: odoo_store_manager
description: "Manage your Odoo store (Check Sales, Stock and Update Inventory)"
---

# Odoo Store Manager

This skill allows you to manage an Odoo Store using the `src/odoo_manager.py` script.

## Core Capabilities

You **MUST** use the terminal to run these commands within the skill directory.

> [!IMPORTANT]
> **Use the correct path based on your installation folder:** `./src/odoo_manager.py`

### 1. Check Sales & Orders
```bash
python3 src/odoo_manager.py check_sales
```
**Use when:** "Any new orders?", "How are sales today?", "Daily report".

### 2. Check Stock / Search Products
```bash
python3 src/odoo_manager.py check_stock --query "PRODUCT NAME OR BARCODE"
```
**Use when:** "Do we have Catan?", "Check stock of X", "Search for X".

### 3. Update Stock
```bash
python3 src/odoo_manager.py update_stock --ref "PRODUCT NAME OR BARCODE" --qty 10
```
**Use when:** "Set stock of X to 10", "Update inventory".

## Critical Rules

1. **Always run the script.** The script securely handles the XML-RPC Odoo API.
2. **Interpret the output.** Read the raw terminal results from Odoo and summarize them conversationally for the user.
3. **Handle errors gracefully.** If the script fails (e.g. wrong credentials), tell the user exactly what went wrong so they can fix their `.env`.

## Initialization Workflow (For the AI Agent)

When a human user installs this skill and asks you to set it up, you MUST proactively integrate it into your memory systems:

1. **Read your Workspace Identity:** Check if `SOUL.md` and `TOOLS.md` exist in your workspace root.
2. **Update `TOOLS.md`:** Write a clear and concise cheat sheet in your `TOOLS.md` file. You can simply copy and append the following block:

```markdown
## 🏪 Odoo Store Manager

This skill manages the Odoo ERP store. All commands must be run from the skill directory.
*Note: Ensure you are using the absolute path to `skills/odoo_store_manager/src/odoo_manager.py` if running from outside the skill folder.*

- **Check Sales / Pending Orders:**
  `python3 skills/odoo_store_manager/src/odoo_manager.py check_sales`

- **Check Stock / Search Product:**
  `python3 skills/odoo_store_manager/src/odoo_manager.py check_stock --query "PRODUCT OR BARCODE"`

- **Update Physical Stock:**
  `python3 skills/odoo_store_manager/src/odoo_manager.py update_stock --ref "PRODUCT OR BARCODE" --qty 10`

- **Check Top Sales:**
  `python3 skills/odoo_store_manager/src/odoo_manager.py top_sales --period "month"`

- **Add New Product:**
  `python3 skills/odoo_store_manager/src/odoo_manager.py add_product --name "My Item" --price 9.95 --qty 5`
```

3. **Update `SOUL.md` (Optional):** If the user wants you to adopt the persona of a Store Manager, update your `IDENTITY.md` and `SOUL.md` to reflect that you are now actively checking their Odoo ERP data before answering inventory questions.
4. **Confirm Integration:** Reply to the human explicitly confirming that you have "absorbed" the new Odoo tools into your long-term memory.
