import argparse
import subprocess
import json
import sys
import os
import datetime

def run_command(cmd, env=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"Error executing command: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout

def main():
    parser = argparse.ArgumentParser(description="Run eonik Creative Experimentation Audit Pipeline")
    parser.add_argument("--config", required=True, help="Path to config.json")
    args = parser.parse_args()

    # Load config to get account_id and days
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)

    account_id = config.get("meta", {}).get("account_id")
    days = config.get("meta", {}).get("evaluation_days", 7)
    
    if account_id == "YOUR_ACCOUNT_ID_OR_LEAVE_BLANK_TO_AUTO_RESOLVE" or account_id == "":
        account_id = None

    run_date = datetime.datetime.now().strftime("%Y-%m-%d")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, f"audit-{run_date}.json")

    # Step 1: Run Audit
    print("=== Stage 1: Running Creative Experimentation Audit ===")
    audit_cmd = [
        sys.executable, "scripts/audit.py",
        "--days", str(days)
    ]
    if account_id:
        audit_cmd.extend(["--account_id", account_id])
    # Security: Pass only the explicitly required variables to the child process.
    safe_env = {
        "PATH": os.environ.get("PATH", ""),
        "EONIK_API_KEY": os.environ.get("EONIK_API_KEY", "")
    }
    audit_out = run_command(audit_cmd, env=safe_env)    
    with open(report_path, "w") as f:
        f.write(audit_out)
    
    print(f"Audit complete. Report saved to {report_path}")

    # Step 2: Format and Display Report
    print("\n\n=== eonik Creative Experimentation Report ===")
    try:
        data = json.loads(audit_out)
        if data.get("status") != "success":
            print(f"Audit Status: {data.get('status', 'failed')}")
            sys.exit(1)

        cs = data.get('currency_symbol', '$')
        spent = data.get('total_leaked_spend', 0.0)
        flagged = data.get('flagged_ads_count', 0)

        # --- Impact Summary ---
        print(f"\n💰 Impact Summary")
        print(f"   Flags Found: {flagged}")
        print(f"   Wasted Spend Detected: {cs}{spent:,.2f}")

        # --- Creative Intelligence ---
        insight = data.get("creative_insight")
        if insight:
            print(f"\n🧬 Creative Intelligence")
            print(f"   {insight}")

        # --- Pause / Refresh Recommendations ---
        pauses = data.get("pause_recommendations", [])
        if pauses:
            print(f"\n🚨 Urgent Actions ({len(pauses)} ads)")
            for i, ad in enumerate(pauses, 1):
                rec = ad.get("recommendation", {})
                category = ad.get("category", "Flagged")
                action = rec.get("action", "PAUSE")
                reason = rec.get("reason", "")
                ad_name = ad.get("ad_name", "Unknown")
                ad_id = ad.get("ad_id", "")
                
                action_emoji = "⏸️" if action == "PAUSE" else "🔄"
                print(f"\n   {action_emoji} [{action}] {ad_name}")
                print(f"     Category: {category}")
                print(f"     Reason: {reason}")
                
                # Metrics
                spend = ad.get("spend", 0)
                cpa = ad.get("cpa", 0)
                ctr = ad.get("ctr", 0)
                hook = ad.get("hook_rate", 0)
                print(f"     Spend: {cs}{spend:,.2f} | CPA: {cs}{cpa:,.2f} | CTR: {ctr:.2f}%", end="")
                if hook > 0:
                    print(f" | Hook Rate: {hook:.1f}%")
                else:
                    print()

                # Signals
                for sig in ad.get("signals", []):
                    print(f"     └ {sig.get('label')}: {sig.get('detail')}")

                # Genome Tags
                genome = ad.get("genome_tags")
                if genome:
                    tags = [f"{k}: {v}" for k, v in genome.items() if v and v != "unknown"]
                    if tags:
                        print(f"     🧬 Creative DNA: {' | '.join(tags)}")

        # --- Scale Recommendations ---
        scales = data.get("scale_recommendations", [])
        if scales:
            print(f"\n🚀 Scale Opportunities ({len(scales)} ads)")
            for i, ad in enumerate(scales, 1):
                rec = ad.get("recommendation", {})
                reason = rec.get("reason", "")
                ad_name = ad.get("ad_name", "Unknown")
                
                print(f"\n   📈 [SCALE] {ad_name}")
                print(f"     Reason: {reason}")
                
                spend = ad.get("spend", 0)
                cpa = ad.get("cpa", 0)
                ctr = ad.get("ctr", 0)
                roas = ad.get("roas", 0)
                print(f"     Spend: {cs}{spend:,.2f} | CPA: {cs}{cpa:,.2f} | CTR: {ctr:.2f}% | ROAS: {roas:.2f}")

                for sig in ad.get("signals", []):
                    print(f"     └ {sig.get('label')}: {sig.get('detail')}")

                genome = ad.get("genome_tags")
                if genome:
                    tags = [f"{k}: {v}" for k, v in genome.items() if v and v != "unknown"]
                    if tags:
                        print(f"     🧬 Winning DNA: {' | '.join(tags)}")

        if not pauses and not scales:
            print("\n✅ No critical issues found. All ads are within healthy baselines.")

        print("\n\n✅ Report dispatched to active OpenCLAW channel.")
    except Exception as e:
        print(f"Failed to parse or format the audit report: {e}")
        
    print("\nPipeline Complete!")

if __name__ == "__main__":
    main()
