// Lifecycle manager — daemon mode for continuous learning.

const { runDigest } = require('../temper/digest');
const { readRawSparks, readDigestReports } = require('../core/storage');

var CHECK_INTERVAL_MS = Number(process.env.STP_CHECK_INTERVAL_HOURS || 3) * 60 * 60 * 1000;
var DIGEST_INTERVAL_MS = Number(process.env.STP_DIGEST_INTERVAL_HOURS || 12) * 60 * 60 * 1000;

function getDigestIntervalMs() {
  return DIGEST_INTERVAL_MS;
}

function shouldRunDigest() {
  var reports = readDigestReports();
  if (reports.length === 0) {
    var sparks = readRawSparks();
    return sparks.length > 0;
  }
  var last = reports[reports.length - 1];
  var lastTime = new Date(last.created_at).getTime();
  return (Date.now() - lastTime) >= DIGEST_INTERVAL_MS;
}

async function runLoop() {
  var checkHours = (CHECK_INTERVAL_MS / 3600000).toFixed(1);
  var digestHours = (DIGEST_INTERVAL_MS / 3600000).toFixed(1);
  console.log('[sparker] Starting learning daemon...');
  console.log('[sparker] Check every ' + checkHours + 'h, digest every ' + digestHours + 'h');

  async function tick() {
    try {
      if (shouldRunDigest()) {
        console.log('[sparker] Running digest...');
        var report = await runDigest();
        if (report && report.skipped) {
          console.log('[sparker] Digest skipped: ' + (report.skip_reason || 'already running'));
        } else {
          console.log('[sparker] Digest complete: ' + report.summary.new_raw_sparks + ' new sparks, ' +
            report.summary.promoted_to_refined + ' promoted');
        }
      }
    } catch (e) {
      console.error('[sparker] Error in digest:', e.message);
    }
  }

  await tick();
  setInterval(tick, CHECK_INTERVAL_MS);
}

module.exports = { runLoop, shouldRunDigest, getDigestIntervalMs };
