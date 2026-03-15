// Spark chain detection — automatically discovers relationships between sparks.
// Detects: supports, contradicts, refines, requires, supersedes.

const { computeSimilarities, sparkToText } = require('../core/similarity');
const { generateId, getNodeId } = require('../core/asset-id');

const SIMILARITY_THRESHOLD = 0.6;

function createRelation(type, targetId, strength, evidence) {
  return {
    type: type,
    target_id: targetId,
    strength: typeof strength === 'number' ? strength : 0.5,
    evidence: evidence || '',
    created_by: getNodeId(),
    created_at: new Date().toISOString(),
  };
}

// Detect relationships between a new spark and existing sparks
async function detectRelations(newSpark, existingSparks) {
  var relations = [];
  var newText = sparkToText(newSpark);
  var newDomain = (newSpark.domain || 'general').split('.')[0];

  var sameDomainSparks = existingSparks.filter(s => {
    var d = (s.domain || 'general').split('.')[0];
    return d === newDomain && s.id !== newSpark.id;
  });

  if (sameDomainSparks.length === 0) return relations;

  var similarities = await computeSimilarities(newText, sameDomainSparks);

  for (var i = 0; i < similarities.length; i++) {
    var sim = similarities[i];
    if (sim.score < SIMILARITY_THRESHOLD) continue;

    var existing = sim.item;
    var relType = inferRelationType(newSpark, existing, sim.score);

    if (relType) {
      relations.push(createRelation(
        relType.type,
        existing.id,
        sim.score,
        relType.evidence
      ));
    }
  }

  return relations;
}

function inferRelationType(newSpark, existingSpark, similarity) {
  var newContent = (newSpark.content || sparkToText(newSpark)).toLowerCase();
  var existContent = (existingSpark.content || sparkToText(existingSpark)).toLowerCase();

  // Check for contradiction signals
  var contradictionSignals = [
    { pos: /应该|要|必须|推荐/, neg: /不要|避免|不应|禁止/ },
    { pos: /快速|简短|直接/, neg: /详细|深入|慢慢/ },
    { pos: /开放|公开/, neg: /私密|保密|限制/ },
  ];

  for (var i = 0; i < contradictionSignals.length; i++) {
    var sig = contradictionSignals[i];
    if ((sig.pos.test(newContent) && sig.neg.test(existContent)) ||
        (sig.neg.test(newContent) && sig.pos.test(existContent))) {
      return {
        type: 'contradicts',
        evidence: 'Opposing advice detected: possible context-dependent contradiction',
      };
    }
  }

  // Check for refinement (new is more specific)
  var newDomain = newSpark.domain || '';
  var existDomain = existingSpark.domain || '';
  if (newDomain.startsWith(existDomain + '.') || newContent.length > existContent.length * 1.5) {
    if (similarity > 0.7) {
      return {
        type: 'refines',
        evidence: 'New spark provides more specific guidance in the same area',
      };
    }
  }

  // Check for supersedes (new is newer and has higher confidence)
  var newConf = newSpark.confidence || (newSpark.credibility && newSpark.credibility.composite) || 0;
  var existConf = existingSpark.confidence || (existingSpark.credibility && existingSpark.credibility.composite) || 0;
  if (newConf > existConf && similarity > 0.8) {
    var newDate = new Date(newSpark.created_at || 0).getTime();
    var existDate = new Date(existingSpark.created_at || 0).getTime();
    if (newDate > existDate) {
      return {
        type: 'supersedes',
        evidence: 'Newer spark with higher confidence on the same topic',
      };
    }
  }

  // Default: supports (high similarity, same direction)
  if (similarity > 0.65) {
    return {
      type: 'supports',
      evidence: 'Similar insights that reinforce each other',
    };
  }

  return null;
}

// Detect contradictions specifically (for user notification)
async function detectContradictions(newSpark, existingSparks) {
  var relations = await detectRelations(newSpark, existingSparks);
  return relations.filter(r => r.type === 'contradicts');
}

module.exports = {
  createRelation,
  detectRelations,
  inferRelationType,
  detectContradictions,
  SIMILARITY_THRESHOLD,
};
