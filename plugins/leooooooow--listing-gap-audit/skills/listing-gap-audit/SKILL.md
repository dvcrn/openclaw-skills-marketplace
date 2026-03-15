---
name: listing-gap-audit
description: "Listing Gap Audit"
---

        # Listing Gap Audit

        ## Skill Card

        - **Category:** PDP Optimization
        - **Core problem:** How does our listing underperform compared with competitors?
        - **Best for:** Listing rewrite prioritization
        - **Expected input:** Your listing text + competitor listings + product constraints
        - **Expected output:** Gap report across title, bullets, proof, offer framing, and action priorities
        - **Creatop handoff:** Send priority rewrites into script/copy generation workflows

        ## Workflow

        1. Parse listing components: headline, bullets, proof, offer, objections.
2. Benchmark against competitor structure and claim density.
3. Score gaps by conversion impact and implementation effort.
4. Generate rewrite priorities with before/after guidance.

        ## Output format

        Return in this order:
        1. Executive summary (max 5 lines)
        2. Priority actions (P0/P1/P2)
        3. Evidence table (signal, confidence, risk)
        4. 7-day execution plan

        ## Quality and safety rules

        - Do not copy competitor claims verbatim.
- Flag compliance-sensitive claims explicitly.
- Keep recommendations feasible for current product constraints.

        ## License

Copyright (c) 2026 **Razestar**.

This skill is provided under **CC BY-NC-SA 4.0** for non-commercial use.
You may reuse and adapt it with attribution to Razestar, and share derivatives
under the same license.

Commercial use requires a separate paid commercial license from **Razestar**.
No trademark rights are granted.
