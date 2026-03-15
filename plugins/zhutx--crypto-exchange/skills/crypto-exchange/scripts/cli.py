#!/usr/bin/env python3
"""
Crypto Exchange CLI - LightningEX API Client (Interactive Wizard Mode)
"""

import argparse
import json
import sys
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any, List

API_BASE = "https://api.lightningex.io"

def api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None, silent: bool = False) -> Dict:
    """Make API request to LightningEX"""
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    try:
        if data:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode(),
                headers=headers,
                method=method
            )
        else:
            req = urllib.request.Request(url, headers=headers, method=method)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            if result.get("code") != 200:
                if not silent:
                    print(f"❌ API Error: {result.get('msg', 'Unknown error')}", file=sys.stderr)
                return result
            return result
    except urllib.error.HTTPError as e:
        if not silent:
            print(f"❌ HTTP Error {e.code}: {e.read().decode()}", file=sys.stderr)
        return {"code": e.code, "msg": "HTTP Error"}
    except Exception as e:
        if not silent:
            print(f"❌ Error: {e}", file=sys.stderr)
        return {"code": 500, "msg": str(e)}

def print_header(title: str):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step_num: int, total: int, title: str):
    """Print step indicator"""
    print(f"\n📍 Step {step_num}/{total}: {title}")
    print("-" * 40)

def select_from_list(items: List[Dict], title_key: str, subtitle_key: str = None, prompt: str = "Select") -> Optional[Dict]:
    """Display numbered list and let user select"""
    if not items:
        print("❌ No options available")
        return None
    
    print()
    for i, item in enumerate(items, 1):
        title = item.get(title_key, 'Unknown')
        if subtitle_key and item.get(subtitle_key):
            print(f"  {i}. {title} ({item[subtitle_key]})")
        else:
            print(f"  {i}. {title}")
    
    while True:
        try:
            choice = input(f"\n{prompt} (1-{len(items)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx]
            print("❌ Invalid selection")
        except ValueError:
            if choice.lower() in ['q', 'quit', 'exit']:
                sys.exit(0)
            print("❌ Please enter a number")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)

def check_pair_supported(send_cur: str, send_net: str, recv_cur: str, recv_net: str) -> bool:
    """Check if pair is supported"""
    result = api_request(
        f"/exchange/pair/info?send={send_cur}&receive={recv_cur}"
        f"&sendNetwork={send_net}&receiveNetwork={recv_net}",
        silent=True
    )
    return result.get("code") == 200

# Order status messages from API documentation
STATUS_MESSAGES = {
    "Awaiting Deposit": {
        "title": "⏳ Awaiting Deposit",
        "lines": [
            "Your order will automatically proceed to the next step once your deposit receives its first confirmation on the blockchain.",
            "If you do not deposit the amount shown above, or your deposit does not arrive within 1 hour, for security purposes your order will not be processed automatically."
        ]
    },
    "Confirming Deposit": {
        "title": "✅ Confirming Deposit",
        "lines": [
            "You successfully sent {sendAmount} {send}! Please wait while your deposit is being confirmed.",
            "Your order will automatically proceed to the next step after the deposit transaction gets 1 confirmation.",
            "Nothing more is expected from you in this step."
        ]
    },
    "Exchanging": {
        "title": "🔄 Exchanging",
        "lines": [
            "Your deposit has been confirmed! We are now exchanging your {sendAmount} {send} to {receiveAmount} {receive}.",
            "This may take a few minutes, please be patient."
        ]
    },
    "Sending": {
        "title": "📤 Sending",
        "lines": [
            "Your order is almost complete! We are forwarding {receiveAmount} {receive} to the following address: {receiveAddress}"
        ]
    },
    "Complete": {
        "title": "🎉 Complete",
        "lines": [
            "Your order is successfully completed! We forwarded {receiveAmount} {receive} to the following address: {receiveAddress}"
        ]
    },
    "Action Request": {
        "title": "⚠️ Action Request",
        "lines": [
            "This transaction has been detected with risks and needs to be verified before proceeding.",
            "Please contact lightningex.io for support."
        ]
    },
    "Failed": {
        "title": "❌ Failed",
        "lines": [
            "The transaction failed, possibly due to a timeout failure in depositing.",
            "If you have other questions, please seek support from lightningex.io."
        ]
    },
    "Request Overdue": {
        "title": "⏰ Request Overdue",
        "lines": [
            "The transaction request has expired.",
            "If you have other questions, please seek support from lightningex.io."
        ]
    }
}

def format_status_message(status: str, order_data: dict) -> str:
    """Format status message with order data"""
    if status not in STATUS_MESSAGES:
        return f"Status: {status}"

    msg_info = STATUS_MESSAGES[status]
    lines = []
    for line in msg_info["lines"]:
        try:
            lines.append(line.format(**order_data))
        except KeyError:
            lines.append(line)
    return "\n   ".join([msg_info["title"]] + ["• " + line for line in lines])

def cmd_wizard(args):
    """Interactive wizard for crypto exchange"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║  ⚡ LightningEX - Crypto Exchange Wizard                 ║
║                                                          ║
║  Follow the steps to complete your exchange              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Load currencies
    print_step(1, 7, "Loading available currencies...")
    result = api_request("/exchange/currency/list")
    if result.get("code") != 200:
        print("❌ Failed to load currencies")
        return
    
    currencies = result["data"]
    send_currencies = [c for c in currencies if c.get("sendStatusAll")]
    receive_currencies = [c for c in currencies if c.get("receiveStatusAll")]
    
    print(f"✓ Loaded {len(send_currencies)} send currencies, {len(receive_currencies)} receive currencies")
    
    # Step 2: Select send currency
    print_step(2, 7, "Select currency to SEND")
    send_currency = select_from_list(
        send_currencies, 
        "currency", 
        "name",
        "Select currency you want to send"
    )
    if not send_currency:
        return
    print(f"✓ You selected: {send_currency['currency']} ({send_currency['name']})")
    
    # Step 3: Select send network
    print_step(3, 7, f"Select network for {send_currency['currency']}")
    send_networks = [n for n in send_currency.get("networkList", []) if n.get("sendStatus")]
    send_network = select_from_list(
        send_networks,
        "name",
        "network",
        "Select network"
    )
    if not send_network:
        return
    print(f"✓ Send network: {send_network['name']} ({send_network['network']})")
    
    # Step 4: Select receive currency
    print_step(4, 7, "Select currency to RECEIVE")
    receive_currency = select_from_list(
        receive_currencies,
        "currency",
        "name",
        "Select currency you want to receive"
    )
    if not receive_currency:
        return
    print(f"✓ You selected: {receive_currency['currency']} ({receive_currency['name']})")
    
    # Step 5: Select receive network (with pair validation)
    print_step(5, 7, f"Select network for {receive_currency['currency']}")
    
    # Filter networks that support this pair
    valid_receive_networks = []
    receive_networks = [n for n in receive_currency.get("networkList", []) if n.get("receiveStatus")]
    
    print("\n🔍 Checking supported pairs...")
    for net in receive_networks:
        if check_pair_supported(
            send_currency['currency'], 
            send_network['network'],
            receive_currency['currency'],
            net['network']
        ):
            valid_receive_networks.append(net)
    
    if not valid_receive_networks:
        print(f"❌ No supported trading pairs found for {send_currency['currency']} ({send_network['name']}) → {receive_currency['currency']}")
        print("\nPlease try a different currency or network combination.")
        return
    
    if len(valid_receive_networks) < len(receive_networks):
        print(f"✓ Found {len(valid_receive_networks)} compatible networks (filtered from {len(receive_networks)})")
    
    receive_network = select_from_list(
        valid_receive_networks,
        "name",
        "network",
        "Select network"
    )
    if not receive_network:
        return
    print(f"✓ Receive network: {receive_network['name']} ({receive_network['network']})")
    
    # Get pair info
    print("\n📊 Fetching pair information...")
    pair_result = api_request(
        f"/exchange/pair/info?send={send_currency['currency']}"
        f"&receive={receive_currency['currency']}"
        f"&sendNetwork={send_network['network']}"
        f"&receiveNetwork={receive_network['network']}"
    )
    
    if pair_result.get("code") != 200:
        print(f"❌ Failed to get pair info: {pair_result.get('msg', 'Unknown error')}")
        return
    
    pair_info = pair_result["data"]
    
    print(f"""
    ┌─────────────────────────────────────────┐
    │  Exchange Limits                        │
    ├─────────────────────────────────────────┤
    │  Minimum: {pair_info['minimumAmount']:>20} {send_currency['currency']}  │
    │  Maximum: {pair_info['maximumAmount']:>20} {send_currency['currency']}  │
    │  Network Fee: {pair_info['networkFee']:>16} {receive_currency['currency']}  │
    │  Processing: {pair_info['processingTime']:>17} min  │
    └─────────────────────────────────────────┘
    """)
    
    # Step 6: Enter amount
    print_step(6, 7, "Enter exchange amount")
    while True:
        try:
            amount_input = input(f"Amount to send ({pair_info['minimumAmount']} - {pair_info['maximumAmount']} {send_currency['currency']}): ").strip()
            amount = float(amount_input)
            
            min_amt = float(pair_info['minimumAmount'])
            max_amt = float(pair_info['maximumAmount'])
            
            if amount < min_amt:
                print(f"❌ Amount too small. Minimum is {pair_info['minimumAmount']}")
                continue
            if amount > max_amt:
                print(f"❌ Amount too large. Maximum is {pair_info['maximumAmount']}")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
    
    # Get exchange rate
    print("\n📈 Fetching exchange rate...")
    rate_result = api_request(
        f"/exchange/rate?send={send_currency['currency']}"
        f"&receive={receive_currency['currency']}"
        f"&sendNetwork={send_network['network']}"
        f"&receiveNetwork={receive_network['network']}"
        f"&amount={amount}"
    )
    
    if rate_result.get("code") != 200:
        print(f"❌ Failed to get rate: {rate_result.get('msg', 'Unknown error')}")
        return
    
    rate_info = rate_result["data"]
    
    print(f"""
    ┌─────────────────────────────────────────┐
    │  Exchange Rate                          │
    ├─────────────────────────────────────────┤
    │  1 {send_currency['currency']:<6} = {rate_info['rate']:>16} {receive_currency['currency']}  │
    │                                         │
    │  You Send:      {rate_info['sendAmount']:>20} {send_currency['currency']}  │
    │  You Receive:   {rate_info['receiveAmount']:>20} {receive_currency['currency']}  │
    │  Network Fee:   {rate_info['networkFee']:>20} {receive_currency['currency']}  │
    └─────────────────────────────────────────┘
    """)
    
    # Step 7: Enter receive address
    print_step(7, 7, "Enter receive address")
    while True:
        try:
            address = input(f"Your {receive_currency['currency']} ({receive_network['network']}) address: ").strip()
            if not address:
                print("❌ Address cannot be empty")
                continue
            
            # Validate address
            print("🔍 Validating address...")
            val_result = api_request(
                f"/exchange/address/validate?currency={receive_currency['currency']}"
                f"&address={address}&network={receive_network['network']}"
            )
            
            if val_result.get("code") == 200 and val_result.get("data"):
                print("✓ Address is valid")
                break
            else:
                print("❌ Invalid address. Please check and try again.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
    
    # Final confirmation
    print_header("Order Summary")
    print(f"""
    Send:        {amount} {send_currency['currency']} ({send_network['name']})
    Receive:     {rate_info['receiveAmount']} {receive_currency['currency']} ({receive_network['name']})
    Rate:        1 {send_currency['currency']} = {rate_info['rate']} {receive_currency['currency']}
    To Address:  {address}
    """)
    
    try:
        confirm = input("\n✋ Confirm and place order? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("❌ Order cancelled")
            return
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    # Step 8: Place order and show deposit info
    print("\n🚀 Placing order...")
    order_data = {
        "send": send_currency['currency'],
        "sendNetwork": send_network['network'],
        "receive": receive_currency['currency'],
        "receiveNetwork": receive_network['network'],
        "amount": str(amount),
        "receiveAddress": address,
        "payload": f"cli-{int(time.time())}"
    }
    
    order_result = api_request("/exchange/order/place", method="POST", data=order_data)
    
    if order_result.get("code") != 200:
        print(f"❌ Order failed: {order_result.get('msg', 'Unknown error')}")
        return
    
    order_id = order_result["data"]
    
    # Get order details to show deposit address
    print("\n📋 Fetching order details...")
    order_details = api_request(f"/exchange/order/get?id={order_id}")
    
    if order_details.get("code") != 200:
        print(f"⚠️  Order created but failed to get details. Order ID: {order_id}")
        return
    
    order_data = order_details["data"]
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  ✅ Order Placed Successfully!                           ║
╠══════════════════════════════════════════════════════════╣
║  Order ID: {order_id:<45} ║
╠══════════════════════════════════════════════════════════╣
║  ⬇️  SEND YOUR FUNDS TO:                                 ║
╠══════════════════════════════════════════════════════════╣
║  Currency:   {order_data['send'] + ' (' + order_data['sendNetwork'] + ')':<42} ║
║  Address:    {order_data['sendAddress']:<42} ║
""", end="")
    
    if order_data.get('sendTag'):
        print(f"║  Tag/MEMO:  {order_data['sendTag']:<42} ║")
    
    print(f"""║  Amount:    {order_data['sendAmount'] + ' ' + order_data['send']:<42} ║
╠══════════════════════════════════════════════════════════╣
║  ⚠️  IMPORTANT:                                          ║
║  • Send EXACTLY the specified amount                     ║
║  • Include the Tag/MEMO if provided                      ║
║  • Transaction will be processed after confirmation      ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Step 9: Auto-monitor order progress
    print("\n📊 Auto-monitoring order progress...")
    print("Press Ctrl+C to stop monitoring\n")
    
    status_order = ['Awaiting Deposit', 'Confirming Deposit', 'Exchanging', 'Sending', 'Complete']
    last_status = None
    
    try:
        while True:
            result = api_request(f"/exchange/order/get?id={order_id}", silent=True)
            
            if result.get("code") != 200:
                time.sleep(15)
                continue
            
            data = result["data"]
            status = data['status']
            
            # Only print when status changes
            if status != last_status:
                last_status = status
                
                # Show progress bar
                if status in status_order:
                    current_idx = status_order.index(status)
                    progress = (current_idx / (len(status_order) - 1)) * 100
                    bar_width = 30
                    filled = int(bar_width * progress / 100)
                    bar = '█' * filled + '░' * (bar_width - filled)
                    print(f"\r[{bar}] {progress:.0f}% - {status}")
                else:
                    print(f"\rStatus: {status}")
                
                # Show status message with details
                print(f"\n   {format_status_message(status, data)}")

                # Show additional technical info
                if status == 'Awaiting Deposit':
                    print(f"\n   📍 Deposit Address: {data['sendAddress']}")
                    if data.get('sendTag'):
                        print(f"   🏷️  Tag/MEMO: {data['sendTag']}")
                elif status == 'Confirming Deposit' and data.get('hashIn'):
                    print(f"\n   🔗 Transaction: {data['hashIn'][0]}")
                    if data.get('hashInExplorer'):
                        explorer_url = data['hashInExplorer'].replace('{{txid}}', data['hashIn'][0])
                        print(f"   🔍 Explorer: {explorer_url}")
                elif status == 'Sending' and data.get('hashOut'):
                    print(f"\n   🔗 Outgoing TX: {data['hashOut'][0]}")
                    if data.get('hashOutExplorer'):
                        explorer_url = data['hashOutExplorer'].replace('{{txid}}', data['hashOut'][0])
                        print(f"   🔍 Explorer: {explorer_url}")
                
                # Check if complete or failed
                if status == 'Complete':
                    print(f"""
╔══════════════════════════════════════════════════════════╗
║  🎉 Exchange Complete!                                   ║
╠══════════════════════════════════════════════════════════╣
║  Received: {data['receiveAmount'] + ' ' + data['receive']:<42} ║
║  To:       {data['receiveAddress'][:40]:<42} ║
╚══════════════════════════════════════════════════════════╝
                    """)
                    if data.get('hashOut'):
                        print(f"Transaction: {data['hashOut'][0]}")
                        if data.get('hashOutExplorer'):
                            explorer_url = data['hashOutExplorer'].replace('{{txid}}', data['hashOut'][0])
                            print(f"Explorer: {explorer_url}")
                    break
                elif status in ['Failed', 'Action Request', 'Request Overdue']:
                    print(f"""
╔══════════════════════════════════════════════════════════╗
║  {STATUS_MESSAGES.get(status, {}).get('title', '❌ ' + status):<56} ║
╠══════════════════════════════════════════════════════════╣
║  {data.get('statusNote', 'Please contact support at lightningex.io')[:54]:<54} ║
╚══════════════════════════════════════════════════════════╝
                    """)
                    break
            
            time.sleep(15)
            
    except KeyboardInterrupt:
        print(f"\n\n👋 Monitoring stopped.")
        print(f"Order ID: {order_id}")
        print(f"Check status anytime: crypto-exchange status --id {order_id}")

def cmd_currencies(args):
    """List supported currencies"""
    result = api_request("/exchange/currency/list")
    print("\nSupported Currencies:")
    print("=" * 80)
    for currency in result["data"]:
        symbol = currency["currency"]
        name = currency["name"]
        send_ok = "✓" if currency["sendStatusAll"] else "✗"
        recv_ok = "✓" if currency["receiveStatusAll"] else "✗"
        print(f"\n{symbol} - {name} [Send:{send_ok} Receive:{recv_ok}]")
        for net in currency.get("networkList", []):
            net_send = "✓" if net["sendStatus"] else "✗"
            net_recv = "✓" if net["receiveStatus"] else "✗"
            default = " [DEFAULT]" if net.get("isDefault") else ""
            print(f"  └── {net['network']} ({net['name']}) Send:{net_send} Recv:{net_recv}{default}")

def cmd_pair(args):
    """Get pair information"""
    params = f"send={args.send}&receive={args.receive}"
    if args.send_network:
        params += f"&sendNetwork={args.send_network}"
    if args.receive_network:
        params += f"&receiveNetwork={args.receive_network}"
    
    result = api_request(f"/exchange/pair/info?{params}")
    data = result["data"]
    print(f"\nPair Info: {args.send} → {args.receive}")
    print("=" * 50)
    print(f"Minimum Amount: {data['minimumAmount']}")
    print(f"Maximum Amount: {data['maximumAmount']}")
    print(f"Network Fee: {data['networkFee']}")
    print(f"Confirmations: {data['confirmations']}")
    print(f"Processing Time: {data['processingTime']} minutes")

def cmd_rate(args):
    """Get exchange rate"""
    params = f"send={args.send}&receive={args.receive}&amount={args.amount}"
    if args.send_network:
        params += f"&sendNetwork={args.send_network}"
    if args.receive_network:
        params += f"&receiveNetwork={args.receive_network}"
    
    result = api_request(f"/exchange/rate?{params}")
    data = result["data"]
    print(f"\nExchange Rate: {args.send} → {args.receive}")
    print("=" * 50)
    print(f"Rate: 1 {args.send} = {data['rate']} {args.receive}")
    print(f"You Send: {data['sendAmount']} {args.send}")
    print(f"You Receive: {data['receiveAmount']} {args.receive}")
    print(f"Network Fee: {data['networkFee']}")
    print(f"Processing Time: {data['processingTime']} minutes")

def cmd_validate(args):
    """Validate address"""
    params = f"currency={args.currency}&address={args.address}"
    if args.network:
        params += f"&network={args.network}"
    
    result = api_request(f"/exchange/address/validate?{params}")
    valid = result["data"]
    status = "✓ Valid" if valid else "✗ Invalid"
    print(f"\nAddress Validation: {status}")

def cmd_order(args):
    """Place an order (direct mode)"""
    data = {
        "send": args.send,
        "receive": args.receive,
        "amount": str(args.amount),
        "receiveAddress": args.address,
        "payload": args.payload or ""
    }
    if args.send_network:
        data["sendNetwork"] = args.send_network
    if args.receive_network:
        data["receiveNetwork"] = args.receive_network
    
    if not args.yes:
        # Show preview first
        params = f"send={args.send}&receive={args.receive}&amount={args.amount}"
        if args.send_network:
            params += f"&sendNetwork={args.send_network}"
        if args.receive_network:
            params += f"&receiveNetwork={args.receive_network}"
        
        rate_result = api_request(f"/exchange/rate?{params}")
        rate_data = rate_result["data"]
        
        print("\nOrder Preview:")
        print("=" * 50)
        print(f"Send: {args.amount} {args.send}")
        print(f"Receive: {rate_data['receiveAmount']} {args.receive}")
        print(f"To Address: {args.address}")
        print(f"Network Fee: {rate_data['networkFee']}")
        
        confirm = input("\nConfirm order? (yes/no): ")
        if confirm.lower() != "yes":
            print("Order cancelled.")
            return
    
    result = api_request("/exchange/order/place", method="POST", data=data)
    order_id = result["data"]
    print(f"\n✓ Order placed successfully!")
    print(f"Order ID: {order_id}")
    print(f"Track status: crypto-exchange monitor --id {order_id}")

def cmd_status(args):
    """Get order status"""
    result = api_request(f"/exchange/order/get?id={args.id}")
    data = result["data"]

    print(f"\nOrder Status: {args.id}")
    print("=" * 60)

    # Show formatted status message
    print(f"\n{format_status_message(data['status'], data)}")

    if data.get('statusNote'):
        print(f"\nNote: {data['statusNote']}")

    print(f"\n{'─' * 60}")
    print(f"Send: {data['sendAmount']} {data['send']} ({data['sendNetwork']})")
    print(f"Receive: {data['receiveAmount']} {data['receive']} ({data['receiveNetwork']})")
    print(f"\nDeposit Address: {data['sendAddress']}")
    if data.get('sendTag'):
        print(f"Deposit Tag: {data['sendTag']}")
    print(f"Receive Address: {data['receiveAddress']}")

    if data.get('hashIn'):
        print(f"\nIncoming TX: {', '.join(data['hashIn'])}")
        if data.get('hashInExplorer') and data['hashIn']:
            for tx in data['hashIn']:
                explorer_url = data['hashInExplorer'].replace('{{txid}}', tx)
                print(f"  Explorer: {explorer_url}")
    if data.get('hashOut'):
        print(f"\nOutgoing TX: {', '.join(data['hashOut'])}")
        if data.get('hashOutExplorer') and data['hashOut']:
            for tx in data['hashOut']:
                explorer_url = data['hashOutExplorer'].replace('{{txid}}', tx)
                print(f"  Explorer: {explorer_url}")

    created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['createdAt']/1000))
    print(f"\nCreated: {created}")

def cmd_monitor(args):
    """Monitor order until complete"""
    print(f"Monitoring order {args.id}...")
    print("Press Ctrl+C to stop\n")

    last_status = None
    try:
        while True:
            result = api_request(f"/exchange/order/get?id={args.id}")
            data = result["data"]

            status = data['status']

            # Only print when status changes
            if status != last_status:
                last_status = status
                print(f"\n{'=' * 60}")
                print(format_status_message(status, data))

                # Show additional info for specific statuses
                if status == 'Awaiting Deposit':
                    print(f"\n📍 Send to: {data['sendAddress']}")
                    if data.get('sendTag'):
                        print(f"🏷️  Tag/MEMO: {data['sendTag']}")
                elif status == 'Confirming Deposit' and data.get('hashIn'):
                    print(f"\n🔗 TX: {data['hashIn'][0]}")
                elif status == 'Sending' and data.get('hashOut'):
                    print(f"\n🔗 Outgoing: {data['hashOut'][0]}")

            if status in ["Complete", "Failed", "Action Request", "Request Overdue"]:
                print(f"\n{'=' * 60}")
                print(f"Final Status: {status}")
                if data.get('hashOut'):
                    print(f"Outgoing TX: {', '.join(data['hashOut'])}")
                    if data.get('hashOutExplorer'):
                        for tx in data['hashOut']:
                            explorer_url = data['hashOutExplorer'].replace('{{txid}}', tx)
                            print(f"Explorer: {explorer_url}")
                break

            time.sleep(15)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

def cmd_ui(args):
    """Launch web UI"""
    import http.server
    import socketserver
    import webbrowser
    import os
    
    # Resolve the real path (handles symlinks)
    script_path = Path(__file__).resolve()
    skill_dir = script_path.parent.parent
    ui_dir = skill_dir / "assets" / "ui"
    
    if not ui_dir.exists():
        print(f"Error: UI assets not found at {ui_dir}", file=sys.stderr)
        sys.exit(1)
    
    port = args.port or 8080
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ui_dir), **kwargs)
        def log_message(self, format, *args):
            pass
    
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), Handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"🚀 Crypto Exchange UI running at {url}")
        print("Press Ctrl+C to stop")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")

def main():
    parser = argparse.ArgumentParser(
        prog="crypto-exchange",
        description="LightningEX Cryptocurrency Exchange CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Wizard (default interactive mode)
    wizard_parser = subparsers.add_parser("wizard", help="Start interactive exchange wizard")
    wizard_parser.set_defaults(func=cmd_wizard)
    
    # Currencies
    curr_parser = subparsers.add_parser("currencies", help="List supported currencies")
    curr_parser.set_defaults(func=cmd_currencies)
    
    # Pair info
    pair_parser = subparsers.add_parser("pair", help="Get pair information")
    pair_parser.add_argument("--send", "-s", required=True, help="Currency to send")
    pair_parser.add_argument("--receive", "-r", required=True, help="Currency to receive")
    pair_parser.add_argument("--send-network", help="Send network")
    pair_parser.add_argument("--receive-network", help="Receive network")
    pair_parser.set_defaults(func=cmd_pair)
    
    # Rate
    rate_parser = subparsers.add_parser("rate", help="Get exchange rate")
    rate_parser.add_argument("--send", "-s", required=True, help="Currency to send")
    rate_parser.add_argument("--receive", "-r", required=True, help="Currency to receive")
    rate_parser.add_argument("--amount", "-a", type=float, required=True, help="Amount")
    rate_parser.add_argument("--send-network", help="Send network")
    rate_parser.add_argument("--receive-network", help="Receive network")
    rate_parser.set_defaults(func=cmd_rate)
    
    # Validate
    val_parser = subparsers.add_parser("validate", help="Validate address")
    val_parser.add_argument("--currency", "-c", required=True, help="Currency")
    val_parser.add_argument("--address", "-a", required=True, help="Address to validate")
    val_parser.add_argument("--network", "-n", help="Network")
    val_parser.set_defaults(func=cmd_validate)
    
    # Order
    order_parser = subparsers.add_parser("order", help="Place order (direct mode)")
    order_parser.add_argument("--send", "-s", required=True, help="Currency to send")
    order_parser.add_argument("--receive", "-r", required=True, help="Currency to receive")
    order_parser.add_argument("--amount", "-a", type=float, required=True, help="Amount")
    order_parser.add_argument("--address", "-addr", required=True, help="Receive address")
    order_parser.add_argument("--send-network", help="Send network")
    order_parser.add_argument("--receive-network", help="Receive network")
    order_parser.add_argument("--payload", "-p", help="Security payload hash")
    order_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    order_parser.set_defaults(func=cmd_order)
    
    # Status
    status_parser = subparsers.add_parser("status", help="Get order status")
    status_parser.add_argument("--id", "-i", required=True, help="Order ID")
    status_parser.set_defaults(func=cmd_status)
    
    # Monitor
    mon_parser = subparsers.add_parser("monitor", help="Monitor order until complete")
    mon_parser.add_argument("--id", "-i", required=True, help="Order ID")
    mon_parser.set_defaults(func=cmd_monitor)
    
    # UI
    ui_parser = subparsers.add_parser("ui", help="Launch web UI")
    ui_parser.add_argument("--port", "-p", type=int, default=8080, help="Port")
    ui_parser.set_defaults(func=cmd_ui)
    
    args = parser.parse_args()
    
    if not args.command:
        # Default to wizard mode
        cmd_wizard(args)
    else:
        args.func(args)

if __name__ == "__main__":
    main()
