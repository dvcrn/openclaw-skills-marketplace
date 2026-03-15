import argparse
import urllib.request
import urllib.error
import urllib.parse
import json
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Trigger the eonik Creative Experimentation audit")
    parser.add_argument("--account_id", required=False, help="Meta Ad Account ID (Optional, will use connected account if omitted)")
    parser.add_argument("--days", type=int, default=7, help="Days to evaluate (default: 7)")
    args = parser.parse_args()

    api_key = os.environ.get("EONIK_API_KEY")
    if not api_key:
        print(json.dumps({
            "status": "error",
            "message": "EONIK_API_KEY environment variable is not set."
        }, indent=2), file=sys.stderr)
        sys.exit(1)

    # Security: Drop the ephemeral key from the execution environment securely.
    os.environ.pop("EONIK_API_KEY", None)

    endpoint = "https://api.eonik.ai/api/budget-agent/run-audit"

    headers = {
        "x-api-key": str(api_key),
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    params = {
        "days": args.days
    }
    
    if args.account_id:
        params["account_id"] = args.account_id

    try:
        query_string = urllib.parse.urlencode(params)
        full_url = f"{endpoint}?{query_string}"

        req = urllib.request.Request(full_url, headers=headers, method="POST")

        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            report = json.loads(body)

        # Pass through the full enriched report
        print(json.dumps({
            "status": "success",
            "account_id": report.get("account_id", ""),
            "audit_date": report.get("audit_date", ""),
            "currency_symbol": report.get("currency_symbol", "$"),
            "flagged_ads_count": report.get("flagged_ads_count", 0),
            "total_leaked_spend": report.get("total_leaked_spend", 0.0),
            "creative_insight": report.get("creative_insight"),
            "pause_recommendations": report.get("pause_recommendations", []),
            "scale_recommendations": report.get("scale_recommendations", []),
            "monitor_recommendations": report.get("monitor_recommendations", [])
        }, indent=2))
        
    except urllib.error.HTTPError as http_err:
        err_body = http_err.read().decode('utf-8')
        print(json.dumps({
            "status": "error",
            "message": f"HTTP error occurred: {http_err.code} {http_err.reason}",
            "response_text": err_body
        }, indent=2), file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(json.dumps({
            "status": "error",
            "message": f"An unexpected error occurred: {err}"
        }, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
