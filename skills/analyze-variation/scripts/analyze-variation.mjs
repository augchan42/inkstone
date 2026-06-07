#!/usr/bin/env node
/**
 * analyze-variation.mjs — deterministic sentence/post length-variation analyzer.
 *
 * The skill (SKILL.md) is just the wrapper that tells the agent to run THIS
 * script — all numbers are computed here in Node, not by the model. CJK-aware,
 * dependency-free (Node built-ins only). Voice-agnostic: it measures rhythm and
 * length spread; it does not enforce any house style (keep tone/voice rules in
 * your own project's style guide).
 *
 * Input modes:
 *   <file ...>        one or more files; each file = one post (sequence analysis)
 *   --md <glob ...>   same, explicit
 *   --text "..."      a single post inline
 *   (stdin)           a single post piped in
 *
 * Flags:
 *   --json            machine-readable output
 *   --write <path>    also emit a markdown report
 *
 * Examples:
 *   node analyze-variation.mjs posts/*.md
 *   pbpaste | node analyze-variation.mjs
 *   node analyze-variation.mjs --text "Short. A much longer sentence follows it."
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { basename } from 'node:path';

// Tunable heuristics — keep in sync with the canonical spec.
const MONOTONE_CV_THRESHOLD = 0.35; // sentence-length CV below this = monotone
const NEIGHBOR_SIMILARITY_THRESHOLD = 0.15; // adjacent posts within this = too similar
const FOLD = 280; // X in-timeline "Show more" fold (informational)

const CJK = /[㐀-鿿豈-﫿]/g;
const LATIN_WORD = /[A-Za-z0-9][A-Za-z0-9'’-]*/g;
const ABBR = new Set(['e.g.', 'i.e.', 'vs.', 'dr.', 'mr.', 'mrs.', 'etc.', 'st.', 'fig.']);

const round1 = (x) => Math.round(x * 10) / 10;
const round2 = (x) => Math.round(x * 100) / 100;

// --- pure functions (deterministic, no IO) --------------------------------

export function countTokens(s) {
  const latin = (s.match(LATIN_WORD) || []).length;
  const cjk = (s.match(CJK) || []).length;
  return latin + cjk;
}

export function weightedLen(s) {
  let n = 0;
  for (const ch of s) n += /[ᄀ-ᇿ⺀-﫿＀-￯]/.test(ch) ? 2 : 1;
  return n;
}

export function splitSentences(prose) {
  const flat = prose.replace(/\s+/g, ' ').trim();
  if (!flat) return [];
  const raw = flat.split(/(?<=[.!?。！？…])\s+/);
  const out = [];
  for (const piece of raw) {
    const prev = out[out.length - 1];
    const lastWord = (prev || '').split(' ').pop()?.toLowerCase();
    // Abbreviation guard: re-join when the previous chunk ended in a known abbr.
    if (prev && lastWord && ABBR.has(lastWord)) out[out.length - 1] = prev + ' ' + piece;
    else out.push(piece);
  }
  return out.map((s) => s.trim()).filter(Boolean);
}

export function mean(xs) {
  return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0;
}

export function stdev(xs) {
  if (!xs.length) return 0;
  const m = mean(xs);
  return Math.sqrt(xs.reduce((a, b) => a + (b - m) ** 2, 0) / xs.length);
}

export function analyzePost(body) {
  const lines = body.split('\n').map((l) => l.trim());
  const sigLines = lines.filter((l) => l.startsWith('>')).length;
  const prose = lines.filter((l) => l && !l.startsWith('>')).join(' ');
  const sentences = splitSentences(prose);
  const lens = sentences.map(countTokens);
  const m = mean(lens);
  const sd = stdev(lens);
  return {
    words: countTokens(prose),
    weighted: weightedLen(body),
    pastFold: Math.max(0, weightedLen(body) - FOLD),
    cjk: (body.match(CJK) || []).length,
    sentences: lens.length,
    meanSentenceWords: round1(m),
    stdevSentenceWords: round1(sd),
    cv: m ? round2(sd / m) : 0,
    minSentenceWords: lens.length ? Math.min(...lens) : 0,
    maxSentenceWords: lens.length ? Math.max(...lens) : 0,
    sigLines,
  };
}

export function flagPosts(posts) {
  const flags = [];
  for (const p of posts) {
    if (p.metrics.sentences >= 3 && p.metrics.cv < MONOTONE_CV_THRESHOLD) {
      flags.push({ type: 'monotone', label: p.label, cv: p.metrics.cv });
    }
  }
  for (let i = 1; i < posts.length; i++) {
    const a = posts[i - 1].metrics.weighted;
    const b = posts[i].metrics.weighted;
    const sim = Math.abs(a - b) / Math.max(a, b || 1);
    if (sim < NEIGHBOR_SIMILARITY_THRESHOLD) {
      flags.push({ type: 'neighbor', label: `${posts[i - 1].label} ↔ ${posts[i].label}`, a, b });
    }
  }
  return flags;
}

// --- IO helpers -----------------------------------------------------------

function stripMarkup(src) {
  return src
    .replace(/^---\n[\s\S]*?\n---\n/, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/^#+\s.*$/gm, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/[*_`]/g, '')
    .trim();
}

function render(posts, asJson) {
  const seq = posts.map((p) => p.metrics.weighted);
  const summary = {
    posts: posts.length,
    meanWeighted: round1(mean(seq)),
    stdevWeighted: round1(stdev(seq)),
    cv: mean(seq) ? round2(stdev(seq) / mean(seq)) : 0,
    min: seq.length ? Math.min(...seq) : 0,
    max: seq.length ? Math.max(...seq) : 0,
  };
  const flags = flagPosts(posts);
  if (asJson) return JSON.stringify({ posts, summary, flags }, null, 2);

  const lines = [];
  lines.push('post                              | wt  | sent | mean±sd  | cv');
  lines.push('----------------------------------|-----|------|----------|-----');
  for (const p of posts) {
    const m = p.metrics;
    lines.push(
      `${p.label.slice(0, 33).padEnd(33)} | ${String(m.weighted).padStart(3)} | ${String(m.sentences).padStart(4)} | ${String(m.meanSentenceWords).padStart(4)}±${String(m.stdevSentenceWords).padEnd(3)} | ${m.cv}`,
    );
  }
  if (posts.length > 1) {
    lines.push('');
    lines.push(
      `sequence: ${summary.posts} posts · mean ${summary.meanWeighted} · stdev ${summary.stdevWeighted} · spread(cv) ${summary.cv} · range ${summary.min}–${summary.max} (target cv ≥ 0.35)`,
    );
  }
  lines.push('');
  if (flags.length) {
    lines.push('flags:');
    for (const f of flags) {
      if (f.type === 'monotone') lines.push(`  ⚠ monotone rhythm: ${f.label} (cv ${f.cv})`);
      else lines.push(`  ⚠ too-similar neighbors: ${f.label} (${f.a} vs ${f.b} wt)`);
    }
  } else {
    lines.push('flags: none ✓');
  }
  return lines.join('\n');
}

// --- main -----------------------------------------------------------------

function main() {
  const argv = process.argv.slice(2);
  const asJson = argv.includes('--json');
  const writeIdx = argv.indexOf('--write');
  const writePath = writeIdx >= 0 ? argv[writeIdx + 1] : null;
  const textIdx = argv.indexOf('--text');

  let posts = [];
  if (textIdx >= 0) {
    posts = [{ label: 'inline', metrics: analyzePost(argv[textIdx + 1] || '') }];
  } else {
    // Exclude flags and the argument positions consumed by --write/--text.
    // (Indexing by position, not value, so the first file isn't dropped when
    // those flags are absent and writeIdx/textIdx are -1.)
    const consumed = new Set();
    if (writeIdx >= 0) consumed.add(writeIdx + 1);
    if (textIdx >= 0) consumed.add(textIdx + 1);
    const files = argv.filter((a, i) => !a.startsWith('--') && !consumed.has(i));
    if (files.length) {
      posts = files.map((f) => ({
        label: basename(f).replace(/\.(md|mdx)$/, ''),
        metrics: analyzePost(stripMarkup(readFileSync(f, 'utf8'))),
      }));
    } else {
      const stdin = readFileSync(0, 'utf8');
      if (!stdin.trim()) {
        console.error('No input. Pass files, --text "...", or pipe via stdin.');
        process.exit(1);
      }
      posts = [{ label: 'stdin', metrics: analyzePost(stripMarkup(stdin)) }];
    }
  }

  const out = render(posts, asJson);
  console.log(out);
  if (writePath) {
    const stamp = process.env.REPORT_DATE || 'unspecified date';
    writeFileSync(writePath, `# Variation report (${stamp})\n\n\`\`\`\n${render(posts, false)}\n\`\`\`\n`);
    console.error(`\nwrote ${writePath}`);
  }
}

// Run only as a CLI (allow importing the pure functions for tests).
if (import.meta.url === `file://${process.argv[1]}`) main();
