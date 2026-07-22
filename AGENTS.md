# AGENTS.md

This file provides guidance to coding agents (Claude Code, opencode, and other Agent Skills–compatible tools) when working with code in this repository. `CLAUDE.md` is a symlink to this file.

## What This Is

Inkstone (硯台) is a Claude Code plugin — a collection of agent skills for creative and design workflows. It is installed via the Claude Code plugin marketplace (`/plugin marketplace add augchan42/inkstone`). There is no build step and no dependencies to install. The repo is almost entirely Markdown skill definitions, plus one piece of runtime shell: a Stop hook (`hooks/`) that enforces the plan-review-loop skill's lifecycle.

## Repository Structure

```
.claude-plugin/
  plugin.json          # Plugin manifest — name, version, "skills": "./skills"
  marketplace.json     # Marketplace listing metadata
hooks/
  hooks.json           # Auto-discovered by Claude Code — registers the Stop hook
  stop-hook.sh         # Enforces plan-review-loop completion; no-op when no loop is active
skills/
  <skill-name>/
    SKILL.md           # Skill definition (frontmatter + instructions)
    *.md               # Optional reference files loaded by the skill
examples/
  prompt-examples.md   # Validated reference prompts for ink painting & tech-noir modes
hkoscon-2026/
  hkoscon-2026-talk.html  # Self-contained static talk deck + image assets
  DEPLOY.md               # How to (re)deploy the deck to Vercel
```

## How Skills Work

Each skill is a `SKILL.md` with YAML frontmatter (`name`, `description`, `user-invocable`, `argument-hint`) followed by the full instruction set that Claude Code receives when the skill is invoked. Skills have no runtime code — they are prompt engineering documents that define behavior through instructions, examples, and rules.

When a skill has companion reference files (e.g., `blakean-scene/blakean-reference.md`, `ui-ux-architect/audit-dimensions.md`), the SKILL.md instructs the agent to read them at execution time.

## Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md` with the required frontmatter (`name` must match the directory name)
2. No `plugin.json` edit needed — `"skills": "./skills"` auto-discovers every subdirectory (Claude Code, opencode, and the Agent Skills spec all scan the folder)
3. Add it to the skills table in `README.md` under the appropriate category
4. Bump the version in `plugin.json` if publishing
5. Validate with `./validate-skills.sh` (checks frontmatter against the Agent Skills spec)

## The 17 Skills

### Creative

- **verse-to-prompt** — Converts classical Chinese verse into 50-60 word image generation prompts. Three modes: ink painting (default), stipple (`--stipple`, the production matrix skin — reuses the ink scene and only swaps the render suffix per ADR-173), and tech-noir (`--tech-noir`, an experimental CRT cyberpunk reinterpretation). Enforces 7 mandatory composition rules, 5 style categories, content safety substitution patterns, and disambiguation rules for ambiguous English words.
- **image-to-scene** — Converts ink paintings into video generation motion prompts — 5 motion categories, 6 motion rules, Seedance 2.0 API reference.
- **create-explanation** — Generates bilingual (English + Traditional Chinese) scholarly explanations of classical Chinese oracular verses. English 100-150 words, Chinese 150-200 characters.
- **blakean-scene** — Converts abstract symbolic concepts into 240-280 word Blakean embodied scene prompts using an 8-layer prompt architecture and 8 compositional patterns. Reads `blakean-reference.md` for pattern details.
- **shaughnessy-iching** — Interprets a Zhouyi (I Ching) hexagram or line in Edward Shaughnessy's de-mythologized late–Western Zhou register — divination-manual reading, not wisdom classic. Provenance-flagged, interpret-only (no casting).

### Design / UX

- **ui-ux-architect** — UI/UX audit against 13 dimensions with Jobs/Ive design philosophy. Uses mobile-mcp for live device inspection. Design-only scope — does not touch logic/state/APIs.
- **design-dna** — Extracts an abstract visual/motion blueprint (design DNA) from reference websites, or researches award-winning references from a vibe description. Observes and abstracts only — never implements.
- **motion-craft** — Implements professional web animations in a target repo against an approved design blueprint or explicit motion direction. Plans by default; modifies code only on explicit implement authority.
- **upgrade-site** — Orchestrates a full website design upgrade: snapshot → reference research via design-dna → direction synthesis → gap scoring → prioritized plan → implementation dispatch to motion-craft → verification.

### Engineering Process

- **plan-review-loop** — Adversarial review loop for implementation plans: locate or author the plan, then an independent multi-lane review (zero-context executability; grounding & traceability against the repo and the source spec; task structure & risk) via Codex CLI or context-blind subagents, then address findings with judgment. The source spec is reviewed transitively via the traceability lane. Supports superpowers plans (`docs/superpowers/plans/`), planning-with-files `task_plan.md`, Kiro `tasks.md`. Reviews land in `reviews/plan-review-<id>.md`; state in `.claude/plan-review-loop.local.md`; `cancel` argument clears an active loop. Completion is enforced by the Stop hook in `hooks/`.

### Productivity

- **media-kit** — Interactive multi-phase workflow: interview → write bios (4 lengths) → crop/process photos → generate page → bundle zip.
- **arxiv-search** — Queries the arXiv API (Atom XML) by topic, author, or paper ID. No auth needed.
- **analyze-variation** — Measures sentence- and post-length variation across a batch of social copy/drafts — deterministic Node script flags metronomic rhythm and same-size posts.
- **voice-calibration** — Interactive voice profiling via live terminal prompts. Asks 8 writing prompts (4 general, 4 domain-specific), collects raw typed responses, and distills a reusable voice profile capturing sentence rhythm, rhetorical habits, vocabulary, and tonal signature. Profiles saved to `skills/voice-calibration/profiles/`.

### Web / App Store / Video

- **nextjs-i18n-seo** — Diagnoses and fixes the 307→301 redirect bug in Next.js App Router i18n middleware that kills PageRank transfer.
- **market-pulse** — App Store market overview via web search — competitor movements, trending keywords, Apple featuring, new releases. No paid API subscriptions needed.
- **video-to-shorts** — Turns a long video into vertical shorts: transcribe, auto-suggest the best soundbites, cut, 9:16 crop, burn-in subtitles. Cross-platform (macOS/Linux/WSL); stops at an upload-ready mp4.

## Conference Slides (hkoscon-2026/)

`hkoscon-2026/` holds the "Teaching Taste to an Agent" talk deck — a self-contained static HTML file plus image assets, separate from the plugin itself. It's deployed to Vercel at https://hkoscon-2026-inkstone.vercel.app/ and is **not** git auto-deployed: pushing to `main` does not update the live site. To (re)deploy, follow `hkoscon-2026/DEPLOY.md`.

## Key Domain Knowledge

The ink painting skills encode methodology from generating 4,096 unique images for SixLines.online using `fal-ai/z-image/turbo`. Core insight: **style is not a suffix** — appending "Chinese ink painting style" to a prompt fails; instead, prompts must read like the caption under an ink painting, with painterly metaphors woven throughout. Same principle applies to tech-noir mode.

Content safety substitutions exist because 52 of 4,096 images failed generation filters. Violence from ancient texts is depicted through atmosphere and aftermath, never the act itself.

## The Stop Hook (hooks/)

`hooks/hooks.json` is auto-discovered by Claude Code (no plugin.json field needed) and runs `hooks/stop-hook.sh` on every Stop event, in every project where inkstone is installed. Conventions, mirrored from the review-loop plugin this design is based on:

- **Fast no-op:** the first check is for `.claude/plan-review-loop.local.md`; absent → immediate `{"decision":"approve"}`. The hook must stay cheap because it fires on every stop.
- **Coexistence:** if `.claude/review-loop.local.md` (the hamel-review/review-loop plugin's state) exists, approve immediately — that plugin's own stop hook drives the stop cycle. Never double-block. The plan-review-loop setup script also refuses to start while that loop is active.
- **Phase contract:** `locate`/`review` → block until the review file exists; `addressing` → block until `## Disposition` is in the review file, then approve + clean up (the skill sets `phase: confirm` *before* dispositioning when a critical finding was fixed, so this completion rule only fires when no confirmation is owed); `confirm` → block until `## Confirmation` is in the review file, then approve + clean up.
- **Fail-open:** on any error, malformed state, invalid `review_id` (validated against `^[0-9]{8}-[0-9]{6}-[0-9a-f]{6}$` to prevent path traversal), or exhausted block budget (at most 2 blocks per phase without a phase transition, tracked via `hook_blocks`/`hook_block_phase` in the state file, enforced only under `stop_hook_active`), clean up state and approve — never trap the user.
- **JSON-only stdout**, cross-platform shell (macOS + Linux), timestamped telemetry to `.claude/plan-review-loop.log`.
- After modifying `stop-hook.sh`, re-test every path with piped hook-input JSON: no-state, defer-to-original, review-phase block, block-budget fail-open, addressing block (no disposition), addressing approve (with disposition), confirm block (no verdict), confirm approve (with `## Confirmation`), invalid review_id, `active: false`, unknown phase. Verify each output with `jq .`.

## Conventions

- Prompts target 50-60 words (verse-to-prompt) or 240-280 words (blakean-scene) — stay within these ranges
- End ink painting prompts with "Chinese ink painting."; stipple (matrix skin) prompts reuse the ink scene and end with the luminous-stipple suffix ("Golden age science fiction stipple illustration, … phosphor-green and amber palette on black."); tech-noir prompts end with "phosphor-green tech-noir illustration, CRT scanlines, flat deep blacks, stylized graphic art, not photorealistic."
- Disambiguation is mandatory: write "crane bird" not "crane", "swallow bird" not "swallow", etc.
- Traditional Chinese (繁體中文) is used in bilingual outputs, not Simplified
- Bio writing avoids year counts ("enterprise architecture background" not "12 years of...")
