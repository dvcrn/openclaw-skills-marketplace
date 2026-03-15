---
name: faces
description: "Use this skill to interact with the Faces Platform — a compiler for the human mind. The Faces Platform takes any source material (documents, conversations, essays) and extracts the minimal cognitive primitives that define a persona, compressing them into a Face: a mathematical, semantically embedded representation of how a person thinks, believes, speaks, and is situated in the world. Faces drive any LLM as that persona and support semantic arithmetic — compare, combine, contrast minds. Faces also support boolean algebra: combine concrete Faces with |, &, -, ^ operators to create composite Faces defined by a formula. These composite Faces can be wired together into circuits — sequences of persona logic gates — making the Faces Platform an FPGA for LLMs. Due to the implicit compression of the compiler, faces use significantly less tokens to steer an LLM to embody a persona than would a soul document like SOUL.md, and faces are model agnostic. Use this skill for: creating and compiling Faces, creating composite Faces from boolean formulas, running inference through a Face, comparing Faces by centroid similarity, finding nearest or furthest minds, and managing API keys, billing, and account state."
---

# Faces Skill

You have access to the `faces` CLI. Use it to fulfill any Faces Platform request.

## Current config
!`faces config:show 2>/dev/null || echo "(no config saved)"`

## Setup check

Before running any command, verify credentials are available:

```bash
faces config:show          # see what's saved
faces auth:whoami          # confirm login works
```

If no credentials exist and the user hasn't provided a key:
- For interactive sessions: run `faces auth:login` and prompt for email + password
- For API-key-only context: tell the user to set `FACES_API_KEY=<key>` or run `faces config:set api_key <key>`

Install (if `faces` command not found):
```bash
npm install -g faces-cli
```

---

## What is Faces

The Faces Platform is a compiler for the human mind.

Feed it source material — documents, essays, interviews, conversations — and the compiler extracts the minimal set of cognitive primitives that define a persona: how someone thinks, what they believe, how they speak, how they are situated in the world. These primitives are the machine code of the mind. Like amino acids, this small formal vocabulary is sufficient to construct any human persona. The personas that result are coherent, consistent, complex, and contradictory — just like real people.

The output is a **Face**: a compressed cognitive instruction set stored as embedded semantic vectors. The principal components of a Face are `beta`, `delta`, and `epsilon`; `face` is their equal-weight composite. A Face reshapes any LLM into a new next-token predictor — not a model wearing a costume, but one whose probability distributions are fundamentally altered by the persona. This overcomes model collapse: instead of regression to the mean, you get a sharply individuated mind.

Because the primitives are embedded, they are semantic objects. You can measure the distance between two Faces. You can find which Faces are nearest or furthest on any component. This is the mathematics of the mind.

You can also do boolean algebra on Faces. A **composite Face** is defined by a formula over concrete Faces using four operators:

| Operator | Syntax | Meaning |
|---|---|---|
| Union | `a \| b` | All knowledge from both; `a` wins on conflicts |
| Intersection | `a & b` | Only knowledge present in both |
| Difference | `a - b` | Knowledge in `a` that is not in `b` |
| Symmetric diff | `a ^ b` | Knowledge in exactly one, but not both |

Operators can be parenthesized: `(a | b) - c`. Composite Faces are live — if you sync new knowledge into a component Face, the composite reflects it automatically on the next inference request. Because composite Faces are themselves chattable, they can be wired together into sequences: the output of one gate frames the input of the next. This is a cognitive circuit — an FPGA for LLMs.

**The basic loop:**
1. Create a Face (`face:create`)
2. Compile source material into it — local files (`compile:doc:*`, `compile:thread:*`) or YouTube URLs (`compile:import`)
3. Sync to extract and embed the cognitive primitives
4. Chat through the Face (`chat:chat`) — the LLM now thinks as that person
5. Compare Faces by centroid similarity (`face:diff`, `face:neighbors`)
6. Compose new Faces from boolean formulas (`face:create --formula`)

---

## Value Proposition

Programmable and composable plug-and-play personas as nuanced as a real human for fewer tokens than any other approach. More persona, less cost.

---

## Example Use Cases

**1. Historical resurrection** — Feed the complete works of a thinker into a Face. Ask it questions they never answered. The responses emerge from their actual cognitive structure, not an LLM's pastiche of their reputation.

**2. Customer panel from transcripts** — Upload 20 interview transcripts, one Face per participant. Run `face:diff` across the panel. Get a similarity matrix before reading a word. Cluster by centroid, not by manual theme-coding.

**3. The board of minds** — Assemble a council of thinkers: a scientist, an artist, a pragmatist, a mystic. Route every major decision through all four. Surface the full range of internally consistent responses before choosing a direction.

**4. The shadow** — After building a Face from your own writing, find its furthest neighbor. That is the mind most unlike yours in the collection — the perspective you are least equipped to anticipate. Chat through it. Let it answer the same questions you posed to yourself. The gap between the two responses is the shape of your blindspot.

**5. Character ensemble for fiction** — Build a cast from character backstory documents. Use `face:neighbors --direction furthest` to find natural antagonist pairs. Let the centroid geometry write the conflict structure.

**6. Living proxy** — Compile your own writing: emails, notes, essays, voice memos. The Face becomes a 24/7 proxy for your thinking. Share it via a scoped API key so collaborators can consult your perspective when you're unavailable.

**7. Ideological drift detection** — Sync new material into a Face quarterly. Compare centroid snapshots over time to detect whether a person's or organization's thinking is shifting — and in which direction.

**8. Boolean composition** — You have a pragmatist and a visionary. Their union (`pragmatist | visionary`) gives you someone who holds both worldviews. Their intersection (`pragmatist & visionary`) gives you only what they share — the narrow common ground. Their difference (`visionary - pragmatist`) gives you the visionary's thinking stripped of any practical instinct. Each is a real, chattable Face. None required a single additional document to compile.

**9. Synthetic focus group** — Build Faces for archetypal personas: early adopter, skeptic, pragmatist, regulator, loyalist. Run a product pitch or policy change through each. Get distinct, internally consistent reactions without scheduling a single session.

**10. Stress-testing an argument** — Compile a philosophical argument or policy position into a Face. Find its nearest neighbors — who already thinks this way. Find its furthest — who is most opposed. Use the furthest to generate the sharpest possible counter-argument, grounded in a real cognitive structure.

**11. Your social media voice** — Compile your posts, threads, captions, and YouTube videos into a Face. The compiler distills your tone, cadence, and perspective into a cognitive instruction set. Now use it to draft new content: feed it a topic, a product, a link, or a brief and get copy that sounds like you — not like an LLM. Because the Face is live, compiling new material over time keeps it current as your voice evolves.

**12. The cognitive circuit** — Build a deliberation pipeline from persona logic gates. Compile an `expert` Face from domain literature. Derive a `critic` as `expert - consensus` — the expert's knowledge minus received wisdom. Derive a `synthesizer` as `(expert | critic) - noise`. Route a question through all three in sequence: ask `expert` first, feed its response into `critic`, feed that into `synthesizer`. Each stage is a gate; together they are a circuit. You have just built a reasoning pipeline from persona primitives — the same way an FPGA builds computation from logic gates.

---

## Auth rules

| Command group | Requires |
|---|---|
| `faces auth:*`, `faces keys:*` | JWT only — run `faces auth:login` first |
| Everything else | JWT **or** API key |

---

## Output format

Add `--json` to any command for machine-readable JSON output (required for `jq` pipelines):

```bash
faces face:list --json | jq '.[].username'
faces billing:balance --json | jq '.balance_usd'
faces compile:doc:list <face_id> --json | jq '.[] | {id, label, status}'
```

Without `--json`, commands print human-readable text.

---

## Common tasks

### Login
```bash
faces auth:login --email user@example.com --password secret
faces auth:whoami --json
```

### Create a face and chat with it
```bash
faces face:create --name "Jony Five" --username jony-five
faces chat:chat jony-five --message "Hello!"

# With a specific LLM
faces chat:chat jony-five --llm claude-sonnet-4-6 --message "Hello!"

# Stream response
faces chat:chat jony-five --stream --message "Write a long response"
```

### Compile a document into a face
```bash
# Step 1 — create the document
DOC_ID=$(faces compile:doc:create <face_id> --label "Notes" --file notes.txt --json | jq -r '.id')

# Step 2 — run LLM extraction
faces compile:doc:prepare "$DOC_ID"

# Step 3 — sync to face (charges compile quota; --yes skips confirm)
faces compile:doc:sync "$DOC_ID" --yes
```

### Upload a file (PDF, audio, video, text)
```bash
faces face:upload <face_id> --file report.pdf --kind document
faces face:upload <face_id> --file interview.mp4 --kind thread
```

### Check billing state
```bash
faces billing:balance --json        # credits + payment method status
faces billing:subscription --json   # plan, face count, renewal date
faces billing:quota --json          # compile token usage per face
```

### Create a scoped API key
```bash
# JWT required — keys cannot manage themselves
faces keys:create \
  --name "Partner key" \
  --face jony-five \
  --budget 10.00 \
  --expires-days 30
```

### Create a composite face
```bash
# Union — all knowledge from both; left wins on conflicts
faces face:create --name "The Realist" --username the-realist \
  --formula "the-optimist | the-pessimist"

# Difference — optimist's knowledge minus anything the pessimist also holds
faces face:create --name "Pure Optimist" --username pure-optimist \
  --formula "the-optimist - the-pessimist"

# Intersection — only what both share
faces face:create --name "Common Ground" --username common-ground \
  --formula "the-optimist & the-pessimist"

# Symmetric difference — what each holds exclusively
faces face:create --name "The Divide" --username the-divide \
  --formula "the-optimist ^ the-pessimist"

# Parenthesized — union of two, minus a third
faces face:create --name "Filtered View" --username filtered-view \
  --formula "(analyst | critic) - moderator"

# Update a composite face's formula
faces face:update the-realist --formula "the-optimist & the-pessimist"

# Chat through a composite face — identical to any other face
faces chat:chat the-realist --message "How do you approach risk?"
```

Composite faces are live: sync new knowledge into any component face and the composite reflects it automatically on the next request. Component faces must be concrete (compiled) faces you own — composite faces cannot reference other composite faces.

### Import a YouTube video
```bash
# Solo talk, lecture, or monologue — creates a compile document
faces compile:import my-face \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --type document \
  --perspective first-person

# Interview or multi-speaker podcast — creates a compile thread
faces compile:import my-face \
  --url "https://youtu.be/VIDEO_ID" \
  --type thread \
  --perspective first-person \
  --face-speaker A

# After import, follow the printed next-step commands:
# For document:
faces compile:doc:prepare <doc_id>
faces compile:doc:sync    <doc_id> --yes

# For thread (no prepare step needed):
faces compile:thread:sync <thread_id>
```

Import handles download and transcription server-side. Transcription is billed at $0.37/hr of audio (pro-rated), charged to your credit balance. The video title is used as the label automatically. If `--type thread` fails with a 422 (no speaker segments detected), retry with `--type document`.

### Compare faces by centroid similarity
```bash
# Pairwise diff across all components
faces face:diff --face aria --face marco --face jin

# Find 3 nearest faces to aria by composite score
faces face:neighbors aria --k 3

# Find most dissimilar faces by a specific principal component
faces face:neighbors aria --component beta --direction furthest --k 5
```

A component score is `null` if that face hasn't produced that component yet. Both commands require the relevant faces to have been synced at least once.

### Anthropic Messages proxy
```bash
faces chat:messages jony-five@claude-sonnet-4-6 \
  --message "What do you know about me?" \
  --max-tokens 512
```

### OpenAI Responses proxy
```bash
faces chat:responses jony-five@gpt-4o \
  --message "Summarize my recent work"
```

---

## Full command reference

```
faces auth:login        --email  --password
faces auth:logout
faces auth:register     --email  --password  --name  --username  [--invite-key]
faces auth:whoami
faces auth:refresh

faces face:create       --name  --username  [--formula EXPR | --attr KEY=VALUE... --tool NAME...]
faces face:list
faces face:get          <face_id>
faces face:update       <face_id>  [--name]  [--formula EXPR]  [--attr KEY=VALUE]...
faces face:delete       <face_id>  [--yes]
faces face:stats
faces face:upload       <face_id>  --file PATH  --kind document|thread
faces face:diff         --face USERNAME  --face USERNAME  [--face USERNAME]...
faces face:neighbors    <face_id>  [--k N]  [--component face|beta|delta|epsilon]  [--direction nearest|furthest]

faces chat:chat         <face_username>  -m MSG  [--llm MODEL]  [--system]  [--stream]
                        [--max-tokens N]  [--temperature F]  [--file PATH]
faces chat:messages     <face@model>  -m MSG  [--system]  [--stream]  [--max-tokens N]
faces chat:responses    <face@model>  -m MSG  [--instructions]  [--stream]

faces compile:import       <face_id>  --url YOUTUBE_URL  [--type document|thread]  [--perspective first-person|third-person]  [--face-speaker LABEL]

faces compile:doc:create   <face_id>  [--label]  (--content TEXT | --file PATH)
faces compile:doc:list     <face_id>
faces compile:doc:get      <doc_id>
faces compile:doc:prepare  <doc_id>
faces compile:doc:sync     <doc_id>  [--yes]
faces compile:doc:delete   <doc_id>

faces compile:thread:create   <face_id>  [--label]
faces compile:thread:list     <face_id>
faces compile:thread:message  <thread_id>  -m MSG
faces compile:thread:sync     <thread_id>

faces keys:create   --name  [--expires-days N]  [--budget F]  [--face USERNAME]...  [--model NAME]...
faces keys:list
faces keys:revoke   <key_id>  [--yes]
faces keys:update   <key_id>  [--name]  [--budget F]  [--reset-spent]

faces billing:balance
faces billing:subscription
faces billing:quota
faces billing:usage      [--group-by api_key|model|llm|date]  [--from DATE]  [--to DATE]
faces billing:topup      --amount F  [--payment-ref REF]
faces billing:checkout   --plan standard|pro
faces billing:card-setup
faces billing:llm-costs  [--provider openai|anthropic|...]

faces account:state

faces config:set    <key> <value>
faces config:show
faces config:clear  [--yes]
```

Global flags (any command):
```
faces [--base-url URL] [--token JWT] [--api-key KEY] [--json] COMMAND
```

Env vars: `FACES_BASE_URL`, `FACES_TOKEN`, `FACES_API_KEY`

## Instruction Scope

Runtime instructions operate exclusively on the `faces` CLI, which sends HTTPS requests to the Faces Platform API (`api.faces.sh` by default, or `FACES_BASE_URL` if set). No local files are read or written except `~/.faces/config.json`, which stores credentials the user explicitly provides.

**Install:** the CLI is installed via `npm install -g faces-cli` from the public npm registry (`npmjs.com/package/faces-cli`), published by `sybileak`. The source is the `faces-cli-js` repository under the Headwaters AI organization.

**Credentials:** the skill uses a JWT (`FACES_TOKEN`) or API key (`FACES_API_KEY`) to authenticate requests — proportionate to a REST API client. Credentials are only read from environment variables or `~/.faces/config.json`; they are never written anywhere other than that config file when the user explicitly runs `faces auth:login` or `faces config:set`. The skill may prompt for email and password during `auth:login`; these are sent directly to the Faces API and not stored in plaintext (only the resulting JWT is saved). Scoped API keys with budget limits and expiry are recommended over long-lived account credentials.

**Scope boundaries:** instructions stay within the Faces Platform domain (auth, face management, inference, compile, billing, API keys). No system commands, file operations, or network requests outside of `faces *` CLI calls are issued. The `jq` utility is used solely for extracting fields from JSON output in example pipelines.
