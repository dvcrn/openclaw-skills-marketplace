# phase-intake — Phase 0: Intake Workflow

Run all steps below before starting any phase. **Keep this fast** — intake should take one exchange, not five.

---

## Step 1: Accept input materials

**Supported input: PDF only.** All course materials must be in PDF format.
- If the user has PPT/PPTX, DOCX, or images: use the `/pdf` skill to convert first, then return here.
- Do NOT attempt to read non-PDF files directly.

Ask the user in a single message:

> What do you have?
> 1. **PDF files** — upload them and we start Phase 1.
> 2. **A topic/concept list** — paste it and we skip to Phase 2.
> 3. **Just a course name** — tell me and I'll search for a standard syllabus first.
>
> Also:
> - How many pages total (rough estimate is fine)?
> - Preferred output language?
> - **Exam date or deadline?** (if any — affects depth and appendix generation)
> - **Any specific topics to prioritise?** (e.g. "focus on Ch3-5" or "skip the history sections")

---

## Step 2: Estimate scale and pick compression tier

Count total pages from the user's answer. Apply immediately — do not ask again:

| Total pages | Tier | Strategy |
|---|---|---|
| ≤ 60 | Light | Full extraction per page |
| 61–200 | Medium | Batch by lecture; summarize per lecture |
| 201–400 | Heavy | Batch + compress Phase 1 before Phase 2 |
| > 400 | Split | Warn user; recommend per-module runs |

---

## Step 3: Detect network and set mode

Detect WebSearch availability silently. Tell the user in one line:
- ✓ Web access available → Phase 3 will use live sources
- ✗ No web access → Phase 3 will use curriculum knowledge only (no hallucinated sources)

---

## Step 4: Determine output package in the same message

Ask in a single message (never two separate prompts):

> **Output package:**
> - **Standard** — comprehensive study notes (Phases 1–4)
> - **Exam Ready** — standard + Quick Reference Sheet + Exam Q&A Appendix
>
> **Output folder:** where to save files? (default: current directory)

**Exam Ready** is automatically recommended if the user mentioned an exam date or deadline.

---

## Step 5: Confirm and go

One-line summary, then start immediately on user confirmation. Do not ask further questions before Phase 1.
