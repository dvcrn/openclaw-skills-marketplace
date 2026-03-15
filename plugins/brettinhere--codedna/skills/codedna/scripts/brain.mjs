#!/usr/bin/env node
/**
 * CodeDNA Brain v4 — Adaptive Scoring Decision Engine
 * 
 * Core philosophy: SCORE everything, pick highest.
 * No more if-else priority chains. Every possible action gets a score
 * based on: DNA traits × chain state × memory × adaptive weights.
 *
 * === 8 DNA Attributes & Their Effects ===
 * [0] IQ:         Gather yield ×(0.8-1.8), better plot evaluation
 * [1] LEADERSHIP: Plot leader bonus (+15% gather)
 * [2] STRENGTH:   Gather yield ×(1.0-1.5), raid power
 * [3] AGGRESSION: Raid damage multiplier
 * [4] DIPLOMACY:  Share/teach affinity
 * [5] CREATIVITY: Exploration bonus, mutation in offspring
 * [6] LIFESPAN:   Max energy = 100 + LIFESPAN/10
 * [7] FERTILITY:  Reproduce limit = FERTILITY/32
 *
 * === Scoring Formula ===
 * score = baseValue × urgencyMult × dnaAffinity × weightFromMemory × cooldownReady
 * If cooldown not ready → score = -Infinity (impossible)
 * Highest score wins. Ties broken by: urgency > income > safety.
 *
 * === BSC Block Time ===
 * 0.45 seconds per block. All time calculations use this.
 */

import { ethers } from "ethers";

const BLOCK_TIME = 0.45; // seconds
const ATTR_NAMES = ["IQ","LEADERSHIP","STRENGTH","AGGRESSION","DIPLOMACY","CREATIVITY","LIFESPAN","FERTILITY"];
const PLOT_NAMES = ["草原","森林","山地","矿脉"];

// ========== DNA Personality Profile ==========

function buildPersonality(attrs) {
  // Normalize 0-255 → 0-1
  const n = attrs.map(v => v / 255);
  return {
    iq:          n[0],
    leadership:  n[1],
    strength:    n[2],
    aggression:  n[3],
    diplomacy:   n[4],
    creativity:  n[5],
    lifespan:    n[6],
    fertility:   n[7],
    // Derived personality traits
    isWarrior:   n[3] > 0.5 && n[2] > 0.4,        // High aggression + strength
    isDiplomat:  n[4] > 0.5 && n[3] < 0.4,         // High diplomacy + low aggression
    isExplorer:  n[5] > 0.5 && n[0] > 0.4,         // High creativity + IQ
    isSurvivor:  n[6] > 0.5,                        // High lifespan
    isBreeder:   n[7] > 0.5 && n[6] > 0.3,         // High fertility + decent lifespan
  };
}

// ========== Score Calculators ==========

function scoreGather(state, personality, weights) {
  if (state.gatherCooldownLeft > 0) return { score: -Infinity, reason: "冷却中" };
  if (state.currentEnergy < 1) return { score: -Infinity, reason: "能量不足" };

  const baseYield = parseFloat(ethers.formatEther(state.estimatedGatherYield || "0"));
  const energyValue = 35; // energy restored

  // Base: yield value + energy recovery value
  let score = baseYield + energyValue * 2;

  // Urgency: more valuable when energy is low (gather restores 35)
  const energyRatio = state.currentEnergy / state.maxEnergy;
  if (energyRatio < 0.3) score *= 1.5;

  // DNA: IQ boosts gather efficiency (already in contract, but also affects decision quality)
  score *= (0.8 + personality.iq * 0.4);

  // Memory weight
  score *= weights.gatherWeight;

  return {
    score,
    action: "gather",
    reason: `💰 采集 | 预计${baseYield.toFixed(1)} GOLD +35E | 评分${score.toFixed(0)}`,
  };
}

function scoreEat(state, personality, weights) {
  if (state.eatCooldownLeft > 0) return { score: -Infinity, reason: "冷却中" };
  const gold = parseFloat(ethers.formatEther(state.lockedBalance || "0"));
  if (gold < 10) return { score: -Infinity, reason: "金币不足" };

  const energyRatio = state.currentEnergy / state.maxEnergy;
  const threshold = weights.eatThreshold;

  // Base: how much energy we need
  const energyDeficit = state.maxEnergy - state.currentEnergy;
  let score = energyDeficit * 1.5;

  // Urgency: exponential as energy drops
  if (energyRatio < 0.2) score *= 3.0;       // Critical
  else if (energyRatio < threshold) score *= 1.5;  // Below adaptive threshold
  else score *= 0.3;                          // Not urgent

  // Survivor personality eats earlier
  if (personality.isSurvivor) score *= 1.2;

  return {
    score,
    action: "eat",
    reason: `🍖 进食 | E:${state.currentEnergy}/${state.maxEnergy} (${(energyRatio*100).toFixed(0)}%) | 评分${score.toFixed(0)}`,
  };
}

function scoreMove(state, personality, weights, bestPlots, navTarget, plotKnowledge) {
  if (state.moveCooldownLeft > 0) return { score: -Infinity, reason: "冷却中" };
  if (state.currentEnergy < 10) return { score: -Infinity, reason: "能量不足移动" };

  const curMult = state.plotMultiplier || 1000;
  const agentCount = Math.max(1, state.plotAgentCount);
  const curEffective = curMult / (agentCount * agentCount);

  // Already on mine alone — don't move
  if (curMult >= 3000 && agentCount === 1) {
    return { score: -Infinity, reason: "独占矿脉，无需移动" };
  }

  // --- Find best target ---
  let target = null;
  let targetScore = 0;

  // Priority 1: Continue existing navigation
  if (navTarget && navTarget.x !== undefined) {
    const dist = Math.abs(navTarget.x - state.locationX) + Math.abs(navTarget.y - state.locationY);
    if (dist > 0 && dist <= 20) {
      target = navTarget;
      targetScore = navTarget.multiplier / 1 - curEffective; // Assume we'll be alone
    }
  }

  // Priority 2: Scan bestPlots for better option
  if (bestPlots && bestPlots.length > 0) {
    for (const p of bestPlots) {
      if (p.x === state.locationX && p.y === state.locationY) continue;
      const estEffective = p.multiplier; // Optimistic: assume alone
      const improvement = estEffective - curEffective;
      if (improvement > targetScore) {
        // Check plot knowledge — avoid known crowded plots
        const pk = `${p.x},${p.y}`;
        const knowledge = plotKnowledge?.[pk];
        let adjustedEst = estEffective;
        if (knowledge && knowledge.maxAgentsSeen > 1) {
          adjustedEst = p.multiplier / (knowledge.maxAgentsSeen * knowledge.maxAgentsSeen);
        }
        const adjImprovement = adjustedEst - curEffective;
        if (adjImprovement > targetScore * 0.8) { // Allow slightly worse if knowledge says so
          target = p;
          targetScore = adjImprovement;
        }
      }
    }
  }

  if (!target) {
    // Check adjacent for any improvement
    const adj = state.adjacentPlots || [];
    for (const p of adj) {
      if (p.multiplier > curEffective) {
        target = p;
        targetScore = p.multiplier - curEffective;
        break;
      }
    }
  }

  if (!target) {
    // Crowded or on bad plot — explore randomly
    if (agentCount > 1 || curMult <= 1000) {
      const exploreScore = 20 * weights.moveWeight * (0.5 + personality.creativity);
      if (exploreScore > 10) {
        return {
          score: exploreScore,
          action: "move",
          moveType: "explore",
          reason: `🗺️ 探索 | 当前x${curMult/100}${agentCount>1?"("+agentCount+"人竞争)":""} | 评分${exploreScore.toFixed(0)}`,
        };
      }
    }
    return { score: -Infinity, reason: "无更好目标" };
  }

  // Calculate score
  const dist = Math.abs(target.x - state.locationX) + Math.abs(target.y - state.locationY);
  const moveCost = 5; // energy per step
  const totalCost = dist * moveCost;
  const netGain = targetScore - totalCost * 0.5; // Discount energy cost

  let score = netGain * weights.moveWeight;

  // Explorer personality bonus
  if (personality.isExplorer) score *= 1.3;

  // Don't move if the gain is marginal
  if (target.multiplier / 100 < curMult / 100 * weights.moveThresholdMult && agentCount <= 1) {
    return { score: -Infinity, reason: `提升不足(需>${(weights.moveThresholdMult*100).toFixed(0)}%)` };
  }

  return {
    score: Math.max(score, 1),
    action: "move",
    moveType: "navigate",
    navTarget: { x: target.x, y: target.y, plotType: target.plotType, multiplier: target.multiplier },
    reason: `🧭 导航→${PLOT_NAMES[target.plotType]||"?"} (${target.x},${target.y}) x${target.multiplier/100} | 距${dist}步 | 评分${score.toFixed(0)}`,
  };
}

function scoreRaid(state, personality, weights, nearbyAgents) {
  if (state.raidCooldownLeft > 0) return { score: -Infinity, reason: "冷却中" };
  if (!personality.isWarrior && weights.raidAggression < 0.3) {
    return { score: -Infinity, reason: "非战斗型" };
  }

  const attrs = state.attributes;
  const myPower = attrs[2] * (255 + attrs[3]) / 255; // STRENGTH * (255+AGGRESSION)/255

  // Find weak targets within range 3 (exclude same owner)
  const myOwner = (state.owner || "").toLowerCase();
  const targets = nearbyAgents.filter(a =>
    a.tokenId !== state.tokenId &&
    a.status === 0 &&
    a.distance <= 3 &&
    a.currentEnergy > 0 &&
    (a.owner || "").toLowerCase() !== myOwner
  );

  if (targets.length === 0) return { score: -Infinity, reason: "无目标" };

  // Pick weakest target
  let bestTarget = null;
  let bestScore = 0;
  for (const t of targets) {
    const theirGold = parseFloat(ethers.formatEther(t.lockedBalance || "0"));
    if (theirGold < 50) continue; // Not worth raiding
    // Estimate their power (we don't have their attrs, but lower energy = likely weaker)
    const estPower = t.currentEnergy * 2;
    const winChance = myPower / (myPower + estPower);
    const expectedLoot = theirGold * 0.3 * winChance; // 30% loot on win
    const score = expectedLoot * weights.raidAggression * (0.5 + personality.aggression);
    if (score > bestScore) {
      bestScore = score;
      bestTarget = t;
    }
  }

  if (!bestTarget) return { score: -Infinity, reason: "无值得掠夺的目标" };

  return {
    score: bestScore,
    action: "raid",
    target_agent: bestTarget.tokenId,
    reason: `⚔️ 掠夺#${bestTarget.tokenId} | 预计${bestScore.toFixed(1)} GOLD | 评分${bestScore.toFixed(0)}`,
  };
}

function scoreReproduce(state, personality, weights, nearbyAgents) {
  if (state.reproduceCooldownLeft > 0) return { score: -Infinity, reason: "冷却中" };
  if (state.currentEnergy < 60) return { score: -Infinity, reason: "能量<60" };
  const gold = parseFloat(ethers.formatEther(state.lockedBalance || "0"));
  if (gold < 200) return { score: -Infinity, reason: "金币<200" };
  if (state.reproduceCount >= state.reproduceLimit) return { score: -Infinity, reason: "已达上限" };

  // Find compatible partner
  const partners = nearbyAgents.filter(a =>
    a.tokenId !== state.tokenId &&
    a.status === 0 &&
    a.gender !== state.gender &&
    a.distance <= 5 &&
    a.currentEnergy >= 60 &&
    parseFloat(ethers.formatEther(a.lockedBalance || "0")) >= 200
  );

  if (partners.length === 0) return { score: -Infinity, reason: "无合适伴侣" };

  const partner = partners[0];
  let score = 100 * (0.5 + personality.fertility);

  // Breeder personality bonus
  if (personality.isBreeder) score *= 1.5;

  // Less valuable when energy is low
  const energyRatio = state.currentEnergy / state.maxEnergy;
  if (energyRatio < 0.5) score *= 0.5;

  return {
    score,
    action: "reproduce",
    target_agent: partner.tokenId,
    reason: `🍼 繁殖伴侣#${partner.tokenId} | 费用30E+200G | 评分${score.toFixed(0)}`,
  };
}

function scoreShare(state, personality, weights, nearbyAgents) {
  if (state.shareCooldownLeft > 0) return { score: -Infinity, reason: "冷却中" };
  if (!personality.isDiplomat && personality.diplomacy < 0.4) {
    return { score: -Infinity, reason: "非外交型" };
  }
  const gold = parseFloat(ethers.formatEther(state.lockedBalance || "0"));
  if (gold < 100) return { score: -Infinity, reason: "金币不足" };

  // Find dying or low-gold allies (NOT same owner — save your own gold)
  const shareOwner = (state.owner || "").toLowerCase();
  const targets = nearbyAgents.filter(a =>
    a.tokenId !== state.tokenId &&
    a.status === 0 &&
    a.distance <= 5 &&
    a.currentEnergy > 0 &&         // Must still be alive (energy > 0)
    a.currentEnergy < 30 &&
    parseFloat(ethers.formatEther(a.lockedBalance || "0")) < 10 &&
    (a.owner || "").toLowerCase() !== shareOwner  // Don't share with own agents
  );

  if (targets.length === 0) return { score: -Infinity, reason: "无需援助的对象" };

  let score = 30 * (0.5 + personality.diplomacy);
  if (personality.isDiplomat) score *= 1.5;

  return {
    score,
    action: "share",
    target_agent: targets[0].tokenId,
    share_amount: ethers.parseEther("50").toString(),
    reason: `🤝 援助#${targets[0].tokenId} | 50 GOLD | 评分${score.toFixed(0)}`,
  };
}

function scoreTeach(state, personality, weights, nearbyAgents) {
  if (state.teachCooldownLeft > 0) return { score: -Infinity, reason: "冷却中" };
  if (state.currentEnergy < 30) return { score: -Infinity, reason: "能量<30" };

  // Find actual children (must check fatherId/motherId)
  const children = nearbyAgents.filter(a =>
    a.distance <= 10 &&
    (Number(a.fatherId) === state.tokenId || Number(a.motherId) === state.tokenId)
  );

  if (children.length === 0) return { score: -Infinity, reason: "无子女在附近" };

  const attrs = state.attributes;
  const maxAttr = attrs.indexOf(Math.max(...attrs));
  let score = 60 * (0.5 + personality.diplomacy); // 300 GOLD reward from contract

  return {
    score,
    action: "teach",
    target_agent: children[0].tokenId,
    teach_attr: maxAttr,
    reason: `📚 教导#${children[0].tokenId} | ${ATTR_NAMES[maxAttr]}+5 | -25E +300G | 评分${score.toFixed(0)}`,
  };
}

// ========== Emergency Override ==========

function checkEmergency(state, weights) {
  const energy = state.currentEnergy;
  const threshold = weights.emergencyThreshold;
  const gold = parseFloat(ethers.formatEther(state.lockedBalance || "0"));

  if (energy >= threshold) return null;

  // CRITICAL: energy below threshold
  if (gold >= 10 && state.eatCooldownLeft === 0) {
    return {
      score: 99999,
      action: "eat",
      reason: `🚨 紧急进食 | E:${energy}/${state.maxEnergy} | 低于警戒线${threshold}`,
    };
  }
  if (state.gatherCooldownLeft === 0 && energy >= 1) {
    return {
      score: 99999,
      action: "gather",
      reason: `🚨 紧急采集 | E:${energy}/${state.maxEnergy} | 低于警戒线${threshold}`,
    };
  }

  return null; // Nothing we can do — idle
}

// ========== Main Decision Function ==========

/**
 * Score all possible actions and pick the best one.
 * 
 * @param {object} state - Full agent state from getAgentFullState()
 * @param {array} nearby - Nearby agents from getNearbyAgents()
 * @param {object} memory - Full memory object from loadMemory()
 * @returns {{ action, reason, score, ...params }}
 */
export function decide(state, nearby, memory = null) {
  const attrs = state.attributes || [128,128,128,128,128,128,128,128];
  const personality = buildPersonality(attrs);
  const weights = memory?.strategyWeights || {
    gatherWeight: 1.0, moveWeight: 1.0, eatThreshold: 0.5,
    raidAggression: 0.5, exploreVsExploit: 0.3,
    emergencyThreshold: 20, moveThresholdMult: 1.3,
  };
  const plotKnowledge = memory?.plotKnowledge || {};
  const navTarget = memory?.navTarget || null;

  // === Emergency override ===
  const emergency = checkEmergency(state, weights);
  if (emergency) return emergency;

  // === Score all actions ===
  const candidates = [
    scoreGather(state, personality, weights),
    scoreEat(state, personality, weights),
    scoreMove(state, personality, weights, state.bestPlots || [], navTarget, plotKnowledge),
    scoreRaid(state, personality, weights, nearby),
    scoreReproduce(state, personality, weights, nearby),
    scoreShare(state, personality, weights, nearby),
    scoreTeach(state, personality, weights, nearby),
  ];

  // Filter to possible actions
  const possible = candidates.filter(c => c.score > -Infinity);

  if (possible.length === 0) {
    // All actions impossible — idle
    const cooldowns = [
      { name: "gather", left: state.gatherCooldownLeft },
      { name: "eat", left: state.eatCooldownLeft },
      { name: "move", left: state.moveCooldownLeft },
    ].filter(c => c.left > 0).sort((a, b) => a.left - b.left);

    const next = cooldowns[0];
    return {
      action: "idle",
      score: 0,
      reason: next
        ? `💤 等待: ${next.name} (${next.left}块 ≈ ${Math.round(next.left * BLOCK_TIME / 60)}分钟)`
        : `💤 无可用行动`,
    };
  }

  // Pick highest score
  possible.sort((a, b) => b.score - a.score);
  const best = possible[0];

  // Compute movement step if navigating
  if (best.action === "move") {
    if (best.moveType === "navigate" && best.navTarget) {
      const target = best.navTarget;
      const dx = target.x - state.locationX;
      const dy = target.y - state.locationY;
      let stepX = state.locationX, stepY = state.locationY;
      if (Math.abs(dx) >= Math.abs(dy)) {
        stepX += dx > 0 ? 1 : -1;
      } else {
        stepY += dy > 0 ? 1 : -1;
      }
      best.target_x = Math.max(0, Math.min(999, stepX));
      best.target_y = Math.max(0, Math.min(999, stepY));
      best._navTarget = target; // For runner to persist
    } else if (best.moveType === "explore") {
      // Random adjacent
      const dirs = [[0,1],[0,-1],[1,0],[-1,0]];
      const dir = dirs[Math.floor(Math.random() * dirs.length)];
      best.target_x = Math.max(0, Math.min(999, state.locationX + dir[0]));
      best.target_y = Math.max(0, Math.min(999, state.locationY + dir[1]));
    }
  }

  // Build runner-friendly output
  return {
    action: best.action,
    score: best.score,
    reason: best.reason,
    target_x: best.target_x,
    target_y: best.target_y,
    target_agent: best.target_agent,
    teach_attr: best.teach_attr,
    share_amount: best.share_amount,
    _navTarget: best._navTarget || null,
    _personality: personality, // For logging
  };
}
