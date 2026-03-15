#!/usr/bin/env node
/**
 * image-gen skill — generate.js
 * Unified image generation script for OpenClaw.
 * Supports: Midjourney (Legnext.ai), Flux Pro/Dev/Schnell, SDXL Lightning,
 *           Nano Banana Pro (Gemini), Ideogram v3, Recraft v3 (all via fal.ai)
 *
 * Usage:
 *   node generate.js --model <id> --prompt "<text>" [options]
 *   node generate.js --model midjourney --action upscale --index 2 --job-id <id>
 *   node generate.js --model nano-banana --prompt "<text>" --reference-images "url1,url2"
 *
 * Async (non-blocking) mode for Midjourney:
 *   node generate.js --model midjourney --prompt "<text>" --async
 *     → Submits job and returns immediately with job_id (does NOT wait)
 *   node generate.js --model midjourney --poll --job-id <id>
 *     → Checks job status once and returns immediately (no waiting)
 */

import { fal } from "@fal-ai/client";
import https from "https";
import { parseArgs } from "util";

// ── Parse CLI arguments ────────────────────────────────────────────────────
const { values: args } = parseArgs({
  options: {
    model:              { type: "string", default: "flux-dev" },
    prompt:             { type: "string", default: "" },
    "aspect-ratio":     { type: "string", default: "1:1" },
    "num-images":       { type: "string", default: "1" },
    "negative-prompt":  { type: "string", default: "" },
    action:             { type: "string", default: "" },   // upscale | variation | reroll
    index:              { type: "string", default: "1" },  // 1-4 for MJ actions
    "job-id":           { type: "string", default: "" },   // MJ jobId for actions
    "upscale-type":     { type: "string", default: "0" },  // 0=Subtle, 1=Creative
    "variation-type":   { type: "string", default: "0" },  // 0=Subtle, 1=Strong
    mode:               { type: "string", default: "turbo" }, // turbo | fast | relax
    seed:               { type: "string", default: "" },
    async:              { type: "boolean", default: false }, // submit and return immediately
    poll:               { type: "boolean", default: false }, // check status once, no wait
    "reference-images": { type: "string", default: "" },   // comma-separated URLs for nano-banana context
  },
  strict: false,
});

const MODEL          = args["model"];
const PROMPT         = args["prompt"];
const AR             = args["aspect-ratio"];
const NUM_IMAGES     = parseInt(args["num-images"], 10) || 1;
const NEG_PROMPT     = args["negative-prompt"];
const ACTION         = args["action"];
const INDEX          = parseInt(args["index"], 10) || 1;
const JOB_ID         = args["job-id"];
const UPSCALE_TYPE   = parseInt(args["upscale-type"], 10) || 0;
const VARIATION_TYPE = parseInt(args["variation-type"], 10) || 0;
const MODE           = args["mode"] || "turbo";  // turbo (~10-20s), fast (~30-60s), relax (free but slow)
const SEED           = args["seed"] ? parseInt(args["seed"], 10) : undefined;
const ASYNC_MODE     = args["async"] === true;
const POLL_MODE      = args["poll"] === true;
// Reference images: comma-separated URLs (for nano-banana context/character consistency)
const REFERENCE_IMAGES = args["reference-images"]
  ? args["reference-images"].split(",").map(u => u.trim()).filter(Boolean)
  : [];

// ── Environment variables ──────────────────────────────────────────────────
const FAL_KEY      = process.env.FAL_KEY;
const LEGNEXT_KEY  = process.env.LEGNEXT_KEY;

// ── fal.ai model IDs ───────────────────────────────────────────────────────
const FAL_MODELS = {
  "flux-pro":      "fal-ai/flux-pro/v1.1",
  "flux-dev":      "fal-ai/flux/dev",
  "flux-schnell":  "fal-ai/flux/schnell",
  "sdxl":          "fal-ai/lightning-models/sdxl-lightning-4step",
  "nano-banana":   "fal-ai/nano-banana-pro",
  "ideogram":      "fal-ai/ideogram/v3",
  "recraft":       "fal-ai/recraft-v3",
};

// ── Aspect ratio helpers ───────────────────────────────────────────────────
function arToWidthHeight(ar) {
  const map = {
    "1:1":  [1024, 1024],
    "16:9": [1344, 768],
    "9:16": [768, 1344],
    "4:3":  [1152, 864],
    "3:4":  [864, 1152],
    "3:2":  [1216, 832],
    "2:3":  [832, 1216],
    "21:9": [1536, 640],
  };
  return map[ar] || [1024, 1024];
}
function arToFalImageSize(ar) {
  const map = {
    "1:1":  "square_hd",
    "16:9": "landscape_16_9",
    "9:16": "portrait_16_9",
    "4:3":  "landscape_4_3",
    "3:4":  "portrait_4_3",
  };
  return map[ar] || "square_hd";
}

// ── Output helper ──────────────────────────────────────────────────────────
function output(obj) {
  process.stdout.write(JSON.stringify(obj, null, 2) + "\n");
}
function error(msg, detail) {
  output({ success: false, error: msg, detail });
  process.exit(1);
}

// ── Legnext.ai helpers ─────────────────────────────────────────────────────
function legnextRequest(method, path, body) {
  return new Promise((resolve, reject) => {
    // Legnext API v1: base path is /api/v1/, auth via x-api-key header
    const fullPath = path.startsWith("/api/") ? path : "/api/v1" + path;
    const isGet = method === "GET";
    const data = isGet ? null : JSON.stringify(body);
    const headers = {
      "Content-Type": "application/json",
      "x-api-key": LEGNEXT_KEY,
    };
    if (!isGet && data) headers["Content-Length"] = Buffer.byteLength(data);
    const req = https.request({
      hostname: "api.legnext.ai",
      path: fullPath,
      method,
      headers,
    }, (res) => {
      let raw = "";
      res.on("data", c => raw += c);
      res.on("end", () => {
        try { resolve(JSON.parse(raw)); }
        catch { resolve({ _raw: raw }); }
      });
    });
    req.on("error", reject);
    if (!isGet && data) req.write(data);
    req.end();
  });
}

async function legnextPoll(jobId, maxWaitMs = 120000, intervalMs = 5000) {
  const start = Date.now();
  while (true) {
    const res = await legnextRequest("GET", `/job/${jobId}`, {});
    const status = res.status || res.state;
    // Check for real errors: error.code != 0 means actual error
    if (!res || res._raw) error("Legnext poll error: invalid response", res);
    if (res.error && res.error.code && res.error.code !== 0) error("Legnext poll error: " + (res.error.message || JSON.stringify(res.error)), res);
    if (status === "not_found") error("Job not found", { jobId });
    if (status === "failed" || status === "error") {
      const msg = (res.error && res.error.message) || res.error_message || JSON.stringify(res);
      error("Midjourney generation failed: " + msg);
    }
    if (status === "completed" || status === "done") return res;
    process.stderr.write(`[MJ] Status: ${status} ...\n`);
    if (Date.now() - start > maxWaitMs) error("Timeout waiting for Midjourney job", { jobId });
    await new Promise(r => setTimeout(r, intervalMs));
  }
}

// ── Midjourney via Legnext.ai ──────────────────────────────────────────────
async function generateMidjourney() {
  if (!LEGNEXT_KEY) error("LEGNEXT_KEY is not set. Please configure it in your OpenClaw skill env.");

  // ── Poll-only mode ─────────────────────────────────────────────────────
  if (POLL_MODE) {
    if (!JOB_ID) error("--job-id is required for --poll mode.");
    const res = await legnextRequest("GET", `/job/${JOB_ID}`, {});
    const status = res.status || res.state;
    if (status === "completed" || status === "done") {
      output({
        success: true,
        model: "midjourney",
        jobId: JOB_ID,
        status: "completed",
        imageUrl: res.output?.image_url || null,
        imageUrls: res.output?.image_urls || [],
        seed: res.output?.seed || null,
      });
    } else {
      output({ success: false, model: "midjourney", jobId: JOB_ID, status: status || "unknown", pending: true });
    }
    return;
  }

  // ── Action mode: upscale / variation / reroll ──────────────────────────
  if (ACTION === "upscale" || ACTION === "variation" || ACTION === "reroll") {
    if (!JOB_ID) error(`--job-id is required for --action ${ACTION}.`);
    let endpoint, body;
    if (ACTION === "upscale") {
      endpoint = "/diffusion/upscale";
      body = { job_id: JOB_ID, index: INDEX, type: UPSCALE_TYPE };
    } else if (ACTION === "variation") {
      endpoint = "/diffusion/variation";
      body = { job_id: JOB_ID, index: INDEX, type: VARIATION_TYPE };
    } else {
      endpoint = "/diffusion/reroll";
      body = { job_id: JOB_ID };
    }
    process.stderr.write(`[MJ] Running ${ACTION} on job ${JOB_ID}...\n`);
    const res = await legnextRequest("POST", endpoint, body);
    if (!res.job_id) error(`Legnext ${ACTION} failed`, res);
    const newJobId = res.job_id;
    process.stderr.write(`[MJ] ${ACTION} job submitted: ${newJobId}\n`);
    if (ASYNC_MODE) {
      output({ success: true, model: "midjourney", action: ACTION, jobId: newJobId, status: "submitted", pending: true });
      return;
    }
    const result = await legnextPoll(newJobId);
    output({
      success: true,
      model: "midjourney",
      action: ACTION,
      jobId: newJobId,
      imageUrl: result.output?.image_url || null,
      imageUrls: result.output?.image_urls || [],
    });
    return;
  }

  // ── Imagine mode ───────────────────────────────────────────────────────
  if (!PROMPT) error("--prompt is required.");
  let mjPrompt = PROMPT;
  if (AR && AR !== "1:1") {
    const arMap = { "16:9": "16:9", "9:16": "9:16", "4:3": "4:3", "3:4": "3:4", "3:2": "3:2", "2:3": "2:3", "21:9": "21:9" };
    if (arMap[AR]) mjPrompt += ` --ar ${arMap[AR]}`;
  }
  if (MODE === "turbo") {
    mjPrompt += " --turbo";
  } else if (MODE === "fast") {
    mjPrompt += " --fast";
  } else if (MODE === "relax") {
    mjPrompt += " --relax";
  }
  process.stderr.write(`[MJ] Submitting imagine via Legnext.ai (mode=${MODE}): "${mjPrompt}"\n`);
  const res = await legnextRequest("POST", "/diffusion", {
    text: mjPrompt,
  });
  if (!res.job_id) error("Legnext imagine submission failed", res);
  const jobId = res.job_id;
  process.stderr.write(`[MJ] Job submitted: ${jobId}\n`);
  if (ASYNC_MODE) {
    output({
      success: true,
      model: "midjourney",
      provider: "legnext.ai",
      jobId,
      status: "submitted",
      pending: true,
      prompt: mjPrompt,
      message: `✅ Midjourney job submitted! job_id: ${jobId}\n\nGeneration takes ~10-20s (turbo) or ~30-60s (fast). I'll notify you when it's done.\n\nTo check manually: node generate.js --model midjourney --poll --job-id ${jobId}`,
    });
    return;
  }
  const result = await legnextPoll(jobId);
  output({
    success: true,
    model: "midjourney",
    provider: "legnext.ai",
    jobId,
    prompt: mjPrompt,
    imageUrl: result.output?.image_url || null,
    imageUrls: result.output?.image_urls || [],
    seed: result.output?.seed || null,
    note: "4 images generated. Use --action upscale --index <1-4> --job-id to upscale, or --action variation to create variants.",
  });
}

// ── fal.ai models ──────────────────────────────────────────────────────────
async function generateFal(modelKey) {
  if (!FAL_KEY) error("FAL_KEY is not set. Please configure it in your OpenClaw skill env.");
  fal.config({ credentials: FAL_KEY });
  const modelId = FAL_MODELS[modelKey];
  if (!modelId) error(`Unknown fal.ai model key: ${modelKey}`);
  if (!PROMPT) error("--prompt is required.");
  const [width, height] = arToWidthHeight(AR);
  const imageSize = arToFalImageSize(AR);
  let input = {};
  if (modelKey === "flux-pro") {
    input = {
      prompt: PROMPT,
      image_size: imageSize,
      num_images: Math.min(NUM_IMAGES, 4),
      ...(SEED !== undefined && { seed: SEED }),
      safety_tolerance: "2",
      output_format: "jpeg",
    };
  } else if (modelKey === "flux-dev") {
    input = {
      prompt: PROMPT,
      image_size: imageSize,
      num_inference_steps: 28,
      num_images: Math.min(NUM_IMAGES, 4),
      enable_safety_checker: true,
      ...(SEED !== undefined && { seed: SEED }),
    };
  } else if (modelKey === "flux-schnell") {
    input = {
      prompt: PROMPT,
      image_size: imageSize,
      num_inference_steps: 4,
      num_images: Math.min(NUM_IMAGES, 4),
      enable_safety_checker: true,
      ...(SEED !== undefined && { seed: SEED }),
    };
  } else if (modelKey === "sdxl") {
    input = {
      prompt: PROMPT,
      negative_prompt: NEG_PROMPT || "blurry, low quality, distorted",
      image_size: { width, height },
      num_images: Math.min(NUM_IMAGES, 4),
      ...(SEED !== undefined && { seed: SEED }),
    };
  } else if (modelKey === "nano-banana") {
    input = {
      prompt: PROMPT,
      image_size: imageSize,
      num_images: Math.min(NUM_IMAGES, 4),
      ...(SEED !== undefined && { seed: SEED }),
      // Reference images for character/scene consistency (up to 14 images)
      ...(REFERENCE_IMAGES.length > 0 && {
        reference_images: REFERENCE_IMAGES.map(url => ({ url })),
      }),
    };
  } else if (modelKey === "ideogram") {
    input = {
      prompt: PROMPT,
      aspect_ratio: AR,
      num_images: Math.min(NUM_IMAGES, 4),
      ...(NEG_PROMPT && { negative_prompt: NEG_PROMPT }),
      ...(SEED !== undefined && { seed: SEED }),
    };
  } else if (modelKey === "recraft") {
    input = {
      prompt: PROMPT,
      image_size: imageSize,
      style: "realistic_image",
      num_images: Math.min(NUM_IMAGES, 4),
    };
  }
  process.stderr.write(`[fal] Calling ${modelId} ...\n`);
  if (REFERENCE_IMAGES.length > 0) {
    process.stderr.write(`[fal] Using ${REFERENCE_IMAGES.length} reference image(s) for context consistency\n`);
  }
  const result = await fal.subscribe(modelId, {
    input,
    onQueueUpdate(update) {
      if (update.status === "IN_QUEUE") {
        process.stderr.write(`[fal] Queue position: ${update.position ?? "?"}\n`);
      } else if (update.status === "IN_PROGRESS") {
        process.stderr.write(`[fal] Generating...\n`);
      }
    },
  });
  const images = (result.data?.images || []).map((img) =>
    typeof img === "string" ? img : img.url
  );
  output({
    success: true,
    model: modelKey,
    modelId,
    prompt: PROMPT,
    images,
    imageUrl: images[0] || null,
    seed: result.data?.seed ?? null,
    timings: result.data?.timings ?? null,
  });
}

// ── Main ───────────────────────────────────────────────────────────────────
async function main() {
  if (MODEL === "midjourney") {
    await generateMidjourney();
  } else if (FAL_MODELS[MODEL]) {
    await generateFal(MODEL);
  } else {
    error(`Unknown model: "${MODEL}". Valid options: midjourney, flux-pro, flux-dev, flux-schnell, sdxl, nano-banana, ideogram, recraft`);
  }
}
main().catch((err) => {
  error(err.message, err.stack);
});
