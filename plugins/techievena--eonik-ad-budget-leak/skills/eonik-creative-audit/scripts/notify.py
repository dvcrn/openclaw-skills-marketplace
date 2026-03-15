import argparse
import json
import urllib.request
import urllib.error
import sys
import os

def format_message(report):
    flagged = report.get("flagged_ads_count", 0)
    leaked = report.get("total_leaked_spend", 0.0)
    
    msg = f"🚨 *Meta Ads Budget Audit Alert* 🚨\n\n"
    msg += f"We found *{flagged} ads* that need your attention.\n"
    msg += f"Estimated Budget Leak: *${leaked:,.2f}*\n\n"
    
    pauses = report.get("pause_recommendations", [])
    if pauses:
        msg += "🔴 *Recommended Pauses:*\n"
        for ad in pauses[:3]: # Limit to top 3 for brevity
            msg += f"• {ad.get('ad_name', 'Unknown Ad')} (ID: {ad.get('ad_id')})\n"
            msg += f"  Reason: {ad.get('reason', 'Burn without Signal')}\n"
        if len(pauses) > 3:
            msg += f"  ... and {len(pauses)-3} more.\n\n"
            
    scales = report.get("scale_recommendations", [])
    if scales:
        msg += "🟢 *Early Winners to Scale:*\n"
        for ad in scales[:3]:
            msg += f"• {ad.get('ad_name', 'Unknown Ad')} (ID: {ad.get('ad_id')})\n"
        if len(scales) > 3:
            msg += f"  ... and {len(scales)-3} more.\n\n"
            
    return msg

def send_slack(webhook_url, text):
    payload = {"text": text}
    req = urllib.request.Request(
        webhook_url, 
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    urllib.request.urlopen(req)

def send_telegram(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    urllib.request.urlopen(req)

def send_whatsapp(api_url, token, phone_number_id, text):
    # Simplified generic WhatsApp Business API call
    url = f"{api_url}/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number_id, # Simplified: sending to self or configured number
        "type": "text",
        "text": {"body": text}
    }
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        method='POST'
    )
    urllib.request.urlopen(req)

def main():
    parser = argparse.ArgumentParser(description="Dispatch audit notifications")
    parser.add_argument("--config", required=True, help="Path to config.json")
    parser.add_argument("--report", required=True, help="Path to audit report JSON")
    args = parser.parse_args()

    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(args.report, 'r') as f:
            report = json.load(f)
    except Exception as e:
        print(f"Error loading report: {e}", file=sys.stderr)
        sys.exit(1)
        
    if report.get("status") != "success":
        print("Report status is not success, skipping notifications.", file=sys.stderr)
        sys.exit(0)

    msg = format_message(report)
    notifications = config.get("notifications", {})
    
    # Slack
    slack = notifications.get("slack", {})
    if slack.get("enabled"):
        try:
            send_slack(slack.get("webhook_url"), msg)
            print("Successfully sent to Slack.")
        except Exception as e:
            print(f"Slack error: {e}", file=sys.stderr)
            
    # Telegram
    telegram = notifications.get("telegram", {})
    if telegram.get("enabled"):
        try:
            send_telegram(telegram.get("bot_token"), telegram.get("chat_id"), msg)
            print("Successfully sent to Telegram.")
        except Exception as e:
            print(f"Telegram error: {e}", file=sys.stderr)
            
    # WhatsApp
    whatsapp = notifications.get("whatsapp", {})
    if whatsapp.get("enabled"):
        try:
            send_whatsapp(whatsapp.get("api_url"), whatsapp.get("token"), whatsapp.get("phone_number_id"), msg)
            print("Successfully sent to WhatsApp.")
        except Exception as e:
            print(f"WhatsApp error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
