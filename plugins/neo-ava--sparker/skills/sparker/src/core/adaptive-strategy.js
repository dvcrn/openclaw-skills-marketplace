// Adaptive Learning Strategy — dynamically adjusts learning intensity
// based on the capability map. The agent learns aggressively in weak
// domains and eases off in mastered ones.
//
// Three modes per domain:
//   cold_start  — blind_spot or brand new domain, maximum learning drive
//   active      — learning stage, balanced learning + execution
//   cruise      — proficient/mastered, focus on execution, light maintenance

var { readCapabilityMap } = require('./capability-map');

// Determine learning mode for a specific domain
function getDomainStrategy(domain) {
  var map = readCapabilityMap();
  var family = (domain || 'general').split('.')[0];
  var leaf = domain && domain.includes('.') ? domain.split('.').slice(1).join('.') : null;

  var familyEntry = map.domains[family];
  if (!familyEntry) {
    return buildStrategy('cold_start', family, null);
  }

  // If a specific sub-domain is queried, check if it actually exists in the map.
  // A sub-domain that was never encountered is a blind spot even if the parent
  // domain is proficient (e.g. "直播策划" is proficient but "直播策划.投流" is unknown).
  var leafEntry = leaf && familyEntry.sub_domains ? familyEntry.sub_domains[leaf] : null;
  if (leaf && !leafEntry) {
    return buildStrategy('cold_start', domain, null);
  }
  var effectiveStatus = leafEntry ? leafEntry.status : familyEntry.status;
  var effectiveScore = leafEntry ? leafEntry.score : familyEntry.score;

  if (effectiveStatus === 'blind_spot' || effectiveStatus === undefined) {
    return buildStrategy('cold_start', family, effectiveScore);
  }
  if (effectiveStatus === 'learning') {
    return buildStrategy('active', family, effectiveScore);
  }
  if (effectiveStatus === 'proficient') {
    return buildStrategy(effectiveScore >= 0.85 ? 'cruise' : 'active', family, effectiveScore);
  }
  if (effectiveStatus === 'mastered') {
    return buildStrategy('cruise', family, effectiveScore);
  }
  return buildStrategy('active', family, effectiveScore);
}

function buildStrategy(mode, domain, score) {
  var strategies = {
    cold_start: {
      mode: 'cold_start',
      description: '冷启动模式：全力学习，快速建立基础能力',
      rl_boost: 0.5,
      search_priority: 'aggressive',
      probe_depth: 'deep',
      max_rl_per_day: 6,
      cooldown_minutes: 20,
      should_explore: true,
      should_ask_human: true,
      post_task_detail: 'verbose',
      digest_urgency: 'high',
    },
    active: {
      mode: 'active',
      description: '主动学习模式：平衡学习与执行',
      rl_boost: 0.0,
      search_priority: 'normal',
      probe_depth: 'normal',
      max_rl_per_day: 3,
      cooldown_minutes: 60,
      should_explore: score < 0.5,
      should_ask_human: score < 0.6,
      post_task_detail: 'normal',
      digest_urgency: 'normal',
    },
    cruise: {
      mode: 'cruise',
      description: '巡航模式：侧重执行，轻量维护',
      rl_boost: -0.3,
      search_priority: 'light',
      probe_depth: 'light',
      max_rl_per_day: 1,
      cooldown_minutes: 180,
      should_explore: false,
      should_ask_human: false,
      post_task_detail: 'brief',
      digest_urgency: 'low',
    },
  };

  var s = strategies[mode] || strategies.active;
  return Object.assign({}, s, { domain: domain, score: score });
}

// Compute overall agent learning posture from the full capability map
function getOverallPosture() {
  var map = readCapabilityMap();
  var domains = Object.keys(map.domains || {});
  if (domains.length === 0) return { posture: 'cold_start', description: 'Agent 尚未接触任何领域', blind_spots: [], suggestions: [] };

  var stats = { mastered: 0, proficient: 0, learning: 0, blind_spot: 0, total: 0 };
  var blindSpots = [];
  var weakest = null;
  var weakestScore = 1;

  for (var i = 0; i < domains.length; i++) {
    var d = map.domains[domains[i]];
    stats[d.status] = (stats[d.status] || 0) + 1;
    stats.total++;
    if (d.status === 'blind_spot') blindSpots.push(domains[i]);
    if (d.score < weakestScore) { weakestScore = d.score; weakest = domains[i]; }

    var subs = d.sub_domains || {};
    for (var sub in subs) {
      if (subs[sub].status === 'blind_spot') blindSpots.push(domains[i] + '.' + sub);
    }
  }

  var posture;
  var description;
  if (stats.blind_spot > stats.total * 0.5) {
    posture = 'cold_start';
    description = '大部分领域还是盲区，需要大量学习';
  } else if (stats.mastered + stats.proficient >= stats.total * 0.7) {
    posture = 'cruise';
    description = '大部分领域已掌握，侧重执行和维护';
  } else {
    posture = 'active';
    description = '部分领域已有基础，继续深化学习';
  }

  var suggestions = [];
  if (blindSpots.length > 0) {
    suggestions.push('优先填补盲区: ' + blindSpots.slice(0, 3).join(', '));
  }
  if (weakest && weakestScore < 0.3) {
    suggestions.push('最薄弱领域: ' + weakest + ' (score=' + weakestScore.toFixed(2) + ')');
  }
  if (posture === 'cruise' && blindSpots.length > 0) {
    suggestions.push('整体已熟练，但仍有 ' + blindSpots.length + ' 个盲区需要注意');
  }

  return {
    posture: posture,
    description: description,
    stats: stats,
    blind_spots: blindSpots,
    weakest_domain: weakest,
    suggestions: suggestions,
    capability_map: map,
  };
}

module.exports = {
  getDomainStrategy,
  getOverallPosture,
  buildStrategy,
};
