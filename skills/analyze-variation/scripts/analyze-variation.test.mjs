#!/usr/bin/env node
/**
 * Tests for analyze-variation.mjs — run with: node analyze-variation.test.mjs
 * Uses Node's built-in assert; no test framework dependency.
 */
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  countTokens,
  splitSentences,
  mean,
  stdev,
  analyzePost,
  flagPosts,
} from './analyze-variation.mjs';

const SCRIPT = join(dirname(fileURLToPath(import.meta.url)), 'analyze-variation.mjs');
let passed = 0;
const ok = (name) => {
  passed++;
  console.log(`  ✓ ${name}`);
};

// --- pure functions -------------------------------------------------------

assert.equal(countTokens('one two three'), 3);
assert.equal(countTokens("don't split-hyphen ok"), 3); // contractions/hyphens = one token
ok('countTokens');

assert.deepEqual(splitSentences('Short. A longer one follows it.'), [
  'Short.',
  'A longer one follows it.',
]);
// Abbreviation guard: "e.g." must not end a sentence.
assert.equal(splitSentences('Use a tool, e.g. a hammer, to build.').length, 1);
ok('splitSentences + abbreviation guard');

assert.equal(mean([2, 4, 6]), 4);
assert.equal(stdev([4, 4, 4]), 0); // no variance
ok('mean / stdev');

const m = analyzePost('Short. A much longer sentence trails along behind the short one.');
assert.equal(m.sentences, 2);
assert.ok(m.cv > 0, 'cv should be positive when sentence lengths differ');
ok('analyzePost');

// flagPosts: monotone (cv below threshold, >=3 sentences) and too-similar neighbors.
const flags = flagPosts([
  { label: 'a', metrics: { sentences: 4, cv: 0.1, weighted: 1000 } },
  { label: 'b', metrics: { sentences: 4, cv: 0.9, weighted: 1010 } },
]);
assert.ok(flags.some((f) => f.type === 'monotone' && f.label === 'a'));
assert.ok(flags.some((f) => f.type === 'neighbor')); // 1000 vs 1010 within 15%
ok('flagPosts');

// --- regression: first file argument must NOT be dropped ------------------
// (Bug: argv[textIdx+1] resolved to argv[0] when --text/--write absent.)
const dir = mkdtempSync(join(tmpdir(), 'analyze-var-'));
try {
  writeFileSync(join(dir, 'first.md'), 'Alpha one. Alpha two is a good deal longer than one.\n');
  writeFileSync(join(dir, 'second.md'), 'Beta one. Beta two is also a fair bit longer here.\n');
  const out = execFileSync('node', [SCRIPT, join(dir, 'first.md'), join(dir, 'second.md')], {
    encoding: 'utf8',
  });
  assert.ok(out.includes('first'), 'first file must appear in output');
  assert.ok(out.includes('second'), 'second file must appear in output');
  assert.ok(out.includes('2 posts'), 'sequence summary should count both posts');
  ok('regression: first file arg not dropped');

  // Single file must also work (was: dropped → "No input").
  const solo = execFileSync('node', [SCRIPT, join(dir, 'first.md')], { encoding: 'utf8' });
  assert.ok(solo.includes('first'), 'single file must analyze, not report No input');
  ok('regression: single file arg analyzes');
} finally {
  rmSync(dir, { recursive: true, force: true });
}

console.log(`\n${passed} checks passed.`);
