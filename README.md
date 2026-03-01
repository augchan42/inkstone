# Inkstone 硯台

**Custom Claude Code skills by Augustin Chan.**

A collection of agent skills for creative and design workflows, built for [Claude Code](https://claude.ai/code).

## Install

```shell
/plugin marketplace add augchan42/inkstone
/plugin install inkstone@augchan42-inkstone
```

## Skills

### Creative

| Skill | Description |
|-------|-------------|
| **verse-to-prompt** | Generate Chinese ink painting prompts from classical verse — 7 composition rules, 5 style categories, content safety patterns |
| **create-explanation** | Produce bilingual scholarly explanations for Jiaoshi Yilin verses |

### Design / UX

| Skill | Description |
|-------|-------------|
| **ui-ux-architect** | Premium UI/UX audit with Jobs/Ive philosophy — visual hierarchy, spacing, typography, color, motion, accessibility, dark mode |

## Background

### Ink Painting Skills

The ink painting skills are the methodology behind [SixLines.online](https://sixlines.online)'s image pipeline — 4,096 unique ink paintings generated from Han dynasty oracular poetry (the Jiaoshi Yilin, 焦氏易林, ~40 BCE). These rules were developed iteratively across four rounds of testing and refined through generating the full corpus.

The name comes from the inkstone (硯台), one of the Four Treasures of the Study (文房四寶) — the tool you grind ink on before painting.

- Blog post: [Teaching Taste to an Agent](https://augustinchan.dev/posts/teaching-taste-to-agents-yilin-image-pipeline)
- Sample output: [SixLines.online — Hexagram 14](https://sixlines.online/en/hexagrams/14)
- Product: [SixLines.online](https://sixlines.online) — I-Ching reference and Chinese almanac for iOS

### UI/UX Architect

A design audit skill that evaluates screens against 13 dimensions (visual hierarchy, spacing, typography, color, alignment, components, iconography, motion, states, dark mode, density, responsiveness, accessibility). Uses mobile-mcp for live device inspection.

## License

MIT
