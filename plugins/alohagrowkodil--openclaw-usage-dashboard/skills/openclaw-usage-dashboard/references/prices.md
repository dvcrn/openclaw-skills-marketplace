# Multi-Provider Pricing Reference

> **Stand: März 2026** — Preise in USD pro 1M Tokens.  
> Diese Datei dokumentiert die im Skill unterstützten Provider und Preise.

## Preis-Updates

Wenn sich Preise ändern oder neue Modelle hinzukommen:

1. **Direkt im Script** (`scripts/usage-dashboard-generic.py` oder `usage-dashboard.py`):
   - `PRICES` Dictionary erweitern
   - `MODEL_COLORS` erweitern (für Visualisierung)
   - Optional: `ALIAS_MAP` erweitern (für kurze Modellnamen)

2. **Diese Datei aktualisieren** mit neuen Preisen und Quellen

---

## Anthropic

| Modell | Input | Output | Cache Read | Cache Write |
|---|---|---|---|---|
| claude-opus-4-6 | $15.00 | $75.00 | $1.50 | $18.75 |
| claude-sonnet-4-6 | $3.00 | $15.00 | $0.30 | $3.75 |
| claude-sonnet-4-5 | $3.00 | $15.00 | $0.30 | $3.75 |
| claude-haiku-4-5 | $0.80 | $4.00 | $0.08 | $1.00 |

🔗 https://www.anthropic.com/pricing

---

## OpenAI

| Modell | Input | Output | Cache Read | Cache Write |
|---|---|---|---|---|
| gpt-4o | $2.50 | $10.00 | $1.25 | $2.50 |
| gpt-4o-mini | $0.15 | $0.60 | $0.075 | $0.15 |
| o3-mini | $1.10 | $4.40 | $0.55 | $1.10 |
| o1 | $15.00 | $60.00 | $7.50 | $15.00 |
| o1-mini | $1.10 | $4.40 | $0.55 | $1.10 |

🔗 https://platform.openai.com/docs/pricing

---

## Google (Gemini)

| Modell | Input | Output | Cache Read | Cache Write |
|---|---|---|---|---|
| gemini-2.0-flash | $0.10 | $0.40 | $0.025 | $0.10 |
| gemini-2.0-pro | $3.50 | $10.50 | $0.875 | $3.50 |
| gemini-1.5-pro | $1.25 | $5.00 | $0.312 | $1.25 |
| gemini-1.5-flash | $0.075 | $0.30 | $0.019 | $0.075 |

🔗 https://ai.google.dev/pricing

---

## Moonshot / Kimi

| Modell | Input | Output | Cache Read | Cache Write |
|---|---|---|---|---|
| kimi-k2.5 | $0.00* | $0.00* | $0.00* | $0.00* |
| moonshot-v1-8k | $0.00* | $0.00* | $0.00* | $0.00* |

> *Preise werden nicht per API geloggt — $0.00 als Platzhalter.  
> Tatsächliche Preise: https://platform.moonshot.cn/pricing

---

## Mistral AI

| Modell | Input | Output | Cache Read | Cache Write |
|---|---|---|---|---|
| mistral-large-latest | $2.00 | $6.00 | $0.50 | $2.00 |
| mistral-medium | $0.60 | $1.80 | $0.15 | $0.60 |
| mistral-small | $0.10 | $0.30 | $0.025 | $0.10 |
| codestral | $0.20 | $0.60 | $0.05 | $0.20 |

🔗 https://mistral.ai/technology/#pricing

---

## Cohere

| Modell | Input | Output | Cache Read | Cache Write |
|---|---|---|---|---|
| command-r-plus | $2.50 | $10.00 | $0.625 | $2.50 |
| command-r | $0.50 | $1.50 | $0.125 | $0.50 |

🔗 https://cohere.com/pricing

---

## Groq

| Modell | Input | Output | Cache Read | Cache Write |
|---|---|---|---|---|
| llama-3.3-70b-versatile | $0.59 | $0.79 | — | — |
| llama-3.1-8b-instant | $0.05 | $0.08 | — | — |
| gemma2-9b-it | $0.20 | $0.40 | — | — |

> Ultra-schnelle Inference, kein Caching  
> 🔗 https://groq.com/pricing/

---

## Hinweise

- **Cache-Preise** gelten nur wenn Prompt Caching vom Modell unterstützt und aktiv ist
- **Groq**: Kein Caching verfügbar, Preise pro 1M Input/Output Tokens
- **Moonshot**: Preise werden nicht in OpenClaw Session-Logs gespeichert — Dashboard zeigt $0.00
- Preise können sich ändern — immer offizielle Provider-Seiten prüfen
