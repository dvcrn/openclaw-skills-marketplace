#!/usr/bin/env node
/**
 * ingest-email.js — Schema-correct email knowledge capture for MindGraph
 *
 * Usage:
 *   node skills/mindgraph/ingest-email.js --input <email.json>
 *
 * Input JSON shape:
 * {
 *   id: string,          // Gmail thread ID
 *   from: string,        // "Name <email@domain.com>"
 *   subject: string,
 *   date: string,        // ISO or Gmail date string
 *   body: string,        // Full plain-text body
 *   emailType: string,   // 'newsletter' | 'personal' | 'outreach_reply' | 'announcement' | 'unknown'
 *   source: string,      // e.g. "Financial Times", "ACLS Newsletter", "Aaron Goh"
 *   // Optional — pre-extracted by LLM before calling this script:
 *   facts?: Array<{
 *     label: string,
 *     content: string,
 *     factType: 'claim' | 'observation' | 'announcement' | 'signal' | 'question' | 'pattern',
 *     // For claims:
 *     evidence?: string,
 *     warrant?: string,
 *     // For signals — connect to goal:
 *     relatedGoalLabel?: string,
 *   }>
 * }
 *
 * Output: JSON summary of all nodes created, with UIDs.
 *
 * Design principles:
 *  - Source node first: every email gets a Source node (the email itself as a document)
 *  - Facts are Snippets extracted from the Source, each with PART_OF edge
 *  - factType drives which endpoint is called — never flatten everything to ingest()
 *  - Sender entity resolved/created and linked to Source via AUTHORED_BY
 *  - Claim + Evidence + Warrant bundled via addArgument() — not split across calls
 *  - Session framing optional but recommended
 */

'use strict';

const fs = require('fs');
const path = require('path');
const mg = require('./mindgraph-client.js');
const { resolveEntity } = require('/home/node/.openclaw/workspace/skills/mindgraph/entity-resolution.js');

const AGENT_ID = 'email-monitor';

// ─── Sender parsing ───────────────────────────────────────────────────────────

function parseSender(fromStr) {
  // "Name <email@domain.com>" or "email@domain.com"
  const match = fromStr.match(/^(.+?)\s*<([^>]+)>$/);
  if (match) return { name: match[1].trim(), email: match[2].trim() };
  return { name: fromStr.trim(), email: fromStr.trim() };
}

// ─── Sender entity resolution ─────────────────────────────────────────────────

async function resolveSender(fromStr) {
  const { name, email } = parseSender(fromStr);

  // Try name first, then email
  let uid = await resolveEntity(name, 'Entity', { createIfMissing: false });
  if (!uid && email !== name) {
    uid = await resolveEntity(email, 'Entity', { createIfMissing: false });
  }

  if (uid) {
    console.error(`  [sender] Resolved: "${name}" → ${uid}`);
    return { uid, name, email, isNew: false };
  }

  // Determine entity type from email domain
  const domain = email.split('@')[1] || '';
  const isOrg = /\.(com|org|io|ai|co)$/.test(domain) &&
    !['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com'].includes(domain);

  const result = await mg.manageEntity({
    action: 'create',
    label: name,
    entityType: isOrg ? 'Organization' : 'Person',
    props: { description: `Email contact. Address: ${email}` },
    agentId: AGENT_ID,
  });
  const newUid = result?.uid || result?.entity_uid;
  console.error(`  [sender] Created: "${name}" → ${newUid}`);
  return { uid: newUid, name, email, isNew: true };
}

// ─── Source node (the email itself) ──────────────────────────────────────────

async function createEmailSource(email, senderUid) {
  const timestamp = email.date ? Math.floor(new Date(email.date).getTime() / 1000) : Math.floor(Date.now() / 1000);

  const result = await mg.ingest(
    `[Email] ${email.source || email.from}: ${email.subject}`,
    email.body.slice(0, 500), // brief content — full body in snippets
    'source',
    {
      url: `gmail:${email.id}`,
      timestamp,
      agentId: AGENT_ID,
    }
  );
  const sourceUid = result?.uid || result?.source_uid;
  console.error(`  [source] Created: ${sourceUid}`);

  // Link sender → source via AUTHORED_BY
  if (sourceUid && senderUid) {
    await mg.link(senderUid, sourceUid, 'AUTHORED_BY').catch(() => {});
  }

  return sourceUid;
}

// ─── Fact ingestion by type ───────────────────────────────────────────────────

async function ingestFact(fact, sourceUid, sessionUid) {
  const { label, content, factType, evidence, warrant, relatedGoalLabel } = fact;

  let resultUid = null;

  switch (factType) {

    // Reported event or state at a point in time — Observation
    case 'observation':
    case 'announcement': {
      const result = await mg.ingest(label, content, 'observation', {
        sourceUid,
        agentId: AGENT_ID,
      });
      resultUid = result?.uid || result?.observation_uid;
      console.error(`  [observation] ${label} → ${resultUid}`);
      break;
    }

    // Substantive claim with backing evidence — use addArgument for full structure
    case 'claim':
    case 'signal': {
      if (evidence || warrant) {
        const result = await mg.addArgument({
          claim: { label, content },
          evidence: evidence ? [{ label: `Evidence: ${label}`, description: evidence }] : undefined,
          warrant: warrant ? { label: `Warrant: ${label}`, principle: warrant } : undefined,
          sourceUids: sourceUid ? [sourceUid] : undefined,
          agentId: AGENT_ID,
        });
        resultUid = result?.claim_uid || result?.uid;
        console.error(`  [argument] ${label} → ${resultUid}`);
      } else {
        // Claim without explicit evidence — still use addArgument, evidence implicit from source
        const result = await mg.addArgument({
          claim: { label, content },
          sourceUids: sourceUid ? [sourceUid] : undefined,
          agentId: AGENT_ID,
        });
        resultUid = result?.claim_uid || result?.uid;
        console.error(`  [claim] ${label} → ${resultUid}`);
      }

      // If this signal relates to an active goal — link it
      if (relatedGoalLabel) {
        const goalUid = await resolveEntity(relatedGoalLabel, 'Goal', { createIfMissing: false });
        if (goalUid && resultUid) {
          await mg.link(resultUid, goalUid, 'ADDRESSES').catch(() => {});
        }
      }
      break;
    }

    // An open question raised by the content
    case 'question': {
      const result = await mg.addInquiry(label, content, 'question', {
        status: 'open',
        agentId: AGENT_ID,
      });
      resultUid = result?.uid || result?.question_uid;
      console.error(`  [question] ${label} → ${resultUid}`);
      break;
    }

    // A recurring pattern or generalizable lesson
    case 'pattern': {
      const result = await mg.addStructure(label, content, 'pattern', {
        agentId: AGENT_ID,
      });
      resultUid = result?.uid;
      console.error(`  [pattern] ${label} → ${resultUid}`);
      break;
    }

    // Hypothesis — proposed explanation, uncertain
    case 'hypothesis': {
      const result = await mg.addInquiry(label, content, 'hypothesis', {
        status: 'open',
        confidence: 0.5,
        agentId: AGENT_ID,
      });
      resultUid = result?.uid;
      console.error(`  [hypothesis] ${label} → ${resultUid}`);
      break;
    }

    default: {
      // Fallback: Snippet from Source
      const result = await mg.ingest(label, content, 'snippet', {
        sourceUid,
        agentId: AGENT_ID,
      });
      resultUid = result?.uid || result?.snippet_uid;
      console.error(`  [snippet] ${label} → ${resultUid}`);
    }
  }

  // Trace to session if open
  if (sessionUid && resultUid) {
    await mg.sessionOp({
      action: 'trace',
      sessionUid,
      traceContent: `Ingested [${factType}]: ${label}`,
      relevantNodeUids: [resultUid],
      agentId: AGENT_ID,
    }).catch(() => {});
  }

  // Link fact node back to source with DERIVED_FROM
  if (sourceUid && resultUid && resultUid !== sourceUid) {
    await mg.link(resultUid, sourceUid, 'DERIVED_FROM').catch(() => {});
  }

  return resultUid;
}

// ─── Classify sender relevance against graph ──────────────────────────────────

async function classifySender(senderUid, senderName) {
  if (!senderUid) return { priority: 'unknown', connectedGoals: [] };

  try {
    // Traverse neighborhood to find goal/project connections
    const cfg = JSON.parse(fs.readFileSync('/home/node/.openclaw/mindgraph.json', 'utf8'));
    const http = require('http');

    const steps = await new Promise((resolve, reject) => {
      const body = JSON.stringify({ action: 'neighborhood', start_uid: senderUid, max_depth: 2 });
      const req = http.request({
        host: '127.0.0.1', port: 18790, path: '/traverse', method: 'POST',
        headers: {
          'Authorization': 'Bearer ' + cfg.token,
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(body),
        },
      }, (r) => {
        let s = '';
        r.on('data', d => s += d);
        r.on('end', () => {
          try { resolve(JSON.parse(s).steps || []); } catch { resolve([]); }
        });
      });
      req.on('error', () => resolve([]));
      req.write(body);
      req.end();
    });

    const HIGH_VALUE = new Set(['Goal', 'Project', 'Decision', 'Task']);
    const connectedGoals = steps
      .filter(s => HIGH_VALUE.has(s.node_type))
      .map(s => ({ label: s.label, type: s.node_type, uid: s.node_uid }));

    const priority = connectedGoals.length > 0 ? 'high' : 'normal';
    return { priority, connectedGoals };
  } catch {
    return { priority: 'unknown', connectedGoals: [] };
  }
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const inputIdx = args.indexOf('--input');
  const sessionIdx = args.indexOf('--session-uid');

  if (inputIdx === -1) {
    console.log('Usage: node ingest-email.js --input <email.json> [--session-uid <uid>]');
    process.exit(0);
  }

  const inputPath = args[inputIdx + 1];
  const sessionUid = sessionIdx !== -1 ? args[sessionIdx + 1] : null;

  const email = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  const results = { emailId: email.id, subject: email.subject, nodes: [] };

  console.error(`\n[ingest-email] Processing: "${email.subject}" from ${email.from}`);

  // 1. Resolve sender
  const sender = await resolveSender(email.from);
  results.sender = { uid: sender.uid, name: sender.name, isNew: sender.isNew };

  // 2. Classify sender relevance
  const { priority, connectedGoals } = await classifySender(sender.uid, sender.name);
  results.senderPriority = priority;
  results.connectedGoals = connectedGoals;
  console.error(`  [classify] Sender priority: ${priority}, connected to: ${connectedGoals.map(g => g.label).join(', ') || 'none'}`);

  // 3. Create Source node for the email
  const sourceUid = await createEmailSource(email, sender.uid);
  results.sourceUid = sourceUid;

  // 4. Ingest facts using schema-correct endpoints
  const facts = email.facts || [];
  if (facts.length === 0) {
    console.error('  [facts] No facts provided — only Source node created');
  }

  for (const fact of facts) {
    const uid = await ingestFact(fact, sourceUid, sessionUid);
    if (uid) results.nodes.push({ label: fact.label, type: fact.factType, uid });
  }

  // 5. Output summary
  console.log(JSON.stringify(results, null, 2));
  console.error(`\n[ingest-email] Done: ${results.nodes.length} fact nodes created for "${email.subject}"`);
}

main().catch(e => {
  console.error('Error:', e.message);
  process.exit(1);
});
