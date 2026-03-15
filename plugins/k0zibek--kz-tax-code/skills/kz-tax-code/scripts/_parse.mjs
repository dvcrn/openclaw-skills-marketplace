import { readFileSync, writeFileSync } from "fs";

const [,, inFile, outFile] = process.argv;
const html = readFileSync(inFile).toString("utf-8");

// Extract article element
const match = html.match(/<article[^>]*>([\s\S]*?)<\/article>/i);
if (!match) {
  // Try div.doc-content or main
  const m2 = html.match(/<div[^>]*class="[^"]*doc[^"]*"[^>]*>([\s\S]*?)<\/div>/i);
  if (!m2) { console.error("No <article> found. Page length:", html.length); process.exit(1); }
}
let content = (match || [])[1] || html;

// Remove scripts/styles
content = content
  .replace(/<script[\s\S]*?<\/script>/gi, "")
  .replace(/<style[\s\S]*?<\/style>/gi, "");

function clean(s) {
  return s
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(parseInt(n)))
    .replace(/\s+/g, " ")
    .trim();
}

const lines = [];
// Split on closing block tags
const parts = content.split(/<\/(?:p|h[1-4]|li|div|td|tr)>/i);
for (const part of parts) {
  const m = part.match(/<(h[1-4]|p|li|td)[^>]*>([\s\S]*)$/i);
  if (!m) continue;
  const tag  = m[1].toLowerCase();
  const text = clean(m[2]);
  if (!text || text.length < 2) continue;
  // Article patterns (both Russian and Kazakh)
  const isRuArticle  = /^Статья\s+\d+[\.\-]/.test(text);
  const isKazArticle = /^\d+-бап[.\s]/.test(text);

  if (tag === "h1") lines.push("# " + text);
  else if (tag === "h2") lines.push("## " + text);
  else if (tag === "h3") {
    // Kazakh articles live in h3 elements — promote to article level
    if (isKazArticle || isRuArticle) lines.push("\n## " + text);
    else lines.push("### " + text);
  }
  else if (tag === "h4") lines.push("#### " + text);
  else if (tag === "li") lines.push("- " + text);
  else if (isRuArticle || isKazArticle) lines.push("\n## " + text);
  else lines.push(text);
}

const md = lines.join("\n\n").replace(/\n{4,}/g, "\n\n\n").trim();
writeFileSync(outFile, md, "utf-8");
console.log("Saved", Math.round(md.length / 1024) + "KB,", lines.length, "blocks");
