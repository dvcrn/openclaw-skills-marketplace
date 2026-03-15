// Data sanitizer — strips PII and sensitive information before publishing.
// Enforces STP privacy rules (Section 7.2).

const PII_PATTERNS = [
  /[\w.-]+@[\w.-]+\.\w{2,}/g,                    // email
  /\b1[3-9]\d{9}\b/g,                             // Chinese phone
  /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g,               // US phone
  /\b\d{6}(19|20)\d{2}(0[1-9]|1[0-2])\d{6}\b/g,  // Chinese ID
  /\b\d{3}-\d{2}-\d{4}\b/g,                       // US SSN
];

const NAME_PATTERNS = [
  /(?:我叫|我是|姓名[：:]?\s*)[^\s,，。.]{2,8}/g,
  /(?:name[:\s]+)\w[\w\s]{1,30}/gi,
];

const COMPANY_PATTERNS = [
  /(?:公司|企业|集团|Corporation|Inc\.|Ltd\.)[：:]\s*[^\s,，。.]+/g,
];

const CREDENTIAL_PATTERNS = [
  /(?:password|密码|token|secret|key|apikey|api_key)[=:\s]+\S+/gi,
  /(?:bearer|authorization)[:\s]+\S+/gi,
  /sk-[a-zA-Z0-9]{20,}/g,
];

const FORBIDDEN_CONTENT_PATTERNS = [
  /(?:如何|how to).*(?:欺诈|fraud|hack|攻击|attack)/i,
  /(?:绕过|bypass).*(?:安全|security|验证|auth)/i,
];

function sanitizeText(text) {
  if (!text) return text;
  var result = text;

  for (var i = 0; i < PII_PATTERNS.length; i++) {
    result = result.replace(PII_PATTERNS[i], '[REDACTED]');
  }
  for (var j = 0; j < NAME_PATTERNS.length; j++) {
    result = result.replace(NAME_PATTERNS[j], '[NAME_REDACTED]');
  }
  for (var k = 0; k < COMPANY_PATTERNS.length; k++) {
    result = result.replace(COMPANY_PATTERNS[k], '[COMPANY_REDACTED]');
  }
  for (var m = 0; m < CREDENTIAL_PATTERNS.length; m++) {
    result = result.replace(CREDENTIAL_PATTERNS[m], '[CREDENTIAL_REDACTED]');
  }

  return result;
}

function sanitizeObject(obj) {
  if (!obj) return obj;
  if (typeof obj === 'string') return sanitizeText(obj);
  if (Array.isArray(obj)) return obj.map(sanitizeObject);
  if (typeof obj === 'object') {
    var result = {};
    for (var key in obj) {
      result[key] = sanitizeObject(obj[key]);
    }
    return result;
  }
  return obj;
}

// Sanitize a RefinedSpark for publishing as Ember
function sanitizeForPublishing(refinedSpark) {
  var clean = JSON.parse(JSON.stringify(refinedSpark));

  clean.summary = sanitizeText(clean.summary);
  if (clean.insight) {
    clean.insight = sanitizeObject(clean.insight);
  }
  if (clean.applicable_when) {
    clean.applicable_when = clean.applicable_when.map(sanitizeText);
  }
  if (clean.not_applicable_when) {
    clean.not_applicable_when = clean.not_applicable_when.map(sanitizeText);
  }

  // Sanitize contributor chain — keep type, role, and focus; redact specific IDs
  if (Array.isArray(clean.contributor_chain)) {
    for (var i = 0; i < clean.contributor_chain.length; i++) {
      var c = clean.contributor_chain[i];
      if (c.type === 'human') {
        c.id = 'contributor_' + (i + 1);
      }
      if (Array.isArray(c.focus)) {
        c.focus = c.focus.map(sanitizeText);
      }
    }
  }

  // Sanitize six-dimension fields
  if (clean.when) {
    clean.when.trigger = sanitizeText(clean.when.trigger);
    if (Array.isArray(clean.when.conditions)) {
      clean.when.conditions = clean.when.conditions.map(sanitizeText);
    }
  }
  if (clean.where) {
    clean.where.scenario = sanitizeText(clean.where.scenario);
    clean.where.audience = sanitizeText(clean.where.audience);
  }
  if (clean.why) {
    clean.why = sanitizeText(clean.why);
  }
  if (clean.how) {
    clean.how.summary = sanitizeText(clean.how.summary);
    clean.how.detail = sanitizeText(clean.how.detail);
  }
  if (clean.result) {
    clean.result.expected_outcome = sanitizeText(clean.result.expected_outcome);
    if (Array.isArray(clean.result.feedback_log)) {
      clean.result.feedback_log = clean.result.feedback_log.map(function(entry) {
        var cleaned = Object.assign({}, entry);
        if (cleaned.text) cleaned.text = sanitizeText(cleaned.text);
        delete cleaned.session_id;
        return cleaned;
      });
    }
  }
  if (Array.isArray(clean.not)) {
    clean.not = clean.not.map(function(n) {
      return {
        condition: sanitizeText(n.condition),
        effect: n.effect,
        reason: sanitizeText(n.reason),
      };
    });
  }

  // Remove private context fields
  delete clean.context;
  delete clean.related_task;
  delete clean.related_session;

  // Strip PII from card.context_envelope — keep professional context
  if (clean.card && clean.card.context_envelope) {
    delete clean.card.context_envelope.contributor_name;
    delete clean.card.context_envelope.contributor_company;
    delete clean.card.context_envelope.contributor_location;
    delete clean.card.context_envelope.contributor_email;
    delete clean.card.context_envelope.contributor_phone;
  }

  // Strip contributor real names — keep only type and anonymized id
  if (clean.contributor && clean.contributor.type === 'human') {
    clean.contributor.id = 'contributor_0';
  }

  return clean;
}

// Check for forbidden content
function checkContentSafety(text) {
  if (!text) return { safe: true, issues: [] };
  var issues = [];
  for (var i = 0; i < FORBIDDEN_CONTENT_PATTERNS.length; i++) {
    if (FORBIDDEN_CONTENT_PATTERNS[i].test(text)) {
      issues.push('Potentially unsafe content detected');
      break;
    }
  }
  return { safe: issues.length === 0, issues: issues };
}

module.exports = {
  sanitizeText,
  sanitizeObject,
  sanitizeForPublishing,
  checkContentSafety,
};
