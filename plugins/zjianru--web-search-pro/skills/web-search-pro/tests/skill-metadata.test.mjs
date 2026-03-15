import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const SKILL_PATH = path.resolve(process.cwd(), "SKILL.md");
const content = fs.readFileSync(SKILL_PATH, "utf8");

function getMetadataObject(markdown) {
  const match = markdown.match(/^metadata:\s+(.+)$/m);
  assert.ok(match, "metadata frontmatter line must exist");
  return JSON.parse(match[1]);
}

test("skill metadata does not overstate credential requirements", () => {
  const metadata = getMetadataObject(content);
  const openclaw = metadata.openclaw ?? {};

  assert.deepEqual(openclaw.requires?.bins ?? [], ["node"]);
  assert.equal(openclaw.always, undefined);
  assert.equal(openclaw.primaryEnv, undefined);
  assert.deepEqual(openclaw.requires?.env ?? [], []);
});

test("skill documentation still states that at least one provider key is required", () => {
  assert.match(content, /At least one API key must be configured/);
  assert.match(content, /Any one of these keys can enable part of the skill/);
});
