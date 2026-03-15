// Arena Agent - Configuration
// REST API client for Burner Empire AI Arena

// ── Auto-load .env from script directory (no dependencies) ──────────
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

try {
  const __dir = dirname(fileURLToPath(import.meta.url));
  const envText = readFileSync(join(__dir, '.env'), 'utf8');
  for (const line of envText.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq < 1) continue;
    const key = trimmed.slice(0, eq).trim();
    const val = trimmed.slice(eq + 1).trim();
    if (!process.env[key]) process.env[key] = val;   // never override existing
  }
} catch {}   // silently skip if .env doesn't exist
// ─────────────────────────────────────────────────────────────────────

export const ARENA_API_URL = process.env.ARENA_API_URL || 'https://burnerempire.com';
export const ARENA_API_KEY = process.env.ARENA_API_KEY || '';

// LLM
export const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || '';
export const OPENROUTER_BASE_URL = process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1';
export const ARENA_LLM_MODEL = process.env.ARENA_LLM_MODEL || 'qwen/qwen3-32b';
export const LLM_MAX_TOKENS = parseInt(process.env.LLM_MAX_TOKENS || '384');
export const LLM_TEMPERATURE = parseFloat(process.env.LLM_TEMPERATURE || '0.4');

// Timing
export const TICK_INTERVAL_MS = parseInt(process.env.ARENA_TICK_MS || '15000');  // 15s between decisions
export const POLL_NOTIFICATIONS_MS = parseInt(process.env.ARENA_POLL_MS || '5000');

// Logging
export const LOGS_DIR = new URL('./logs/', import.meta.url).pathname;

// Game constants (mirrors server/src/constants.rs)
export const RANK_TITLES = [
  'Street Rat', 'Corner Hustler', 'Block Runner', 'Shot Caller',
  'Lieutenant', 'Underboss', 'Kingpin', 'Cartel Boss',
];

export const DISTRICTS = [
  'downtown', 'eastside', 'the_docks', 'college',
  'the_strip', 'industrial', 'southside', 'uptown',
];

export const DRUGS = ['weed', 'coke', 'meth', 'heroin', 'pills'];

export const DRUG_RANK_REQ = { weed: 0, pills: 1, meth: 2, coke: 3, heroin: 4 };

export const DRUG_PRECURSOR_COST = { weed: 100, pills: 250, meth: 350, coke: 500, heroin: 700 };

export const DRUG_BASE_YIELD = { weed: 12, coke: 5, meth: 8, heroin: 4, pills: 12 };

export const DRUG_BASE_PRICE = { weed: 50, coke: 200, meth: 150, heroin: 300, pills: 100 };

export const QUALITY_TIERS = ['cut', 'standard', 'pure'];

export const GEAR_CATALOG = [
  { type: 'brass_knuckles', name: 'Brass Knuckles', slot: 'weapon', cost: 500, atk: 10, def: 0, consumable: true, special: 'press_double' },
  { type: 'switchblade', name: 'Switchblade', slot: 'weapon', cost: 1500, atk: 5, def: 2, consumable: false },
  { type: 'piece', name: 'Burner Piece', slot: 'weapon', cost: 3000, atk: 8, def: 0, consumable: false, special: 'win_ties' },
  { type: 'leather_jacket', name: 'Leather Jacket', slot: 'protection', cost: 400, atk: 0, def: 6, consumable: false },
  { type: 'kevlar_vest', name: 'Kevlar Vest', slot: 'protection', cost: 2000, atk: 0, def: 12, consumable: true, special: 'survive_loss' },
  { type: 'plated_carrier', name: 'Plated Carrier', slot: 'protection', cost: 5000, atk: 0, def: 15, consumable: true, special: 'survive_loss' },
];

// Heat
export const HEAT_MAX = 100;
export const BUST_CHECK_MIN_HEAT = 25.0;
export const BRIBE_BASE_COST = 500;
export const BRIBE_COST_PER_HEAT = 50;

// PvP
export const PVP_MIN_RANK = 2;
export const STANDOFF_MAX_ROUNDS = 5;

// Cash reserve — never launder below this amount of dirty cash
export const AGENT_DIRTY_CASH_RESERVE = 250;

// Crew
export const CREW_CREATE_COST = 5000;     // clean cash
export const CREW_MAX_MEMBERS = 8;

// HQ Tiers
export const HQ_TIERS = [
  { tier: 0, name: 'None', buy_cost: 0, upkeep: 0 },
  { tier: 1, name: 'Trap House', buy_cost: 50_000, upkeep: 2_000, bonus: '+10% dealer eff' },
  { tier: 2, name: 'Stash House', buy_cost: 200_000, upkeep: 8_000, bonus: '+10% dealer, -10% heat, unlocks Wars' },
  { tier: 3, name: 'Warehouse', buy_cost: 750_000, upkeep: 25_000, bonus: '+15% dealer, -15% heat, +15% launder cap, unlocks Lab' },
  { tier: 4, name: 'Nightclub', buy_cost: 2_500_000, upkeep: 75_000, bonus: '+20% dealer, -20% heat, -5% launder fee, unlocks Vault' },
  { tier: 5, name: 'Penthouse', buy_cost: 10_000_000, upkeep: 250_000, bonus: '+25% dealer, -25% heat, -10% launder fee, -15% bust' },
];

// Feature unlock tiers
export const WAR_MIN_HQ_TIER = 2;
export const LAB_MIN_HQ_TIER = 3;
export const VAULT_MIN_HQ_TIER = 4;

// Additives
export const ADDITIVE_CATALOG = [
  { type: 'acetone', cost: 300 },
  { type: 'benzocaine', cost: 400 },
  { type: 'caffeine', cost: 250 },
  { type: 'lavender_oil', cost: 500 },
  { type: 'phosphorus_red', cost: 800 },
  { type: 'lidocaine', cost: 600 },
];

// Turfs
export const TURF_CLAIM_COST = 5000;       // clean cash
export const TURF_MAX_SOLO = 1;
export const CONTEST_TURF_MIN_RANK = 2;

// Rackets
export const RACKET_TYPES = ['numbers_game', 'protection_ring', 'chop_shop', 'party_pipeline'];

// Front businesses
export const FRONT_TYPES = [
  { type: 'laundromat', cost: 10_000, fee: 0.15, cap: 6_000 },
  { type: 'restaurant', cost: 30_000, fee: 0.12, cap: 15_000 },
  { type: 'car_wash', cost: 20_000, fee: 0.18, cap: 9_000 },
];

// War
export const WAR_BASE_COST = 10_000;

// Stuck detection
export const MAX_ACTION_HISTORY = 5;
export const STUCK_THRESHOLD = 3;

// Rate limit circuit breaker
export const RATE_LIMIT_WINDOW_MS = 60_000;    // 60s window
export const RATE_LIMIT_MAX_HITS = 3;          // 3 rate limits in window → pause
export const RATE_LIMIT_PAUSE_MS = 120_000;    // 2 minute pause
