---
name: price-gap-monitor
description: "Price Gap Monitor"
---

        # Price Gap Monitor

        ## Skill Card

        - **Category:** Competitive Intel
        - **Core problem:** When should we react to competitor price/promo changes without destroying margin?
        - **Best for:** Weekly price and promo decisions
        - **Expected input:** Your price/margin constraints + competitor price snapshots + promo context
        - **Expected output:** Price-gap alerts with recommended actions under margin guardrails
        - **Creatop handoff:** Send accepted actions to promo calendar and listing updates

        ## Workflow

        1. Ingest current and historical competitor price snapshots.
2. Compute gap bands vs your target margin floor and promo windows.
3. Classify alerts into watch/act-now/do-not-react.
4. Recommend action with risk note and expected downside.

        ## Output format

        Return in this order:
        1. Executive summary (max 5 lines)
        2. Priority actions (P0/P1/P2)
        3. Evidence table (signal, confidence, risk)
        4. 7-day execution plan

        ## Quality and safety rules

        - Never recommend below margin floor unless explicitly allowed.
- Avoid reacting to one-off noisy price anomalies.
- Show confidence level for each alert.

        ## License

Copyright (c) 2026 **Razestar**.

This skill is provided under **CC BY-NC-SA 4.0** for non-commercial use.
You may reuse and adapt it with attribution to Razestar, and share derivatives
under the same license.

Commercial use requires a separate paid commercial license from **Razestar**.
No trademark rights are granted.
