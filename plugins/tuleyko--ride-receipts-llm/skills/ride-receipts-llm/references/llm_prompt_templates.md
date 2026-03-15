# LLM prompt templates (ride-receipts-llm)

Use these templates when running the semantic extraction step.

## One-shot extraction prompt (per email)

System/user message to the LLM (adapt as needed):

- Input: one email JSON object with keys like:
  `provider, gmail_message_id, email_date, subject, from, snippet, text_html`

Prompt:

> You are extracting a structured ride record from ONE ride receipt email.
> 
> Use `text_html` as primary (raw HTML). Use `snippet` only if `text_html` is empty.
> 
> Return EXACTLY one JSON object matching this schema:
> 
> {
>   "provider": "Uber|Bolt|Yandex|Lyft",
>   "source": {"gmail_message_id":"...","email_date":"YYYY-MM-DD HH:MM","subject":"..."},
>   "ride": {
>     "start_time_text": "...",
>     "end_time_text": "...",
>     "total_text": "...",
>     "currency": "EUR|PLN|USD|BYN|RUB|UAH|null",
>     "amount": 12.34,
>     "pickup": "...",
>     "dropoff": "...",
>     "pickup_city": "...",
>     "pickup_country": "...",
>     "dropoff_city": "...",
>     "dropoff_country": "...",
>     "payment_method": "...",
>     "driver": "...",
>     "distance_text": "...",
>     "duration_text": "...",
>     "notes": "..."
>   }
> }
> 
> Constraints:
> - Never hallucinate. If missing/unclear, use null.
> - Keep addresses verbatim.
> - `amount` must be numeric; if you only have text, set amount=null and put the text in total_text.
> - Use the email’s exact wording for times/addresses; do not normalize.

## Repair prompt (only when important fields are missing)

Inputs:
- the same email JSON object
- the previously extracted ride JSON object
- a list of missing important fields

Prompt:

> You are repairing a previously extracted ride record.
> 
> Goal: fill ONLY these missing fields (leave everything else unchanged): <MISSING_FIELDS>
> 
> Use the email body (`text_html`, and `snippet` as fallback) to find values.
> 
> Rules:
> - Do NOT overwrite any existing non-null value.
> - Never hallucinate; if not present, keep null.
> - Return EXACTLY one JSON object with the SAME schema as before.
> 
> Provide values only if supported by the email.
