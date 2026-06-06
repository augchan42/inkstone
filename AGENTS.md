# AGENTS.md

This file provides guidance to coding agents (Claude Code, opencode, and other Agent Skills–compatible tools) when working with code in this repository. `CLAUDE.md` is a symlink to this file.

## What This Is

Inkstone (硯台) is a Claude Code plugin — a collection of agent skills for creative and design workflows. It is installed via the Claude Code plugin marketplace (`/plugin marketplace add augchan42/inkstone`). There is no build step, no tests, no dependencies to install. The repo is pure Markdown skill definitions.

## Repository Structure

```
.claude-plugin/
  plugin.json          # Plugin manifest — name, version, "skills": "./skills"
  marketplace.json     # Marketplace listing metadata
skills/
  <skill-name>/
    SKILL.md           # Skill definition (frontmatter + instructions)
    *.md               # Optional reference files loaded by the skill
examples/
  prompt-examples.md   # Validated reference prompts for ink painting & tech-noir modes
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

## The 10 Skills

- **verse-to-prompt** — Converts classical Chinese verse into 50-60 word image generation prompts. Three modes: ink painting (default), stipple (`--stipple`, the production matrix skin — reuses the ink scene and only swaps the render suffix per ADR-173), and tech-noir (`--tech-noir`, an experimental CRT cyberpunk reinterpretation). Enforces 7 mandatory composition rules, 5 style categories, content safety substitution patterns, and disambiguation rules for ambiguous English words.
- **image-to-scene** — Converts ink paintings into video generation motion prompts — 5 motion categories, 6 motion rules, Seedance 2.0 API reference.
- **create-explanation** — Generates bilingual (English + Traditional Chinese) scholarly explanations of classical Chinese oracular verses. English 100-150 words, Chinese 150-200 characters.
- **blakean-scene** — Converts abstract symbolic concepts into 240-280 word Blakean embodied scene prompts using an 8-layer prompt architecture and 8 compositional patterns. Reads `blakean-reference.md` for pattern details.
- **ui-ux-architect** — UI/UX audit against 13 dimensions with Jobs/Ive design philosophy. Uses mobile-mcp for live device inspection. Design-only scope — does not touch logic/state/APIs.
- **media-kit** — Interactive multi-phase workflow: interview → write bios (4 lengths) → crop/process photos → generate page → bundle zip.
- **arxiv-search** — Queries the arXiv API (Atom XML) by topic, author, or paper ID. No auth needed.
- **nextjs-i18n-seo** — Diagnoses and fixes the 307→301 redirect bug in Next.js App Router i18n middleware that kills PageRank transfer.
- **market-pulse** — App Store market overview via web search — competitor movements, trending keywords, Apple featuring, new releases. No paid API subscriptions needed.
- **voice-calibration** — Interactive voice profiling via live terminal prompts. Asks 8 writing prompts (4 general, 4 domain-specific), collects raw typed responses, and distills a reusable voice profile capturing sentence rhythm, rhetorical habits, vocabulary, and tonal signature. Profiles saved to `skills/voice-calibration/profiles/`.

## Key Domain Knowledge

The ink painting skills encode methodology from generating 4,096 unique images for SixLines.online using `fal-ai/z-image/turbo`. Core insight: **style is not a suffix** — appending "Chinese ink painting style" to a prompt fails; instead, prompts must read like the caption under an ink painting, with painterly metaphors woven throughout. Same principle applies to tech-noir mode.

Content safety substitutions exist because 52 of 4,096 images failed generation filters. Violence from ancient texts is depicted through atmosphere and aftermath, never the act itself.

## Conventions

- Prompts target 50-60 words (verse-to-prompt) or 240-280 words (blakean-scene) — stay within these ranges
- End ink painting prompts with "Chinese ink painting."; stipple (matrix skin) prompts reuse the ink scene and end with the luminous-stipple suffix ("Golden age science fiction stipple illustration, … phosphor-green and amber palette on black."); tech-noir prompts end with "phosphor-green tech-noir illustration, CRT scanlines, flat deep blacks, stylized graphic art, not photorealistic."
- Disambiguation is mandatory: write "crane bird" not "crane", "swallow bird" not "swallow", etc.
- Traditional Chinese (繁體中文) is used in bilingual outputs, not Simplified
- Bio writing avoids year counts ("enterprise architecture background" not "12 years of...")
