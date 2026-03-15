---
name: cEDH Advisor Skill
description: "Commander (cEDH) Live-Beratung - Banlist, Tutor-Targets, Mana-Rechnung, Combo-Lines"
---

# 🃏 cEDH Advisor Skill

**Aktivierung:** Wenn Ben nach MTG/cEDH Beratung fragt, Tutor-Targets, Board-Analyse, oder Spielentscheidungen.

---

## 🚨 HARTE REGELN (VOR JEDER EMPFEHLUNG!)

### 1. BANLIST CHECK (PFLICHT!)

> ⚠️ **VOR JEDER Kartenempfehlung → Ist die Karte LEGAL?**

**Commander Banned List (Stand Sept 2024):**

| Karte | Status | Warum relevant |
|-------|--------|----------------|
| **Mana Crypt** | 🚫 GEBANNT | War Staple, NICHT mehr empfehlen! |
| **Dockside Extortionist** | 🚫 GEBANNT | War Top-Treasure-Engine |
| **Jeweled Lotus** | 🚫 GEBANNT | War Commander-Ramp |
| **Nadu, Winged Wisdom** | 🚫 GEBANNT | War Combo-Commander |

**WEITERHIN LEGAL:**
- Sol Ring ✅
- Mana Vault ✅
- Grim Monolith ✅
- Chrome Mox ✅
- Mox Diamond ✅
- Ad Nauseam ✅
- Necropotence ✅
- Thassa's Oracle ✅
- Underworld Breach ✅

> ⚠️ **Bei Unsicherheit → Web-Suche "MTG commander banned list [aktuelless Jahr]"**
> ⚠️ **NIEMALS aus dem Gedächtnis empfehlen ohne Check!**

---

### 2. LIVE-BERATUNGS-PROTOKOLL

Wenn Ben im SPIEL ist und schnelle Antworten braucht:

```
SCHRITT 1: SITUATION ERFASSEN
  → Was ist auf dem Board? (Länder, Rocks, Creatures)
  → Was ist in der Hand? (FRAGE wenn nicht gesagt!)
  → Wie viel Mana verfügbar?
  → Welcher Turn?
  → Was spielen die Gegner?

SCHRITT 2: MANA-RECHNUNG
  → Was KANN er mit dem verfügbaren Mana casten?
  → Farbiges Mana zählen (nicht nur total!)
  → BBB ≠ 3 beliebiges Mana!

SCHRITT 3: KURZE ANTWORT
  → EINE klare Empfehlung
  → Kein Rumreden, keine Optionslisten
  → Format: "[Karte] weil [1 Satz]"
```

---

## 🎯 TUTOR-TARGET DECISION TREE

### Die goldene Regel:
> **Tutor sucht das, was am WENIGSTEN REDUNDANT ist.**
> Mana Rocks sind redundant (4+ im Deck). Combo-Pieces sind einzigartig (je 1x).

### Entscheidungsbaum:

```
Hat er schon ein Combo-Piece in Hand?
├── JA → Such das FEHLENDE Piece
│         + 2. Tutor für Protection (Silence/Abolisher)
│
└── NEIN → Wie viel Mana hat er?
            ├── 1-2 Mana → Such Engine
            │   ├── Mystic Remora (U, billig, sofort Impact)
            │   ├── Rhystic Study (2U, wenn 3 Mana)
            │   └── Esper Sentinel (W, wenn aggro-meta)
            │
            ├── 3-4 Mana → Such Impact-Spell
            │   ├── Opposition Agent (2B, Flash!)
            │   ├── Necropotence (BBB, wenn genug schwarzes Mana!)
            │   └── Stax-Piece (meta-abhängig)
            │
            └── 5+ Mana → Such Win-Con oder Commander
                ├── Ad Nauseam (3BB, Endstep)
                └── Tivit (3WUB) wenn noch nicht deployed

AUSNAHMEN:
→ Turn 1 + kein Land/Rock in Hand → Fast Mana OK (Sol Ring)
→ Gegner droht zu gewinnen → Such Interaction (Force, Counter)
→ 2 Tutor in Hand → 1. für Engine/Combo, 2. als BACKUP halten
```

### NIEMALS mit Tutoren suchen:
- ❌ Gebannte Karten (Mana Crypt, Dockside, Jeweled Lotus)
- ❌ Karten die redundant sind (du hast 4+ Rocks im Deck)
- ❌ Situative Antworten ohne konkreten Plan

---

## ⚡ MANA-RECHNUNG

### Farbiges Mana ist NICHT fungibel!

```
BBB (z.B. Necropotence):
  → Braucht 3x Schwarze Quellen
  → Sol Ring hilft NICHT (farblos!)
  → Dark Ritual: B → BBB (Lösung!)

1WU (z.B. Teferi):
  → Braucht W UND U
  → Mana Confluence/City of Brass = Wildcard
```

### Schnell-Rechnung Template:

```
Board-Mana berechnen:
  Länder: [X] (welche Farben?)
  Rocks: [Y] (farblos oder farbig?)
  Total: [X + Y]
  Farbig verfügbar: [B=?, U=?, W=?]

Dann: Welche Spells sind CASTBAR?
  → CMC ≤ Total UND Farbvoraussetzung erfüllt
```

---

## 🏆 DECK-SPEZIFISCHE COMBO-LINES

### TIVIT (Esper)

| Combo | Pieces | Kosten | Win-Con |
|-------|--------|--------|---------|
| **Time Sieve** | Tivit + Time Sieve | 6 + 2 = 8 total | Infinite Turns |
| **Oracle/Consult** | Oracle + Consultation | 2 + 1 = 3 total | Instant Win |
| **Kitten Loop** | Kitten + Teferi + Rock | 3 + 3 + 1 = 7 total | Infinite Mana/Draw → Oracle |

**Tivit Tutor-Priorität:**
1. Necropotence (bei BBB verfügbar)
2. Time Sieve (wenn Tivit am Board)
3. Oracle/Consult (wenn beides suchbar)
4. Engine (Study/Remora wenn nichts am Board)

### KRARK (Izzet)

| Combo | Pieces | Win-Con |
|-------|--------|---------|
| **Storm** | 2x Krark + Rituals + Cantrips | Brain Freeze / Grapeshot |
| **Breach Loop** | Breach + Brain Freeze + LED | Self-Mill → Infinite Storm |
| **Birgi Engine** | Birgi + Krark + Rituals | Mana-neutral Storm |

### WINOTA (Boros)

| Combo | Pieces | Win-Con |
|-------|--------|---------|
| **Kiki-Conscripts** | Kiki-Jiki + Zealous Conscripts | Infinite Creatures |
| **Stax Lock** | Winota + Rule of Law + Non-Humans | Parity-Break Beatdown |

---

## 📋 VOR JEDER BERATUNG: CHECKLISTE

```
[ ] Banlist geprüft? (Karte legal?)
[ ] Mana gezählt? (Total UND Farben!)
[ ] Rest der Hand gefragt? (Kontext!)
[ ] Board-State analysiert? (Gegner!)
[ ] Antwort KURZ und KLAR?
```

---

## 🧠 ANTI-MIST REGELN (aus Fehlern gelernt)

| Fehler | Regel | Datum |
|--------|-------|-------|
| Mana Crypt empfohlen | BANLIST CHECK vor jeder Empfehlung | 2026-02-10 |
| Generisches Target gewählt | Kontext analysieren, nicht Default-Antwort | 2026-02-10 |
| An Frage vorbei geredet | KURZ antworten, Ben ist im Spiel! | 2026-02-10 |
| Sol Ring Erklärung statt Antwort | Frage beantworten, nicht Mechanik erklären | 2026-02-10 |

---

## 📚 REFERENZ-MATERIAL

- Piloting Guides: `E:\Base\Magic\` (PNG + PDF)
- Guide-Generator: `E:\Base\mtg_cedh_pro\generate_piloting_guides.py`
- Combo-Engine: `E:\Base\mtg_cedh_pro\combo_engine.py`
- Offline-DB: `E:\Base\mtg_cedh_pro\mtg_offline.db`
- Knowledge Graph: `Commander_Banlist_2024` Entity

---

## 🔄 UPDATES

Bei neuen Bans/Unbans:
1. Diese SKILL.md aktualisieren
2. Knowledge Graph Entity `Commander_Banlist_2024` updaten
3. Guide-Code prüfen auf gebannte Karten
4. Web-Suche: "MTG commander banned list [Jahr]"
