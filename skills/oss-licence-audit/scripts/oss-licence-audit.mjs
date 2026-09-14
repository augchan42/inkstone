// oss-licence-audit.mjs — manifest-based open-source licence inventory (v1).
// Dependency-free (Node built-ins only). Reads the target repo's manifests and
// installed packages, classifies each licence, and prints a Markdown report.
//
// What it does: inventory + triage. What it never does: legal conclusions.
// Every report ends with the gaps this scan cannot see and a handoff section
// for a lawyer. See ../SKILL.md and ../references/licence-classes.md.
//
// v1 scope: npm/pnpm/node (package.json + node_modules). Other ecosystems are
// reported as present-but-unscanned. No network calls — offline-safe.

import { readFileSync, existsSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

const CLASS_ORDER = ['permissive', 'weak-copyleft', 'strong-copyleft', 'network-copyleft'];
const CLASS_LABEL = {
  'permissive': 'Permissive',
  'weak-copyleft': 'Weak copyleft',
  'strong-copyleft': 'Strong copyleft',
  'network-copyleft': 'Network copyleft / source-available',
  'review': 'Needs review',
};

const PERMISSIVE = new Set([
  'MIT', 'ISC', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'BSD-3-Clause-Clear',
  'CC0-1.0', 'Unlicense', 'Python-2.0', '0BSD', 'Artistic-2.0', 'Zlib', 'BSL-1.0',
  'PostgreSQL', 'WTFPL', 'CC-BY-4.0', 'CC-BY-3.0', 'OpenSSL', 'PSF-2.0',
  'BlueOak-1.0.0',
]);
const WEAK = new Set([
  'LGPL-2.0', 'LGPL-2.0-only', 'LGPL-2.0-or-later', 'LGPL-2.1', 'LGPL-2.1-only',
  'LGPL-2.1-or-later', 'LGPL-3.0', 'LGPL-3.0-only', 'LGPL-3.0-or-later',
  'MPL-2.0', 'MPL-1.1', 'EPL-1.0', 'EPL-2.0', 'CDDL-1.0', 'CPL-1.0',
]);
const STRONG = new Set([
  'GPL-2.0', 'GPL-2.0-only', 'GPL-2.0-or-later', 'GPL-3.0', 'GPL-3.0-only',
  'GPL-3.0-or-later', 'GPL-1.0', 'GPL-1.0-only',
]);
const NETWORK = new Set([
  'AGPL-3.0', 'AGPL-3.0-only', 'AGPL-3.0-or-later', 'AGPL-1.0',
  'SSPL-1.0', 'Elastic-2.0', 'BUSL-1.1', 'Commons-Clause', 'Parity-7.0.0',
]);

function classifyToken(token) {
  const t = token.trim();
  if (!t) return null;
  const base = t.replace(/\+$/, ''); // "GPL-2.0+" -> "GPL-2.0"
  if (PERMISSIVE.has(base)) return 'permissive';
  if (WEAK.has(base)) return 'weak-copyleft';
  if (STRONG.has(base)) return 'strong-copyleft';
  if (NETWORK.has(base)) return 'network-copyleft';
  // Common non-SPDX spellings seen in package.json licence fields
  const lower = base.toLowerCase();
  if (lower === 'mit' || lower === 'isc' || lower === 'apache 2.0' || lower === 'apache-2' || lower === 'bsd') return 'permissive';
  if (lower.startsWith('apache license')) return 'permissive';
  return 'review';
}

// Strictest class wins for compound expressions ("MIT OR GPL-3.0" -> strong).
function classifyExpression(expr) {
  if (!expr || typeof expr !== 'string') return { cls: 'review', note: 'no licence field' };
  const parts = expr.split(/\s+(?:OR|AND)\s+|\s*\|\|\s*|\s*\/\s*/).map(p => p.replace(/\s*WITH\s+.*$/i, '').trim()).filter(Boolean);
  if (parts.length === 0) return { cls: 'review', note: 'unparseable licence field' };
  let worst = 'permissive';
  const unknown = [];
  for (const p of parts) {
    const c = classifyToken(p);
    if (c === 'review') unknown.push(p);
    if (CLASS_ORDER.indexOf(c) > CLASS_ORDER.indexOf(worst)) worst = c;
  }
  if (unknown.length > 0 && parts.length > 1) {
    return { cls: worst === 'permissive' ? 'review' : worst, note: `compound expression; unrecognised part: ${unknown.join(', ')}` };
  }
  if (unknown.length > 0) return { cls: 'review', note: `unrecognised licence id: ${unknown.join(', ')}` };
  if (parts.length > 1) return { cls: worst, note: `dual/compound: ${expr}` };
  return { cls: worst, note: '' };
}

function readJson(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return null;
  }
}

function licenceOfInstalled(pkgDir) {
  const pj = readJson(join(pkgDir, 'package.json'));
  if (!pj) return { version: '?', licence: '', cls: 'review', note: 'no package.json found' };
  const raw = typeof pj.license === 'string' ? pj.license
    : Array.isArray(pj.licenses) ? pj.licenses.map(l => l.type || l).join(' OR ')
    : '';
  const { cls, note } = classifyExpression(raw);
  return { version: pj.version || '?', licence: raw || '(none declared)', cls, note };
}

function isSkippableDir(name) {
  return name === '.bin' || name === '.pnpm' || name === '.modules.yaml' || name === '.cache';
}

// pnpm layout: node_modules/.pnpm/<name@ver>/node_modules/<name>/package.json
// (<name> is "@scope+name" for scoped packages)
function scanPnpmStore(target) {
  const found = new Map(); // key: name@version -> { name, version, dir }
  const store = join(target, 'node_modules', '.pnpm');
  if (!existsSync(store)) return found;
  for (const entry of readdirSync(store)) {
    if (entry.startsWith('.')) continue;
    const inner = join(store, entry, 'node_modules');
    if (!existsSync(inner)) continue;
    let subs;
    try { subs = readdirSync(inner); } catch { continue; }
    for (const sub of subs) {
      if (sub.startsWith('.')) continue;
      const at = sub.startsWith('@') ? join(inner, sub) : null;
      const candidates = at && existsSync(at) && statSync(at).isDirectory()
        ? readdirSync(at).map(n => ({ name: `${sub}/${n}`, dir: join(at, n) }))
        : [{ name: sub, dir: join(inner, sub) }];
      for (const { name, dir } of candidates) {
        const pj = readJson(join(dir, 'package.json'));
        const version = (pj && pj.version) || '?';
        const key = `${name}@${version}`;
        if (!found.has(key)) found.set(key, { name, version, dir });
      }
    }
  }
  return found;
}

// npm/yarn flat layout: node_modules/<name>/package.json (+ @scope/<name>)
function scanFlatModules(target) {
  const found = new Map();
  const mods = join(target, 'node_modules');
  if (!existsSync(mods)) return found;
  for (const entry of readdirSync(mods)) {
    if (entry.startsWith('.') || isSkippableDir(entry)) continue;
    const full = join(mods, entry);
    if (!existsSync(full) || !statSync(full).isDirectory()) continue;
    if (entry.startsWith('@')) {
      let subs;
      try { subs = readdirSync(full); } catch { continue; }
      for (const sub of subs) {
        const dir = join(full, sub);
        if (!statSync(dir).isDirectory()) continue;
        const pj = readJson(join(dir, 'package.json'));
        const version = (pj && pj.version) || '?';
        found.set(`${entry}/${sub}@${version}`, { name: `${entry}/${sub}`, version, dir });
      }
    } else {
      const pj = readJson(join(full, 'package.json'));
      const version = (pj && pj.version) || '?';
      found.set(`${entry}@${version}`, { name: entry, version, dir: full });
    }
  }
  return found;
}

function main() {
  const args = process.argv.slice(2).filter(a => !a.startsWith('--'));
  const cliFlags = process.argv.slice(2).filter(a => a.startsWith('--'));
  const target = resolve(args[0] || process.cwd());
  const asJson = cliFlags.includes('--json');
  const writeIdx = cliFlags.indexOf('--write');
  const writePath = writeIdx >= 0 ? resolve(process.argv.slice(2)[writeIdx + 1] || 'licence-audit.md') : null;

  const manifest = readJson(join(target, 'package.json'));
  const prodDeps = manifest ? Object.keys(manifest.dependencies || {}) : [];
  const devDeps = manifest ? Object.keys(manifest.devDependencies || {}) : [];
  const hasManifest = !!manifest;
  const hasLockfile = ['pnpm-lock.yaml', 'package-lock.json', 'yarn.lock', 'bun.lockb', 'npm-shrinkwrap.json']
    .some(f => existsSync(join(target, f)));
  const hasNodeModules = existsSync(join(target, 'node_modules'));

  // Other ecosystems: report presence, do not pretend to scan.
  const otherEcosystems = [];
  if (existsSync(join(target, 'requirements.txt')) || existsSync(join(target, 'pyproject.toml')) || existsSync(join(target, 'Pipfile'))) otherEcosystems.push('Python (requirements.txt/pyproject/Pipfile)');
  if (existsSync(join(target, 'go.mod'))) otherEcosystems.push('Go (go.mod)');
  if (existsSync(join(target, 'Cargo.toml'))) otherEcosystems.push('Rust (Cargo.toml)');
  if (existsSync(join(target, 'Gemfile'))) otherEcosystems.push('Ruby (Gemfile)');
  if (existsSync(join(target, 'composer.json'))) otherEcosystems.push('PHP (composer.json)');
  if (existsSync(join(target, 'Dockerfile')) || existsSync(join(target, 'docker-compose.yml'))) otherEcosystems.push('Docker (base images carry their own licences)');

  const noticeFiles = ['NOTICE', 'NOTICE.txt', 'NOTICE.md', 'THIRD-PARTY-NOTICES', 'THIRD-PARTY-NOTICES.md', 'THIRDPARTY.md']
    .filter(f => existsSync(join(target, f)));

  const installed = new Map([...scanPnpmStore(target), ...scanFlatModules(target)]);
  const prodSet = new Set(prodDeps);
  const devSet = new Set(devDeps);

  const rows = [];
  for (const [key, { name, version, dir }] of installed) {
    const { version: v, licence, cls, note } = licenceOfInstalled(dir);
    const scope = prodSet.has(name) ? 'prod' : devSet.has(name) ? 'dev' : 'transitive';
    rows.push({ name, version: v !== '?' ? v : version, scope, licence, cls, note });
  }
  rows.sort((a, b) => CLASS_ORDER.indexOf(b.cls) - CLASS_ORDER.indexOf(a.cls) || a.name.localeCompare(b.name));

  const count = cls => rows.filter(r => r.cls === cls).length;
  const flags = [];
  for (const r of rows.filter(r => r.cls === 'network-copyleft' && r.scope === 'prod')) {
    flags.push({ level: 'HIGH', text: `${r.name}@${r.version} is ${r.licence} in production dependencies. Network copyleft can oblige source disclosure for hosted use. Confirm integration and distribution model with counsel before shipping.` });
  }
  for (const r of rows.filter(r => r.cls === 'strong-copyleft' && r.scope === 'prod')) {
    flags.push({ level: 'HIGH', text: `${r.name}@${r.version} is ${r.licence} in production dependencies. Strong copyleft can oblige disclosing the combined work's source on distribution. Confirm how it is linked and distributed with counsel before shipping.` });
  }
  for (const r of rows.filter(r => r.cls === 'weak-copyleft' && r.scope === 'prod')) {
    flags.push({ level: 'MEDIUM', text: `${r.name}@${r.version} is ${r.licence} in production dependencies. Weak copyleft usually allows proprietary combination but requires notices and sometimes source of the component itself. Confirm with counsel.` });
  }
  for (const r of rows.filter(r => r.cls === 'weak-copyleft' && r.scope !== 'prod')) {
    flags.push({ level: 'MEDIUM', text: `${r.name}@${r.version} is ${r.licence} (${r.scope}). Confirm whether it ships in your distribution — server bundles and container images count. If it ships, the component's source offer and notices apply.` });
  }
  for (const r of rows.filter(r => (r.cls === 'network-copyleft' || r.cls === 'strong-copyleft') && r.scope !== 'prod')) {
    flags.push({ level: 'MEDIUM', text: `${r.name}@${r.version} is ${r.licence} (${r.scope}). Lower risk, but confirm it is genuinely not bundled or shipped — build tooling sometimes leaks into bundles.` });
  }
  const reviewRows = rows.filter(r => r.cls === 'review');
  if (reviewRows.length > 0) {
    flags.push({ level: 'REVIEW', text: `${reviewRows.length} package(s) need a human look: ${reviewRows.slice(0, 12).map(r => r.name).join(', ')}${reviewRows.length > 12 ? ` (+${reviewRows.length - 12} more)` : ''}. Undeclared or unrecognised licences are the most common source of surprises.` });
  }
  if (noticeFiles.length === 0 && rows.some(r => r.scope === 'prod')) {
    flags.push({ level: 'HYGIENE', text: 'No NOTICE or third-party-attributions file found. Even permissive licences (MIT, Apache-2.0, BSD) require attribution in the shipped product.' });
  }
  if (!hasLockfile) {
    flags.push({ level: 'HYGIENE', text: 'No lockfile found. Without one, the shipped dependency tree — and therefore this inventory — is not reproducible.' });
  }

  const report = {
    target,
    manifest: hasManifest ? 'package.json' : 'none found',
    lockfile: hasLockfile,
    node_modules: hasNodeModules,
    counts: {
      total: rows.length,
      prod: rows.filter(r => r.scope === 'prod').length,
      dev: rows.filter(r => r.scope === 'dev').length,
      transitive: rows.filter(r => r.scope === 'transitive').length,
      permissive: count('permissive'),
      weakCopyleft: count('weak-copyleft'),
      strongCopyleft: count('strong-copyleft'),
      networkCopyleft: count('network-copyleft'),
      needsReview: count('review'),
    },
    otherEcosystems,
    noticeFiles,
    flags,
    inventory: rows,
  };

  let out;
  if (asJson) {
    out = JSON.stringify(report, null, 2);
  } else {
    const L = [];
    L.push(`# OSS licence inventory — ${target}`);
    L.push('');
    L.push(`Manifest: ${report.manifest} · lockfile: ${hasLockfile ? 'yes' : 'NO'} · node_modules scanned: ${hasNodeModules ? 'yes' : 'NO'}`);
    L.push(`Packages: ${report.counts.total} total (${report.counts.prod} prod, ${report.counts.dev} dev, ${report.counts.transitive} transitive)`);
    L.push(`Permissive ${report.counts.permissive} · weak copyleft ${report.counts.weakCopyleft} · strong copyleft ${report.counts.strongCopyleft} · network copyleft ${report.counts.networkCopyleft} · needs review ${report.counts.needsReview}`);
    L.push('');
    if (otherEcosystems.length > 0) {
      L.push(`Other ecosystems present but NOT scanned by this script (v1 is npm-only): ${otherEcosystems.join('; ')}.`);
      L.push('');
    }
    L.push('## Flags');
    L.push('');
    if (flags.length === 0) L.push('None. No copyleft in production scope, no unrecognised licences, attribution file present.');
    for (const f of flags) L.push(`- **[${f.level}]** ${f.text}`);
    L.push('');
    L.push('## Inventory');
    L.push('');
    L.push('| Package | Version | Scope | Licence | Class | Note |');
    L.push('|---|---|---|---|---|---|');
    for (const r of rows) {
      L.push(`| ${r.name} | ${r.version} | ${r.scope} | ${r.licence} | ${CLASS_LABEL[r.cls]} | ${r.note} |`);
    }
    L.push('');
    L.push('## What this scan cannot see (state these to the client, do not silently accept them)');
    L.push('');
    L.push('- Vendored or copy-pasted code with no package entry (the classic miss).');
    L.push('- Bundled frontend JavaScript and anything baked into Docker images or mobile builds.');
    L.push('- Dual-licensing and commercial exceptions (requires reading the actual terms, not the SPDX id).');
    L.push('- Whether a copyleft component forms a combined/derivative work with proprietary code (architecture question, not a scanner question).');
    L.push('- Licence changes between the scanned version and what actually ships.');
    L.push('');
    L.push('## Lawyer handoff');
    L.push('');
    L.push('Send counsel: this inventory, the repo at a pinned commit, and answers to: SaaS-only or also distributed (on-prem, mobile, containers, OEM)? How is each flagged component integrated (linked, vendored, separate process, API)? Any modified OSS shipped to customers?');
    L.push('');
    L.push('_This inventory is a technical input to legal review, not a legal opinion. Licence interpretation and the combined-work question belong to a lawyer._');
    out = L.join('\n');
  }

  if (writePath) writeFileSync(writePath, out);
  else process.stdout.write(out + '\n');
}

main();
