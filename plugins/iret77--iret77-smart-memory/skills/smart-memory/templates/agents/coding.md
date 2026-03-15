# Coding Agent — Domain Knowledge [TEMPLATE]
# Wird in JEDEN Coding-Agent-Spawn injiziert, unabhängig vom Projekt.
# Enthält: Dev-Environment, Git-Regeln, Modell-Regeln, cross-project Learnings.

---

## Pflicht: Fortschritts-Reporting
<Snippet das jeder Coding-Agent ausführen muss um Fortschritt zu melden.
Z.B. Mission Control Events, Slack-Posts, etc.>

## LLM-Modell-Regeln
- <Welches Modell für was — mit Begründung>
- Beispiel: "Für Swift-Code nur Opus — GPT erfindet nicht-existente API-Typen"

## Git-Regeln (keine Ausnahmen)
- Niemals force push
- Niemals git history rewrite auf gepushte Commits
- <weitere projektübergreifende Git-Regeln>

## Build & Deploy Umgebung
- <Was ist verfügbar, was nicht — z.B. "Swift nur in CI, nicht lokal">
- <Wie wird deployed>
- <CI-Debug-Tricks>

## Code-Qualität Standards
- Fehler sofort fixen, nicht mit TODO hinterlassen
- Nach Task: CONTEXT.md des Projekts mit neuen Erkenntnissen updaten
- <weitere Standards>

## Slack / Reporting
- <Username beim Posten>
- <Welcher Channel für was>
