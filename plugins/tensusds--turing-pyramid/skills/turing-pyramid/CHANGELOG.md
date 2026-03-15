# Changelog

## v1.17.1 (2026-03-08)
- **Research thread integration**: 3 new actions in `understanding` need — continue/start/synthesize research threads (migrated from weighted-daemon)
- **Understanding need tuned**: importance 3→4, decay 12h→8h — fires more often to support research work
- **Scanner upgrade**: `scan_understanding.sh` now detects recent activity in `research/threads/`
- **Cross-need impact**: added understanding → coherence (+0.15)
- **14 new tests**: config validation, cross-need impacts, scanner thread detection, weight distribution
- **Token optimization**: designed to replace isolated daemon sessions with in-heartbeat research actions

## v1.17.0 (2026-03-08)
- **Follow-up system**: create-followup.sh, resolve-followup.sh, integrated in run-cycle.sh + mark-satisfied.sh
- **35 follow-up tests**: all passing

## v1.15.2 (2026-03-07)
- **ClawHub review fixes** — removed `primaryEnv` (WORKSPACE is not a credential), added Pre-Install Checklist, clarified no API keys required by default

## v1.15.0 (2026-03-07)
- **Starvation Guard** — prevents low-importance needs from being perpetually ignored
  - Detects needs at satisfaction floor (≤ threshold) without action for N hours
  - Forces starving needs into cycle, bypassing probability roll
  - Reserves slots: forced needs first, remaining for top-N by tension
  - Configurable: `settings.starvation_guard` in needs-config.json
    - `enabled` (default: true)
    - `threshold_hours` (default: 48) — how long at floor before forcing
    - `sat_threshold` (default: 0.5) — satisfaction level considered "floor"
    - `max_forced_per_cycle` (default: 1) — max forced actions per cycle
  - `mark-satisfied.sh` now records `last_action_at` timestamp per need
  - 8 new test cases in `tests/test_starvation_guard.sh`
- **Action Staleness** — penalizes recently-selected actions to increase variety
  - Tracks `action_history` per need in state file (action name → last selected timestamp)
  - Actions selected within `window_hours` get weight × `penalty` multiplier
  - `min_weight` floor prevents total suppression (always some chance)
  - Configurable: `settings.action_staleness` in needs-config.json
    - `enabled` (default: true)
    - `window_hours` (default: 24) — how long an action stays "stale"
    - `penalty` (default: 0.2) — weight multiplier for stale actions (80% reduction)
    - `min_weight` (default: 5) — minimum effective weight
  - 8 new test cases in `tests/test_action_staleness.sh` (statistical distribution tests)
- **Needs Customization Onboarding** — guided conversation for agent + human to review/adjust need priorities, importance weights, and decay rates on first install

## v1.14.7 (2026-03-06)
- **Intention actions refactored** — better triggering in mid-range:
  - Renamed "execute intention" → "work on intention from INTENTIONS.md" (impact 2.1→1.5)
  - Added "continue progress on active intention" (impact 1.3, weight 35)
  - Both now mid-range (1.0-1.9) for ~45% chance at sat=2.0

## v1.14.6 (2026-03-04)
- **Post-install chmod instructions** — ClawHub doesn't preserve +x bits, added fix to SKILL.md

## v1.14.4 (2026-03-04)
- **Rounding fix** — sat→0.5 formula now correctly rounds to nearest 0.5
- **Config-driven action_probability** — reads from config instead of hardcoded case
- **flock in mark-satisfied.sh** — prevents race conditions with run-cycle.sh
- **TODO.md cleanup** — reflects current state accurately
- **Minor fixes:**
  - SKILL.md version reference updated
  - Stress test formula aligned with production
  - Removed unused timezone field from decay-config.json

## v1.14.3 (2026-03-04)
- **Critical test suite overhaul** — tests now verify REAL code, not reimplementations:
  - test_decay.sh: Fixed to test linear decay (was exponential)
  - test_tension.sh: Fixed formula to `importance × (3 - round(sat))`
  - test_floor_ceiling.sh: Added floor enforcement test
  - test_full_cycle.sh: Fixed expectations for integer rounding
- **SKIP_SCANS=true** for unit tests — predictable state without event scan interference
- **Discovered scan design**: scan scripts use `last_satisfied`, not current satisfaction
- **All 12 tests pass** (11 unit + 1 integration)

## v1.14.2 (2026-03-04)
- **More mid-impact autonomy actions** — "continue existing work" pattern:
  - "continue yesterday's unfinished task" (1.5)
  - "push incremental progress on active project" (1.6)
  - "complete a TODO item I added myself" (1.5)
  - "review and iterate on recent output" (1.3)
- **Autonomy now has 23 actions** — better coverage across all impact levels
- **New tests:**
  - test_autonomy_coverage.sh — verifies impact range distribution + continue-work actions
  - test_crisis_mode.sh — verifies all needs have ≥3 high-impact actions
- **Total: 11 unit tests, 4 integration/regression tests**

## v1.14.1 (2026-03-04)
- **Expanded test coverage:**
  - test_action_probability.sh — 6-level probability config
  - test_impact_matrix.sh — 6-level impact distribution
  - test_day_night_decay.sh — multiplier logic
  - test_audit_scrubbing.sh — sensitive data redaction
- **Total: 9 unit tests, 3 integration tests**

## v1.14.0 (2026-03-04)
- **Mid-impact autonomy actions** — fills gap between "start new" and "just note":
  - "execute intention from INTENTIONS.md" (2.1)
  - "advance project/thread from TODO.md or dashboard" (1.9)
  - "refine script/skill/doc I created in workspace" (1.7)

## v1.13.1 (2026-03-03)
- **6-level action probability** — granular base chances (100%→90%→75%→50%→25%→0%)
- **Consistent skip at sat=3.0** — both action probability and impact selection skip
- **Configurable probabilities** — `action_probability` section in needs-config.json

## v1.13.0 (2026-03-03)
- **Autonomy decay slowdown** — 24h → 36h (reduces chronic tension)
- **6-level impact matrix** — granular sat levels (0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
- **Smoother transitions** — big action probability decreases gradually as satisfaction rises
- **sat=3.0 skip** — fully satisfied needs don't waste action slots
- **Crisis mode** — sat=0.5 guarantees 100% big actions (all needs have ≥3)
- **Test improvements** — homeostasis test now sets WORKSPACE, increased cycles 30→50

## v1.12.3 (2026-03-03)
- **Audit log scrubbing** — sensitive patterns (tokens, emails, passwords, cards) redacted before logging
- **SKILL.md frontmatter** — added metadata with `requires.env: [WORKSPACE]` and `requires.bins` for ClawHub registry
- **Documentation** — scrubbing patterns documented

## v1.12.2 (2026-03-03)
- **Final ClawHub fixes:**
  - Curiosity removed from needs-state.json (was only in cross-impact before)
  - Added explicit "No Network/System Access" section to SKILL.md
  - Removed stale backup files from assets/
  - grep-verified: scripts contain no curl/wget/ssh/sudo/systemctl/docker

## v1.12.1 (2026-03-03)
- **ClawHub analyzer fixes:**
  - Curiosity orphan removed from cross-need-impact.json
  - External actions flagged with `"external": true, "requires_approval": true`
  - Limitations documented honestly (audit = claims, not verified facts)
  - Env vars (WORKSPACE, TURING_CALLER) now explicit in SKILL.md

## v1.12.0 (2026-03-03)
- **Audit trail** — all mark-satisfied calls logged to `assets/audit.log` with timestamp, reason, caller
- **--reason parameter** — mark-satisfied.sh now accepts `--reason "..."` for transparency
- **Data transparency docs** — SKILL.md now documents exactly what files are read/written
- **TURING_CALLER env** — distinguishes heartbeat vs manual calls in audit

## v1.11.0 (2026-03-03)
- **Day/Night decay matrices** — slower decay at night (×0.5), configurable in `assets/decay-config.json`
- **Race condition protection** — flock on state file prevents parallel cycle corruption
- **Garbage cleanup action** — new integrity action to scan workspace for unused/orphaned files
- **Stress test** — `tests/integration/test_stress_homeostasis.sh` validates recovery from crisis state
- New script: `scripts/get-decay-multiplier.sh`

## v1.10.11 (2026-02-27)
- Version alignment fix

## v1.10.1 (2026-02-25)
- **fix:** STATE_FILE path bug (`.needs.$need` → `.$need`)
- **docs:** Clean SKILL.md with ASCII tables

## v1.10.0 (2026-02-25)
- Test infrastructure (6 tests: unit, integration, regression)
- Homeostasis stability test

## v1.9.0 (2026-02-25)
- Autonomous Dashboard system
- Personal intentions tracking

## v1.8.0 (2026-02-24)
- VALUES.md integration
- Boundary logging system

## v1.7.1 (2026-02-25)
Balance fixes after stress testing:
- connection decay: 4h → 6h
- closure decay: 8h → 12h  
- security → autonomy deprivation: -0.30 → -0.20

## v1.7.0 (2026-02-25)
- **Cross-need impact system** — needs influence each other
- on_action: satisfying one need boosts related needs
- on_deprivation: deprived needs drag down related needs
- 22 cross-need connections
- Float satisfaction (0.00-3.00)
- Protection: floor=0.5, ceiling=3.0, cooldown=4h

## v1.6.0 (2026-02-24)
- Float impacts (0.0-3.0)
- Impact ranges: low/mid/high
- Weighted action selection

## v1.5.3 (2026-02-24)
- Dynamic max_tension from config

## v1.5.0 (2026-02-24)
- Tension bonus to action probability
- Formula: `final_chance = base + (tension × 50 / max_tension)`

## v1.4.3
- Complete 10-need system
- Decay mechanics
- Impact matrix
