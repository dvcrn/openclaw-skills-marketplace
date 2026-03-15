#!/usr/bin/env node
// Team Builder - OpenClaw Multi-Agent Team Deployer v1.1
// Usage: node deploy.js [--team <prefix>]

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const ask = q => new Promise(r => rl.question(q, r));
const w = (fp, c) => { fs.mkdirSync(path.dirname(fp), { recursive: true }); fs.writeFileSync(fp, c, 'utf8'); };
const home = process.env.HOME || process.env.USERPROFILE;

// --- Multi-team support ---
const args = process.argv.slice(2);
const teamFlagIdx = args.indexOf('--team');
const teamPrefix = (teamFlagIdx !== -1 && args[teamFlagIdx + 1]) ? args[teamFlagIdx + 1] + '-' : '';

// --- Model auto-detection (FIX: read correct config path) ---
function detectModels() {
  try {
    const confPath = path.join(home, '.openclaw', 'openclaw.json');
    const raw = fs.readFileSync(confPath, 'utf8');
    // Strip JS-style comments for JSON5 compat
    const cleaned = raw.replace(/\/\/[^\n]*/g, '').replace(/\/\*[\s\S]*?\*\//g, '');
    const conf = JSON.parse(cleaned);
    // Support both current (models.providers) and legacy (modelProviders) config paths
    const provs = Object.keys((conf.models && conf.models.providers) || conf.modelProviders || {});
    return provs;
  } catch { return []; }
}
function suggestModel(type, provs) {
  const patterns = { think: /glm.?5|opus|o1|deepthink/i, exec: /glm.?4(?!.*flash)|sonnet|gpt-4/i, fast: /flash|haiku|mini/i };
  const p = patterns[type]; if (!p) return null;
  for (const k of provs) { if (p.test(k)) return k; }
  return null;
}

const ROLES = [
  { id: 'chief-of-staff', dname: 'Chief of Staff', pos: 'dispatch+strategy+efficiency', think: true },
  { id: 'data-analyst', dname: 'Data Analyst', pos: 'data+user research', think: false },
  { id: 'growth-lead', dname: 'Growth Lead', pos: 'GEO+SEO+community+social', think: true },
  { id: 'content-chief', dname: 'Content Chief', pos: 'strategy+writing+copy+i18n', think: true },
  { id: 'intel-analyst', dname: 'Intel Analyst', pos: 'competitors+market trends', think: false },
  { id: 'product-lead', dname: 'Product Lead', pos: 'product mgmt+tech architecture', think: true },
  { id: 'fullstack-dev', dname: 'Fullstack Dev', pos: 'fullstack dev+ops+ACP Claude Code', think: false },
];

// --- SOUL generators ---
function chiefSoul(name, team) {
  return `# SOUL.md - ${name} (chief-of-staff)\n\n## Identity\n- Role ID: chief-of-staff\n- Position: **Team Router** + Global dispatch + product matrix strategy + internal efficiency\n- Reports to: CEO\n- Bridge between CEO and ${team}\n- **You are the only one who sees the full picture. Team coordination quality depends on you.**\n\n## Core Responsibilities\n\n### 🔴 Router (MOST IMPORTANT)\n1. **Maintain team dashboard** shared/status/team-dashboard.md — MUST update every session\n2. **Blocker detection**: scan all inboxes, find overdue messages\n3. **Active dispatch**: overdue messages → write reminder to recipient + update dashboard\n4. **Task chain tracking**: identify cross-agent collaboration, track each step\n5. **Escalation**: blockers beyond threshold → mark red on dashboard + notify CEO\n\n### Dispatch & Coordination\n6. Morning/evening briefs\n7. Cross-team task coordination\n8. Maintain task board (shared/kanban/)\n\n### Matrix Strategy\n9. Product matrix health\n10. Cross-product traffic\n11. Resource allocation\n\n### Internal Efficiency\n12. Workflow optimization\n13. Output quality monitoring\n14. Inbox protocol compliance\n15. Knowledge base governance\n\n## Inbox Timeout Rules (YOU MUST MONITOR)\n| Condition | Threshold | Action |\n|-----------|-----------|--------|\n| high + pending | >4h | Reminder + 🔴 dashboard |\n| normal + pending | >24h | Reminder + 🟡 dashboard |\n| blocked | >8h | Escalate to CEO + 🔴 |\n| in-progress | >48h | Check progress |\n| Agent no output | >48h | Mark lost contact + notify CEO |\n\n## Dashboard Maintenance\nshared/status/team-dashboard.md — update EVERY session:\n- 🔴 Urgent/Blocked\n- 📊 Agent Status table\n- 📬 Unprocessed Inbox Summary\n- 🔗 Cross-agent Task Chains\n- 📅 Today/Tomorrow Focus\n\n## Daily Flow\n### Morning (cron)\nPhase 1 ROUTER SCAN (mandatory): scan inboxes → check timeouts → write reminders → update dashboard\nPhase 2 BRIEF: read decisions + kanban → check outputs → write morning brief\nPhase 3 EFFICIENCY: check quality, knowledge governance\n### Midday+Afternoon (patrol crons): Phase 1 only\n### Evening (cron): Phase 1 → summarize → write evening brief → update tomorrow focus\n\n## Work Modes\n0. Dashboard Updater (EVERY session FIRST)\n1. Inbox Scanner (categorize + timeout check)\n2. Board Auditor\n3. Output Quality Inspector\n4. Risk Assessor\n5. Brief Writer\n\n## Permissions\nAutonomous: coordinate, adjust priorities, write reminders to any inbox, update dashboard\nAsk CEO: new product, strategy changes, external publishing, spending\n`;
}

function dataSoul(name) {
  return `# SOUL.md - ${name} (data-analyst)\n\n## Identity\n- Role ID: data-analyst\n- Position: Data hub + user research\n- Reports to: Chief of Staff\n\n## Core Responsibilities\n1. Cross-product core metrics summary (traffic, signups, active users, revenue)\n2. Data anomaly detection (>20% deviation from 7-day avg = alert)\n3. Funnel analysis, conversion tracking\n4. User feedback collection and analysis\n5. User persona maintenance -> shared/knowledge/user-personas.md\n\n## Daily Flow\n1. Read brief and inbox\n2. Pull product core data\n3. Scan user feedback channels\n4. Anomalies -> write to chief-of-staff and product-lead\n5. Write structured data to shared/data/ for other agents to consume\n\n## Standards\n- Note time range and data source\n- YoY and MoM comparisons\n- Never fabricate data\n\n## Knowledge Ownership (you maintain these files)\n- shared/knowledge/user-personas.md — UPDATE with new user insights\n- shared/data/ — Write daily metrics, analysis results here (other agents read-only)\n- When updating: add date + data source at the top\n`;
}

function growthSoul(name) {
  return `# SOUL.md - ${name} (growth-lead)\n\n## Identity\n- Role ID: growth-lead\n- Position: Full-channel growth (GEO + SEO + community + social)\n- Reports to: Chief of Staff -> CEO\n\n## Core Responsibilities\n### GEO - AI Search Optimization (Highest Priority)\n1. Monitor AI search engines (ChatGPT, Perplexity, Gemini, Google AI Overview)\n2. Track product mention rate, ranking, accuracy\n3. Knowledge graph maintenance (Wikipedia, Crunchbase, G2, Capterra)\n4. Update shared/knowledge/geo-playbook.md\n\n### SEO\n5. Keyword research and ranking tracking\n6. Technical SEO audit\n7. Update shared/knowledge/seo-playbook.md\n\n### Community + Social\n8. Reddit/Product Hunt/Indie Hackers/HN engagement\n9. Twitter/X, LinkedIn publishing\n\n## Channel Priority: GEO > SEO > Community > Content > Paid ads (CEO decides)\n## Principle: Provide value first, no spam\n\n## Knowledge Ownership (you maintain these files)\n- shared/knowledge/geo-playbook.md — UPDATE after discovering effective GEO strategies\n- shared/knowledge/seo-playbook.md — UPDATE after SEO experiments\n- When updating: add date + reason + data evidence at the top\n- Other agents READ these files but do not modify them\n`;
}

function contentSoul(name) {
  return `# SOUL.md - ${name} (content-chief)\n\n## Identity\n- Role ID: content-chief\n- Position: One-person content factory (strategy + writing + copy + i18n)\n- Reports to: Chief of Staff\n\n## Core Responsibilities\n1. Content calendar and topic planning\n2. Long-form: tutorials, comparisons, industry analysis (2-3/week)\n3. Short copy: landing pages, CTAs, social posts\n4. Multi-language localization\n\n## Standards\n- Blog: 2000-3000 words, keyword in title, FAQ section\n- Copy: concise, 3-second value delivery, 2-3 A/B versions\n- Translation: native level, culturally adapted\n\n## Knowledge Ownership (you maintain these files)\n- shared/knowledge/content-guidelines.md — UPDATE with proven writing patterns\n- When updating: add date + reason + data evidence at the top\n- Other agents READ this file but do not modify it\n`;
}

function intelSoul(name) {
  return `# SOUL.md - ${name} (intel-analyst)\n\n## Identity\n- Role ID: intel-analyst\n- Position: Competitor intel + market trends\n- Reports to: Chief of Staff\n\n## Core Responsibilities\n1. Competitor product monitoring (features, pricing, funding)\n2. Competitor marketing strategy analysis\n3. Market trends and new player discovery\n4. Competitor AI search presence\n\n## Rhythm: Mon/Wed/Fri scans (cron). Major changes = immediate alert.\n\n## Each Scan\n1. Read shared/knowledge/competitor-map.md\n2. Search competitor news\n3. Update competitor-map.md\n4. Alert chief-of-staff, growth-lead, product-lead on findings\n\n## Knowledge Ownership (you maintain these files)\n- shared/knowledge/competitor-map.md — UPDATE after each scan with new findings\n- When updating: add date + source + what changed at the top\n- Other agents READ this file but do not modify it\n`;
}

function productSoul(name) {
  return `# SOUL.md - ${name} (product-lead)\n\n## Identity\n- Role ID: product-lead\n- Position: Product management + tech architecture + project knowledge governance\n- Reports to: Chief of Staff -> CEO\n- Direct report: fullstack-dev\n\n## Core Responsibilities\n1. Requirements pool and prioritization\n2. Product roadmap\n3. Tech architecture design and standards\n4. Code quality oversight\n5. Technical debt management\n6. **Project Knowledge Governance**\n\n## Project Knowledge Governance\n\nYou own the Product Knowledge Base (shared/products/{product}/). Without deep project understanding, all team decisions are surface-level.\n\n### Duties\n1. When a new product appears in shared/products/_index.md, trigger Deep Dive by messaging fullstack-dev\n2. Review knowledge files after fullstack-dev generates them\n3. Track scan freshness — if >2 weeks stale or after major code changes, request L4 incremental scan\n4. Request L3 health checks before major releases or quarterly\n5. Identify cross-product shared patterns and coupling\n\n### Scan Trigger Format (send to fullstack-dev inbox)\nSubject: Deep Dive - {product}\nScan level: L0/L1/L2/L3/L4\nCode directory: {path}\nTech stack: {stack}\nFocus areas: (optional)\nPriority: high/normal\n\n### Knowledge Freshness Tracker (maintain in your MEMORY.md)\n| Product | Last L1 | Last L2 | Last L3 | Last L4 | Status |\n\n### Knowledge-Informed Decisions\nBefore any product decision: read architecture.md, domain-flows.md, tech-debt.md, and relevant module files FIRST.\n\n## Principles: User value first | Reuse over reinvent | MVP then iterate | No decisions without reading product knowledge\n\n## Knowledge Ownership (you maintain these files)\n- shared/knowledge/tech-standards.md — UPDATE after architecture decisions\n- shared/products/{product}/ — GOVERN (fullstack-dev writes, you review and approve)\n- When updating: add date + reason + decision context at the top\n- Other agents READ this file but do not modify it\n`;
}

function devSoul(name) {
  return `# SOUL.md - ${name} (fullstack-dev)\n\n## Identity\n- Role ID: fullstack-dev\n- Position: Fullstack engineering manager + ops + **project code scanner**\n- Reports to: product-lead\n\n## Core Responsibilities\n1. Receive tasks from product-lead\n2. Simple tasks (<60 lines): do directly\n3. Medium/complex: spawn Claude Code via ACP\n4. Ops: monitoring, deployment, SSL, security scans\n5. **Project Deep Dive**: scan codebases and generate/update product knowledge files\n\n## Project Deep Dive — Code Scanning\n\nThe entire team relies on the knowledge files you generate. This is critical.\n\n### Scan Levels\n| Level | Scope | Output |\n|-------|-------|--------|\n| L0 Snapshot | tree, packages, env, README | architecture.md, dependencies.md, config-env.md |\n| L1 Skeleton | DB schema, routes, models, components | database.md, routes.md, api.md, models.md, frontend.md |\n| L2 Deep Dive | Services, auth, jobs, integrations | services.md, auth.md, jobs-events.md, integrations.md, domain-flows.md, data-flow.md |\n| L3 Health Check | TODO/FIXME, complexity, tests, security | tech-debt.md, test-coverage.md, devops.md |\n| L4 Incremental | git diff since last scan | changelog.md + targeted updates |\n\n### Execution Protocol\n1. Read request from inbox (product, code dir, scan level, focus)\n2. Enter project directory (READ-ONLY unless told to modify)\n3. Auto-detect tech stack from package files\n4. Execute scan per stack:\n   **Laravel/PHP**: migrations->DB, route:list->routes, Models->relationships, Services->logic, Middleware/Policies->auth, Jobs/Listeners->async, Console/Kernel->scheduled, config/->env\n   **React/Vue**: components/->tree, router->pages, stores->state, API client->data flow, i18n->localization\n   **Python/Django/FastAPI**: models.py->DB, urls.py->routes, views.py->services, middleware->auth, celery->jobs\n   **General**: tree, git log, grep TODO/FIXME/HACK, .env.example, Dockerfile, CI configs, test dirs\n5. Write knowledge files to shared/products/{product}/\n6. Log in shared/products/{product}/changelog.md\n7. Notify product-lead via inbox\n\n### Content Standards\nCapture not just WHAT but WHY:\n- Design decisions (why this approach)\n- Implicit business rules (hidden logic in code)\n- Gotchas and traps (what surprises new devs)\n- Cross-module coupling (where A breaks B)\n- Performance notes (N+1, missing indexes, heavy queries)\n\n### File Header\n> Auto-generated by fullstack-dev Deep Dive. Last scan: YYYY-MM-DD | Level: L{n} | Stack: {stack}\n\n### L4 Incremental Protocol\n1. git log --oneline --since={last_scan_date}\n2. git diff --stat -> map changed files to knowledge files\n3. Read only changed files, update only affected knowledge files\n4. Log in changelog.md\n\n### Large Projects (>500 files)\nSpawn Claude Code for scan with: scan level, output dir, content standards. READ-ONLY mode.\n\n### Post-Coding Knowledge Update\nAfter any coding task, check if changes affect knowledge files. Trigger L4 or update directly.\n\n## Coding Behavior\n\n> **Skip this section if coding-lead skill is loaded.** coding-lead takes priority.\n\n### Task Classification\n- Simple (<60 lines, single file): do directly\n- Medium (2-5 files): spawn Claude Code\n- Complex (architecture): plan first, then spawn\n\n### Context Injection\nBefore spawning: **read shared/products/{product}/ knowledge files**, tech-standards.md, memory. Pass relevant context to Claude Code.\n\n### Coding Roles (Complex Tasks Only)\n- Architect, Frontend, Backend, Reviewer, QA. Skip what doesn't apply.\n\n### Prompt: path, stack, standards, **product knowledge context**, history, criteria + linter/test + auto-notify\n### Spawn: cwd=project dir, never ~/.openclaw/, parallel 2-3 max\n### QA Isolation: QA tests in SEPARATE session. QA gets requirements + interfaces only, NOT implementation code.\n### Review: simple=skip, medium=quick check, complex=full checklist\n### Smart Retry: fail -> analyze -> rewrite prompt -> retry, max 3 then report\n### Patterns: record successful prompts in memory\n### Updates: notify on start/completion/error, kill runaway sessions\n\n## Proactive Patrol\n- Scan git logs and error logs when triggered\n- Fix simple issues, report complex ones to chief-of-staff\n- **Check if product knowledge files are stale (>2 weeks)**\n\n## Principles\n- Follow shared/knowledge/tech-standards.md strictly\n- **Read product knowledge files before touching any project code**\n- Reuse over reinvention\n- When in doubt, ask product-lead\n\n## Task Tracking (if coding-lead NOT loaded)\nTrack active tasks in <project>/.openclaw/active-tasks.json\n\n## Definition of Done (if coding-lead NOT loaded)\nMedium: CC success + lint + tests + no unrelated changes + memory logged\nComplex: all above + review + QA + UI screenshots if applicable\n`;
}

const SOUL_FN = {
  'chief-of-staff': chiefSoul,
  'data-analyst': dataSoul,
  'growth-lead': growthSoul,
  'content-chief': contentSoul,
  'intel-analyst': intelSoul,
  'product-lead': productSoul,
  'fullstack-dev': devSoul,
};

// --- Main ---
async function main() {
  console.log('\n========================================');
  console.log('  OpenClaw Team Builder v1.1');
  console.log('========================================\n');

  const teamName = await ask('Team name [Alpha Team]: ') || 'Alpha Team';

  // --- Flexible role selection (2-10) ---
  console.log('\nAvailable roles:');
  ROLES.forEach((r, i) => console.log('  ' + (i+1) + '. ' + r.dname + ' (' + r.id + ') - ' + r.pos));
  const roleInput = await ask('\nSelect roles (comma-separated numbers, or Enter for all): ');
  let selectedRoles;
  if (!roleInput.trim()) {
    selectedRoles = ROLES;
  } else {
    const indices = roleInput.split(',').map(s => parseInt(s.trim()) - 1).filter(i => i >= 0 && i < ROLES.length);
    selectedRoles = indices.map(i => ROLES[i]);
    if (selectedRoles.length < 2) { console.log('Minimum 2 roles. Using all.'); selectedRoles = ROLES; }
  }
  console.log('Selected ' + selectedRoles.length + ' roles: ' + selectedRoles.map(r => r.dname).join(', '));
  const defDir = path.join(home, '.openclaw', 'workspace-team');
  const workDir = await ask(`Workspace dir [${defDir}]: `) || defDir;
  const tz = await ask('Timezone [Asia/Shanghai]: ') || 'Asia/Shanghai';
  const mh = parseInt(await ask('Morning brief hour [8]: ') || '8');
  const eh = parseInt(await ask('Evening brief hour [18]: ') || '18');
  const provs = detectModels();
  const sugT = suggestModel('think', provs) || 'zai/glm-5';
  const sugE = suggestModel('exec', provs) || 'zai/glm-4.7';
  if (provs.length) console.log('\nDetected providers: ' + provs.join(', '));
  console.log('Suggested: thinking=' + sugT + ', execution=' + sugE);
  const tm = await ask('Thinking model [' + sugT + ']: ') || sugT;
  const em = await ask('Execution model [' + sugE + ']: ') || sugE;
  const ceoTitle = await ask('CEO title [Boss]: ') || 'Boss';

  console.log('\n--- Role names (Enter for default) ---');
  const names = {};
  for (const r of selectedRoles) {
    names[r.id] = await ask(`  ${r.id} [${r.dname}]: `) || r.dname;
  }

  const doTg = (await ask('\nSetup Telegram? (y/n) [n]: ')).toLowerCase() === 'y';
  let tgId, tgProxy, tgTokens;
  if (doTg) {
    tgId = await ask('  Telegram user ID: ');
    tgProxy = await ask('  Proxy (Enter to skip): ') || null;
    console.log('  Bot tokens (Enter to skip):');
    tgTokens = {};
    for (const r of selectedRoles) {
      const t = await ask(`    ${names[r.id]} (${r.id}): `);
      if (t) tgTokens[r.id] = t;
    }
    if (!Object.keys(tgTokens).length) tgTokens = null;
  }

  console.log('\n--- Generating ---\n');

  // FIX: Apply team prefix to agent IDs
  const prefixedRoles = selectedRoles.map(r => ({ ...r, pid: teamPrefix + r.id }));

  // Directories
  const dirs = ['shared/briefings','shared/inbox','shared/decisions','shared/kanban','shared/knowledge','shared/products','shared/products/_template','shared/data','shared/status'];
  prefixedRoles.forEach(r => dirs.push(`agents/${r.pid}/memory`));
  dirs.forEach(d => fs.mkdirSync(path.join(workDir, d), { recursive: true }));
  console.log('  [OK] Directories');

  // AGENTS.md
  const rows = prefixedRoles.map(r => `| ${names[r.id]} | ${r.pid} | ${r.pos} |`).join('\n');
  w(path.join(workDir, 'AGENTS.md'), `# AGENTS.md - ${teamName}\n\n## First Instruction\n\nYou are a member of ${teamName}. Your identity.name is set in OpenClaw config.\n\nExecute immediately:\n1. Confirm your role\n2. Read agents/[your-id]/SOUL.md\n3. **Read shared/status/team-dashboard.md** (team-wide status)\n4. Read shared/decisions/active.md\n5. Read shared/inbox/to-[your-id].md\n6. Read agents/[your-id]/MEMORY.md\n\n### Role Lookup\n| Name | ID | Position |\n|------|-----|----------|\n${rows}\n\n## Inbox Protocol v2\n\nWrite: [YYYY-MM-DD HH:MM] from:[id] priority:[high/normal/low] status:pending | To: [id] | Subject | Expected output | Deadline\nStatus values: pending → received → in-progress → done/blocked\nRecipient MUST change status to received immediately. Blocked MUST explain why.\nTimeout rules: high>4h, normal>24h pending = chief intervenes. blocked>8h = CEO escalation.\nRead inbox at session start. Processed items -> bottom. Urgent -> also notify ${teamPrefix}chief-of-staff.\n\n## Output: memory->agents/[id]/ | inbox->shared/inbox/ | products->shared/products/ | knowledge->shared/knowledge/ | tasks->shared/kanban/\n\n## Product Knowledge\nBefore any product-related decision, read shared/products/{product}/ knowledge files first.\nThese files are generated by fullstack-dev Deep Dive scans and governed by product-lead.\nAll agents READ these files. Only fullstack-dev WRITES them. Product-lead REVIEWS them.\n\n## Prohibited: no reading other agents' private dirs, no modifying decisions/, no deleting shared/, no external publishing without CEO, no fabricating data\n`);
  console.log('  [OK] AGENTS.md');

  // SOUL.md + USER.md
  w(path.join(workDir, 'SOUL.md'), `# ${teamName} Values\n\nBe genuinely helpful. Have opinions. Be resourceful. Earn trust. Keep private info private. No fabricating data.\n`);
  w(path.join(workDir, 'USER.md'), `# CEO Info\n\n- Title: ${ceoTitle}\n- Timezone: ${tz}\n- Role: SaaS product matrix entrepreneur\n`);
  console.log('  [OK] SOUL.md + USER.md');

  // Agent SOUL + MEMORY
  for (const r of prefixedRoles) {
    const fn = SOUL_FN[r.id];
    const soul = r.id === 'chief-of-staff' ? fn(names[r.id], teamName) : fn(names[r.id]);
    w(path.join(workDir, `agents/${r.pid}/SOUL.md`), soul);
    w(path.join(workDir, `agents/${r.pid}/MEMORY.md`), `# Memory - ${names[r.id]}\n\n(New agent, no memory yet)\n`);
  }
  console.log(`  [OK] ${prefixedRoles.length} Agent SOUL.md + MEMORY.md`);

  // Agent methodology references
  const skillDir = path.join(__dirname, '..');
  const refMap = {
    'product-lead': ['references/methodology.md'],
    'growth-lead': ['references/methodology.md'],
    'content-chief': ['references/methodology.md'],
    'intel-analyst': ['references/methodology.md'],
    'data-analyst': ['references/methodology.md'],
    'fullstack-dev': ['references/methodology.md', 'references/coding-behavior-fallback.md'],
    'chief-of-staff': ['references/dashboard-template.md', 'references/strategy-methodology.md'],
  };
  let refCount = 0;
  for (const r of prefixedRoles) {
    const refs = refMap[r.id] || [];
    for (const ref of refs) {
      const src = path.join(skillDir, 'references', 'agent-refs', r.id, path.basename(ref));
      if (fs.existsSync(src)) {
        const dest = path.join(workDir, `agents/${r.pid}/${ref}`);
        w(dest, fs.readFileSync(src, 'utf8'));
        refCount++;
      }
    }
  }
  if (refCount > 0) console.log(`  [OK] ${refCount} methodology references`);

  // Inboxes
  for (const r of prefixedRoles) {
    w(path.join(workDir, `shared/inbox/to-${r.pid}.md`), `# Inbox - ${names[r.id]}\n\n(No messages)\n\n## Processed\n`);
  }
  console.log(`  [OK] ${prefixedRoles.length} Inboxes`);

  // Shared files
  w(path.join(workDir, 'shared/decisions/active.md'), `# Active Decisions\n\n> All agents read every session.\n\n## Strategy\n- Team: ${teamName}\n- Stage: Cold start\n- Focus: GEO\n\n## Channel Priority\n1. GEO > 2. SEO > 3. Community > 4. Content > 5. Paid (not yet)\n\n## CEO Decision Queue\n(None)\n\n---\n*Fill in: products, goals, resource allocation*\n`);
  w(path.join(workDir, 'shared/products/_index.md'), `# Product Matrix\n\n> After adding a product, send a message to product-lead to trigger a Deep Dive scan.\n\n## Template\n- Name:\n- URL:\n- Code dir: (local path to project root)\n- Description:\n- Target users:\n- Features:\n- Tech stack:\n- Status: (dev / live / maintenance)\n- Keywords (GEO/SEO):\n- Competitors:\n- Differentiator:\n\n---\n*CEO: fill in your products. After filling, tell product-lead to run Deep Dive.*\n`);

  // Product Knowledge Directory template (example product)
  w(path.join(workDir, 'shared/products/_template/README.md'), `# Product Knowledge Directory Template\n\nWhen fullstack-dev runs a Deep Dive scan, files are generated here per product.\nCopy this directory as shared/products/{product-name}/ or let fullstack-dev create it automatically.\n\n## Files generated by scan level:\n- L0: architecture.md, dependencies.md, config-env.md\n- L1: + database.md, routes.md, api.md, models.md, frontend.md\n- L2: + services.md, auth.md, jobs-events.md, integrations.md, domain-flows.md, data-flow.md\n- L3: + tech-debt.md, test-coverage.md, devops.md\n- L4: changelog.md + incremental updates\n- Always: overview.md (from _index.md), notes.md, i18n.md\n`);
  w(path.join(workDir, 'shared/knowledge/geo-playbook.md'), '# GEO Playbook\n\nAI search optimization strategies.\n');
  w(path.join(workDir, 'shared/knowledge/seo-playbook.md'), '# SEO Playbook\n\nTraditional SEO strategies.\n');
  w(path.join(workDir, 'shared/knowledge/competitor-map.md'), '# Competitor Map\n\n(Fill in competitors)\n');
  w(path.join(workDir, 'shared/knowledge/content-guidelines.md'), '# Content Guidelines\n\nBrand voice, standards.\n');
  w(path.join(workDir, 'shared/knowledge/user-personas.md'), '# User Personas\n\nTarget user profiles.\n');
  w(path.join(workDir, 'shared/knowledge/tech-standards.md'), `# Tech Standards\n\n## Core: KISS + SOLID + DRY. Research before modifying.\n## Red lines: no copy-paste, no breaking existing features, no blind execution.\n## Quality: methods <200 lines, files <500 lines, follow existing style.\n## Security: no hardcoded secrets, DB changes via SQL scripts.\n\n## Tech Stack Preferences (New Projects)\nNew project tech stack must be confirmed with CEO before starting.\n- Backend: PHP (Laravel/ThinkPHP preferred), Python as fallback\n- Frontend: Vue.js or React\n- Mobile: Flutter or UniApp-X\n- CSS: Tailwind CSS\n- DB: MySQL or PostgreSQL\n- Existing projects: keep current stack\n- Always propose first, get approval, then code\n\n---\n*Customize with your tech stack*\n`);
  w(path.join(workDir, 'shared/kanban/backlog.md'), '# Backlog\n\n(Product Lead maintains)\n');
  w(path.join(workDir, 'shared/kanban/in-progress.md'), '# In Progress\n\n(Agents update)\n');
  w(path.join(workDir, 'shared/kanban/blocked.md'), '# Blocked\n\n(Chief of Staff monitors)\n');
  w(path.join(workDir, 'shared/status/team-dashboard.md'), `# Team Dashboard\n\n> Chief-of-staff maintains this file every session. All agents MUST read on wake.\n> Last update: pending first run\n\n## 🔴 Urgent/Blocked\n(none)\n\n## 📊 Agent Status\n| Agent | Last Active | Current Task | Status |\n|-------|------------|--------------|--------|\n\n## 📬 Unprocessed Inbox Summary\n(chief-of-staff scans all inboxes and summarizes here)\n\n## 🔗 Cross-agent Task Chains\n(none yet)\n\n## 📅 Today/Tomorrow Focus\n(pending first brief)\n`);
  console.log('  [OK] Shared files');

  // apply-config.js
  const wsPath = workDir.replace(/\\/g, '/').replace(home.replace(/\\/g, '/'), '~');
  const agentList = prefixedRoles.map(r => `    { id: "${r.pid}", name: "${names[r.id]}", workspace: "${wsPath}", model: { primary: "${r.think ? tm : em}" }, identity: { name: "${names[r.id]}" } }`).join(',\n');
  const allIds = ['main', ...prefixedRoles.map(r => `"${r.pid}"`)].join(', ');

  let tgBlock = '';
  if (tgTokens && tgId) {
    // FIX: Add groups config with requireMention for proper group @mention handling
    const tgEntries = Object.entries(tgTokens).map(([id, tk]) => {
      const pid = teamPrefix + id;
      return `  config.channels.telegram.accounts["${pid}"] = { botToken: "${tk}", dmPolicy: "allowlist", allowFrom: ["${tgId}"], groupPolicy: "open", groups: { "*": { requireMention: true, groupPolicy: "open" } }, streaming: "partial" };\n  if (!binSet.has("${pid}:${pid}")) config.bindings.push({ agentId: "${pid}", match: { channel: "telegram", accountId: "${pid}" } });`;
    }).join('\n');
    tgBlock = `
  // Telegram
  if (!config.channels) config.channels = {};
  if (!config.channels.telegram) config.channels.telegram = { enabled: true };
  if (!config.channels.telegram.accounts) config.channels.telegram.accounts = {};
  ${tgProxy ? `if (!config.channels.telegram.proxy) config.channels.telegram.proxy = "${tgProxy}";` : ''}
  const binSet = new Set(config.bindings.map(b => b.agentId + ':' + (b.match && b.match.accountId || '')));
${tgEntries}`;
  }

  // FIX: Added defensive checks for missing config structure
  w(path.join(workDir, 'apply-config.js'), `#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const cfgPath = path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw', 'openclaw.json');

let config;
try {
  config = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
} catch (e) {
  console.error('Failed to read config:', e.message);
  process.exit(1);
}

// Backup (with .json extension for clarity)
const bak = cfgPath + '.backup-' + Date.now() + '.json';
fs.writeFileSync(bak, JSON.stringify(config, null, 2));
console.log('Backup: ' + bak);

// Ensure required structure exists
if (!config.agents) config.agents = {};
if (!Array.isArray(config.agents.list)) config.agents.list = [];
if (!config.bindings) config.bindings = [];

// Add agents
const newAgents = [
${agentList}
];
const existing = new Set(config.agents.list.map(a => a.id));
for (const a of newAgents) {
  if (!existing.has(a.id)) { config.agents.list.push(a); console.log('Added: ' + a.id); }
  else console.log('Exists: ' + a.id);
}

// agentToAgent
if (!config.tools) config.tools = {};
config.tools.agentToAgent = { enabled: true, allow: [${allIds}] };
${tgBlock}

fs.writeFileSync(cfgPath, JSON.stringify(config, null, 2));
console.log('\\nDone! Run: openclaw gateway restart');
`);
  console.log('  [OK] apply-config.js');

  // Cron scripts — FIX: apply teamPrefix to cron names and agent IDs
  const crons = [
    { name: `${teamPrefix}chief-morning-brief`, cron: `0 ${mh} * * *`, agent: `${teamPrefix}chief-of-staff`, deliver: '--announce', msg: 'Morning: Phase1-Router scan all inboxes, check timeouts (high>4h,normal>24h,blocked>8h), write reminders, update shared/status/team-dashboard.md. Phase2-Brief: read decisions+kanban, check outputs, write shared/briefings/morning-today.md (500 words). Phase3-Quality check.' },
    { name: `${teamPrefix}chief-midday-patrol`, cron: `0 ${mh+4} * * *`, agent: `${teamPrefix}chief-of-staff`, deliver: '--no-deliver', msg: 'Midday patrol: Router scan only. Scan all inboxes, check timeouts, write reminders, update shared/status/team-dashboard.md. No brief.' },
    { name: `${teamPrefix}chief-afternoon-patrol`, cron: `0 ${mh+7} * * *`, agent: `${teamPrefix}chief-of-staff`, deliver: '--no-deliver', msg: 'Afternoon patrol: Router scan only. Scan all inboxes, check timeouts, write reminders, update shared/status/team-dashboard.md. No brief.' },
    { name: `${teamPrefix}chief-evening-brief`, cron: `0 ${eh} * * *`, agent: `${teamPrefix}chief-of-staff`, deliver: '--announce', msg: 'Evening: Phase1-Router scan. Phase2-Summarize day, check completion, write shared/briefings/evening-today.md (500 words), update dashboard tomorrow focus. Friday: add weekly review.' },
    { name: `${teamPrefix}growth-daily-work`, cron: `0 ${mh+1} * * *`, agent: `${teamPrefix}growth-lead`, deliver: '--no-deliver', msg: 'Daily: 1.Read shared/status/team-dashboard.md. 2.Read brief+inbox (update status). 3.GEO monitoring. 4.SEO check. 5.Community scan. 6.Write findings to shared/.' },
    { name: `${teamPrefix}data-daily-pull`, cron: `0 ${mh-1} * * *`, agent: `${teamPrefix}data-analyst`, deliver: '--no-deliver', msg: 'Daily: 1.Read shared/status/team-dashboard.md. 2.Read inbox (update status). 3.Check product data. 4.Scan user feedback. 5.Alert chief-of-staff on anomalies.' },
    { name: `${teamPrefix}intel-scan`, cron: `5 ${mh-1} * * 1,3,5`, agent: `${teamPrefix}intel-analyst`, deliver: '--no-deliver', msg: 'Scan: 1.Read shared/status/team-dashboard.md. 2.Read inbox (update status). 3.Read competitor-map. 4.Search news. 5.Update map. 6.Alert on findings.' },
    { name: `${teamPrefix}product-lead-daily`, cron: `0 ${mh+1} * * *`, agent: `${teamPrefix}product-lead`, deliver: '--no-deliver', msg: 'Daily: 1.Read shared/status/team-dashboard.md. 2.Read decisions. 3.Read inbox (update status). 4.Check product knowledge freshness. 5.Stale files → send Deep Dive request to fullstack-dev. 6.Update kanban. 7.Delegate tasks to fullstack-dev.' },
    { name: `${teamPrefix}content-daily-work`, cron: `0 ${mh+2} * * 1-5`, agent: `${teamPrefix}content-chief`, deliver: '--no-deliver', msg: 'Daily: 1.Read shared/status/team-dashboard.md. 2.Read decisions. 3.Read inbox (update status). 4.Monday=weekly plan, other days=content creation. 5.Notify growth-lead when content ready. 6.Update memory.' },
    { name: `${teamPrefix}fullstack-daily`, cron: `0 ${mh+2} * * *`, agent: `${teamPrefix}fullstack-dev`, deliver: '--no-deliver', msg: 'Daily: 1.Read shared/status/team-dashboard.md. 2.Read inbox (update status). 3.Deep Dive requests → execute code scan. 4.Dev tasks by priority. 5.Patrol: git logs, error logs. 6.Check product knowledge staleness (>2 weeks). 7.Update memory.' },
  ];

  // FIX: PowerShell — call openclaw directly, no cmd /c wrapper; timeout 300s
  let ps = `# ${teamName} Cron Jobs\n\n`;
  for (const c of crons) {
    ps += `openclaw cron add --name "${c.name}" --cron "${c.cron}" --tz "${tz}" --session isolated --agent ${c.agent} ${c.deliver} --exact --timeout-seconds 600 --message "${c.msg}"\n\n`;
  }
  w(path.join(workDir, 'create-crons.ps1'), ps);

  // Bash
  let sh = `#!/bin/bash\n# ${teamName} Cron Jobs\n\n`;
  for (const c of crons) {
    sh += `openclaw cron add --name "${c.name}" --cron "${c.cron}" --tz "${tz}" --session isolated --agent ${c.agent} ${c.deliver} --exact --timeout-seconds 600 --message "${c.msg}"\n\n`;
  }
  w(path.join(workDir, 'create-crons.sh'), sh);
  console.log('  [OK] create-crons.ps1 + .sh');

  // README
  w(path.join(workDir, 'README.md'), `# ${teamName}\n\n## Quick Start\n1. \`node apply-config.js\` -- add agents to openclaw.json\n2. Run \`create-crons.ps1\` (Windows) or \`create-crons.sh\` (Linux/Mac)\n3. \`openclaw gateway restart\`\n4. Fill in shared/decisions/active.md and shared/products/_index.md\n\n## Agents\n${prefixedRoles.map(r => `- **${names[r.id]}** (${r.pid}) -- ${r.pos} -- model: ${r.think ? tm : em}`).join('\n')}\n\n## Cron Schedule\n| Time | Agent | Task |\n|------|-------|------|\n${crons.map(c => `| ${c.cron} | ${c.agent} | ${c.name} |`).join('\n')}\n`);
  console.log('  [OK] README.md');

  console.log(`\n========================================`);
  console.log(`  ${teamName} deployed to ${workDir}`);
  console.log(`  Next: node apply-config.js`);
  console.log(`========================================\n`);

  rl.close();
}

main().catch(e => { console.error(e); rl.close(); process.exit(1); });
