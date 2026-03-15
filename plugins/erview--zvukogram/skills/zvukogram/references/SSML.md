# Zvukogram SSML — Agent Reference (Complete)

Source (official): https://zvukogram.com/node/ssml/

This reference is a **practical, agent-readable** summary of Zvukogram SSML behavior (with Zvukogram-specific extensions/voice limitations). Treat it as the canonical contract for what we generate in podcast pipelines.

## 0) General rules

- SSML is **XML**. Tags must be well-formed.
- Most tags have opening+closing pairs: `<tag>...</tag>`.
- Self-closing example: `<break time="200ms"/>`.
- Some voices may ignore certain tags/attributes (see per-tag notes).

## 1) Safety / formatting contract for pipelines

When producing TTS-ready text for Zvukogram:

- ✅ Allowed: plain text + SSML tags listed in this doc.
- ❌ Forbidden: arbitrary XML/HTML/JSON/YAML structures (e.g. `<tool>...</tool>`), markdown tables/code blocks, or any non-SSML markup.
- If you include SSML, **only** use the supported tags and attributes below.

## 2) Supported tags (overview)

### Pauses
- `<break time="200ms"/>` — pause

### Substitutions / aliases
- `<sub alias="...">TEXT</sub>` — replace how TEXT is spoken

### Prosody / intonation
- `<prosody pitch="..." rate="..." volume="...">...</prosody>`
- `<emphasis level="strong|moderate|reduced|none">...</emphasis>`

### Pronunciation (expert)
- `<phoneme alphabet="ipa" ph="...">...</phoneme>`

### `say-as` interpret-as (main formatting tool)
- `<say-as interpret-as="spell-out|verbatim|characters">...</say-as>`
- `<say-as interpret-as="cardinal">...</say-as>`
- `<say-as interpret-as="ordinal">...</say-as>`
- `<say-as interpret-as="fraction">...</say-as>`
- `<say-as interpret-as="date" format="..." detail="...">...</say-as>`
- `<say-as interpret-as="time" format="hms12|hms24">...</say-as>`
- `<say-as interpret-as="telephone" detail="use-round-word">...</say-as>`
- `<say-as interpret-as="currency">...</say-as>`
- `<say-as interpret-as="money" format="CASE" detail="CURRENCY[_full-form|_short-form][_say-null-cents]">...</say-as>`
- `<say-as interpret-as="bleep|expletive">...</say-as>`

---

## 3) Tag details

### 3.1 `<break>` — pauses

**Syntax:**
```xml
<break time="200ms"/>
<break time="1000ms"/>
```
- `time` can be in `ms` or `s`.

Notes:
- Multiple pauses can be placed sequentially.

Source: https://zvukogram.com/node/pausa/

---

### 3.2 `<sub alias="...">` — alias / substitution

**Use when:** you need consistent pronunciation (brands, acronyms, names).

**Syntax:**
```xml
<sub alias="Оупен Эй Ай">OpenAI</sub>
```

---

### 3.3 `<prosody>` — pitch / rate / volume

**Important:** Zvukogram explicitly warns that `<prosody>` works best on **a whole sentence**. If you wrap only a single word in the middle of a sentence, you may get unwanted pauses around the tag.

**Syntax examples:**
```xml
<prosody pitch="-2st" rate="fast" volume="+3dB">Это пример.</prosody>
<prosody rate="150%">Быстрее на 50%.</prosody>
<prosody pitch="+40Hz">Некоторые голоса поддерживают Hz.</prosody>
```

Allowed attribute families (varies by voice):
- `pitch`: semitones (`+6st`), percent (`-20%`), constants (`x-low|low|medium|high|x-high|default`), sometimes `Hz`.
- `rate`: constants (`x-slow|slow|medium|fast|x-fast|default`), percent styles (`+70%`, `50%`, `150%`).
- `volume`: `dB` (`-15dB`, `+10dB`), constants (e.g. `silent`, `low`, `high`, ...), sometimes percent (`+50%`).

Source: https://zvukogram.com/node/prosody/

---

### 3.4 `<emphasis>` — simple expressiveness

**Syntax:**
```xml
<emphasis level="strong">А сегодня тепло и солнечно!</emphasis>
```

`level` values:
- `strong` (louder + slower)
- `moderate` (default)
- `reduced` (softer + faster)
- `none`

Source: https://zvukogram.com/node/emphasis/

---

### 3.5 `<phoneme alphabet="ipa" ph="...">` — IPA phonemes (expert)

**Use when:** you need precise pronunciation/stress and `+` stress marks are not available/insufficient for a chosen voice.

**Syntax:**
```xml
<phoneme alphabet="ipa" ph="nʲɪkˈitʲənko">Никитенко</phoneme>
```

Notes:
- Stress mark uses the IPA symbol `ˈ`.
- For Russian, unstressed vowels often require different IPA symbols (Zvukogram doc explains `ə`, `ɐ`, etc.).

Source: https://zvukogram.com/node/mfa/

---

## 4) `say-as` interpret-as modes

### 4.1 spell-out / verbatim / characters

**Spell-out (letters):**
```xml
<say-as interpret-as="spell-out">банан</say-as>
<say-as interpret-as="spell-out">ООО</say-as>
```

Notes:
- Different voices may read abbreviations differently.
- Some voices support `verbatim` or `characters` as alternatives.

Source: https://zvukogram.com/node/spell-out/

---

### 4.2 cardinal (quantity)

**Syntax:**
```xml
<say-as interpret-as="cardinal">5</say-as>
```

Use when you need to force "сколько?" (quantity) rather than ordinal.

Advanced voices: support grammatical `format="GENDER_CASE"` (examples in source). Max range: up to billions (trillions may not be spoken).

Source: https://zvukogram.com/node/cardinal/

---

### 4.3 ordinal (order)

**Syntax:**
```xml
Возьми <say-as interpret-as="ordinal">3</say-as> ящик слева
```

Advanced voices: support grammatical `format="GENDER_CASE"` (examples in source).

Source: https://zvukogram.com/node/ordinal/

---

### 4.4 fraction (fractions)

**Syntax:**
```xml
<say-as interpret-as="fraction">1/2</say-as>
<say-as interpret-as="fraction">3+1/2</say-as>
```

Notes:
- `3+1/2` means "три целых и одна вторая" (no spaces).
- Not supported by all voices.

Source: https://zvukogram.com/node/fraction/

---

### 4.5 date

**Basic voices (W3C style):**
```xml
<say-as interpret-as="date" format="dmy" detail="1">5/7/24</say-as>
<say-as interpret-as="date" format="ymd" detail="1">1945.05.09</say-as>
```

Rules:
- Separators: `-`, `/`, `.`
- `format` is one of: `dmy`, `mdy`, `ymd`, `ym`, `my`, `md`, `dm`, `d`, `m`, `y`
- Keep `detail="1"` for this mode.

Not supported by some voices (explicitly listed in source).

**Advanced voices (case + template):**
```xml
<say-as interpret-as="date" format="accusative" detail="d-m-y">25-1-2000</say-as>
<say-as interpret-as="date" format="accusative" detail="m-yw">02-2000</say-as>
```

- `format` becomes grammatical case (`nominative|genitive|dative|accusative|ablative|prepositional`).
- `detail` becomes template (e.g. `d-m-y`, `d-m-yw`, `m-y`, `m-yw`, etc.).
- `y` includes word “год/года”; `yw` suppresses it.
- In advanced mode, VALUE must use `-` as a separator.

Source: https://zvukogram.com/node/date/

---

### 4.6 time

**Syntax:**
```xml
<say-as interpret-as="time">13:45</say-as>
<say-as interpret-as="time" format="hms12">4:50</say-as>
<say-as interpret-as="time" format="hms12">4:50am</say-as>
```

Source: https://zvukogram.com/node/time/

---

### 4.7 telephone

**Syntax:**
```xml
<say-as interpret-as="telephone">88005557778</say-as>
<say-as interpret-as="telephone" detail="use-round-word">+7 (495) 600-35-56</say-as>
```

Notes:
- If you format number with spaces/dashes manually, voices often read it correctly even without `telephone`.
- When using separators, groups should be <= 3 digits or an error may occur.
- Not supported by some voices (explicitly listed in source).

Source: https://zvukogram.com/node/telephone/

---

### 4.8 currency + money

**currency (general):**
```xml
<say-as interpret-as="currency">99.9 USD</say-as>
<say-as interpret-as="currency">10.5 EUR</say-as>
```

**money (advanced voices, with cases):**
```xml
<say-as interpret-as="money" detail="USD">21</say-as>
<say-as interpret-as="money" detail="USD_full-form">21,15</say-as>
<say-as interpret-as="money" detail="USD_short-form_say-null-cents">10</say-as>
```

Notes:
- `money` supports grammatical `format` cases similar to date.
- Supported currencies for `money` are limited (see source).

Source: https://zvukogram.com/node/currency/

---

### 4.9 bleep / expletive (censorship)

**Syntax:**
```xml
Это <say-as interpret-as="bleep">цензурное</say-as> слово
```

Notes:
- `interpret-as="expletive"` is also accepted; effect is the same.
- Bleep duration matches the spoken duration of the censored chunk.

Source: https://zvukogram.com/node/expletive/

---

## 5) Voice support: important exceptions (Zvukogram-specific)

Zvukogram uses different underlying engines; some voices ignore or break on some tags.

Key groups mentioned in official docs:

### “Advanced voices” (cases/gender templates)
These voices are repeatedly called out as “advanced” for `cardinal/ordinal/date/telephone/money`:
- Наталья, Борислав, Марфа, Тарас, Александра, Сергей

### Fraction support
Only the following Russian voices support `fraction` (per source):
- Елена, Карина, Дмитрий, Анна, Борис, Катя, Денис, Дарья, Даниил, Светлана, Екатерина, Бот Татьяна, Бот Максим

### currency / expletive support
`currency` support list (per source):
- Карина, Дмитрий, Анна, Борис, Катя, Денис, Дарья, Даниил, Светлана, Екатерина

`bleep/expletive` support list (per source):
- Карина, Дмитрий, Анна, Борис, Катя, Денис, бот Максим, бот Татьяна

### date exceptions
Voices explicitly listed as NOT supporting the basic `date` mode:
- Алена, Филипп, Оксана, Джейн, Омаж, Захар, Эрмил, Мартын

### telephone exceptions
Voices explicitly listed as NOT supporting `telephone` (except a narrow `+XXXXXXXX` case):
- Филипп, Эрмил, Захар, Алена, Оксана

---

## 6) Quick validation checklist (before calling TTS)

- [ ] Text is plain text + supported SSML only.
- [ ] XML tags are well-formed.
- [ ] No `<voice>` / `<speak>` wrappers are assumed (API may not support them; multi-voice is done by fragmenting).
- [ ] `prosody` wraps whole sentences (avoid wrapping single mid-sentence words).
- [ ] `date/time/telephone/fraction/currency` tags are only used with voices that support them.

